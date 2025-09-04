from enum import Enum


class ChatParticipantRole(str, Enum):
    """
    This object represents a possible participant role in a chat.

    Source:
        https://trueconf.com/docs/chatbot-connector/en/objects/#chatparticipantroleenum
    """

    OWNER = "owner"
    ADMIN = "admin"
    USER = "user"
    CONF_OWNER = "conf_owner"
    CONF_MODERATOR = "conf_moderator"
    FAVORITES_OWNER = "favorites_owner"
    WRITER = "writer"
