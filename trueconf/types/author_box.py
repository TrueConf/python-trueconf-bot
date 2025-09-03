from dataclasses import dataclass

from mashumaro import DataClassDictMixin

from trueconf.enums import EnvelopeAuthorType


@dataclass
class EnvelopeAuthor(DataClassDictMixin):
    id: str
    type: EnvelopeAuthorType

@dataclass
class EnvelopeBox(DataClassDictMixin):
    id: int
    position: str