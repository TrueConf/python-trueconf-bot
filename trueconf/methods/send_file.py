from __future__ import annotations
from __future__ import annotations
from dataclasses import dataclass
from trueconf.methods.base import TrueConfMethod
from trueconf.types.responses.send_file_response import SendFileResponse


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
