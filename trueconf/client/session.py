from __future__ import annotations
import asyncio
import contextlib
import json
import logging
from typing import Awaitable, Callable, Optional

logger = logging.getLogger("chat_bot")


class WebSocketSession:
    """
    Владеет объектом ws, поднимает фоновый listener и
    пробрасывает сырые сообщения в callback on_message(raw: str).
    """
    def __init__(self, on_message: Optional[Callable[[str], Awaitable[None]]] = None):
        self.ws = None
        self._listener_task: Optional[asyncio.Task] = None
        self._on_message = on_message

    def attach(self, ws) -> None:
        """Подключить актуальный ws и запустить фонового listener-а."""
        self.ws = ws
        if self._listener_task and not self._listener_task.done():
            self._listener_task.cancel()
        self._listener_task = asyncio.create_task(self._listener())

    async def detach(self) -> None:
        """Остановить listener (ws остаётся под управлением ChatBot/connect loop)."""
        if self._listener_task:
            try:
                self._listener_task.cancel()
                with contextlib.suppress(asyncio.CancelledError):
                    await self._listener_task
            finally:
                self._listener_task = None
        self.ws = None

    async def close(self) -> None:
        """Закрыть ws и listener."""
        if self.ws:
            await self.ws.close()
        await self.detach()

    async def send_json(self, message: dict) -> None:
        if not self.ws:
            raise RuntimeError("WS is not attached")
        await self.ws.send(json.dumps(message))

    async def _listener(self):
        try:
            async for raw in self.ws:
                if self._on_message:
                    try:
                        await self._on_message(raw)
                    except Exception as e:
                        logger.error(f"on_message callback error: {e}")
        except Exception as e:
            # Закрытие/обрыв — это нормально, верхний цикл переподключит
            logger.debug(f"Session listener stopped: {type(e).__name__}: {e}")