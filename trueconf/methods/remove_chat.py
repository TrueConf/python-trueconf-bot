from __future__ import annotations
from dataclasses import dataclass
from trueconf.methods.base import TrueConfMethod
from trueconf.types.responses.remove_chat_response import RemoveChatResponse


@dataclass
class RemoveChat(TrueConfMethod[RemoveChatResponse]):
    __api_method__ = "removeChat"
    __returning__ = RemoveChatResponse

    chat_id: str

    def __post_init__(self):
        super().__init__()

    def payload(self):
        return {
            "chatId": self.chat_id,
        }
