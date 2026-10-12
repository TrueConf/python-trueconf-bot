from __future__ import annotations

from trueconf.enums.message_type import MessageType
from trueconf.types.content.parser import SYSTEM_CONTENT_TYPES, USER_CONTENT_TYPES, UnsupportedMessageType
from trueconf.types.message import Message
from trueconf.types.system_message import SystemMessage


def deserialize_envelope(raw: dict) -> Message | SystemMessage:
    # Live membership: `ForwardMessage` self-registers after this module loads.
    try:
        message_type = MessageType(raw.get("type", 0))
    except ValueError as error:
        raise UnsupportedMessageType(raw.get("type")) from error

    if message_type in USER_CONTENT_TYPES:
        return Message.from_dict(raw)
    if message_type in SYSTEM_CONTENT_TYPES:
        return SystemMessage.from_dict(raw)
    raise UnsupportedMessageType(message_type)


def deserialize_envelopes(raw: list[dict]) -> list[Message | SystemMessage]:
    return [deserialize_envelope(item) for item in raw]
