from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from trueconf.types.content.base import AbstractEnvelopeContent
from trueconf.types.keyboard import InlineKeyboardMarkup


@dataclass
class TextContent(AbstractEnvelopeContent):
    text: str
    parse_mode: str = field(metadata={"alias": "parseMode"})
    buttons: InlineKeyboardMarkup | None = field(default=None)

    @classmethod
    def __pre_deserialize__(cls, d: dict[str, Any]) -> dict[str, Any]:
        data = dict(d)
        # Сервер присылает content.buttons как матрицу кнопок (list[list[dict]]),
        # а InlineKeyboardMarkup ждёт объект вида {"buttons": [...]}.
        if isinstance(data.get("buttons"), list):
            data["buttons"] = {"buttons": data["buttons"]}
        return data
