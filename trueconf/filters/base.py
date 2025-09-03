from typing import Any
from typing import Protocol, runtime_checkable

Event = Any

@runtime_checkable
class Filter(Protocol):
    async def __call__(self, event: Event) -> bool: ...