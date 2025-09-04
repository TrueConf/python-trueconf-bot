from __future__ import annotations
from dataclasses import dataclass, field
from mashumaro import DataClassDictMixin
from trueconf.client.context_controller import BoundToBot
from trueconf.types.author_box import EnvelopeAuthor


@dataclass
class RemovedChatParticipant(BoundToBot, DataClassDictMixin):
    """
        **Event type:** a participant was removed from a chat.

        This object is received in the handler when a user is removed from a group, channel, or conference chat.

        Notes:
            This class is used as the event type in handler functions decorated with `@<router>.removed_chat_participant()`.

        Source:
            https://trueconf.com/docs/chatbot-connector/en/server-requests/#removeChatParticipant

        Attributes:
            timestamp (int): Unix timestamp (milliseconds) of when the event occurred.
            chat_id (str): Unique identifier of the chat where the participant was removed.
            user_id (str): TrueConf ID of the participant who was removed.
            removed_by (EnvelopeAuthor): Information about the user who removed the participant.

        Examples:
            ```python
            from trueconf.types import RemovedChatParticipant

            @<router>.removed_chat_participant()
            async def on_removed(event: RemovedChatParticipant):
                print(event.user_id)
            ```
        """
    timestamp: int
    chat_id: str = field(metadata={"alias": "chatId"})
    user_id: str = field(metadata={"alias": "userId"})
    removed_by: EnvelopeAuthor = field(metadata={"alias": "removedBy"})
