from dataclasses import dataclass

from .base import TrueConfMethod
from ..types.responses import CreateGroupChatResponse


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

