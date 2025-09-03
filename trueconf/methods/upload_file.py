from dataclasses import dataclass

from .base import TrueConfMethod
from ..types.responses import UploadFileResponse


@dataclass
class UploadFile(TrueConfMethod[UploadFileResponse]):
    __api_method__ = "uploadFile"
    __returning__ = UploadFileResponse

    file_size: int

    def __post_init__(self):
        super().__init__()

    def payload(self):
        return {
            "fileSize": self.file_size,
        }
