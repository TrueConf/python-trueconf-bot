from dataclasses import dataclass, field
from typing import Optional, Union

from mashumaro import DataClassDictMixin

from trueconf.enums import MessageType
from .author_box import EnvelopeAuthor
from .content import (
    TextContent,
    AttachmentContent,
    SurveyContent,
    ParticipantRoleContent,
    RemoveParticipant,
    ForwardMessage
)


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
