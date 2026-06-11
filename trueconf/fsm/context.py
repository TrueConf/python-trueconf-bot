from __future__ import annotations

from collections.abc import Mapping
from typing import Any, overload

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

    @property
    def storage(self) -> BaseStorage:
        return self._storage

    async def get_state(self) -> str | None:
        return await self._storage.get_state(self._key)

    async def set_state(self, state: State | str | None) -> None:
        value = str(state) if isinstance(state, State) else state
        await self._storage.set_state(self._key, value)

    async def get_data(self) -> dict[str, Any]:
        return await self._storage.get_data(self._key)

    async def set_data(self, data: Mapping[str, Any]) -> None:
        await self._storage.set_data(self._key, dict(data))

    @overload
    async def get_value(self, key: str) -> Any | None: ...

    @overload
    async def get_value(self, key: str, default: Any) -> Any: ...

    async def get_value(self, key: str, default: Any | None = None) -> Any | None:
        return await self._storage.get_value(self._key, key, default)

    async def update_data(
        self,
        data: Mapping[str, Any] | None = None,
        **kwargs: Any,
    ) -> dict[str, Any]:
        if data:
            kwargs.update(data)
        return await self._storage.update_data(self._key, kwargs)

    async def clear(self) -> None:
        await self.set_state(None)
        await self.set_data({})
