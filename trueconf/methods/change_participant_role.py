from __future__ import annotations
from dataclasses import dataclass
from trueconf.methods.base import TrueConfMethod
from trueconf.types.responses.change_participant_role_response import ChangeParticipantRoleResponse


@dataclass
class ChangeParticipantRole(TrueConfMethod[ChangeParticipantRoleResponse]):
    __api_method__ = "changeParticipantRole"
    __returning__ = ChangeParticipantRoleResponse

    chat_id: str
    user_id: str
    role: str


    def __post_init__(self):
        super().__init__()

    def payload(self):
        return {
            "chatId": self.chat_id,
            "userId": self.user_id,
            "role": self.role,
        }
