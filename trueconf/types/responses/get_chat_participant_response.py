from __future__ import annotations
from dataclasses import dataclass, field
from mashumaro import DataClassDictMixin
from trueconf.enums.chat_participant_role import ChatParticipantRole
from trueconf.enums.envelope_author_type import EnvelopeAuthorType


@dataclass
class GetChatParticipantResponse(DataClassDictMixin):
    role: ChatParticipantRole
    type: EnvelopeAuthorType
    user_id: str = field(metadata={"alias": "userId"})
