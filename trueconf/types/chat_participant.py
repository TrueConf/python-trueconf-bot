from __future__ import annotations
from dataclasses import dataclass, field
from mashumaro import DataClassDictMixin

from trueconf.enums import ChatParticipantRole

@dataclass
class ChatParticipant(DataClassDictMixin):
    user_id: str = field(metadata={"alias": "id"})
    role: ChatParticipantRole