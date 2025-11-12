from __future__ import annotations
from dataclasses import dataclass, field
from mashumaro import DataClassDictMixin


@dataclass
class CreateFavoritesChatResponse(DataClassDictMixin):
    chat_id: str = field(metadata={"alias": "chatId"})
