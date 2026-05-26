from abc import ABC, abstractmethod
from typing import Any

from trueconf.fsm.key_builder import StorageKey


class BaseStorage(ABC):
    @abstractmethod
    async def get_state(self, key: StorageKey) -> str | None: ...

    @abstractmethod
    async def set_state(self, key: StorageKey, state: str | None) -> None: ...

    @abstractmethod
    async def get_data(self, key: StorageKey) -> dict[str, Any]: ...

    @abstractmethod
    async def set_data(self, key: StorageKey, data: dict[str, Any]) -> None: ...

    @abstractmethod
    async def update_data(self, key: StorageKey, updates: dict[str, Any]) -> dict[str, Any]: ...

    @abstractmethod
    async def clear(self, key: StorageKey) -> None: ...

    async def close(self) -> None:
        pass
