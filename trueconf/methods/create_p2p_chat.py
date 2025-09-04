from __future__ import annotations
from dataclasses import dataclass
from trueconf.methods.base import TrueConfMethod
from trueconf.types.responses.create_p2p_chat_response import CreateP2PChatResponse


@dataclass
class CreateP2PChat(TrueConfMethod[CreateP2PChatResponse]):
    __api_method__ = "createP2PChat"
    __returning__ = CreateP2PChatResponse

    user_id: str

    def __post_init__(self):
        super().__init__()

    def payload(self):
        return {
            "userId": self.user_id,
        }
