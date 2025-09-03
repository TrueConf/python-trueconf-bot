from dataclasses import dataclass

from .base import TrueConfMethod
from ..types.responses import GetChatByIdResponse


@dataclass
class GetChatByID(TrueConfMethod[GetChatByIdResponse]):
    __api_method__ = "getChatByID"
    __returning__ = GetChatByIdResponse

    chat_id: str

    def __post_init__(self):
        super().__init__()

    def payload(self):
        return {
            "chatId": self.chat_id
        }
