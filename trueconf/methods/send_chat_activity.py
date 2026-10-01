from __future__ import annotations

from dataclasses import dataclass

from trueconf.enums.chat_activity import ChatActivity
from trueconf.methods.base import TrueConfMethod
from trueconf.types.responses.send_chat_activity_response import (
    SendChatActivityResponse,
)


@dataclass
class SendChatActivity(TrueConfMethod[SendChatActivityResponse]):
    __api_method__ = "sendChatActivity"
    __returning__ = SendChatActivityResponse
    chat_id: str
    activity_type: ChatActivity | str

    def __post_init__(self):
        super().__init__()

    def payload(self):
        return {
            "chatId": self.chat_id,
            "activityType": self.activity_type,
        }
