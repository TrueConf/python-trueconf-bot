from dataclasses import dataclass

from .base import TrueConfMethod
from ..types.responses import GetMessageByIdResponse


@dataclass
class GetMessageById(TrueConfMethod[GetMessageByIdResponse]):
    __api_method__ = "getMessageById"
    __returning__ = GetMessageByIdResponse
    message_id: str

    def __post_init__(self):
        super().__init__()

    def payload(self):
        return {
            "messageId": self.message_id
        }
