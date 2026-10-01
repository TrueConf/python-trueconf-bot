from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from mashumaro import DataClassDictMixin
from mashumaro.helper import pass_through

from trueconf.client.context_controller import BoundToBot
from trueconf.enums.message_type import MessageType
from trueconf.types.author_box import EnvelopeAuthor, EnvelopeBox
from trueconf.types.chat import Chat
from trueconf.types.content.parser import SystemMessageContent, deserialize_system_content


@dataclass
class SystemMessage(BoundToBot, DataClassDictMixin):
    """A system Envelope recorded in chat history or received as a live message."""

    chat: Chat
    timestamp: int
    type: MessageType
    author: EnvelopeAuthor
    box: EnvelopeBox
    content: SystemMessageContent = field(metadata={"deserialize": pass_through})
    message_id: str = field(metadata={"alias": "messageId"})

    @classmethod
    def __pre_deserialize__(cls, d: dict[str, Any]) -> dict[str, Any]:
        data = dict(d)
        message_type = MessageType(data["type"])
        data["content"] = deserialize_system_content(message_type, data.get("content", {}))
        return data
