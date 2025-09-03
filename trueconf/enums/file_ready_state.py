from enum import Enum


class FileReadyState(int, Enum):
    """
    This enumeration is used to indicate the status of a file on the server.

    Source:
        https://trueconf.com/docs/chatbot-connector/en/objects/#filereadystateenum
    """

    NOT_AVAILABLE = 0
    UPLOADING = 1
    READY = 2
