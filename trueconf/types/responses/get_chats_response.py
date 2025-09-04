from __future__ import annotations
from dataclasses import dataclass, field
from typing import List
from mashumaro import DataClassDictMixin
from trueconf.types.responses.get_chat_by_id_response import GetChatByIdResponse


@dataclass
class GetChatsResponse(DataClassDictMixin):
    chats: List[GetChatByIdResponse] = field(
        default_factory=list,
        metadata={"alias": "chats"})
