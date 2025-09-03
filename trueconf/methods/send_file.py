from dataclasses import dataclass

from .base import TrueConfMethod
from ..types.responses import SendFileResponse


@dataclass
class SendFile(TrueConfMethod[SendFileResponse]):
    __api_method__ = "sendFile"
    __returning__ = SendFileResponse

    chat_id: str
    temporal_file_id: str

    def __post_init__(self):
        super().__init__()

    def payload(self):
        return {
            "chatId": self.chat_id,
                "content": {
                    "temporalFileId": self.temporal_file_id,
                }
        }
