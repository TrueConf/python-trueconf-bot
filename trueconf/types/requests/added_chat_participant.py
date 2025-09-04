from __future__ import annotations
from dataclasses import dataclass, field
from mashumaro import DataClassDictMixin
from trueconf.client.context_controller import BoundToBot
from trueconf.types.author_box import EnvelopeAuthor


@dataclass
class AddedChatParticipant(BoundToBot, DataClassDictMixin):
    """
    **Event type:** a new participant was added to a chat.

    This object is received in the handler when a user is added to a personal chat, group chat, channel, or conference chat.

    Notes:
        This class is used as the event type in handler functions decorated with `@<router>.added_chat_participant()`.

    Source:
        https://trueconf.com/docs/chatbot-connector/en/server-requests/#addChatParticipant

    Attributes:
        timestamp (int): Unix timestamp (milliseconds) of when the event occurred.
        chat_id (str): Unique identifier of the chat where the participant was added.
        user_id (str): TrueConf ID of the participant who was added.
        added_by (EnvelopeAuthor): Information about the user who added the participant.

    Examples:
        ```python
        from trueconf.types import AddedChatParticipant

        @<router>.added_chat_participant()
        async def on_added(event: AddedChatParticipant):
            print(event.user_id)
        ```
    """

    timestamp: int
    chat_id: str = field(metadata={"alias": "chatId"})
    user_id: str = field(metadata={"alias": "userId"})
    added_by: EnvelopeAuthor = field(metadata={"alias": "addedBy"})
