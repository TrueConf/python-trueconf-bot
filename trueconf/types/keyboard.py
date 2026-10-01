from __future__ import annotations

from dataclasses import dataclass, field, replace
from urllib.parse import urlsplit

from mashumaro import DataClassDictMixin
from mashumaro.config import BaseConfig

from trueconf.enums import ALLOWED_BUTTON_URL_SCHEMES, ButtonStyle, ButtonType

MAX_INLINE_KEYBOARD_ROWS = 8
MAX_INLINE_KEYBOARD_WIDTH = 8
MAX_INLINE_KEYBOARD_BUTTONS = 64


@dataclass(frozen=True, slots=True)
class InlineKeyboardButton(DataClassDictMixin):
    text: str | None = field(default=None, metadata={"alias": "label"})
    command: str | None = None
    url: str | None = None
    message: str | None = None
    copy_data: str | None = field(default=None, metadata={"alias": "data"})
    custom_data: str | None = field(default=None, metadata={"alias": "customData"})
    wait_reply: bool = field(default=False, metadata={"alias": "waitReply"})
    to: str | None = None
    draft: bool = False
    button_id: str | None = field(default=None, metadata={"alias": "id"})
    style: ButtonStyle | None = None
    type: ButtonType = field(init=False)

    class Config(BaseConfig):
        serialize_by_alias = True
        omit_none = True
        omit_default = True

    def __post_init__(self) -> None:  # noqa: C901
        if self.wait_reply:
            raise NotImplementedError(
                "This functionality is supported by TrueConf Server, provided that client applications "
                "support it as well. It is not yet available in this library and will be enabled once "
                "client-side support becomes available. Please follow library updates for announcements."
            )

        actions = {
            ButtonType.COMMAND: self.command,
            ButtonType.URL: self.url,
            ButtonType.MESSAGE: self.message,
            ButtonType.COPY: self.copy_data,
        }
        selected_actions = [button_type for button_type, value in actions.items() if value is not None]
        if len(selected_actions) != 1:
            selected = ", ".join(button_type.value for button_type in selected_actions) if selected_actions else "none"
            raise ValueError(f"Exactly one button action must be specified; got: {selected}")

        button_type = selected_actions[0]
        if self.text is None and button_type is not ButtonType.URL:
            raise ValueError(f"Button text is required for button action '{button_type.value}'")
        if self.text is not None and not 1 <= len(self.text) <= 32:
            raise ValueError(f"Button text length must be between 1 and 32 characters; got: {len(self.text)}")
        if self.draft and button_type is not ButtonType.MESSAGE:
            raise ValueError(f"Field 'draft' is only valid for button action 'message'; got: {button_type.value}")

        if button_type is not ButtonType.COMMAND:
            if self.custom_data is not None:
                raise ValueError(
                    f"Field 'custom_data' is only valid for button action 'command'; got: {button_type.value}"
                )
            if self.wait_reply:
                raise ValueError(
                    f"Field 'wait_reply' is only valid for button action 'command'; got: {button_type.value}"
                )
            if self.to is not None:
                raise ValueError(f"Field 'to' is only valid for button action 'command'; got: {button_type.value}")

        if self.command is not None:
            if not 1 <= len(self.command) <= 255:
                raise ValueError(
                    f"Button command length must be between 1 and 255 characters; got: {len(self.command)}"
                )
            if not self.command.isascii():
                raise ValueError("Button command must contain ASCII characters only")

        if self.to == "":
            raise ValueError("Button recipient 'to' must not be empty")

        if self.custom_data is not None:
            if not 1 <= len(self.custom_data) <= 4096:
                raise ValueError(
                    f"Button custom data length must be between 1 and 4096 characters; got: {len(self.custom_data)}"
                )
            if not self.custom_data.isascii():
                raise ValueError("Button custom data must contain ASCII characters only")

        if self.url is not None:
            if not 8 <= len(self.url) <= 8095:
                raise ValueError(f"Button URL length must be between 8 and 8095 characters; got: {len(self.url)}")
            if not self.url.isascii():
                raise ValueError("Button URL must contain ASCII characters only")
            scheme = urlsplit(self.url).scheme.lower()
            if scheme not in ALLOWED_BUTTON_URL_SCHEMES:
                allowed = ", ".join(ALLOWED_BUTTON_URL_SCHEMES)
                raise ValueError(f"Unsupported button URL scheme {scheme!r}; allowed: {allowed}")

        if self.copy_data is not None and not 1 <= len(self.copy_data) <= 4095:
            raise ValueError(
                f"Copy button data length must be between 1 and 4095 characters; got: {len(self.copy_data)}"
            )

        object.__setattr__(self, "type", button_type)

    def _with_server_name(self, server_name: str) -> InlineKeyboardButton:
        if self.to is None or "@" in self.to:
            return self
        return replace(self, to=f"{self.to}@{server_name}")


@dataclass(frozen=True, slots=True)
class InlineKeyboardMarkup(DataClassDictMixin):
    buttons: list[list[InlineKeyboardButton]] = field(metadata={"alias": "buttons"})

    class Config(BaseConfig):
        serialize_by_alias = True

    @property
    def _requires_server_name(self) -> bool:
        return any(button.to is not None and "@" not in button.to for row in self.buttons for button in row)

    def _with_server_name(self, server_name: str) -> InlineKeyboardMarkup:
        return InlineKeyboardMarkup(
            buttons=[[button._with_server_name(server_name) for button in row] for row in self.buttons]
        )

    def __post_init__(self) -> None:
        button_count = sum(len(row) for row in self.buttons)
        if button_count > MAX_INLINE_KEYBOARD_BUTTONS:
            raise ValueError(
                f"Inline keyboard must contain at most {MAX_INLINE_KEYBOARD_BUTTONS} buttons; got: {button_count}"
            )

        row_count = len(self.buttons)
        if row_count > MAX_INLINE_KEYBOARD_ROWS:
            raise ValueError(f"Inline keyboard must contain at most {MAX_INLINE_KEYBOARD_ROWS} rows; got: {row_count}")

        for index, row in enumerate(self.buttons):
            if len(row) > MAX_INLINE_KEYBOARD_WIDTH:
                raise ValueError(
                    f"Inline keyboard row {index} must contain at most {MAX_INLINE_KEYBOARD_WIDTH} buttons; "
                    f"got: {len(row)}"
                )
