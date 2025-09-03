from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional, Union

from mashumaro import DataClassDictMixin

from trueconf.enums import MessageType
from ..author_box import EnvelopeAuthor, EnvelopeBox
from ..content import (
    TextContent,
    AttachmentContent,
    SurveyContent,
    ParticipantRoleContent,
    RemoveParticipant,
    ForwardMessage
)


@dataclass
class GetMessageByIdResponse(DataClassDictMixin):
    timestamp: int
    type: MessageType
    author: EnvelopeAuthor
    box: EnvelopeBox
    content: Union[TextContent, AttachmentContent, SurveyContent, ParticipantRoleContent, RemoveParticipant, ForwardMessage]
    message_id: str = field(metadata={"alias": "messageId"})
    chat_id: str = field(metadata={"alias": "chatId"})
    is_edited: bool = field(metadata={"alias": "isEdited"})
    reply_message_id: Optional[str] = field(default=None, metadata={"alias": "replyMessageId"})