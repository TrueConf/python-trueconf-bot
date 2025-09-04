from __future__ import annotations
from dataclasses import dataclass, field
from trueconf.types.content.base import AbstractEnvelopeContent


@dataclass
class TextContent(AbstractEnvelopeContent):
    text: str
    parse_mode: str = field(metadata={"alias": "parseMode"})
