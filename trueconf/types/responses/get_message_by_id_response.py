from __future__ import annotations
from dataclasses import dataclass, field
from typing import Optional, Union
from mashumaro import DataClassDictMixin
from trueconf.enums.message_type import MessageType
from trueconf.types.author_box import EnvelopeAuthor, EnvelopeBox
from trueconf.types.content.text import TextContent
from trueconf.types.content.attachment import AttachmentContent
from trueconf.types.content.survey import SurveyContent
from trueconf.types.content.remove_participant import RemoveParticipant
from trueconf.types.content.forward_message import ForwardMessage
from trueconf.types.content.chat_created import ParticipantRoleContent


@dataclass
class GetMessageByIdResponse(DataClassDictMixin):
    timestamp: int
    type: MessageType
    author: EnvelopeAuthor
    box: EnvelopeBox
    content: Union[
        TextContent, AttachmentContent, SurveyContent, ParticipantRoleContent, RemoveParticipant, ForwardMessage]
    message_id: str = field(metadata={"alias": "messageId"})
    chat_id: str = field(metadata={"alias": "chatId"})
    is_edited: bool = field(metadata={"alias": "isEdited"})
    reply_message_id: Optional[str] = field(default=None, metadata={"alias": "replyMessageId"})
