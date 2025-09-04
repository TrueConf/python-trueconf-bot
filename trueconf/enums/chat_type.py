from enum import Enum


class ChatType(int, Enum):
    """
    The enumeration contains possible chat types.

    Source:
        https://trueconf.com/docs/chatbot-connector/en/objects/#chattypeenum
    """

    UNDEF = 0
    P2P = 1
    GROUP = 2
    SYSTEM = 3
    FAVORITES = 5
    CHANNEL = 6
