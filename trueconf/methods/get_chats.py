from __future__ import annotations
from dataclasses import dataclass
from trueconf.methods.base import TrueConfMethod
from trueconf.types.responses.get_chats_response import GetChatsResponse


@dataclass
class GetChats(TrueConfMethod[GetChatsResponse]):
    __api_method__ = "getChats"
    __returning__ = GetChatsResponse

    count: int
    page: int

    def __post_init__(self):
        super().__init__()

    def payload(self):
        return {
            "count": self.count,
            "page": self.page,
        }
