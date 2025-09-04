from __future__ import annotations
from dataclasses import dataclass, field
from mashumaro import DataClassDictMixin
from trueconf.client.context_controller import BoundToBot
from trueconf.types.author_box import EnvelopeAuthor


@dataclass
class RemovedMessage(BoundToBot, DataClassDictMixin):
    """
        **Event type:** a message was removed.

        This object is received in the handler when a message is deleted from a chat.

        Notes:
            This class is used as the event type in handler functions decorated with `@<router>.removed_message()`.

        Source:
            https://trueconf.com/docs/chatbot-connector/en/server-requests/#removeMessage

        Attributes:
            chat_id (str): Unique identifier of the chat from which the message was removed.
            message_id (str): Unique identifier of the removed message.
            removed_by (EnvelopeAuthor): Information about the user who removed the message.

        Examples:
            ```python
            from trueconf.types import RemovedMessage

            @<router>.removed_message()
            async def on_removed(event: RemovedMessage):
                print(f"Message {event.message_id} removed from chat {event.chat_id}")
            ```
        """
    chat_id: str = field(metadata={"alias": "chatId"})
    message_id: str = field(metadata={"alias": "messageId"})
    removed_by: EnvelopeAuthor = field(metadata={"alias": "removedBy"})