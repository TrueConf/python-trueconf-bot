from __future__ import annotations
from dataclasses import dataclass, field
from mashumaro import DataClassDictMixin
from trueconf.client.context_controller import BoundToBot

@dataclass
class EditedChatTitle(BoundToBot, DataClassDictMixin):
    chat_id: str = field(metadata={"alias": "chatId"})
    title: str
