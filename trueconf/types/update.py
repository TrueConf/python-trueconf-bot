from __future__ import annotations
from dataclasses import dataclass
from mashumaro import DataClassDictMixin
from trueconf.client.context_controller import BoundToBot


@dataclass
class Update(BoundToBot, DataClassDictMixin):
    method: str
    type: int
    id: int
    payload: dict
