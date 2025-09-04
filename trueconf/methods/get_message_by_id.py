from __future__ import annotations
from dataclasses import dataclass
from trueconf.methods.base import TrueConfMethod
from trueconf.types.responses.get_message_by_id_response import GetMessageByIdResponse


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
