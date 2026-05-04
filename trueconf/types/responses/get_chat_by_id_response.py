from __future__ import annotations
from dataclasses import dataclass, field
from mashumaro import DataClassDictMixin
from trueconf.types.last_message import LastMessage


@dataclass
class GetChatByIdResponse(DataClassDictMixin):
    title: str
    chat_id: str = field(metadata={"alias": "chatId"})
    chat_type: int = field(metadata={"alias": "chatType"})
    unread_messages: int = field(metadata={"alias": "unreadMessages"})
    avatar_url: str | None = field(default=None, metadata={"alias": "avatarUrl"})
    last_message: LastMessage | None = field(default=None, metadata={"alias": "lastMessage"})
