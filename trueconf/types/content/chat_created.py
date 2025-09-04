from __future__ import annotations
from dataclasses import dataclass, field
from trueconf.types.content.base import AbstractEnvelopeContent


@dataclass
class ParticipantRoleContent(AbstractEnvelopeContent):
    user_id: str = field(metadata={"alias": "userId"})
    role: str
