from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from mashumaro import DataClassDictMixin
from mashumaro.helper import pass_through

from trueconf.enums.message_type import MessageType
from trueconf.types.author_box import EnvelopeAuthor
from trueconf.types.chat import Chat
from trueconf.types.content.attachment import AttachmentContent
from trueconf.types.content.parser import (
    SystemMessageContent,
    UnsupportedMessageType,
    UserMessageContent,
    deserialize_envelope_content,
)
from trueconf.types.content.text import TextContent


@dataclass
class LastMessage(DataClassDictMixin):
    message_id: str = field(metadata={"alias": "messageId"})
    timestamp: int
    author: EnvelopeAuthor
    type: MessageType
    content: UserMessageContent | SystemMessageContent = field(metadata={"deserialize": pass_through})
    chat: Chat

    @classmethod
    def __pre_deserialize__(cls, d: dict[str, Any]) -> dict[str, Any]:
        data = dict(d)
        try:
            message_type = MessageType(data["type"])
        except ValueError as error:
            raise UnsupportedMessageType(data["type"]) from error
        data["content"] = deserialize_envelope_content(message_type, data.get("content", {}))
        return data

    @property
    def content_type(self) -> MessageType:
        return self.type

    @property
    def text(self) -> str | None:
        return self.content.text if isinstance(self.content, TextContent) else None

    @property
    def file(self) -> AttachmentContent | None:
        return self.content if isinstance(self.content, AttachmentContent) else None
