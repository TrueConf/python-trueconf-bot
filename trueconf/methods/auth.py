from dataclasses import dataclass

from .base import TrueConfMethod
from ..types.responses import AuthResponsePayload


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