from __future__ import annotations
from dataclasses import dataclass, field
from mashumaro import DataClassDictMixin
from trueconf.client.context_controller import BoundToBot
from trueconf.enums.chat_type import ChatType
from trueconf.types.last_message import LastMessage


@dataclass
class CreatedPersonalChat(BoundToBot, DataClassDictMixin):
    """
        **Event type:** a new personal chat was created.

        This object is received in the handler when a personal chat is created in TrueConf.

        Notes:
            This class is used as the event type in handler functions decorated with `@<router>.created_personal_chat()`.

        Source:
            https://trueconf.com/docs/chatbot-connector/en/server-requests/#createP2PChat

        Attributes:
            chat_id (str): Unique identifier of the personal chat.
            title (str): Title of the chat (usually the participant’s name).
            chat_type (ChatType): Type of the chat (should be `p2p`).
            last_message (LastMessage | None): The last message in the chat, if available.
            unread_messages (int): Number of unread messages in the personal chat.

        Examples:
            ```python
            from trueconf.types import CreatedPersonalChat

            @<router>.created_personal_chat()
            async def on_created(event: CreatedPersonalChat):
                print(f"Personal chat created with id {event.chat_id}")
            ```
        """
    chat_id: str = field(metadata={"alias": "chatId"})
    title: str
    chat_type: ChatType = field(metadata={"alias": "chatType"})
    last_message: LastMessage | None = field(metadata={"alias": "lastMessage"})
    unread_messages: int = field(metadata={"alias": "unreadMessages"})
