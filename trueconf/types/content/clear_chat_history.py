from __future__ import annotations

from dataclasses import dataclass, field

from trueconf.types.content.base import AbstractEnvelopeContent


@dataclass
class ClearChatHistoryContent(AbstractEnvelopeContent):
    for_all: bool = field(metadata={"alias": "forAll"})
