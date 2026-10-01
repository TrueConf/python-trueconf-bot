from enum import Enum

ALLOWED_BUTTON_URL_SCHEMES = ("http", "https", "mailto", "trueconf")


class ButtonStyle(str, Enum):
    DEFAULT = "default"
    PRIMARY = "primary"
    DANGER = "danger"
    SUCCESS = "success"


class ButtonType(str, Enum):
    COMMAND = "command"
    URL = "url"
    MESSAGE = "message"
    COPY = "copy"
    SHARE = "share"
