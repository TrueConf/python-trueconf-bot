from __future__ import annotations

from dataclasses import dataclass, field

from mashumaro import DataClassDictMixin


@dataclass
class SendFileResponse(DataClassDictMixin):
    timestamp: int
    chat_id: str = field(metadata={"alias": "chatId"})
    message_id: str = field(metadata={"alias": "messageId"})
    file_id: str = field(metadata={"alias": "fileId"})
    caption_message_id: str | None = field(default=None, metadata={"alias": "captionMessageId"})
