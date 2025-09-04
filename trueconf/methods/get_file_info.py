from __future__ import annotations
from dataclasses import dataclass
from trueconf.methods.base import TrueConfMethod
from trueconf.types.responses.get_file_info_response import GetFileInfoResponse


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
