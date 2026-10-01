from __future__ import annotations

import logging
import re
from dataclasses import dataclass, field
from html import unescape
from typing import TYPE_CHECKING, Any

from async_property import async_cached_property
from mashumaro import DataClassDictMixin
from mashumaro.helper import pass_through
from typing_extensions import deprecated

from trueconf.client.context_controller import BoundToBot
from trueconf.enums.message_type import MessageType
from trueconf.enums.parse_mode import ParseMode
from trueconf.exceptions import ApiErrorException
from trueconf.types.author_box import EnvelopeAuthor, EnvelopeBox
from trueconf.types.chat import Chat
from trueconf.types.contact import Contact
from trueconf.types.content.attachment import AttachmentContent
from trueconf.types.content.document import Document
from trueconf.types.content.location import Location
from trueconf.types.content.parser import UserMessageContent, deserialize_user_content
from trueconf.types.content.photo import Photo
from trueconf.types.content.sticker import Sticker
from trueconf.types.content.text import TextContent
from trueconf.types.content.video import Video
from trueconf.types.content.voice import Voice
from trueconf.types.input_file import InputFile
from trueconf.types.keyboard import InlineKeyboardMarkup

if TYPE_CHECKING:
    from trueconf.types.responses.forward_message_response import ForwardMessageResponse
    from trueconf.types.responses.remove_message_response import RemoveMessageResponse
    from trueconf.types.responses.send_file_response import SendFileResponse
    from trueconf.types.responses.send_message_response import SendMessageResponse

