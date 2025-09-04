from __future__ import annotations
from dataclasses import dataclass
from trueconf.methods.base import TrueConfMethod
from trueconf.types.responses.get_chat_participants_response import GetChatParticipantsResponse


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
