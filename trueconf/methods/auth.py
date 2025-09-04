from __future__ import annotations
from dataclasses import dataclass
from trueconf.methods.base import TrueConfMethod
from trueconf.types.responses.auth_response_payload import AuthResponsePayload


@dataclass
class AuthMethod(TrueConfMethod[AuthResponsePayload]):
    __api_method__ = "auth"
    __returning__ = AuthResponsePayload

    token: str
    tokenType: str = "JWT"
    receive_unread_messages: bool = False

    def __post_init__(self):
        super().__init__()

    def payload(self) -> dict:
        return {
            "token": self.token,
            "tokenType": self.tokenType,
            "receiveUnread": self.receive_unread_messages

        }
