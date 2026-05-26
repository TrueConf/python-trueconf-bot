from __future__ import annotations

from typing import Any

from trueconf.fsm.key_builder import StorageKey
from trueconf.fsm.state import State
from trueconf.fsm.storage.base import BaseStorage


class FSMContext:
    def __init__(self, storage: BaseStorage, key: StorageKey) -> None:
        self._storage = storage
        self._key = key

    @property
    def key(self) -> StorageKey:
        return self._key

    async def get_state(self) -> str | None:
        return await self._storage.get_state(self._key)

    async def set_state(self, state: State | str | None) -> None:
        value = str(state) if isinstance(state, State) else state
        await self._storage.set_state(self._key, value)

    async def get_data(self) -> dict[str, Any]:
        return await self._storage.get_data(self._key)

    async def set_data(self, data: dict[str, Any]) -> None:
        await self._storage.set_data(self._key, data)

    async def update_data(self, **kwargs: Any) -> dict[str, Any]:
        return await self._storage.update_data(self._key, kwargs)

    async def clear(self) -> None:
        await self._storage.clear(self._key)
