from __future__ import annotations
from dataclasses import dataclass
from trueconf.methods.base import TrueConfMethod
from trueconf.types.responses.clear_chat_history_response import ClearChatHistoryResponse


@dataclass
class ClearChatHistory(TrueConfMethod[ClearChatHistoryResponse]):
    __api_method__ = "clearHistory"
    __returning__ = ClearChatHistoryResponse

    chat_id: str
    for_all: bool

    def __post_init__(self):
        super().__init__()

    def payload(self):
        return {
            "chatId": self.chat_id,
            "forAll": self.for_all,
        }
