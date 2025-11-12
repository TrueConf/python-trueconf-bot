from __future__ import annotations
from dataclasses import dataclass, field
from mashumaro import DataClassDictMixin
from trueconf.client.context_controller import BoundToBot


@dataclass
class ChangedParticipantRole(BoundToBot, DataClassDictMixin):
    """
    **Event type:** a participant's role was changed in a chat.

    This object is received in the handler when a participant's role is changed in a personal chat, group chat, channel, or conference chat.

    Notes:
        This class is used as the event type in handler functions decorated with `@<router>.changed_chat_participant_role()`.

    Source:
        https://trueconf.com/docs/chatbot-connector/en/chats/#changedParticipantRole

    Attributes:
        timestamp (int): Unix timestamp (in milliseconds) when the role change occurred.
        role (str): New role assigned to the participant.
        chat_id (str): Identifier of the chat where the role change occurred.
        user_id (str): TrueConf ID of the participant whose role was changed.

    Example:
        ```python
        from trueconf.types import ChangedParticipantRole

        @router.changed_chat_participant_role()
        async def on_role_changed(event: ChangedParticipantRole):
            print(f"User {event.user_id} now has role {event.role} in chat {event.chat_id}")
        ```
    """

    timestamp: int
    role: str
    chat_id: str = field(metadata={"alias": "chatId"})
    user_id: str = field(metadata={"alias": "userId"})

