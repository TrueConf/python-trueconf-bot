from __future__ import annotations

import asyncio
import types
from asyncio import Event, Lock
from contextlib import suppress
from typing import TYPE_CHECKING, Any

from typing_extensions import Self

from trueconf.enums.chat_activity import ChatActivity

if TYPE_CHECKING:
    from trueconf.client.bot import Bot

DEFAULT_INITIAL_SLEEP = 0.0


class ChatActivitySender:
    """
    Sends a chat activity (for example, typing) in the background until a long
    operation finishes.

    The TrueConf server shows the activity indicator only for a short time, so it
    needs to be re-sent periodically. This utility starts a background task that
    re-sends the activity while the context is active. The cadence is taken from
    the server: each response carries ``retryAfter`` in milliseconds, and the
    sender waits that long before the next send.

    Examples:
        >>> async with ChatActivitySender.typing(bot=bot, chat_id=chat_id):
        >>>     await generate_text_answer()
    """

    def __init__(
        self,
        *,
        bot: "Bot",
        chat_id: str,
        activity: ChatActivity | str = ChatActivity.TYPING,
        initial_sleep: float = DEFAULT_INITIAL_SLEEP,
    ) -> None:
        """
        Args:
            bot (Bot): Instance of the bot used to send activities.
            chat_id (str): Identifier of the target chat.
            activity (ChatActivity | str, optional): Activity type to show. Defaults to typing.
            initial_sleep (float, optional): Delay before the first send in seconds. Defaults to 0.0.
        """
        self.bot = bot
        self.chat_id = chat_id
        self.activity = activity
        self.initial_sleep = initial_sleep

        self._lock = Lock()
        self._close_event = Event()
        self._closed_event = Event()
        self._task: asyncio.Task[Any] | None = None

    @property
    def running(self) -> bool:
        task = self._task
        return task is not None and not task.done()

    async def _wait(self, interval: float) -> None:
        with suppress(asyncio.TimeoutError):
            await asyncio.wait_for(self._close_event.wait(), interval)

    async def _worker(self) -> None:
        try:
            await self._wait(self.initial_sleep)
            while not self._close_event.is_set():
                response = await self.bot.send_chat_activity(
                    chat_id=self.chat_id,
                    activity_type=self.activity,
                )
                retry_after = response.retry_after / 1000
                await self._wait(retry_after)
        finally:
            self._task = None
            self._closed_event.set()

    async def _run(self) -> None:
        async with self._lock:
            self._close_event.clear()
            self._closed_event.clear()
            if self.running:
                raise RuntimeError("Chat activity sender is already running")
            self._task = asyncio.create_task(self._worker())

    async def _stop(self) -> None:
        async with self._lock:
            if not self.running:
                return
            if not self._close_event.is_set():
                self._close_event.set()
                await self._closed_event.wait()
            self._task = None

    async def __aenter__(self) -> Self:
        await self._run()
        return self

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc_value: BaseException | None,
        traceback: types.TracebackType | None,
    ) -> Any:
        await self._stop()

    @classmethod
    def typing(cls, bot: "Bot", chat_id: str, **kwargs: Any) -> "ChatActivitySender":
        """Create an instance of the sender with the ``typing`` activity."""
        return cls(
            bot=bot,
            chat_id=chat_id,
            activity=ChatActivity.TYPING,
            **kwargs,
        )
