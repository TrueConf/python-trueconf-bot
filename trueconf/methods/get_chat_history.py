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
        payload = {
            "chatId": self.chat_id,
            "count": self.count,
        }
        if self.from_message_id is not None:
            payload["fromMessageId"] = self.from_message_id
        return payload
