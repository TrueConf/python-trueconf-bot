from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from trueconf.enums.command import (
    CommandAnswerType,
    CommandMessageLevel,
    CommandMessageStatus,
    CommandMessageVisibility,
)
from trueconf.methods.base import TrueConfMethod
from trueconf.types.responses.answer_command_response import AnswerCommandResponse


@dataclass
class AnswerCommand(TrueConfMethod[AnswerCommandResponse]):
    __api_method__ = "answerCommand"
    __returning__ = AnswerCommandResponse

    command_id: str
    answer_type: CommandAnswerType | str
    text: str
    status: CommandMessageStatus | str | None = None
    visibility: CommandMessageVisibility | str | None = None
    level: CommandMessageLevel | str | None = None

    def __post_init__(self):
        raise NotImplementedError(
            "This functionality is supported by TrueConf Server, provided that client applications "
            "support it as well. It is not yet available in this library and will be enabled once "
            "client-side support becomes available. Please follow library updates for announcements."
        )
        if not self.command_id:
            raise ValueError("Answer command command_id must not be empty")
        if not 1 <= len(self.text) <= 255:
            raise ValueError(f"Answer command text length must be between 1 and 255 characters; got: {len(self.text)}")
        if not self.text.isascii():
            raise ValueError("Answer command text must contain ASCII characters only")
        super().__init__()

    def payload(self) -> dict:
        payload = {
            "commandId": self.command_id,
            "answerType": self._value(self.answer_type),
        }
        message = {"text": self.text}
        for wire_name, value in (
            ("status", self.status),
            ("visibility", self.visibility),
            ("level", self.level),
        ):
            if value is not None:
                message[wire_name] = self._value(value)
        payload["message"] = message
        return payload

    @staticmethod
    def _value(value: Enum | str) -> str:
        return value.value if isinstance(value, Enum) else value
