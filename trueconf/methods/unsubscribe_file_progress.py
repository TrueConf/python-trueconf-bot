from __future__ import annotations
from __future__ import annotations
from dataclasses import dataclass
from trueconf.methods.base import TrueConfMethod
from trueconf.types.responses.unsubscribe_file_progress_response import UnsubscribeFileProgressResponse


@dataclass
class UnsubscribeFileProgress(TrueConfMethod[UnsubscribeFileProgressResponse]):
    __api_method__ = "unsubscribeFileProgress"
    __returning__ = UnsubscribeFileProgressResponse

    file_id: str

    def __post_init__(self):
        super().__init__()

    def payload(self):
        return {
            "fileId": self.file_id
        }
