from dataclasses import dataclass, field
from typing import Optional, Union

from trueconf.enums import MessageType
from .base import AbstractEnvelopeContent
from ..author_box import EnvelopeAuthor, EnvelopeBox
from ..content.attachment import AttachmentContent
from ..content.survey import SurveyContent
from ..content.text import TextContent


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