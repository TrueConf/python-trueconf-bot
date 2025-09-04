from __future__ import annotations
from dataclasses import dataclass, field
from typing import Optional
from trueconf.client.context_controller import BoundToBot
from trueconf.types.content.base import AbstractEnvelopeContent


@dataclass
class AttachmentContent(BoundToBot, AbstractEnvelopeContent):
    file_name: str = field(metadata={"alias": "name"})
    file_size: int = field(metadata={"alias": "size"})
    file_id: str = field(default="", metadata={"alias": "fileId"})
    mimetype: str = field(default="", metadata={"alias": "mimeType"})
    ready_state: Optional[int] = field(default=None, metadata={"alias": "readyState"})
