from dataclasses import dataclass

from .base import TrueConfMethod
from ..types.responses import AddChatParticipantResponse


@dataclass
class AddChatParticipant(TrueConfMethod[AddChatParticipantResponse]):
    __api_method__ = "addChatParticipant"
    __returning__ = AddChatParticipantResponse

    chat_id: str
    user_id: str

    def __post_init__(self):
        super().__init__()

    def payload(self):
        return {
            "chatId": self.chat_id,
            "userId": self.user_id
        }
