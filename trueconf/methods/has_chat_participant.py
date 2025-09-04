from __future__ import annotations
from dataclasses import dataclass
from trueconf.methods.base import TrueConfMethod
from trueconf.types.responses.has_chat_participant_response import HasChatParticipantResponse


@dataclass
class HasChatParticipant(TrueConfMethod[HasChatParticipantResponse]):
    __api_method__ = "hasChatParticipant"
    __returning__ = HasChatParticipantResponse

    chat_id: str
    user_id: str

    def __post_init__(self):
        super().__init__()

    def payload(self):
        return {
            "chatId": self.chat_id,
            "userId": self.user_id
        }
