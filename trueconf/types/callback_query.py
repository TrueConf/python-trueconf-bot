from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any

from mashumaro import DataClassDictMixin
from mashumaro.helper import pass_through
from typing_extensions import sentinel

from trueconf.client.context_controller import BoundToBot
from trueconf.enums.command import (
    CommandAnswerType,
    CommandMessageLevel,
    CommandMessageStatus,
    CommandMessageVisibility,
)
from trueconf.enums.parse_mode import ParseMode
from trueconf.types.content.text import TextContent
from trueconf.types.keyboard import InlineKeyboardMarkup
from trueconf.types.message import Message
from trueconf.types.responses.answer_command_response import AnswerCommandResponse

if TYPE_CHECKING:
    from trueconf.types.responses.edit_message_response import EditMessageResponse

UNSET = sentinel("UNSET")


@dataclass
class CommandSource(DataClassDictMixin):
    type: str
    message: Message | None = field(default=None, metadata={"deserialize": pass_through})
    button_id: str | None = field(default=None, metadata={"alias": "buttonId"})
    wait_reply: bool = field(default=False, metadata={"alias": "waitReply"})

    @classmethod
    def __pre_deserialize__(cls, d: dict[str, Any]) -> dict[str, Any]:
        data = dict(d)
        if isinstance(data.get("message"), dict):
            data["message"] = Message.from_dict(data["message"])
        return data


@dataclass
class CommandPayload(DataClassDictMixin):
    type: str
    command: str
    custom_data: str | None = field(default=None, metadata={"alias": "customData"})


@dataclass
class CallbackQuery(BoundToBot, DataClassDictMixin):
    command_source: CommandSource = field(metadata={"alias": "commandSource"})
    command_payload: CommandPayload = field(metadata={"alias": "commandPayload"})
    command_id: str | None = field(default=None, metadata={"alias": "commandId"})

    def bind(self, bot):
        super().bind(bot)
        if self.message is not None:
            self.message.bind(bot)
        return self

    @property
    def command(self) -> str:
        return self.command_payload.command

    @property
    def custom_data(self) -> str | None:
        return self.command_payload.custom_data

    @property
    def message(self) -> Message | None:
        return self.command_source.message

    @property
    def chat(self):
        return self.message.chat if self.message is not None else None

    async def edit_message(
        self,
        text: str | UNSET = UNSET,
        parse_mode: ParseMode | str | UNSET = UNSET,
        *,
        buttons: InlineKeyboardMarkup | UNSET | None = UNSET,
    ) -> EditMessageResponse:
        """
        Shortcut for [`bot.edit_message`][trueconf.Bot.edit_message] that edits the
        bot's own message this callback came from.

        The server treats `editMessage` as a full content overwrite (PUT): every
        edit carries the full text, formatting and buttons. Text and `parse_mode`
        are already present in the click event (`commandSource.message.content`),
        so only buttons are missing — when `buttons` is not given explicitly,
        the current buttons are fetched via `getMessageById`:

        - `edit_message(text="new")` — changes text, keeps buttons and formatting
        - `edit_message(buttons=kb)` — changes buttons, keeps text (no extra request)
        - `edit_message(text="new", buttons=kb)` — changes both (no extra request)
        - `edit_message(buttons=None)` — removes buttons, keeps text (no extra request)
        - `edit_message(text="new", buttons=None)` — changes text, removes buttons (no extra request)

        Args:
            text (str | UNSET, optional): New text. `UNSET` keeps the current.
            parse_mode (ParseMode | str | UNSET, optional): Formatting mode.
                `UNSET` keeps the current `content.parseMode`.
            buttons (InlineKeyboardMarkup | None | UNSET, optional): New
                inline keyboard. `UNSET` keeps the current buttons (fetched via
                `getMessageById`); `None` removes them.

        Returns:
            EditMessageResponse: Result of the message update.
        """
        if self.message is None:
            raise ValueError("Cannot edit message: callback query has no message")

        # Текст и parse_mode уже приходят в событии нажатия — берём из него, без запроса.
        if text is UNSET or parse_mode is UNSET:
            event_content = self.message.content
            if not isinstance(event_content, TextContent):
                raise ValueError(
                    "Cannot edit message: click event message has no text content "
                    "(editMessage PUT-semantics requires content.text)"
                )
            if text is UNSET:
                text = event_content.text
            if parse_mode is UNSET:
                parse_mode = event_content.parse_mode

        # Кнопок в событии нет — если их не задали явно, берём текущие с сервера.
        if buttons is UNSET:
            current = await self.bot.get_message_by_id(self.message.message_id)
            current_content = current.content
            if not isinstance(current_content, TextContent):
                raise ValueError(
                    "Cannot edit message: current message has no text content "
                    "(editMessage PUT-semantics requires content.text)"
                )
            buttons = current_content.buttons

        return await self.bot.edit_message(
            message_id=self.message.message_id,
            text=text,
            parse_mode=parse_mode,
            buttons=buttons,
        )

    async def answer(
        self,
        text: str,
        *,
        answer_type: CommandAnswerType | str,
        status: CommandMessageStatus | str | None = None,
        visibility: CommandMessageVisibility | str | None = None,
        level: CommandMessageLevel | str | None = None,
    ) -> AnswerCommandResponse:
        if self.command_id is None:
            raise ValueError(
                "Cannot answer callback query: server did not send command_id "
                "(server 5.5.6 omits commandId even with wait_reply=True buttons)"
            )
        return await self.bot.answer_command(
            command_id=self.command_id,
            answer_type=answer_type,
            status=status,
            visibility=visibility,
            level=level,
            text=text,
        )
