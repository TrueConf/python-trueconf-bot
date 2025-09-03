# trueconf/types/content/text.py
from dataclasses import dataclass, field
from typing import Optional

from .base import AbstractEnvelopeContent


@dataclass
class TextContent(AbstractEnvelopeContent):
    text: str
    parse_mode: str = field(metadata={"alias": "parseMode"})