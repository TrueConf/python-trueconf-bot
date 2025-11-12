from __future__ import annotations
import asyncio
import logging
import inspect
from typing import Callable, Awaitable, List, Tuple, Any, Union
from magic_filter import MagicFilter
from trueconf.filters.base import Event
from trueconf.filters.base import Filter
from trueconf.filters.instance_of import InstanceOfFilter
from trueconf.filters.method import MethodFilter
from trueconf.types.message import Message
from trueconf.types.requests.added_chat_participant import AddedChatParticipant
from trueconf.types.requests.changed_participant_role import ChangedParticipantRole
from trueconf.types.requests.created_channel import CreatedChannel
from trueconf.types.requests.created_favorites_chat import CreatedFavoritesChat
from trueconf.types.requests.created_group_chat import CreatedGroupChat
from trueconf.types.requests.created_personal_chat import CreatedPersonalChat
from trueconf.types.requests.edited_message import EditedMessage
from trueconf.types.requests.removed_chat import RemovedChat
from trueconf.types.requests.removed_chat_participant import RemovedChatParticipant
from trueconf.types.requests.removed_message import RemovedMessage
from trueconf.types.requests.uploading_progress import UploadingProgress

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

    def __init__(self, name: str | None = None, stop_on_first: bool = True):

        self.name = name or hex(id(self))
        self.stop_on_first = stop_on_first
        self._handlers: List[Tuple[Tuple[FilterLike, ...], Handler]] = []
        self._subrouters: List["Router"] = []

    def include_router(self, router: "Router") -> None:
        """Include a child router for hierarchical event routing."""
        self._subrouters.append(router)

    def _iter_all(self) -> List["Router"]:
        """Return a list of this router and all nested subrouters recursively."""
        out = [self]
        for child in self._subrouters:
            out.extend(child._iter_all())
        return out

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

    def removed_message(self, *filters: FilterLike):
        """Register a handler for message deletion events."""
        return self._register((InstanceOfFilter(RemovedMessage), *filters))

    def _register(self, filters: Tuple[FilterLike, ...]):
        """Internal decorator for registering handlers with filters."""

        def decorator(func: Handler):
            async def async_wrapper(evt: Event, **kwargs: Any):
                sig = inspect.signature(func)
                accepted_params = sig.parameters.keys()
                filtered_kwargs = {k: v for k, v in kwargs.items() if k in accepted_params}
                await func(evt, **filtered_kwargs)

            self._handlers.append((filters, async_wrapper))
            return async_wrapper

        return decorator

    async def _feed(self, event: Event) -> bool:
        """Feed an incoming event to the router and invoke the first matching handler."""
        logger.info(f"📥 Incoming event: {event}")
        for flts, handler in self._handlers:

            if not flts:
                self._spawn(handler, event, "<none>")
                return True

            matched = True
            for f in flts:
                try:
                    if not await self._apply_filter(f, event):
                        matched = False
                        break
                except Exception as e:
                    logger.exception(f"Filter {type(f).__name__} error: {e}")
                    matched = False
                    break

            if matched:
                filters_str = ", ".join(
                    getattr(f, "__name__", type(f).__name__) if callable(f) else type(f).__name__
                    for f in flts
                )

                kwargs: dict[str, Any] = {}
                for f in flts:
                    result = await self._apply_filter(f, event)
                    if isinstance(result, dict):
                        kwargs.update(result)

                self._spawn(handler, event, filters_str, kwargs)
                return True
        return False

    def _spawn(self, handler: Handler, event: Event, filters_str: str, kwargs: dict[str, Any]):
        """Internal method to spawn a task for executing the matched handler."""
        name = getattr(handler, "__name__", "<handler>")
        logger.info(f"[router:{self.name}] matched handler={name} filters=[{filters_str}]")

        async def _run():
            try:
                await handler(event, **kwargs)
            except Exception as e:
                logger.exception(f"Handler {name} failed: {e}")

        asyncio.create_task(_run())

    async def _apply_filter(self, f: Filter | Any, event: Event) -> bool:
        """Evaluate a filter (sync or async) against the event."""
        if isinstance(f, MagicFilter):
            try:
                return bool(f.resolve(event))
            except Exception:
                return False

        try:
            res = f(event)
        except Exception:
            return False

        if inspect.isawaitable(res):
            try:
                res = await res
            except Exception:
                return False

        if isinstance(res, (bool, dict)):
            return res
        return bool(res)
