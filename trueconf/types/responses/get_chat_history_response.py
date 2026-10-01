from __future__ import annotations

from dataclasses import dataclass, field

from mashumaro import DataClassDictMixin

from trueconf.client.context_controller import BoundToBot
from trueconf.types.envelope_parser import deserialize_envelopes
from trueconf.types.message import Message
from trueconf.types.system_message import SystemMessage


@dataclass
class GetChatHistoryResponse(BoundToBot, DataClassDictMixin):
    count: int
    chat_id: str = field(metadata={"alias": "chatId"})
    messages: list[Message | SystemMessage] = field(
        default_factory=list,
        metadata={"alias": "messages", "deserialize": deserialize_envelopes},
    )

    def bind(self, bot):
        super().bind(bot)
        for message in self.messages:
            message.bind(bot)
        return self
