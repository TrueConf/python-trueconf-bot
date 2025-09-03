from dataclasses import dataclass

from .base import TrueConfMethod
from ..types.responses import RemoveChatParticipantResponse


@dataclass
class RemoveChatParticipant(TrueConfMethod[RemoveChatParticipantResponse]):
    __api_method__ = "removeChatParticipant"
    __returning__ = RemoveChatParticipantResponse

    chat_id: str
    user_id: str

    def __post_init__(self):
        super().__init__()

    def payload(self):
        return {
            "chatId": self.chat_id,
            "userId": self.user_id
        }
