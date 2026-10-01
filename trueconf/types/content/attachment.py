from __future__ import annotations

import warnings
from dataclasses import dataclass, field

from trueconf.client.context_controller import BoundToBot
from trueconf.types.content.base import AbstractEnvelopeContent


@dataclass
class AttachmentContent(BoundToBot, AbstractEnvelopeContent):
    file_name: str = field(metadata={"alias": "name"})
    file_size: int = field(metadata={"alias": "size"})
    file_id: str = field(default="", metadata={"alias": "fileId"})
    mime_type: str = field(default="", metadata={"alias": "mimeType"})
    ready_state: int | None = field(default=None, metadata={"alias": "readyState"})

    @property
    def mimetype(self) -> str:
        warnings.warn(
            "mimetype is deprecated; use mime_type instead",
            DeprecationWarning,
            stacklevel=2,
        )
        return self.mime_type
