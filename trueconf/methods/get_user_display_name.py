from __future__ import annotations
from dataclasses import dataclass
from trueconf.methods.base import TrueConfMethod
from trueconf.types.responses.get_user_display_name_response import GetUserDisplayNameResponse


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
