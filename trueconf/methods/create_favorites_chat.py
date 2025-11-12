from __future__ import annotations
from dataclasses import dataclass
from trueconf.methods.base import TrueConfMethod
from trueconf.types.responses.create_favorites_chat_response import CreateFavoritesChatResponse


@dataclass
class CreateFavoritesChat(TrueConfMethod[CreateFavoritesChatResponse]):
    __api_method__ = "createFavoritesChat"
    __returning__ = CreateFavoritesChatResponse

    def __post_init__(self):
        super().__init__()

    def payload(self):
        return {}
