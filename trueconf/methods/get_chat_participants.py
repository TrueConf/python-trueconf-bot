from dataclasses import dataclass

from .base import TrueConfMethod
from ..types.responses import GetChatParticipantsResponse


@dataclass
class GetChatParticipants(TrueConfMethod[GetChatParticipantsResponse]):
    __api_method__ = "getChatParticipants"
    __returning__ = GetChatParticipantsResponse

    chat_id: str
    page_size: int
    page_number: int

    def __post_init__(self):
        super().__init__()

    def payload(self):
        return {
            "chatId": self.chat_id,
            "pageSize": self.page_size,
            "pageNumber": self.page_number,
        }
