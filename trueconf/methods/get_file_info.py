from dataclasses import dataclass

from .base import TrueConfMethod
from ..types.responses import GetFileInfoResponse


@dataclass
class GetFileInfo(TrueConfMethod[GetFileInfoResponse]):
    __api_method__ = "getFileInfo"
    __returning__ = GetFileInfoResponse

    file_id: str

    def __post_init__(self):
        super().__init__()

    def payload(self):
        return {
            "fileId": self.file_id
        }
