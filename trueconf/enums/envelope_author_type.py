from enum import Enum


class EnvelopeAuthorType(int, Enum):
    """
    The enumeration contains possible author types.

    Source:
        https://trueconf.com/docs/chatbot-connector/en/objects/#envelopeauthortypeenum
    """

    SYSTEM = 0
    USER = 1
