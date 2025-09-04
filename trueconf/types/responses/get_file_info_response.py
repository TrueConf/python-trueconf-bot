from __future__ import annotations
from dataclasses import dataclass, field
from typing import Optional, List
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
    info_hash: str = field(metadata={"alias": "infoHash"})
