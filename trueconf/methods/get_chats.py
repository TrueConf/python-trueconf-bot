from dataclasses import dataclass

from .base import TrueConfMethod
from ..types.responses import GetChatsResponse


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
