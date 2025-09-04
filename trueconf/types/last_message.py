from __future__ import annotations
from dataclasses import dataclass, field
from typing import Optional, Union
from mashumaro import DataClassDictMixin
from trueconf.enums.message_type import MessageType
from trueconf.types.author_box import EnvelopeAuthor
from trueconf.types.content.text import TextContent
from trueconf.types.content.attachment import AttachmentContent
from trueconf.types.content.survey import SurveyContent
from trueconf.types.content.remove_participant import RemoveParticipant
from trueconf.types.content.forward_message import ForwardMessage
from trueconf.types.content.chat_created import ParticipantRoleContent


@dataclass
class LastMessage(DataClassDictMixin):
    message_id: str = field(metadata={"alias": "messageId"})
    timestamp: int
    author: EnvelopeAuthor
    type: MessageType
    content: Union[TextContent, AttachmentContent, SurveyContent, ParticipantRoleContent, RemoveParticipant, ForwardMessage]

    @property
    def content_type(self) -> MessageType:
        return self.type

    @property
    def text(self) -> Optional[str]:
        return self.content.text if isinstance(self.content, TextContent) else None

    @property
    def file(self) -> Optional[AttachmentContent]:
        return self.content if isinstance(self.content, AttachmentContent) else None
