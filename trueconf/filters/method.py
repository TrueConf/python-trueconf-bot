from __future__ import annotations
from trueconf.filters.base import Event


class MethodFilter:
    def __init__(self, method: str):
        self.method = method

    async def __call__(self, event: Event) -> bool:
        if isinstance(event, dict):
            return event.get("method") == self.method
        return getattr(event, "method", None) == self.method
