from __future__ import annotations
from dataclasses import dataclass, field
from typing import List
from mashumaro import DataClassDictMixin


@dataclass
class Extensions(DataClassDictMixin):
    mode: str
    list: List[str]


@dataclass
class GetFileUploadLimitsResponse(DataClassDictMixin):
    extensions: Extensions | None
    max_size: int | None = field(default=None, metadata={"alias": "maxSize"})