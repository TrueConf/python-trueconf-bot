from __future__ import annotations
from dataclasses import dataclass
from trueconf.methods.base import TrueConfMethod
from trueconf.types.responses.get_chat_by_id_response import GetChatByIdResponse


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
