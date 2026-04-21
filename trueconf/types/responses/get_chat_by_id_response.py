from __future__ import annotations
from dataclasses import dataclass, field
from mashumaro import DataClassDictMixin
from trueconf.types.last_message import LastMessage


@dataclass
class GetChatByIdResponse(DataClassDictMixin):
    chat_id: str = field(metadata={"alias": "chatId"})
    title: str
    chat_type: int = field(metadata={"alias": "chatType"})
    avatar_url: str | None = field(metadata={"alias": "avatarUrl"})
    unread_messages: int = field(metadata={"alias": "unreadMessages"})
    last_message: LastMessage | None = field(default=None, metadata={"alias": "lastMessage"})
