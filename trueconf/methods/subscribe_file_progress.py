from dataclasses import dataclass

from .base import TrueConfMethod
from ..types.responses import SubscribeFileProgressResponse


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
