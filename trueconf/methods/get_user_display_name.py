from dataclasses import dataclass

from .base import TrueConfMethod
from ..types.responses import GetUserDisplayNameResponse


@dataclass
class GetUserDisplayName(TrueConfMethod[GetUserDisplayNameResponse]):
    __api_method__ = "getUserDisplayName"
    __returning__ = GetUserDisplayNameResponse

    user_id: str

    def __post_init__(self):
        super().__init__()

    def payload(self):
        return {
            "userId": self.user_id,
        }
