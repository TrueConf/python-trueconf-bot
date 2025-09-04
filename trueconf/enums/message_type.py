from enum import Enum
from typing import Any


class MessageType(int, Enum):
    """
    The enumeration contains the message type.

    Source:
        https://trueconf.com/docs/chatbot-connector/en/objects/#envelopetypeenum
    """

    ADD_PARTICIPANT = 1
    REMOVE_PARTICIPANT = 2
    PARTICIPANT_ROLE = 110
    PLAIN_MESSAGE = 200
    FORWARDED_MESSAGE = 201
    ATTACHMENT = 202
    SURVEY = 204

    async def __call__(self, event: Any) -> bool:
        if getattr(event, "type", None) is None:
            return False
        try:
            return int(getattr(event, "type")) == int(self)
        except Exception:
            return False
