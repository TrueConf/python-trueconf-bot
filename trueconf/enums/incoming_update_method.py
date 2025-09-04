from enum import Enum


class IncomingUpdateMethod(str, Enum):
    ADDED_CHAT_PARTICIPANT = "addChatParticipant"
    CREATED_CHANNEL = "createChannel"
    CREATED_GROUP_CHAT = "createGroupChat"
    CREATED_PERSONAL_CHAT = "createP2PChat"
    EDITED_MESSAGE = "editMessage"
    REMOVED_CHAT_PARTICIPANT = "removeChatParticipant"
    REMOVED_MESSAGE = "removeMessage"
    MESSAGE = "sendMessage"
    UPLOADING_PROGRESS = "uploadFileProgress"
    REMOVED_CHAT = "removeChat"
