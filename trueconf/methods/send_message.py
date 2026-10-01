from __future__ import annotations

from dataclasses import dataclass, field

from trueconf.methods.base import TrueConfMethod
from trueconf.types.keyboard import InlineKeyboardMarkup
from trueconf.types.responses.send_message_response import SendMessageResponse


@dataclass
class SendMessage(TrueConfMethod[SendMessageResponse]):
    __api_method__ = "sendMessage"
    __returning__ = SendMessageResponse
    chat_id: str
    text: str
    parse_mode: str
    reply_message_id: str | None = None
    buttons: InlineKeyboardMarkup | None = field(default=None, kw_only=True)

    def __post_init__(self):
        super().__init__()

    def payload(self):
        content = {
            "text": self.text,
            "parseMode": self.parse_mode,
        }
        if self.buttons is not None:
            content.update(self.buttons.to_dict())

        return {
            "chatId": self.chat_id,
            "replyMessageId": self.reply_message_id,
            "content": content,
        }
