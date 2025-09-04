from __future__ import annotations
from dataclasses import dataclass, field
from mashumaro import DataClassDictMixin


@dataclass
class AuthResponsePayload(DataClassDictMixin):
    user_id: str = field(metadata={"alias": "userId"})
    connection_id: str = field(metadata={"alias": "connectionId"})
