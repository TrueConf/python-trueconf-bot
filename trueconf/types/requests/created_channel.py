from __future__ import annotations
from dataclasses import dataclass, field
from mashumaro import DataClassDictMixin
from trueconf.client.context_controller import BoundToBot
from trueconf.enums.chat_type import ChatType
from trueconf.types.last_message import LastMessage


@dataclass
class CreatedChannel(BoundToBot, DataClassDictMixin):
    """
    **Event type:** a new channel chat was created.

    This object is received in the handler when a channel is created in TrueConf.

    Notes:
        This class is used as the event type in handler functions decorated with `@<router>.created_channel()`.

    Source:
        https://trueconf.com/docs/chatbot-connector/en/server-requests/#createChannel

    Attributes:
        chat_id (str): Unique identifier of the created channel.
        title (str): Title of the channel.
        chat_type (ChatType): Type of the chat (should be `channel`).
        last_message (LastMessage | None): The last message in the channel, if available.
        unread_messages (int): Number of unread messages in the channel.

    Examples:
        ```python
        from trueconf.types import CreatedChannel

        @<router>.created_channel()
        async def on_created(event: CreatedChannel):
            print(f"Channel {event.title} created with id {event.chat_id}")
        ```
    """
    chat_id: str = field(metadata={"alias": "chatId"})
    title: str
    chat_type: ChatType = field(metadata={"alias": "chatType"})
    last_message: LastMessage | None = field(metadata={"alias": "lastMessage"})
    unread_messages: int = field(metadata={"alias": "unreadMessages"})