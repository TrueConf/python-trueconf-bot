from dataclasses import dataclass, field

from .base import AbstractEnvelopeContent


@dataclass
class ParticipantRoleContent(AbstractEnvelopeContent):
    user_id: str = field(metadata={"alias": "userId"})
    role: str