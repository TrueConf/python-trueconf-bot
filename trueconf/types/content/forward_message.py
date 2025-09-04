from __future__ import annotations
from dataclasses import dataclass, field
from typing import Optional, Union
from trueconf.enums.message_type import MessageType
from trueconf.types.content.base import AbstractEnvelopeContent
from trueconf.types.author_box import EnvelopeAuthor, EnvelopeBox
from trueconf.types.content.attachment import AttachmentContent
from trueconf.types.content.survey import SurveyContent
from trueconf.types.content.text import TextContent


@dataclass
class ForwardMessage(AbstractEnvelopeContent):
    timestamp: int
    type: MessageType
    author: EnvelopeAuthor
    content: Union[TextContent, AttachmentContent, SurveyContent]
    message_id: str = field(metadata={"alias": "messageId"})
    chat_id: str = field(metadata={"alias": "chatId"})
    is_edited: Optional[bool] = field(metadata={"alias": "isEdited"})
    box: Optional[EnvelopeBox]
