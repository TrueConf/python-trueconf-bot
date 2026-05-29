from __future__ import annotations
import logging
from typing import TYPE_CHECKING, Any, Awaitable, Callable, Dict

from trueconf.filters.base import Event

if TYPE_CHECKING:
    pass

logger = logging.getLogger("chat_bot")

MiddlewareHandler = Callable[[Event, Dict[str, Any]], Awaitable[None]]


class BaseMiddleware:
    """
    Base middleware class for event processing pipeline.

    Middleware wraps event handlers and can intercept, modify, or block events
    before they reach the actual handler. To block an event, simply do not call
    ``await handler(event, data)``.

    Example:
        >>> class LoggingMiddleware(BaseMiddleware):
        ...     async def __call__(self, handler, event, data):
        ...         logger.info(f"Event: {event}")
        ...         await handler(event, data)
        ...         logger.info("Done")

        >>> router.outer_middleware(LoggingMiddleware())
    """

    async def __call__(
        self,
        handler: MiddlewareHandler,
        event: Event,
        data: Dict[str, Any],
    ) -> None:
        await handler(event, data)


class SkipSelfMessages(BaseMiddleware):
    """
    Middleware that drops messages sent by the bot itself.

    Prevents the bot from reacting to its own messages when multiple bot sessions
    are running. If the event is a ``Message`` and its ``author.id`` matches
    ``bot.me_id``, the event is silently dropped.

    Registration:
        Automatically registered when ``Bot(skip_self_messages=True)`` (default).
        Alternatively:
        >>> from trueconf.middleware import SkipSelfMessages
        >>> dp.outer_middleware(SkipSelfMessages())
    """

    async def __call__(
        self,
        handler: MiddlewareHandler,
        event: Event,
        data: Dict[str, Any],
    ) -> None:
        bot = data.get("bot")
        if bot is None:
            await handler(event, data)
            return

        from trueconf.types.message import Message

        if isinstance(event, Message) and event.author.id == bot.me_id:
            logger.debug(
                "[SkipSelfMessages] dropped message %s from bot self (author=%s)",
                event.message_id,
                event.author.id,
            )
            return

        await handler(event, data)
