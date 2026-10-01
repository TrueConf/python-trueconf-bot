from __future__ import annotations

from dataclasses import dataclass, field

from mashumaro import DataClassDictMixin

from trueconf.client.context_controller import BoundToBot
from trueconf.enums.chat_type import ChatType


@dataclass
class Chat(BoundToBot, DataClassDictMixin):
    chat_id: str = field(metadata={"alias": "chatId"})
    chat_title: str | None = field(metadata={"alias": "chatTitle"})
    chat_type: ChatType = field(metadata={"alias": "chatType"})
