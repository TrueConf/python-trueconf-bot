from __future__ import annotations
from dataclasses import dataclass, field
from mashumaro import DataClassDictMixin


@dataclass
class UploadFileResponse(DataClassDictMixin):
    upload_task_id: str = field(metadata={"alias": "uploadTaskId"})
