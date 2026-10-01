from __future__ import annotations

from dataclasses import dataclass, field

from trueconf.methods.base import TrueConfMethod
from trueconf.types.keyboard import InlineKeyboardMarkup
from trueconf.types.responses.edit_message_response import EditMessageResponse


@dataclass
class EditMessage(TrueConfMethod[EditMessageResponse]):
    __api_method__ = "editMessage"
    __returning__ = EditMessageResponse
    message_id: str
    text: str
    parse_mode: str
    buttons: InlineKeyboardMarkup | None = field(default=None, kw_only=True)

    def __post_init__(self):
        super().__init__()

    def payload(self):
        content = {
            "text": self.text,
            "parseMode": self.parse_mode,
        }
        if self.buttons is not None:
            content.update(self.buttons.to_dict())

        return {
            "messageId": self.message_id,
            "content": content,
        }
