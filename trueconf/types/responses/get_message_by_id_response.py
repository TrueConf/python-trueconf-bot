from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from mashumaro import DataClassDictMixin
from mashumaro.helper import pass_through

from trueconf.client.context_controller import BoundToBot
from trueconf.enums.message_type import MessageType
from trueconf.types.author_box import EnvelopeAuthor, EnvelopeBox
from trueconf.types.content.parser import UserMessageContent, deserialize_user_content
from trueconf.types.message import Message


@dataclass
class GetMessageByIdResponse(BoundToBot, DataClassDictMixin):
    timestamp: int
    type: MessageType
    author: EnvelopeAuthor
    box: EnvelopeBox
    content: UserMessageContent = field(metadata={"deserialize": pass_through})
    message_id: str = field(metadata={"alias": "messageId"})
    chat_id: str = field(metadata={"alias": "chatId"})
    is_edited: bool = field(metadata={"alias": "isEdited"})
    reply_message_id: str | None = field(default=None, metadata={"alias": "replyMessageId"})
    reply_message: Message | None = field(default=None, metadata={"alias": "replyMessage"})

    @classmethod
    def __pre_deserialize__(cls, d: dict[str, Any]) -> dict[str, Any]:
        data = dict(d)
        message_type = MessageType(data["type"])
        data["content"] = deserialize_user_content(message_type, data.get("content", {}))
        return data

    def bind(self, bot):
        super().bind(bot)
        if self.reply_message is not None:
            self.reply_message.bind(bot)
        return self
