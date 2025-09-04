from __future__ import annotations
from dataclasses import dataclass, field
from mashumaro import DataClassDictMixin
from trueconf.client.context_controller import BoundToBot


@dataclass
class RemovedChat(BoundToBot, DataClassDictMixin):
    """
        **Event type:** a chat was removed.

        This object is received in the handler when a private, group, channel, or conference chat is deleted.

        Notes:
            This class is used as the event type in handler functions decorated with `@<router>.removed_chat()`.

        Source:
            https://trueconf.com/docs/chatbot-connector/en/server-requests/#removeChat

        Attributes:
            chat_id (str): Unique identifier of the chat that was removed.

        Examples:
            ```python
            from trueconf.types import RemovedChat

            @<router>.removed_chat()
            async def on_removed(event: RemovedChat):
                print(f"Chat removed: {event.chat_id}")
            ```
        """
    chat_id: str = field(metadata={"alias": "chatId"})
