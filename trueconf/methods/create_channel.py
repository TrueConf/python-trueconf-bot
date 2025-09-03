from dataclasses import dataclass

from .base import TrueConfMethod
from ..types.responses import CreateChannelResponse


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

