from __future__ import annotations
from __future__ import annotations
from dataclasses import dataclass
from trueconf.methods.base import TrueConfMethod
from trueconf.types.responses.subscribe_file_progress_response import SubscribeFileProgressResponse


@dataclass
class SubscribeFileProgress(TrueConfMethod[SubscribeFileProgressResponse]):
    __api_method__ = "subscribeFileProgress"
    __returning__ = SubscribeFileProgressResponse

    file_id: str

    def __post_init__(self):
        super().__init__()

    def payload(self):
        return {
            "fileId": self.file_id
        }
