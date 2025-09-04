from __future__ import annotations
from dataclasses import dataclass, field
from mashumaro import DataClassDictMixin
from trueconf.client.context_controller import BoundToBot
from trueconf.types.content.text import TextContent


@dataclass
class EditedMessage(BoundToBot, DataClassDictMixin):
    """
       **Event type:** a message was edited.

       This object is received in the handler when a previously sent message is edited in a chat.

       Notes:
           This class is used as the event type in handler functions decorated with `@<router>.edited_message()`.

       Source:
           https://trueconf.com/docs/chatbot-connector/en/server-requests/#editMessage

       Attributes:
           timestamp (int): Unix timestamp (milliseconds) of when the edit occurred.
           content (TextContent): The updated content of the edited message.
           chat_id (str): Unique identifier of the chat where the message was edited.

       Examples:
           ```python
           from trueconf.types import EditedMessage

           @<router>.edited_message()
           async def on_edited(event: EditedMessage):
               print(f"Message in chat {event.chat_id} was edited: {event.content.text}")
           ```
       """
    timestamp: int
    content: TextContent
    chat_id: str = field(metadata={"alias": "chatId"})
