from __future__ import annotations
from dataclasses import dataclass
from trueconf.methods.base import TrueConfMethod
from trueconf.types.responses.get_chat_history_response import GetChatHistoryResponse


@dataclass
class GetChatHistory(TrueConfMethod[GetChatHistoryResponse]):
    __api_method__ = "getChatHistory"
    __returning__ = GetChatHistoryResponse

    chat_id: str
    count: int
    from_message_id: str | None = None

    def __post_init__(self):
        super().__init__()

    def payload(self):
        return {
            "chatId": self.chat_id,
            "count": self.count,
            "fromMessageId": self.from_message_id,
        }
