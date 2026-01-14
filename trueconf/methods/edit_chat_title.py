from __future__ import annotations
from dataclasses import dataclass
from trueconf.methods.base import TrueConfMethod
from trueconf.types.responses.edit_chat_title_response import EditChatTitleResponse


@dataclass
class EditChatTitle(TrueConfMethod[EditChatTitleResponse]):
    __api_method__ = "editChatTitle"
    __returning__ = EditChatTitleResponse

    chat_id: str
    title: str

    def __post_init__(self):
        super().__init__()

    def payload(self):
        return {
            "chatId": self.chat_id,
            "title": self.title,
        }
