from dataclasses import dataclass
from typing import Optional

from .base import TrueConfMethod
from ..types.responses import GetChatHistoryResponse


@dataclass
class GetChatHistory(TrueConfMethod[GetChatHistoryResponse]):
    __api_method__ = "getChatHistory"
    __returning__ = GetChatHistoryResponse

    chat_id: str
    count: int
    from_message_id: Optional[str] = None

    def __post_init__(self):
        super().__init__()

    def payload(self):
        return {
            "chatId": self.chat_id,
            "count": self.count,
            "fromMessageId": self.from_message_id,
        }
