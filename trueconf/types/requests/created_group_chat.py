from __future__ import annotations
from dataclasses import dataclass, field
from mashumaro import DataClassDictMixin
from trueconf.client.context_controller import BoundToBot
from trueconf.enums.chat_type import ChatType
from trueconf.types.last_message import LastMessage


@dataclass
class CreatedGroupChat(BoundToBot, DataClassDictMixin):
    """
        **Event type:** a new group chat was created.

        This object is received in the handler when a group chat is created in TrueConf.

        Notes:
            This class is used as the event type in handler functions decorated with `@<router>.created_group_chat()`.

        Source:
            https://trueconf.com/docs/chatbot-connector/en/server-requests/#createGroupChat

        Attributes:
            chat_id (str): Unique identifier of the group chat.
            title (str): Title of the group chat.
            chat_type (ChatType): Type of the chat (should be `group`).
            last_message (LastMessage | None): The last message in the chat, if available.
            unread_messages (int): Number of unread messages in the group chat.

        Examples:
            ```python
            from trueconf.types import CreatedGroupChat

            @<router>.created_group_chat()
            async def on_created(event: CreatedGroupChat):
                print(f"Group chat {event.title} created with id {event.chat_id}")
            ```
        """
    chat_id: str = field(metadata={"alias": "chatId"})
    title: str
    chat_type: ChatType = field(metadata={"alias": "chatType"})
    last_message: LastMessage | None = field(metadata={"alias": "lastMessage"})
    unread_messages: int = field(metadata={"alias": "unreadMessages"})