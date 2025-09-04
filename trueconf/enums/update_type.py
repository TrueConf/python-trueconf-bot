from enum import Enum


class UpdateType(int, Enum):
    """
    There are three types of messages. Only REQUEST and RESPONSE are applicable.

    Source:
        https://trueconf.com/docs/chatbot-connector/en/objects/#message-type
    """

    RESERVED = 0
    REQUEST = 1
    RESPONSE = 2
