from enum import Enum


class ParseMode(str, Enum):
    """
    Formatting options

    Source:
        https://trueconf.com/docs/chatbot-connector/en/messages/#message-formatting
    """

    TEXT = "text"
    MARKDOWN = "markdown"
    HTML = "html"
