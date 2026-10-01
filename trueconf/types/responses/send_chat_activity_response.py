from __future__ import annotations

from dataclasses import dataclass, field

from mashumaro import DataClassDictMixin


@dataclass
class SendChatActivityResponse(DataClassDictMixin):
    chat_id: str = field(metadata={"alias": "chatId"})
    activity_type: str = field(metadata={"alias": "activityType"})
    retry_after: int = field(metadata={"alias": "retryAfter"})
