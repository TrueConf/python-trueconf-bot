from dataclasses import dataclass

from .base import TrueConfMethod
from ..types.responses import EditMessageResponse


@dataclass
class EditMessage(TrueConfMethod[EditMessageResponse]):
    __api_method__ = "editMessage"
    __returning__ = EditMessageResponse
    message_id: str
    text: str
    parse_mode: str

    def __post_init__(self):
        super().__init__()

    def payload(self):
        return {
            "messageId": self.message_id,
            "content": {
                "text": self.text,
                "parseMode": self.parse_mode,
            },
        }
