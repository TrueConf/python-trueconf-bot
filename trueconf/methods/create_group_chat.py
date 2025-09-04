from __future__ import annotations
from dataclasses import dataclass
from trueconf.methods.base import TrueConfMethod
from trueconf.types.responses.create_group_chat_response import CreateGroupChatResponse


@dataclass
class CreateGroupChat(TrueConfMethod[CreateGroupChatResponse]):
    __api_method__ = "createGroupChat"
    __returning__ = CreateGroupChatResponse

    title: str

    def __post_init__(self):
        super().__init__()

    def payload(self):
        return {
            "title": self.title,
        }
