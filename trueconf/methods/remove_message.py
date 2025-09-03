from dataclasses import dataclass

from .base import TrueConfMethod
from ..types.responses import RemoveMessageResponse


@dataclass
class RemoveMessage(TrueConfMethod[RemoveMessageResponse]):
    __api_method__ = "removeMessage"
    __returning__ = RemoveMessageResponse

    message_id: str
    for_all: bool

    def __post_init__(self):
        super().__init__()

    def payload(self):
        return {
            "messageId": self.message_id,
            "forAll": self.for_all
        }
