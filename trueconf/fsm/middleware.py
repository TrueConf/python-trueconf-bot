from __future__ import annotations

from typing import Any

from trueconf.fsm.manager import FSMManager
from trueconf.middleware import BaseMiddleware


class FSMMiddleware(BaseMiddleware):
    def __init__(self, fsm_manager: FSMManager) -> None:
        self._manager = fsm_manager

    async def __call__(
        self,
        handler: Any,
        event: Any,
        data: dict[str, Any],
    ) -> None:
        bot = data.get("bot")
        if bot is not None:
            context = self._manager.get_context(bot, event)
            data["state"] = context
            data["raw_state"] = await context.get_state()
        return await handler(event, data)
