from __future__ import annotations
from dataclasses import dataclass, field
from mashumaro import DataClassDictMixin


@dataclass
class SendSurveyResponse(DataClassDictMixin):
    chat_id: str = field(metadata={"alias": "chatId"})
    message_id: str = field(metadata={"alias": "messageId"})
    timestamp: int
