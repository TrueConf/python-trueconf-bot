from __future__ import annotations
from dataclasses import dataclass, field
from mashumaro import DataClassDictMixin


@dataclass
class GetUserDisplayNameResponse(DataClassDictMixin):
    display_name: str = field(metadata={"alias": "displayName"})
