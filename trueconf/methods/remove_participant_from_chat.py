from __future__ import annotations
from __future__ import annotations
from dataclasses import dataclass
from trueconf.methods.base import TrueConfMethod
from trueconf.types.responses.remove_chat_participant_response import RemoveChatParticipantResponse


@dataclass
class RemoveChatParticipant(TrueConfMethod[RemoveChatParticipantResponse]):
    __api_method__ = "removeChatParticipant"
    __returning__ = RemoveChatParticipantResponse

    chat_id: str
    user_id: str

    def __post_init__(self):
        super().__init__()

    def payload(self):
        return {
            "chatId": self.chat_id,
            "userId": self.user_id
        }
