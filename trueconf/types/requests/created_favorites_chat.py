from __future__ import annotations
from dataclasses import dataclass, field
from mashumaro import DataClassDictMixin
from trueconf.client.context_controller import BoundToBot
from trueconf.enums.chat_type import ChatType
from trueconf.types.last_message import LastMessage


@dataclass
class CreatedFavoritesChat(BoundToBot, DataClassDictMixin):
    """
    **Event type:** a personal Favorites chat was created.

    This object is received in the handler when a Favorites chat is created for the bot in TrueConf.

    Notes:
        This class is used as the event type in handler functions decorated with `@<router>.created_favorites_chat()`.

    Source:
        https://trueconf.com/docs/chatbot-connector/en/chats/#createdFavoritesChat

    Attributes:
        chat_id (str): Unique identifier of the Favorites chat.
        title (str | None): Title of the chat, if available.
        chat_type (ChatType): Type of the chat (should be `favorites`).
        last_message (LastMessage | None): The last message in the chat, if available.
        unread_messages (int): Number of unread messages in the chat.

    Examples:
        ```python
        from trueconf.types import CreatedFavoritesChat

        @<router>.created_favorites_chat()
        async def on_created(event: CreatedFavoritesChat):
            print(f"Favorites chat created with id {event.chat_id}")
        ```
    """
    chat_id: str = field(metadata={"alias": "chatId"})
    title: str | None = field(metadata={"alias": "title"})
    chat_type: ChatType = field(metadata={"alias": "chatType"})
    last_message: LastMessage | None = field(metadata={"alias": "lastMessage"})
    unread_messages: int = field(metadata={"alias": "unreadMessages"})