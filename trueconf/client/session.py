from __future__ import annotations

import asyncio
import contextlib
import json
import logging
from typing import Awaitable, Callable

logger = logging.getLogger("chat_bot")


class WebSocketSession:
    def __init__(self, on_message: Callable[[str], Awaitable[None]] | None = None):
        self.ws = None
        self._listener_task: asyncio.Task | None = None
        self._on_message = on_message

    def attach(self, ws) -> None:
        self.ws = ws
        if self._listener_task and not self._listener_task.done():
            self._listener_task.cancel()
        self._listener_task = asyncio.create_task(self._listener())

    async def detach(self) -> None:
        if self._listener_task:
            try:
                self._listener_task.cancel()
                with contextlib.suppress(asyncio.CancelledError):
                    await self._listener_task
            finally:
                self._listener_task = None
        self.ws = None

    async def close(self) -> None:
        ws = self.ws
        await self.detach()
        if ws:
            with contextlib.suppress(Exception):
                await ws.close()

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
            logger.debug(f"Session listener stopped: {type(e).__name__}: {e}")
