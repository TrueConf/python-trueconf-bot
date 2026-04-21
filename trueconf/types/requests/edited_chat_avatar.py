from __future__ import annotations
from dataclasses import dataclass, field
from mashumaro import DataClassDictMixin
from trueconf.client.context_controller import BoundToBot

@dataclass
class EditedChatAvatar(BoundToBot, DataClassDictMixin):
    chat_id: str = field(metadata={"alias": "chatId"})
    avatar_url: str = field(metadata={"alias": "avatarUrl"})
