from __future__ import annotations
import asyncio
import logging
import inspect
from typing import TYPE_CHECKING, Callable, Awaitable, Dict, List, Tuple, Any, Union
from magic_filter import MagicFilter
from trueconf.filters.base import Event
from trueconf.filters.base import Filter
from trueconf.filters.instance_of import InstanceOfFilter
from trueconf.filters.method import MethodFilter
from trueconf.types.message import Message
from trueconf.types.requests.added_chat_participant import AddedChatParticipant
from trueconf.types.requests.changed_file_upload_limits import ChangedFileUploadLimits
from trueconf.types.requests.changed_participant_role import ChangedParticipantRole
from trueconf.types.requests.cleared_chat_history import ClearedChatHistory
from trueconf.types.requests.created_channel import CreatedChannel
from trueconf.types.requests.created_favorites_chat import CreatedFavoritesChat
from trueconf.types.requests.created_group_chat import CreatedGroupChat
from trueconf.types.requests.created_personal_chat import CreatedPersonalChat
from trueconf.types.requests.edited_chat_avatar import EditedChatAvatar
from trueconf.types.requests.edited_chat_title import EditedChatTitle
from trueconf.types.requests.edited_message import EditedMessage
from trueconf.types.requests.removed_chat import RemovedChat
from trueconf.types.requests.removed_chat_participant import RemovedChatParticipant
from trueconf.types.requests.removed_message import RemovedMessage
from trueconf.types.requests.uploading_progress import UploadingProgress

if TYPE_CHECKING:
    from trueconf.middleware import BaseMiddleware

logger = logging.getLogger("chat_bot")

Handler = Callable[..., Awaitable[None]]
FilterLike = Union[Filter, MagicFilter, Callable[[Event], bool], Callable[[Event], Awaitable[bool]], Any]


