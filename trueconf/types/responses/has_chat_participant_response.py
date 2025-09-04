from __future__ import annotations
from dataclasses import dataclass
from mashumaro import DataClassDictMixin


@dataclass
class HasChatParticipantResponse(DataClassDictMixin):
    result: bool
