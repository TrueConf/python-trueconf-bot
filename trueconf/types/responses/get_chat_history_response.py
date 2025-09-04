from __future__ import annotations
from dataclasses import dataclass, field
from typing import List
from mashumaro import DataClassDictMixin
from trueconf.types.message import Message

@dataclass
class GetChatHistoryResponse(DataClassDictMixin):
    count: int
    chat_id: str = field(metadata={"alias": "chatId"})
    messages: List[Message] = field(
        default_factory=list,
        metadata={"alias": "messages"})
