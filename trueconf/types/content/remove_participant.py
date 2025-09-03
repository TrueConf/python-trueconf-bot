from dataclasses import dataclass, field

from .base import AbstractEnvelopeContent


@dataclass
class RemoveParticipant(AbstractEnvelopeContent):
    user_id: str = field(metadata={"alias": "userId"})