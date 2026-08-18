from __future__ import annotations
from dataclasses import dataclass, field
from trueconf.types.content.base import AbstractEnvelopeContent


@dataclass
class EditChatAvatarContent(AbstractEnvelopeContent):
    avatar_url: str = field(metadata={"alias": "avatarUrl"})
