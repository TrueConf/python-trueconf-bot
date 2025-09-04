from __future__ import annotations
from typing import Type
from trueconf.filters.base import Event


class InstanceOfFilter:
    def __init__(self, cls: Type[object]):
        self.cls = cls

    async def __call__(self, event: Event) -> bool:
        return isinstance(event, self.cls)
