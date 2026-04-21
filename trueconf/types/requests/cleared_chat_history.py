from __future__ import annotations
from dataclasses import dataclass, field
from mashumaro import DataClassDictMixin
from trueconf.client.context_controller import BoundToBot

@dataclass
class ClearedChatHistory(BoundToBot, DataClassDictMixin):
    chat_id: str = field(metadata={"alias": "chatId"})
    for_all: str = field(metadata={"alias": "forAll"})
