from dataclasses import dataclass

from .base import TrueConfMethod
from ..types.responses import HasChatParticipantResponse


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
