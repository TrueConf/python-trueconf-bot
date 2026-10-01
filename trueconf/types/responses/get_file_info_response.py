from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, List

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
    mimetype: str = field(metadata={"alias": "mimeType"})
    ready_state: FileReadyState = field(metadata={"alias": "readyState"})
    file_id: str = field(metadata={"alias": "fileId"})
    previews: List[Previews] | None = field(default=None)
    download_url: str | None = field(default=None, metadata={"alias": "downloadUrl"})

    @classmethod
    def __pre_deserialize__(cls, d: dict[Any, Any]) -> dict[Any, Any]:
        d = dict(d)
        if "infoHash" in d and "fileId" not in d:
            d["fileId"] = d.pop("infoHash")

        return d
