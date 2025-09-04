from __future__ import annotations
from dataclasses import dataclass
from trueconf.methods.base import TrueConfMethod
from trueconf.types.responses.create_channel_response import CreateChannelResponse


@dataclass
class CreateChannel(TrueConfMethod[CreateChannelResponse]):
    __api_method__ = "createChannel"
    __returning__ = CreateChannelResponse

    title: str

    def __post_init__(self):
        super().__init__()

    def payload(self):
        return {
            "title": self.title,
        }
