from __future__ import annotations
from dataclasses import dataclass
from trueconf.methods.base import TrueConfMethod
from trueconf.types.responses import GetFileUploadLimitsResponse

@dataclass
class GetFileUploadLimits(TrueConfMethod[GetFileUploadLimitsResponse]):
    __api_method__ = "getFileUploadLimits"
    __returning__ = GetFileUploadLimitsResponse

    def __post_init__(self):
        super().__init__()

    def payload(self):
        return {
        }
