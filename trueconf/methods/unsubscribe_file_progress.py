from dataclasses import dataclass

from .base import TrueConfMethod
from ..types.responses import UnsubscribeFileProgressResponse


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
