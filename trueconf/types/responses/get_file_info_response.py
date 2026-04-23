from __future__ import annotations
from dataclasses import dataclass, field
from typing import Optional, List, Any
from mashumaro import DataClassDictMixin
from trueconf.enums.file_ready_state import FileReadyState


@dataclass
class Previews(DataClassDictMixin):
    name: str
    size: int
    mimetype: str = field(metadata={"alias": "mimeType"})
    download_url: str = field(metadata={"alias": "downloadUrl"})


@dataclass
class GetFileInfoResponse(DataClassDictMixin):
    name: str
    size: int
    previews: Optional[List[Previews]]
    mimetype: str = field(metadata={"alias": "mimeType"})
    download_url: Optional[str] = field(metadata={"alias": "downloadUrl"})
    ready_state: FileReadyState = field(metadata={"alias": "readyState"})
    file_id: str = field(metadata={"alias": "fileId"})

    @classmethod
    def __pre_deserialize__(cls, d: dict[Any, Any]) -> dict[Any, Any]:
        d = dict(d)
        if "infoHash" in d and "fileId" not in d:
            d["fileId"] = d.pop("infoHash")

        return d