logger = logging.getLogger("chat_bot")
# The trueconf: link grammar shared by mentions and contact links.
_TRUECONF_HREF = r'href=["\']trueconf:([^"\'&]+)(?:&do=profile)?["\']'
MENTION_RE = re.compile(_TRUECONF_HREF)
CONTACT_RE = re.compile(rf"<a\s+{_TRUECONF_HREF}>(.*?)</a>", re.DOTALL)
QUOTE_RE = re.compile(r'<quote\s+class="reply">(.*?)</quote>', re.DOTALL)
STRIP_QUOTE_RE = re.compile(rf"^{QUOTE_RE.pattern}(?:<br>)+", re.DOTALL)


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
        https://trueconf.com/docs/chatbot-connector/en/messages/#sendMessage

    Attributes:
        timestamp (int): Unix timestamp of the message.
        type (MessageType): Type of the message (e.g., TEXT, ATTACHMENT).
        author (EnvelopeAuthor): Information about the user who sent the message.
        box (EnvelopeBox): Information about the chat (box) where the message was sent.
        content (UserMessageContent): The message content, selected from the
            user-message models according to `type`.
        chat (Chat): The chat this message belongs to.
        message_id (str): Unique identifier of the message.
        chat_id (str): .. deprecated:: Use :attr:`chat.chat_id` instead.
        is_edited (bool): Indicates whether the message was edited.
        reply_message_id (Optional[str]): Identifier of the message this one replies to.
        reply_message (Optional[Message]): Full message this one replies to. The server expands
            only the directly referenced message: if that message is also a reply, its
            `reply_message_id` is available but its `reply_message` remains `None`. Use
            `Bot.get_message_by_id()` to load the next message in the reply chain.

        from_user (EnvelopeAuthor): Shortcut for accessing the message author.
        content_type (MessageType): Returns the type of the message.
        text (Optional[str]): Returns the message text if it contains text, else None.
        quote (Optional[str]): Returns the quoted part of the replied message extracted
            from the ``<quote class="reply">`` block, else None.
        mention (Optional[bool]): Returns True if the message mentions the bot, else None.
        document (Optional[Document]): Returns a document attachment if the message
            contains a non-media file (not photo, video, sticker).
        photo (Optional[Photo]): Returns a photo attachment if available.
        video (Optional[Video]): Returns a video attachment if available.
        sticker (Optional[Sticker]): Returns a sticker attachment if available.
        location (Optional[Location]): Returns the location content if the message
            contains a geolocation, else None.

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

    chat: Chat
    timestamp: int
    type: MessageType
    author: EnvelopeAuthor
    box: EnvelopeBox
    content: UserMessageContent = field(metadata={"deserialize": pass_through})
    message_id: str = field(metadata={"alias": "messageId"})
    is_edited: bool = field(metadata={"alias": "isEdited"})
    reply_message_id: str | None = field(default=None, metadata={"alias": "replyMessageId"})
    reply_message: Message | None = field(default=None, metadata={"alias": "replyMessage"})

    @classmethod
    def __pre_deserialize__(cls, d: dict[str, Any]) -> dict[str, Any]:
        data = dict(d)
        message_type = MessageType(data["type"])
        data["content"] = deserialize_user_content(message_type, data.get("content", {}))
        return data

    def bind(self, bot):
        super().bind(bot)
        if self.reply_message is not None:
            self.reply_message.bind(bot)
        return self

    @property
    @deprecated("Message.chat_id is deprecated, use message.chat.chat_id instead")
    def chat_id(self) -> str:
        return self.chat.chat_id

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

        For a reply with a quote, the leading ``<quote class="reply">...</quote>``
        block (and the following ``<br>`` breaks) is stripped from the returned
        value; use :attr:`quote` to get the quoted fragment itself.

        Returns:
            Optional[str]: Message text, or None if the message has no text content.
        """
        if not isinstance(self.content, TextContent):
            return None

        return STRIP_QUOTE_RE.sub("", self.content.text)

    @property
    def quote(self) -> str | None:
        """
        Returns the quoted part of the replied message, if present.

        Extracts the content of the first ``<quote class="reply">...</quote>``
        block from the message HTML text and unescapes HTML entities, so the
        returned value can be reused as the ``quote`` argument of
        [`Message.reply()`][trueconf.types.message.Message.reply] or
        [`Bot.send_message()`][trueconf.Bot.send_message].

        Returns:
            Optional[str]: Quoted text, or None if the message has no quote block.
        """
        if not isinstance(self.content, TextContent):
            return None

        match = QUOTE_RE.search(self.content.text)
        if match is None:
            return None

        return unescape(match.group(1))

    @property
    def document(self) -> Document | None:
        """
        Returns the attached document if the message contains a non-media file.

        Use this property only for documents that are **not** photos, videos, or stickers.
        For media attachments, use the corresponding properties: `photo`, `video`, or `sticker`.
        If you need to handle **any** attached file (including media), use `message.content` directly.

        Returns:
            Optional[Document]: Document attachment bound to the bot, or None if not applicable.
        """

        if isinstance(self.content, AttachmentContent) and not self.content.mime_type.startswith(
            ("image/", "video/", "audio/")
        ):
            return Document(
                file_id=self.content.file_id,
                file_name=self.content.file_name,
                file_size=self.content.file_size,
                mime_type=self.content.mime_type,
            ).bind(self.bot)

        return None

    @property
    def photo(self) -> Photo | None:
        """
        Returns the attached photo object if the current message contains an image.

        This is a shortcut for accessing photo metadata from image attachments.

        Returns:
            Optional[Photo]: A `Photo` object bound to the bot, or None if the message does not contain an image.
        """

        if isinstance(self.content, AttachmentContent) and self.content.mime_type.startswith("image/"):
            return Photo(
                file_id=self.content.file_id,
                file_name=self.content.file_name,
                file_size=self.content.file_size,
                mime_type=self.content.mime_type,
            ).bind(self.bot)
        return None

    @property
    def video(self) -> Video | None:
        """
        Returns the attached video object if the current message contains a video.

        This is a shortcut for accessing video metadata from video attachments.

        Returns:
            Optional[Video]: A `Video` object bound to the bot, or None if the message does not contain a video.
        """

        if isinstance(self.content, AttachmentContent) and self.content.mime_type.startswith("video/"):
            return Video(
                file_id=self.content.file_id,
                file_name=self.content.file_name,
                file_size=self.content.file_size,
                mime_type=self.content.mime_type,
            ).bind(self.bot)
        return None

    @property
    def voice(self) -> Voice | None:
        """
        Returns the attached voice object if the current message contains a voice message.

        This is a shortcut for accessing video metadata from voice attachments.

        Returns:
            Optional[Voice]: A `Voice` object bound to the bot, or None if the message does not contain a voice.
        """

        if isinstance(self.content, Voice):
            return Voice(
                file_id=self.content.file_id,
                file_size=self.content.file_size,
                mime_type=self.content.mime_type,
                duration=self.content.duration,
            ).bind(self.bot)
        return None

    @property
    def location(self) -> Location | None:
        """
        Returns the location content if the current message contains a geolocation.

        Returns:
            Optional[Location]: The location object with latitude, longitude and
                title, or None if the message is not a location message.
        """

        if not isinstance(self.content, Location):
            return None

        return self.content

    @property
    def sticker(self) -> Sticker | None:
        """
        Returns the attached sticker object if the current message contains a sticker.

        Returns:
            Optional[Sticker]: A `Sticker` object bound to the bot, or None if the message does not contain a sticker.
        """

        if isinstance(self.content, AttachmentContent) and self.content.mime_type.startswith("sticker/"):
            return Sticker(
                file_id=self.content.file_id,
                file_name=self.content.file_name,
                file_size=self.content.file_size,
                mime_type=self.content.mime_type,
            ).bind(self.bot)
        return None

    @property
    def mention(self) -> bool | None:
        """
        Returns whether the current text message mentions the bot.

        The shortcut checks two supported mention formats:

        - ``@all`` — treated as a mention because it targets all chat participants.
        - TrueConf user mentions rendered as HTML links, for example
          ``<a href="trueconf:john_doe@video.example.com">John Doe</a>``.

        For user mentions, the extracted TrueConf ID is compared with ``bot.me_id``.

        Returns:
            bool | None: ``True`` if the message mentions the bot, otherwise ``None``.
        """
        if not isinstance(self.content, TextContent):
            return None

        text = self.content.text.strip()
        if text == "@all":
            return True

        return any(match.group(1) == self.bot.me_id for match in MENTION_RE.finditer(text)) or None

    @async_cached_property
    async def contact(self) -> Contact | None:
        """
        Returns the contact of the current message, if any.

        The result is cached on the message, so a vCard file is downloaded from
        the server only once.

        Two formats are recognized:

        - A **vCard attachment** (``mimeType: text/vcard``). The file is
          downloaded from the server and parsed into a contact with the
          structured name (``N``), phone number (``TEL``) and the raw vCard
          text.
        - A **TrueConf contact link**, i.e. a text message whose entire
          content is exactly one ``<a href="trueconf:login&do=profile">Name</a>``
          link (the same markup `Message.mention` uses for user mentions).
          The display name is fetched from the server via
          `get_user_display_name`; if that fails (e.g. the user was deleted)
          the link text is used instead. ``first_name`` holds the whole
          display name and ``last_name``/``phone_number`` stay ``None``.

        Returns:
            Contact | None: The parsed contact, or None if the message is not
            a vCard attachment or a TrueConf contact link.

        Examples:
            >>> @<router>.message()
            >>> async def on_message(message: Message):
            >>>     contact = await message.contact
            >>>     if contact is not None:
            >>>         await message.answer(f"Phone: {contact.phone_number}")
        """
        if isinstance(self.content, AttachmentContent) and self.content.mime_type.lower() == "text/vcard":
            data = await self.bot.download_file_by_id(self.content.file_id)
            if not isinstance(data, bytes):
                return None
            return Contact._from_vcard(data.decode("utf-8", errors="replace"))

        if isinstance(self.content, TextContent):
            match = CONTACT_RE.fullmatch(self.content.text.strip())
            if match is not None:
                user_id = match.group(1)
                display_name = unescape(match.group(2))
                try:
                    display_name = (await self.bot.get_user_display_name(user_id)).display_name
                except ApiErrorException:
                    pass
                return Contact._from_trueconf(user_id=user_id, display_name=display_name)

        return None

    async def answer_photo(
        self,
        file: InputFile,
        preview: InputFile | None,
        caption: str | None = None,
        parse_mode: ParseMode | str = ParseMode.TEXT,
    ) -> SendFileResponse:
        """
        Shortcut for the [`send_photo`][trueconf.Bot.send_photo] method of the bot instance. Use this method to send a photo in response to the current message.

        Automatically fills the following attributes:
            - `chat_id`

        Source:
            https://trueconf.com/docs/chatbot-connector/en/files/#sending-an-image

        Args:
            file (InputFile): The photo file to upload. Must be a subclass of `InputFile`.
            preview (InputFile | None): Optional preview image. Must also be an `InputFile` if provided.
            caption (str | None): Optional caption to be sent along with the image.
            parse_mode (ParseMode | str): Formatting mode for the caption (e.g., Markdown, HTML, plain text).

        Returns:
            SendFileResponse: Object containing the result of the photo upload. If the photo was
                sent with a caption, `caption_message_id` contains the ID of the caption message.

        Examples:
            >>> @<router>.message()
            >>> async def on_message(message:Message):
            >>>     await message.answer_photo(file=FSInputFile("sticker.webp"), preview=FSInputFile("sticker.webp"))
        """

        return await self.bot.send_photo(
            chat_id=self.chat.chat_id, file=file, caption=caption, preview=preview, parse_mode=parse_mode
        )

    async def answer_document(
        self, file: InputFile, caption: str | None = None, parse_mode: ParseMode | str = ParseMode.TEXT
    ) -> SendFileResponse:
        """
        Shortcut for the [`send_document`][trueconf.Bot.send_document] method of the bot instance. Use this method to send a document in response to the current message.

        Automatically fills the following attributes:
            - `chat_id`

        Source:
            https://trueconf.com/docs/chatbot-connector/en/files/#working-with-files

        Args:
            file (InputFile): The file to be uploaded. Must be a subclass of `InputFile`.
            caption (str | None): Optional caption text to be sent with the file.
            parse_mode (ParseMode | str): Text formatting mode (e.g., Markdown, HTML, or plain text).

        Returns:
            SendFileResponse: Object containing the result of the document upload. If the file was
                sent with a caption, `caption_message_id` contains the ID of the caption message.

        Examples:
            >>> @<router>.message()
            >>> async def on_message(message:Message):
            >>>     await message.answer_document(file=FSInputFile("sticker.webp"))
        """

        return await self.bot.send_document(
            chat_id=self.chat.chat_id, file=file, caption=caption, parse_mode=parse_mode
        )

    async def answer_sticker(self, file: InputFile) -> SendFileResponse:
        """
        Shortcut for the [`send_sticker`][trueconf.Bot.send_sticker] method of the bot instance. Use this method to send a sticker in response to the current message.

        Automatically fills the following attributes:
            - `chat_id`

        Source:
            https://trueconf.com/docs/chatbot-connector/en/files/#upload-file-to-server-storage

        Args:
            file (InputFile): The sticker file in WebP format. Must be a subclass of `InputFile`.

        Returns:
            SendFileResponse: Object containing the result of the sticker delivery.

        Examples:
            >>> @<router>.message()
            >>> async def on_message(message:Message):
            >>>     await message.answer_sticker(file=FSInputFile("sticker.webp"))
        """

        return await self.bot.send_sticker(
            chat_id=self.chat.chat_id,
            file=file,
        )

    async def answer(
        self,
        text: str,
        parse_mode: ParseMode | str = ParseMode.HTML,
        *,
        buttons: InlineKeyboardMarkup | None = None,
    ) -> SendMessageResponse:
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
            chat_id=self.chat.chat_id,
            text=text,
            parse_mode=parse_mode,
            buttons=buttons,
        )

    async def reply(
        self,
        text: str,
        parse_mode: ParseMode | str = ParseMode.HTML,
        *,
        buttons: InlineKeyboardMarkup | None = None,
        quote: str | None = None,
    ) -> SendMessageResponse:
        """
        Shortcut for the [`send_message`][trueconf.Bot.send_message] method.
        Sends a reply to this message in the current chat.

        Automatically fills the following attributes:
            - `chat_id`: Current chat identifier.
            - `reply_message_id`: ID of the current message.

        Source: https://trueconf.com/docs/chatbot-connector/en/messages/#replyMessage

        Args:
            text (str): Text of the reply message.
            parse_mode (ParseMode | str, optional): Text formatting mode. Defaults to HTML.
            quote (str, optional): Part of this message to highlight in the reply
                preview. Must be a substring of the message text; raises `ValueError`
                otherwise. The quote body follows the message `parse_mode`: HTML and
                plain text are wrapped into an HTML quote block (plain text is escaped,
                parse mode becomes HTML), while Markdown uses a ``>quote`` blockquote.

        Returns:
            SendMessageResponse: Object containing the result of the message delivery.
        """

        if quote is not None and self.text is not None and quote not in self.text:
            raise ValueError("quote must be a substring of the replied message")

        return await self.bot.send_message(
            chat_id=self.chat.chat_id,
            reply_message_id=self.message_id,
            text=text,
            parse_mode=parse_mode,
            buttons=buttons,
            quote=quote,
        )

    async def reply_photo(
        self,
        file: InputFile,
        preview: InputFile | None,
        caption: str | None = None,
        parse_mode: ParseMode | str = ParseMode.TEXT,
    ) -> SendFileResponse:
        """
        Shortcut for the [`send_photo`][trueconf.Bot.send_photo] method of the bot instance.
        Sends a photo as a reply to the current message in this chat.

        Automatically fills the following attributes:
            - `chat_id`: Current chat identifier.
            - `reply_message_id`: ID of the current message.

        Source:
            https://trueconf.com/docs/chatbot-connector/en/files/#sending-an-image

        Args:
            file (InputFile): The photo file to upload. Must be a subclass of `InputFile`.
            preview (InputFile | None): Optional preview image. Must also be an `InputFile` if provided.
            caption (str | None): Optional caption to be sent along with the image.
            parse_mode (ParseMode | str): Formatting mode for the caption (e.g., Markdown, HTML, plain text).
            reply_message_id (str | None): Optional identifier of the message to which this message is a reply.

        Returns:
            SendFileResponse: Object containing the result of the photo upload. If the photo was
                sent with a caption, `caption_message_id` contains the ID of the caption message.

        Examples:
            >>> @<router>.message()
            >>> async def on_message(message:Message):
            >>>     await message.answer_photo(file=FSInputFile("sticker.webp"), preview=FSInputFile("sticker.webp"))
        """

        return await self.bot.send_photo(
            chat_id=self.chat.chat_id,
            file=file,
            caption=caption,
            preview=preview,
            parse_mode=parse_mode,
            reply_message_id=self.message_id,
        )

    async def reply_document(
        self, file: InputFile, caption: str | None = None, parse_mode: ParseMode | str = ParseMode.TEXT
    ) -> SendFileResponse:
        """
        Shortcut for the [`send_document`][trueconf.Bot.send_document] method of the bot instance.
        Sends a document as a reply to the current message in this chat.

        Automatically fills the following attributes:
            - `chat_id`: Current chat identifier.
            - `reply_message_id`: ID of the current message.

        Source:
            https://trueconf.com/docs/chatbot-connector/en/files/#working-with-files

        Args:
            file (InputFile): The file to be uploaded. Must be a subclass of `InputFile`.
            caption (str | None): Optional caption text to be sent with the file.
            parse_mode (ParseMode | str): Text formatting mode (e.g., Markdown, HTML, or plain text).

        Returns:
            SendFileResponse: Object containing the result of the document upload. If the file was
                sent with a caption, `caption_message_id` contains the ID of the caption message.

        Examples:
            >>> @<router>.message()
            >>> async def on_message(message:Message):
            >>>     await message.answer_document(file=FSInputFile("sticker.webp"))
        """

        return await self.bot.send_document(
            chat_id=self.chat.chat_id,
            file=file,
            caption=caption,
            parse_mode=parse_mode,
            reply_message_id=self.message_id,
        )

    async def reply_sticker(self, file: InputFile) -> SendFileResponse:
        """
        Shortcut for the [`send_sticker`][trueconf.Bot.send_sticker] method of the bot instance.
        Sends a sticker as a reply to the current message in this chat.

        Automatically fills the following attributes:
            - `chat_id`: Current chat identifier.
            - `reply_message_id`: ID of the current message.

        Source:
            https://trueconf.com/docs/chatbot-connector/en/files/#upload-file-to-server-storage

        Args:
            file (InputFile): The sticker file in WebP format. Must be a subclass of `InputFile`.

        Returns:
            SendFileResponse: Object containing the result of the sticker delivery.

        Examples:
            >>> @<router>.message()
            >>> async def on_message(message:Message):
            >>>     await message.answer_sticker(file=FSInputFile("sticker.webp"))
        """

        return await self.bot.send_sticker(chat_id=self.chat.chat_id, file=file, reply_message_id=self.message_id)

    async def forward(self, chat_id: str) -> ForwardMessageResponse:
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

    async def copy_to(self, chat_id: str) -> SendMessageResponse | None:
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
                chat_id=chat_id, text=self.content.text, parse_mode=self.content.parse_mode
            )

        logger.warning(
            "copy_to(): unsupported content type for non-text message "
            "(type=%s). Nothing was sent. Use forward() if needed.",
            getattr(self.type, "name", self.type),
        )
        return None

    async def delete(self, for_all: bool = False) -> RemoveMessageResponse:
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

    async def save_to_favorites(self, copy: bool = False) -> SendMessageResponse | ForwardMessageResponse | None:
        """
        Saves the current message to the bot's "Favorites" chat.

        By default, the message is **forwarded** to the bot's personal Favorites chat.
        If `copy=True`, the message will be **copied** instead — only for text messages.

        Use this method to store important messages, logs, or media content in the bot’s private space.

        Notes:
            - The Favorites chat is created automatically on first use.
            - `copy=True` only works for text messages and does **not** preserve metadata (like replies or sender info).
            - Non-text messages with `copy=True` will be ignored with a warning.

        Args:
            copy (bool, optional): If True, copies the message instead of forwarding it.
                Defaults to False.

        Returns:
            SendMessageResponse | ForwardMessageResponse | None:
            Result of sending or forwarding the message. Returns `None` if copying is not supported for the message type.

        Example:
            ```python
            @router.message()
            async def on_message(msg: Message):
                await msg.save_to_favorites()           # forwards message
                await msg.save_to_favorites(copy=True)  # copies if possible
            ```
        """

        if copy:
            return await self.copy_to(await self.bot.me_chat)
        else:
            return await self.forward(await self.bot.me_chat)
