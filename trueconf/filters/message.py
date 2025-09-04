from __future__ import annotations
from trueconf.enums.message_type import MessageType
from trueconf.types.message import Message


class MessageFilter:
    """Фильтр по payload.type (= EnvelopeType)."""

    def __init__(self, *types: MessageType):
        self.types = frozenset(int(t) for t in types)

    async def __call__(self, event: Message) -> bool:
        if not isinstance(event, Message):
            return False
        return int(event.type) in self.types
