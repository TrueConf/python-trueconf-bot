from __future__ import annotations
from dataclasses import dataclass, field
from typing import List, Annotated
from mashumaro import DataClassDictMixin
from trueconf.client.context_controller import BoundToBot

DecimalBytes = Annotated[int, "bytes", "SI"]

@dataclass
class Extensions(DataClassDictMixin):
    mode: str
    list: List[str]

@dataclass
class ChangedFileUploadLimits(BoundToBot, DataClassDictMixin):
    max_size: DecimalBytes | None = field(metadata={"alias": "maxSize"})
    extensions: Extensions | None

