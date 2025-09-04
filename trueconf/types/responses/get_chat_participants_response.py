from __future__ import annotations
from dataclasses import dataclass, field
from typing import List
from mashumaro import DataClassDictMixin
from trueconf.types.chat_participant import ChatParticipant


@dataclass
class GetChatParticipantsResponse(DataClassDictMixin):
    participants: List[ChatParticipant] = field(
        default_factory=list,
        metadata={"alias": "participants"})
