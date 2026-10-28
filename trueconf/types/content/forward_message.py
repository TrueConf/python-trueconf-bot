from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from trueconf.enums.message_type import MessageType
from trueconf.types.content.attachment import AttachmentContent
from trueconf.types.content.location import Location
from trueconf.types.content.parser import USER_CONTENT_TYPES
from trueconf.types.content.survey import SurveyContent
from trueconf.types.content.text import TextContent
from trueconf.types.content.voice import Voice
from trueconf.types.message import Message


@dataclass(kw_only=True)
class ForwardMessage(Message):
    """
    Content of a forwarded message (`FORWARDED_MESSAGE`, type 201).

    Corresponds to the [ForwardMessageContent][1] interface: the `Envelope`
    of the forwarded original message without the `box` field. `isEdited` is
    optional here (`False` when absent): the server omits it inside a forward,
    notably in `getChatById`'s `lastMessage`.

    The class inherits from `Message`, so the forwarded original is a fully
    functional message: shortcuts such as `text`, `voice`, `document`,
    `reply_message` and `bind` work on it. The inner `content` carries the
    forwarded original's type (`200`..`205`) and its flat content, which is
    resolved by shape.

    [1]: https://trueconf.ru/docs/chatbot-connector/ru/objects/#ForwardMessageContent
    """

    # Overrides the parent field (no `pass_through`) so mashumaro resolves
    # the content by shape; `Message` last is the fallback for the envelope form.
    content: TextContent | AttachmentContent | SurveyContent | Location | Voice | Message

    # The server omits `isEdited` from `ForwardMessageContent` (observed in
    # `getChatById`'s `lastMessage`), and the inner copy carries no edit state.
    # The parent keeps it required for real `Envelope` updates.
    is_edited: bool = field(default=False, metadata={"alias": "isEdited"})

    @classmethod
    def __pre_deserialize__(cls, d: dict[str, Any]) -> dict[str, Any]:
        # Suppress the parent dispatch; the content union above resolves it.
        return dict(d)


# Self-registration (importing this from `parser` would be circular: the
# class inherits from `Message`, which imports `parser`).
USER_CONTENT_TYPES[MessageType.FORWARDED_MESSAGE] = ForwardMessage