class Router:
    """
        Event router for handling incoming events in a structured and extensible way.

        A `Router` allows you to register event handlers with specific filters,
        such as message types, chat events, or custom logic.

        You can also include nested routers using `include_router()` to build modular and reusable event structures.

        Handlers can be registered for:

        - Messages (`@<router>.message(...)`)
        - Chat creation events (`@<router>.created_personal_chat()`, `@<router>.created_group_chat()`, `@<router>.created_channel()`)
        - Participant events (`@<router>.added_chat_participant()`, `@<router>.removed_chat_participant()`)
        - Message lifecycle events (`@<router>.edited_message()`, `@<router>.removed_message()`)
        - File upload events (`@<router>.uploading_progress()`)
        - Removed chats (`@<router>.removed_chat()`)

        Example:

        ```python
        router = Router()

        @router.message(F.text == "hello")
        async def handle_hello(msg: Message):
            await msg.answer("Hi there!")
        ```

        If you have multiple routers, use `.include_router()` to add them to a parent router.
        """

    def __init__(
        self,
        name: str | None = None,
        allow_child_on_event: bool = False,
        _parent: "Router | None" = None,
    ):
        self.name = name or hex(id(self))
        self.allow_child_on_event = allow_child_on_event
        self._parent: Router | None = _parent
        self._handlers: List[Tuple[Tuple[FilterLike, ...], Handler]] = []
        self._subrouters: List["Router"] = []
        self._outer_middlewares: List["BaseMiddleware"] = []
        self._inner_middlewares: List["BaseMiddleware"] = []

    def _iter_all(self) -> List["Router"]:
        """Return a list of this router and all nested subrouters recursively."""
        out = [self]
        for child in self._subrouters:
            out.extend(child._iter_all())
        return out

    def _ancestors_with_self(self) -> List["Router"]:
        """Return routers from root ancestor down to self."""
        chain: list[Router] = []
        current: Router | None = self
        while current is not None:
            chain.append(current)
            current = current._parent
        chain.reverse()
        return chain

    def _collect_middlewares(
        self, attr: str
    ) -> List["BaseMiddleware"]:
        """Collect middlewares from ancestors → self."""
        result: list[BaseMiddleware] = []
        for router in self._ancestors_with_self():
            result.extend(getattr(router, attr, []))
        return result

    def outer_middleware(self, middleware: "BaseMiddleware") -> None:
        """Register outer middleware (runs before filter/handler matching)."""
        self._outer_middlewares.append(middleware)

    def inner_middleware(self, middleware: "BaseMiddleware") -> None:
        """Register inner middleware (runs after filter match, before handler)."""
        self._inner_middlewares.append(middleware)

    def _register(self, filters: Tuple[FilterLike, ...]):
        """Internal decorator for registering handlers with filters."""
        # Sugar: State instances are auto-wrapped with StateFilter
        from trueconf.fsm.filters import StateFilter
        from trueconf.fsm.state import State
        filters = tuple(
            StateFilter(f) if isinstance(f, State) else f
            for f in filters
        )

        def decorator(func: Handler):
            async def async_wrapper(evt: Event, **kwargs: Any):
                sig = inspect.signature(func)
                accepted_params = sig.parameters.keys()
                filtered_kwargs = {k: v for k, v in kwargs.items() if k in accepted_params}
                await func(evt, **filtered_kwargs)

            self._handlers.append((filters, async_wrapper))
            return async_wrapper

        return decorator

    async def _feed(self, event: Event, data: Dict[str, Any]) -> bool:
        """Feed an incoming event to the router and invoke the first matching handler.

        Pipeline:
            outer_middleware → filter match → inner_middleware → handler

        Returns:
            True  — event was handled or blocked by outer middleware.
            False — no handler matched and outer middleware did not block;
                    the dispatcher may try the next router.
        """
        logger.info("📥 Incoming event: %s", event)

        outer_passed = False
        handler_found = False

        async def _core(evt: Event, ctx: Dict[str, Any]) -> None:
            nonlocal outer_passed, handler_found
            outer_passed = True

            # --- filter search ---
            for flts, handler in self._handlers:
                if not flts:
                    handler_found = True
                    self._spawn(handler, evt, "<none>")
                    return

                matched = True
                kwargs: dict[str, Any] = {}
                for f in flts:
                    try:
                        result = await self._apply_filter(f, evt, ctx)
                    except Exception as e:
                        logger.exception("Filter %s error: %s", type(f).__name__, e)
                        matched = False
                        break

                    if not result:
                        matched = False
                        break

                    if isinstance(result, dict):
                        kwargs.update(result)

                if matched:
                    handler_found = True
                    filters_str = ", ".join(
                        getattr(f, "__name__", type(f).__name__) if callable(f) else type(f).__name__
                        for f in flts
                    )

                    # Merge data dict (bot, state, etc.) with filter-returned kwargs
                    all_kwargs: dict[str, Any] = {**ctx, **kwargs}

                    # --- build inner chain: inner_mw → handler ---
                    async def _inner_base(ievt: Event, ictx: Dict[str, Any]) -> None:
                        self._spawn(handler, ievt, filters_str, **all_kwargs)

                    inner_chain: Callable[[Event, Dict[str, Any]], Awaitable[None]] = _inner_base
                    for mw in reversed(self._collect_middlewares("_inner_middlewares")):
                        nxt = inner_chain
                        inner_chain = self._wrap_middleware(mw, nxt)

                    await inner_chain(evt, ctx)
                    return

        # --- wrap with outer middlewares ---
        chain: Callable[[Event, Dict[str, Any]], Awaitable[None]] = _core
        for mw in reversed(self._collect_middlewares("_outer_middlewares")):
            nxt = chain
            chain = self._wrap_middleware(mw, nxt)

        await chain(event, data)

        if not outer_passed:
            # Outer middleware blocked — event consumed
            return True
        if not handler_found:
            # No handler matched — try next router
            return False
        return True

    @staticmethod
    def _wrap_middleware(
        mw: "BaseMiddleware",
        nxt: Callable[[Event, Dict[str, Any]], Awaitable[None]],
    ) -> Callable[[Event, Dict[str, Any]], Awaitable[None]]:
        async def wrapped(evt: Event, ctx: Dict[str, Any]) -> None:
            await mw(nxt, evt, ctx)
        return wrapped

    def _spawn(self, handler: Handler, event: Event, filters_str: str, **kwargs: dict[str, Any]):
        """Internal method to spawn a task for executing the matched handler."""
        name = getattr(handler, "__name__", "<handler>")
        logger.info(f"[router:{self.name}] matched handler={name} filters=[{filters_str}]")

        async def _run():
            try:
                await handler(event, **kwargs)
            except Exception as e:
                logger.exception(f"Handler {name} failed: {e}")

        asyncio.create_task(_run())

    async def _apply_filter(self, f: Filter | Any, event: Event, data: dict[str, Any] | None = None) -> bool:
        """Evaluate a filter against the event, passing matching kwargs from data."""
        data = data or {}

        if isinstance(f, MagicFilter):
            try:
                return bool(f.resolve(event))
            except Exception:
                return False

        # Resolve which kwargs from data the filter accepts
        kwargs: dict[str, Any] = {}
        has_var_kwargs = False
        try:
            sig = inspect.signature(f)
            for name, param in sig.parameters.items():
                if param.kind == inspect.Parameter.VAR_KEYWORD:
                    has_var_kwargs = True
                    continue
                if name in data and param.kind in (
                    inspect.Parameter.POSITIONAL_OR_KEYWORD,
                    inspect.Parameter.KEYWORD_ONLY,
                ):
                    kwargs[name] = data[name]
        except (ValueError, TypeError):
            pass

        # If filter accepts **kwargs, pass all remaining data
        if has_var_kwargs:
            kwargs.update({k: v for k, v in data.items() if k not in kwargs})

        # Regular filters: let exceptions propagate (config errors must be explicit)
        res = f(event, **kwargs) if kwargs else f(event)

        if inspect.isawaitable(res):
            res = await res

        if isinstance(res, (bool, dict)):
            return res
        return bool(res)

    def include_router(self, router: "Router") -> None:
        """Include a child router for hierarchical event routing."""
        router._parent = self
        self._subrouters.append(router)

    def event(self, method: str, *filters: FilterLike):
        """
            Register a handler for a generic event type, filtered by method name.

            Examples:
                >>> @r.event(F.method == "SendMessage")
                >>> async def handle_message(msg: Message): ...

        """
        mf = MethodFilter(method)
        return self._register((mf, *filters))

    def message(self, *filters: FilterLike):
        """Register a handler for incoming `Message` events."""
        return self._register((InstanceOfFilter(Message), *filters))

    def uploading_progress(self, *filters: FilterLike):
        """Register a handler for file uploading progress events."""
        return self._register((InstanceOfFilter(UploadingProgress), *filters))

    def changed_participant_role(self, *filters: FilterLike):
        """
            **Requires TrueConf Server 5.5.2+**
            Registers a handler for participant role change events in chats.

            This handler is triggered when a user's role is changed in a personal chat, group chat, channel,
            or conference chat. Used with the `ChangedParticipantRole` event type.

            Source:
                https://trueconf.com/docs/chatbot-connector/en/chats/#changedParticipantRole

            Args:
                *filters (FilterLike): Optional filters to apply to the event. Multiple filters can be specified.

            Returns:
                Callable: A decorator function for registering the handler.

            Example:
                ```python
                from trueconf.enums import ChatParticipantRole as role
                from trueconf.types import ChangedParticipantRole

                @router.changed_participant_role()
                async def on_role_changed(event: ChangedParticipantRole):
                    if event.role == role.admin:
                        print(f"{event.user_id} has been promoted to admin in chat {event.chat_id}")
                ```
            """
        return self._register((InstanceOfFilter(ChangedParticipantRole), *filters))

    def changed_file_upload_limits(self, *filters: FilterLike):
        """

            **Requires TrueConf Server 5.5.3+**
            Registers a handler for file upload limits change events.

            This handler is triggered when the server's file upload restrictions are updated.
            The event is represented by the `ChangedFileUploadLimits` type and may include:

            - `max_size` — the maximum allowed file size in bytes (`1 MB = 1000 bytes`).
              If the size limit is disabled, the value is `None`.
            - `extensions` — file extension restrictions. If extension filtering is disabled,
              the value is `None`.

            If `extensions` is provided, it contains:
            - `mode` — restriction mode:
              - `block` — blocked extensions (blacklist)
              - `allow` — allowed extensions (whitelist)
            - `list` — list of file extensions.

            Source:
                https://trueconf.com/docs/chatbot-connector/en/files/#newFileUploadLimits

            Args:
                *filters (FilterLike): Optional filters to apply to the event. Multiple filters can be specified.

            Returns:
                Callable: A decorator function for registering the handler.

            Example:
                ```python
                from trueconf.types import ChangedFileUploadLimits
                @router.changed_file_upload_limits()
                async def on_limits_changed(event: ChangedFileUploadLimits):
                    print(f"Max file size: {event.max_size}")
                    if event.extensions:
                        print(f"Mode: {event.extensions.mode}")
                        print(f"Extensions: {event.extensions.list}")
                ```
        """
        return self._register((InstanceOfFilter(ChangedFileUploadLimits), *filters))

    def cleared_chat_history(self, *filters: FilterLike):
        """
            **Requires TrueConf Server 5.5.3+**
            Registers a handler for chat history clearing events.

            This handler is triggered when the message history of a chat is cleared.
            Used with the `ClearedChatHistory` event type.

            Source:
                https://trueconf.com/docs/chatbot-connector/en/chats/#clearedHistory

            Args:
                *filters (FilterLike): Optional filters to apply to the event. Multiple filters can be specified.

            Returns:
                Callable: A decorator function for registering the handler.

            Example:
                ```python
                from trueconf.types import ClearedChatHistory
                @router.cleared_chat_history()
                async def on_history_cleared(event: ClearedChatHistory):
                    print(f"History was cleared in chat {event.chat_id}. For all: {event.for_all}")

                ```
            """
        return self._register((InstanceOfFilter(ClearedChatHistory), *filters))

    def created_personal_chat(self, *filters: FilterLike):
        """Register a handler for personal chat creation events."""
        return self._register((InstanceOfFilter(CreatedPersonalChat), *filters))

    def created_group_chat(self, *filters: FilterLike):
        """Register a handler for group chat creation events."""
        return self._register((InstanceOfFilter(CreatedGroupChat), *filters))

    def created_favorites_chat(self, *filters: FilterLike):
        """**Requires TrueConf Server 5.5.2+**. Register a handler for favorites chat creation events."""
        return self._register((InstanceOfFilter(CreatedFavoritesChat), *filters))

    def created_channel(self, *filters: FilterLike):
        """Register a handler for channel creation events."""
        return self._register((InstanceOfFilter(CreatedChannel), *filters))

    def added_chat_participant(self, *filters: FilterLike):
        """Register a handler when a participant is added to a chat."""
        return self._register((InstanceOfFilter(AddedChatParticipant), *filters))

    def removed_chat_participant(self, *filters: FilterLike):
        """Register a handler when a participant is removed from a chat."""
        return self._register((InstanceOfFilter(RemovedChatParticipant), *filters))

    def removed_chat(self, *filters: FilterLike):
        """Register a handler when a chat is removed."""
        return self._register((InstanceOfFilter(RemovedChat), *filters))

    def edited_message(self, *filters: FilterLike):
        """Register a handler for message edit events."""
        return self._register((InstanceOfFilter(EditedMessage), *filters))

    def edited_chat_avatar(self, *filters: FilterLike):
        """

            **Requires TrueConf Server 5.5.3+**
            Registers a handler for chat avatar edit events.

            This handler is triggered when a chat avatar is changed.
            Used with the `EditedChatAvatar` event type.

            Source:
                https://trueconf.com/docs/chatbot-connector/en/chats/#editedChatAvatar

            Args:
                *filters (FilterLike): Optional filters to apply to the event. Multiple filters can be specified.

            Returns:
                Callable: A decorator function for registering the handler.

            Example:
                ```python
                from trueconf.types import EditedChatAvatar
                @router.edited_chat_avatar()
                async def on_avatar_changed(event: EditedChatAvatar):
                    print(f"Avatar was updated in chat {event.chat_id}")
                    print(f"New avatar: {event.avatar_url}")
                ```
        """
        return self._register((InstanceOfFilter(EditedChatAvatar), *filters))

    def edited_chat_title(self, *filters: FilterLike):
        """
            **Requires TrueConf Server 5.5.3+**
            Registers a handler for chat title edit events.

            This handler is triggered when a chat title is changed.
            Used with the `EditedChatTitle` event type.

            Source:
                https://trueconf.com/docs/chatbot-connector/en/chats/#editedChatTitle

            Args:
                *filters (FilterLike): Optional filters to apply to the event. Multiple filters can be specified.

            Returns:
                Callable: A decorator function for registering the handler.

            Example:
                ```python
                from trueconf.types import EditedChatTitle
                @router.edited_chat_title()
                async def on_title_changed(event: EditedChatTitle):
                    print(f"Chat {event.chat_id} has a new title: {event.title}")
                ```
        """
        return self._register((InstanceOfFilter(EditedChatTitle), *filters))

    def removed_message(self, *filters: FilterLike):
        """Register a handler for message deletion events."""
        return self._register((InstanceOfFilter(RemovedMessage), *filters))
