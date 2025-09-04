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
from trueconf.types.requests.created_channel import CreatedChannel
from trueconf.types.requests.created_group_chat import CreatedGroupChat
from trueconf.types.requests.created_personal_chat import CreatedPersonalChat
from trueconf.types.requests.edited_message import EditedMessage
from trueconf.types.requests.removed_chat import RemovedChat
from trueconf.types.requests.removed_chat_participant import RemovedChatParticipant
from trueconf.types.requests.removed_message import RemovedMessage
from trueconf.types.requests.uploading_progress import UploadingProgress

logger = logging.getLogger("chat_bot")

Handler = Callable[[Event], Awaitable[None]]
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

    def created_personal_chat(self, *filters: FilterLike):
        """Register a handler for personal chat creation events."""
        return self._register((InstanceOfFilter(CreatedPersonalChat), *filters))

    def created_group_chat(self, *filters: FilterLike):
        """Register a handler for group chat creation events."""
        return self._register((InstanceOfFilter(CreatedGroupChat), *filters))

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
            if not asyncio.iscoroutinefunction(func):
                async def async_wrapper(evt: Event):
                    return func(evt)

                self._handlers.append((filters, async_wrapper))
                return func
            self._handlers.append((filters, func))
            return func

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
                self._spawn(handler, event, filters_str)
                return True
        return False

    def _spawn(self, handler: Handler, event: Event, filters_str: str):
        """Internal method to spawn a task for executing the matched handler."""
        name = getattr(handler, "__name__", "<handler>")
        logger.info(f"[router:{self.name}] matched handler={name} filters=[{filters_str}]")

        async def _run():
            try:
                await handler(event)
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

        if isinstance(res, bool):
            return res
        return bool(res)
