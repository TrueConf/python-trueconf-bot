from __future__ import annotations
from dataclasses import dataclass
from mashumaro import DataClassDictMixin

from trueconf.enums.envelope_author_type import EnvelopeAuthorType


@dataclass
class EnvelopeAuthor(DataClassDictMixin):
    id: str
    type: EnvelopeAuthorType


@dataclass
class EnvelopeBox(DataClassDictMixin):
    id: int
    position: str
