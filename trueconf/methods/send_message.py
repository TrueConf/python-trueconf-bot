from __future__ import annotations
from __future__ import annotations
from dataclasses import dataclass
from typing import Optional
from trueconf.methods.base import TrueConfMethod
from trueconf.types.responses.send_message_response import SendMessageResponse


@dataclass
class SendMessage(TrueConfMethod[SendMessageResponse]):
    __api_method__ = "sendMessage"
    __returning__ = SendMessageResponse
    chat_id: str
    text: str
    parse_mode: str
    reply_message_id: Optional[str] = None

    def __post_init__(self):
        super().__init__()

    def payload(self):
        return {
            "chatId": self.chat_id,
            "replyMessageId": self.reply_message_id,
            "content": {
                "text": self.text,
                "parseMode": self.parse_mode,
            },
        }
