from __future__ import annotations

from typing import Any

from trueconf.fsm.context import FSMContext
from trueconf.fsm.state import State


class StateFilter:
    def __init__(self, *states: State | str | None) -> None:
        self._states: set[str | None] = {
            str(s) if isinstance(s, State) else s for s in states
        }

    async def __call__(
        self,
        event: Any,
        *,
        state: FSMContext | None = None,
    ) -> bool:
        if state is None:
            raise RuntimeError(
                "StateFilter requires FSMContext in data['state'], but it was not found. "
                "Make sure FSMMiddleware is registered as outer middleware "
                "before any StateFilter is evaluated."
            )
        current = await state.get_state()
        return current in self._states
