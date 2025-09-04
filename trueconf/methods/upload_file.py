from __future__ import annotations
from __future__ import annotations
from dataclasses import dataclass
from trueconf.methods.base import TrueConfMethod
from trueconf.types.responses.upload_file_response import UploadFileResponse


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
