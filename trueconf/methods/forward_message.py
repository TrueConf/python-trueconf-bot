from __future__ import annotations
from dataclasses import dataclass
from trueconf.methods.base import TrueConfMethod
from trueconf.types.responses.forward_message_response import ForwardMessageResponse


@dataclass
class ForwardMessage(TrueConfMethod[ForwardMessageResponse]):
    __api_method__ = "forwardMessage"
    __returning__ = ForwardMessageResponse

    message_id: str
    chat_id: str

    def __post_init__(self):
        super().__init__()

    def payload(self):
        return {
            "messageId": self.message_id,
            "chatId": self.chat_id,
        }
