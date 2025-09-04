from __future__ import annotations
from dataclasses import dataclass, field
from typing import Optional, Union
from mashumaro import DataClassDictMixin
from trueconf.enums.message_type import MessageType
from trueconf.types.author_box import EnvelopeAuthor, EnvelopeBox
from trueconf.types.content.text import TextContent
from trueconf.types.content.attachment import AttachmentContent
from trueconf.types.content.survey import SurveyContent
from trueconf.types.content.remove_participant import RemoveParticipant
from trueconf.types.content.forward_message import ForwardMessage
from trueconf.types.content.chat_created import ParticipantRoleContent
from trueconf.types.content.photo import Photo
from trueconf.types.content.video import Video
from trueconf.types.content.sticker import Sticker
from trueconf.types.content.document import Document
from trueconf.client.context_controller import BoundToBot
from trueconf.enums.parse_mode import ParseMode

import logging

logger = logging.getLogger("chat_bot")


@dataclass
class Message(BoundToBot, DataClassDictMixin):
    """
        Represents a single chat message within TrueConf Chatbot Connector.

        The `Message` object is automatically created for each incoming update and
        contains metadata (author, chat, timestamp, type) along with the actual
        message content. It also provides helper properties and shortcut methods
        to interact with the message (e.g., replying, forwarding, deleting, sending
        media files).

        Source:
            https://trueconf.com/docs/chatbot-connector/en/server-requests/#sendMessage

        Attributes:
            timestamp (int): Unix timestamp of the message.
            type (MessageType): Type of the message (e.g., TEXT, ATTACHMENT).
            author (EnvelopeAuthor): Information about the user who sent the message.
            box (EnvelopeBox): Information about the chat (box) where the message was sent.
            content (Union[TextContent, AttachmentContent, SurveyContent,
                ParticipantRoleContent, RemoveParticipant, ForwardMessage]):
                The actual message content, which can be text, media, or service data.
            message_id (str): Unique identifier of the message.
            chat_id (str): Unique identifier of the chat where the message was sent.
            is_edited (bool): Indicates whether the message was edited.
            reply_message_id (Optional[str]): Identifier of the message this one replies to.

            from_user (EnvelopeAuthor): Shortcut for accessing the message author.
            content_type (MessageType): Returns the type of the message.
            text (Optional[str]): Returns the message text if it contains text, else None.
            document (Optional[Document]): Returns a document attachment if the message
                contains a non-media file (not photo, video, sticker).
            photo (Optional[Photo]): Returns a photo attachment if available.
            video (Optional[Video]): Returns a video attachment if available.
            sticker (Optional[Sticker]): Returns a sticker attachment if available.

        Methods:
            answer(text, parse_mode): Sends a text message in the same chat.
            reply(text, parse_mode): Sends a reply message referencing the current one.
            forward(chat_id): Forwards the current message to another chat.
            copy_to(chat_id): Sends a copy of the current message (text-only).
            answer_photo(file_path): Sends a photo to the current chat.
            answer_document(file_path): Sends a document to the current chat.
            answer_sticker(file_path): Sends a sticker to the current chat.
            delete(for_all): Deletes the current message from the chat.
        """

    timestamp: int
    type: MessageType
    author: EnvelopeAuthor
    box: EnvelopeBox
    content: Union[
        TextContent, AttachmentContent, SurveyContent, ParticipantRoleContent, RemoveParticipant, ForwardMessage]
    message_id: str = field(metadata={"alias": "messageId"})
    chat_id: str = field(metadata={"alias": "chatId"})
    is_edited: bool = field(metadata={"alias": "isEdited"})
    reply_message_id: Optional[str] = field(default=None, metadata={"alias": "replyMessageId"})

    @property
    def from_user(self) -> EnvelopeAuthor:
        """
        Returns the author of the current message.

        Returns:
            EnvelopeAuthor: Shortcut for accessing the message author.
        """
        return self.author

    @property
    def content_type(self) -> MessageType:
        """
        Returns the type of the current message content.

        Returns:
            MessageType: Message content type (e.g., TEXT, ATTACHMENT).
        """
        return self.type

    @property
    def text(self) -> str | None:
        """
        Returns the text of the current message if present.

        Returns:
            Optional[str]: Message text, or None if the message has no text content.
        """
        return self.content.text if isinstance(self.content, TextContent) else None

    @property
    def document(self) -> Optional["Document"]:
        """
        Returns the attached document if the message contains a non-media file.

        Use this property only for documents that are **not** photos, videos, or stickers.
        For media attachments, use the corresponding properties: `photo`, `video`, or `sticker`.
        If you need to handle **any** attached file (including media), use `message.content` directly.

        Returns:
            Optional[Document]: Document attachment bound to the bot, or None if not applicable.
        """

        if isinstance(self.content, AttachmentContent) and not self.content.mimetype.startswith(
                ("image/", "video/", "audio/")):
            return Document(
                file_id=self.content.file_id,
                file_name=self.content.file_name,
                file_size=self.content.file_size,
                mimetype=self.content.mimetype,
            ).bind(self.bot)

        return None

    @property
    def photo(self) -> Optional["Photo"]:
        """
        Returns the attached photo object if the current message contains an image.

        This is a shortcut for accessing photo metadata from image attachments.

        Returns:
            Optional[Photo]: A `Photo` object bound to the bot, or None if the message does not contain an image.
        """

        if isinstance(self.content, AttachmentContent) and self.content.mimetype.startswith("image/"):
            return Photo(
                file_id=self.content.file_id,
                file_name=self.content.file_name,
                file_size=self.content.file_size,
                mimetype=self.content.mimetype,
            ).bind(self.bot)
        return None

    @property
    def video(self) -> Optional["Video"]:
        """
        Returns the attached video object if the current message contains a video.

        This is a shortcut for accessing video metadata from video attachments.

        Returns:
            Optional[Video]: A `Video` object bound to the bot, or None if the message does not contain a video.
        """

        if isinstance(self.content, AttachmentContent) and self.content.mimetype.startswith("video/"):
            return Video(
                file_id=self.content.file_id,
                file_name=self.content.file_name,
                file_size=self.content.file_size,
                mimetype=self.content.mimetype,
            ).bind(self.bot)
        return None

    @property
    def sticker(self) -> Optional["Sticker"]:
        """
        Returns the attached sticker object if the current message contains a sticker.

        Returns:
            Optional[Sticker]: A `Sticker` object bound to the bot, or None if the message does not contain a sticker.
        """

        if isinstance(self.content, AttachmentContent) and self.content.mimetype.startswith("sticker/"):
            return Sticker(
                file_id=self.content.file_id,
                file_name=self.content.file_name,
                file_size=self.content.file_size,
                mimetype=self.content.mimetype,
            ).bind(self.bot)
        return None

    async def answer_photo(self, file_path: str, preview_path: str | None) -> object:
        """
        Shortcut for the [`send_photo`][trueconf.Bot.send_photo] method of the bot instance. Use this method to send a photo in response to the current message.

        Automatically fills the following attributes:
            - `chat_id`

        Source:
            https://trueconf.com/docs/chatbot-connector/en/files/#sending-an-image

        Args:
            file_path: Path to the image file (supported formats: `.jpg`, `.jpeg`, `.png`, `.webp`, `.bmp`, `.gif`, `.tiff`).
            preview_path: Path to the preview image.

        Returns:
            SendFileResponse: Object containing the result of the photo upload.

        Examples:
            >>> @<router>.message()
            >>> async def on_message(message:Message):
            >>>     await message.answer_photo(file_path='/path/to/file.jpg', preview_path='/path/to/preview.jpg')
        """

        return await self.bot.send_photo(
            chat_id=self.chat_id,
            file_path=file_path,
            preview_path=preview_path,
        )

    async def answer_document(self, file_path: str) -> object:
        """
        Shortcut for the [`send_document`][trueconf.Bot.send_document] method of the bot instance. Use this method to send a document in response to the current message.

        Automatically fills the following attributes:
            - `chat_id`

        Source:
            https://trueconf.com/docs/chatbot-connector/en/files/#working-with-files

        Args:
            file_path (str): Path to the document file.

        Returns:
            SendFileResponse: Object containing the result of the document upload.

        Examples:
            >>> @<router>.message()
            >>> async def on_message(message:Message):
            >>>     await message.answer_sticker(file_path='/path/to/file.webp')
        """

        return await self.bot.send_document(
            chat_id=self.chat_id,
            file_path=file_path,
        )

    async def answer_sticker(self, file_path: str) -> object:
        """
        Shortcut for the [`send_sticker`][trueconf.Bot.send_sticker] method of the bot instance. Use this method to send a sticker in response to the current message.

        Automatically fills the following attributes:
            - `chat_id`

        Source:
            https://trueconf.com/docs/chatbot-connector/en/files/#upload-file-to-server-storage

        Args:
            file_path (str): Path to the sticker file (must be in WebP format).

        Returns:
            SendFileResponse: Object containing the result of the sticker delivery.

        Examples:
            >>> @<router>.message()
            >>> async def on_message(message:Message):
            >>>     await message.answer_sticker(file_path='/path/to/file.webp')
        """

        return await self.bot.send_sticker(
            chat_id=self.chat_id,
            file_path=file_path,
        )

    async def answer(self, text: str, parse_mode: ParseMode | str = ParseMode.HTML) -> object:
        """
        Shortcut for the [`send_message`][trueconf.Bot.send_message] method of the bot instance. Use this method to send a text message to the current chat.

        Automatically fills the following attributes:
            - `chat_id`

        Source:
            https://trueconf.com/docs/chatbot-connector/en/messages/#sendMessage

        Args:
            text (str): Text of the message to be sent.
            parse_mode (ParseMode | str, optional): Text formatting mode. Defaults to HTML.

        Returns:
            SendMessageResponse: Object containing the result of the message delivery.

        Examples:
            >>> @<router>.message()
            >>> async def on_message(message:Message):
            >>>     await message.answer("Hi, there!")

            >>> @<router>.message()
            >>> async def on_message(message:Message):
            >>>     await message.answer("Hi, **there!**", parse_mode=ParseMode.MARKDOWN)
        """

        return await self.bot.send_message(
            chat_id=self.chat_id,
            text=text,
            parse_mode=parse_mode
        )

    async def reply(self, text: str, parse_mode: ParseMode | str = ParseMode.HTML) -> object:
        """
        Shortcut for the [`reply_message`][trueconf.Bot.reply_message] method of the bot instance. Use this method to send a reply message to the current chat.

        Automatically fills the following attributes:
            - `chat_id`
            - `reply_message_id`

        Source: https://trueconf.com/docs/chatbot-connector/en/messages/#replyMessage

        Args:
            text (str): Text of the reply message.
            parse_mode (ParseMode | str, optional): Text formatting mode. Defaults to HTML.

        Returns:
            SendMessageResponse: Object containing the result of the message delivery.
        """

        return await self.bot.reply_message(
            chat_id=self.chat_id,
            message_id=self.message_id,
            text=text,
            parse_mode=parse_mode,
        )

    async def forward(self, chat_id: str) -> object:
        """
        Shortcut for the [`forward_message`][trueconf.Bot.forward_message] method of the bot instance. Use this method to forward the current message to another chat.

        Automatically fills the following attributes:
            - `message_id`

        Source:
            https://trueconf.com/docs/chatbot-connector/en/messages/#forwardMessage

        Args:
            chat_id (str): Identifier of the target chat to forward the message to.

        Returns:
            ForwardMessageResponse: Object containing the result of the message forwarding.
        """

        return await self.bot.forward_message(
            chat_id=chat_id,
            message_id=self.message_id,
        )

    async def copy_to(self, chat_id: str) -> object:
        """
        Shortcut for the [`send_message`][trueconf.Bot.send_message] method of the bot instance. Use this method to send a copy of the current message (without metadata or reply context) to another chat.

        Automatically fills the following attributes:
            - `text`
            - `parse_mode`

        Source:
            https://trueconf.com/docs/chatbot-connector/en/messages/#sendMessage

        Args:
            chat_id (str): Identifier of the target chat to send the copied message to.

        Returns:
            SendMessageResponse: Object containing the result of the message delivery.
        """

        if isinstance(self.content, TextContent):
            return await self.bot.send_message(
                chat_id=chat_id,
                text=self.content.text,
                parse_mode=self.content.parse_mode
            )

        logger.warning(
            "copy_to(): unsupported content type for non-text message "
            "(type=%s). Nothing was sent. Use forward() if needed.",
            getattr(self.type, "name", self.type),
        )
        return None

    async def delete(self, for_all: bool = False) -> object:
        """
        Shortcut for the [`remove_message`][trueconf.Bot.remove_message] method of the bot instance. Use this method to delete the current message from the chat.

        Automatically fills the following attributes:
            - `message_id`

        Source:
            https://trueconf.com/docs/chatbot-connector/en/messages/#removeMessage

        Args:
            for_all (bool, optional): If True, delete the message for all participants.
                Defaults to False (deletes only for the bot).

        Returns:
            RemoveMessageResponse: Object containing the result of the message deletion.
        """

        return await self.bot.remove_message(
            message_id=self.message_id,
            for_all=for_all,
        )
