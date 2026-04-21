from __future__ import annotations
from dataclasses import dataclass
from trueconf.methods.base import TrueConfMethod
from trueconf.types.responses.edit_chat_avatar_response import EditChatAvatarResponse


@dataclass
class EditChatAvatar(TrueConfMethod[EditChatAvatarResponse]):
    __api_method__ = "editChatAvatar"
    __returning__ = EditChatAvatarResponse

    chat_id: str
    temporal_file_id: str

    def __post_init__(self):
        super().__init__()

    def payload(self):
        return {
            "chatId": self.chat_id,
            "temporalFileId": self.temporal_file_id,
        }
