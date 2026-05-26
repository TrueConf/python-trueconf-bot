from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from trueconf.fsm.key_builder import StorageKey
from trueconf.fsm.storage.base import BaseStorage


@dataclass
class _Record:
    state: str | None = None
    data: dict[str, Any] = field(default_factory=dict)


class MemoryStorage(BaseStorage):
    def __init__(self) -> None:
        self._records: dict[StorageKey, _Record] = {}

    def _get_or_create(self, key: StorageKey) -> _Record:
        if key not in self._records:
            self._records[key] = _Record()
        return self._records[key]

    async def get_state(self, key: StorageKey) -> str | None:
        record = self._records.get(key)
        return record.state if record else None

    async def set_state(self, key: StorageKey, state: str | None) -> None:
        self._get_or_create(key).state = state

    async def get_data(self, key: StorageKey) -> dict[str, Any]:
        record = self._records.get(key)
        return record.data.copy() if record else {}

    async def set_data(self, key: StorageKey, data: dict[str, Any]) -> None:
        self._get_or_create(key).data = data.copy()

    async def update_data(self, key: StorageKey, updates: dict[str, Any]) -> dict[str, Any]:
        record = self._get_or_create(key)
        record.data.update(updates)
        return record.data.copy()

    async def clear(self, key: StorageKey) -> None:
        self._records.pop(key, None)
