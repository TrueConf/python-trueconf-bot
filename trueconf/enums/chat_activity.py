from enum import Enum


class ChatActivity(str, Enum):
    """
    This object represents a type of activity that the bot can show in a chat.

    Source:
        https://trueconf.com/docs/chatbot-connector/en/messages/#sendChatActivity
    """

    TYPING = "typing"
    CHOOSING_STICKER = "choosing_sticker"
    UPLOADING_FILE = "uploading_file"
