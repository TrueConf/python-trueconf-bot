import asyncio

import pytest

from trueconf.client.bot import Bot
from trueconf.enums import ButtonStyle
from trueconf.methods.edit_message import EditMessage
from trueconf.methods.send_message import SendMessage
from trueconf.types.keyboard import InlineKeyboardButton, InlineKeyboardMarkup
from trueconf.types.message import Message
from trueconf.types.responses.send_message_response import SendMessageResponse


def test_command_button_with_wait_reply_is_not_implemented():
    with pytest.raises(NotImplementedError, match="supported by TrueConf Server"):
        InlineKeyboardButton(
            text="Добавить в корзину",
            command="add_to_cart",
            custom_data='{"product_id": 42}',
            wait_reply=True,
        )


def test_button_rejects_multiple_actions():
    expected_error = "Exactly one button action must be specified; got: command, url"

    with pytest.raises(ValueError, match=expected_error):
        InlineKeyboardButton(
            text="Неоднозначная кнопка",
            command="confirm",
            url="https://example.com",
        )


def test_button_rejects_missing_action():
    expected_error = "Exactly one button action must be specified; got: none"

    with pytest.raises(ValueError, match=expected_error):
        InlineKeyboardButton(text="Кнопка без действия")


def test_url_button_serializes_to_trueconf_dict():
    button = InlineKeyboardButton(
        text="Открыть сайт",
        url="https://trueconf.com",
    )

    assert button.to_dict() == {
        "type": "url",
        "label": "Открыть сайт",
        "url": "https://trueconf.com",
    }


def test_url_button_serializes_without_optional_text():
    button = InlineKeyboardButton(url="https://trueconf.com")

    assert button.to_dict() == {
        "type": "url",
        "url": "https://trueconf.com",
    }


@pytest.mark.parametrize(
    ("action", "value"),
    [
        pytest.param("command", "confirm", id="command"),
        pytest.param("message", "Hello", id="message"),
        pytest.param("copy_data", "PROMO", id="copy"),
    ],
)
def test_non_url_button_requires_text(action: str, value: str):
    with pytest.raises(ValueError, match=f"Button text is required for button action '{action.replace('_data', '')}'"):
        InlineKeyboardButton(**{action: value})


def test_url_button_rejects_unsupported_scheme():
    expected_error = "Unsupported button URL scheme 'ftp'; allowed: http, https, mailto, trueconf"

    with pytest.raises(ValueError, match=expected_error):
        InlineKeyboardButton(
            text="Открыть FTP",
            url="ftp://example.com/file",
        )


@pytest.mark.parametrize(
    "url",
    [
        pytest.param("http://", id="too-short"),
        pytest.param("https://" + "a" * 8088, id="too-long"),
    ],
)
def test_url_button_rejects_length_outside_allowed_range(url: str):
    expected_error = f"Button URL length must be between 8 and 8095 characters; got: {len(url)}"

    with pytest.raises(ValueError, match=expected_error):
        InlineKeyboardButton(text="Некорректная ссылка", url=url)


def test_url_button_rejects_non_ascii_characters():
    expected_error = "Button URL must contain ASCII characters only"

    with pytest.raises(ValueError, match=expected_error):
        InlineKeyboardButton(
            text="Ссылка с Unicode",
            url="https://example.com/привет",
        )


def test_message_button_serializes_to_trueconf_dict():
    button = InlineKeyboardButton(
        text="Написать приветствие",
        message="Привет, коллеги!",
        draft=True,
    )

    assert button.to_dict() == {
        "type": "message",
        "label": "Написать приветствие",
        "message": "Привет, коллеги!",
        "draft": True,
    }


def test_button_rejects_draft_for_non_message_action():
    expected_error = "Field 'draft' is only valid for button action 'message'; got: url"

    with pytest.raises(ValueError, match=expected_error):
        InlineKeyboardButton(
            text="Открыть сайт",
            url="https://trueconf.com",
            draft=True,
        )


def test_copy_button_serializes_to_trueconf_dict():
    button = InlineKeyboardButton(
        text="Скопировать промокод",
        copy_data="ПРОМОКОД-12345",
    )

    assert button.to_dict() == {
        "type": "copy",
        "label": "Скопировать промокод",
        "data": "ПРОМОКОД-12345",
    }


@pytest.mark.parametrize(
    "copy_data",
    [
        pytest.param("", id="empty"),
        pytest.param("я" * 4096, id="too-long"),
    ],
)
def test_copy_button_rejects_data_length_outside_allowed_range(copy_data: str):
    expected_error = f"Copy button data length must be between 1 and 4095 characters; got: {len(copy_data)}"

    with pytest.raises(ValueError, match=expected_error):
        InlineKeyboardButton(text="Скопировать", copy_data=copy_data)


@pytest.mark.parametrize(
    ("command", "expected_error"),
    [
        pytest.param(
            "",
            "Button command length must be between 1 and 255 characters; got: 0",
            id="empty",
        ),
        pytest.param(
            "a" * 256,
            "Button command length must be between 1 and 255 characters; got: 256",
            id="too-long",
        ),
        pytest.param(
            "добавить_товар",
            "Button command must contain ASCII characters only",
            id="non-ascii",
        ),
    ],
)
def test_command_button_rejects_invalid_command(command: str, expected_error: str):
    with pytest.raises(ValueError, match=expected_error):
        InlineKeyboardButton(text="Команда", command=command)


@pytest.mark.parametrize(
    ("custom_data", "expected_error"),
    [
        pytest.param(
            "",
            "Button custom data length must be between 1 and 4096 characters; got: 0",
            id="empty",
        ),
        pytest.param(
            "a" * 4097,
            "Button custom data length must be between 1 and 4096 characters; got: 4097",
            id="too-long",
        ),
        pytest.param(
            "корзина:🛒",
            "Button custom data must contain ASCII characters only",
            id="non-ascii",
        ),
    ],
)
def test_command_button_rejects_invalid_custom_data(custom_data: str, expected_error: str):
    with pytest.raises(ValueError, match=expected_error):
        InlineKeyboardButton(
            text="Команда",
            command="action",
            custom_data=custom_data,
        )


def test_command_button_accepts_custom_data_at_maximum_length():
    custom_data = "a" * 4096

    button = InlineKeyboardButton(text="Команда", command="action", custom_data=custom_data)

    assert button.to_dict()["customData"] == custom_data


def test_button_rejects_custom_data_for_non_command_action():
    expected_error = "Field 'custom_data' is only valid for button action 'command'; got: url"

    with pytest.raises(ValueError, match=expected_error):
        InlineKeyboardButton(
            text="Открыть сайт",
            url="https://trueconf.com",
            custom_data="payload",
        )


def test_command_button_serializes_full_recipient_id():
    button = InlineKeyboardButton(
        text="Передать другому боту",
        command="process_order",
        to="orders_bot@remote.example.com",
    )

    assert button.to_dict() == {
        "type": "command",
        "label": "Передать другому боту",
        "command": "process_order",
        "to": "orders_bot@remote.example.com",
    }


def test_button_rejects_recipient_for_non_command_action():
    expected_error = "Field 'to' is only valid for button action 'command'; got: url"

    with pytest.raises(ValueError, match=expected_error):
        InlineKeyboardButton(
            text="Открыть сайт",
            url="https://trueconf.com",
            to="orders_bot@remote.example.com",
        )


def test_command_button_rejects_empty_recipient():
    with pytest.raises(ValueError, match="Button recipient 'to' must not be empty"):
        InlineKeyboardButton(
            text="Передать команду",
            command="process_order",
            to="",
        )


def test_button_serializes_id_and_style():
    button = InlineKeyboardButton(
        text="Добавить в корзину",
        command="add_to_cart",
        button_id="button_98",
        style=ButtonStyle.PRIMARY,
    )

    assert button.to_dict() == {
        "type": "command",
        "label": "Добавить в корзину",
        "command": "add_to_cart",
        "id": "button_98",
        "style": "primary",
    }


@pytest.mark.parametrize(
    "text",
    [
        pytest.param("", id="empty"),
        pytest.param("я" * 33, id="too-long"),
    ],
)
def test_button_rejects_label_length_outside_allowed_range(text: str):
    expected_error = f"Button text length must be between 1 and 32 characters; got: {len(text)}"

    with pytest.raises(ValueError, match=expected_error):
        InlineKeyboardButton(text=text, command="action")


def test_inline_keyboard_serializes_button_matrix():
    keyboard = InlineKeyboardMarkup(
        buttons=[
            [
                InlineKeyboardButton(text="Подтвердить", command="confirm"),
                InlineKeyboardButton(text="Отмена", command="cancel"),
            ],
            [
                InlineKeyboardButton(text="Сайт", url="https://trueconf.com"),
                InlineKeyboardButton(text="Копировать", copy_data="ПРОМО"),
            ],
        ]
    )

    assert keyboard.to_dict() == {
        "buttons": [
            [
                {"type": "command", "label": "Подтвердить", "command": "confirm"},
                {"type": "command", "label": "Отмена", "command": "cancel"},
            ],
            [
                {"type": "url", "label": "Сайт", "url": "https://trueconf.com"},
                {"type": "copy", "label": "Копировать", "data": "ПРОМО"},
            ],
        ]
    }


def test_inline_keyboard_rejects_more_than_eight_rows():
    keyboard = [[InlineKeyboardButton(text="Кнопка", command="action")] for _ in range(9)]

    with pytest.raises(ValueError, match="Inline keyboard must contain at most 8 rows; got: 9"):
        InlineKeyboardMarkup(buttons=keyboard)


def test_inline_keyboard_rejects_more_than_eight_buttons_in_row():
    row = [InlineKeyboardButton(text="Кнопка", command="action") for _ in range(9)]

    with pytest.raises(ValueError, match="Inline keyboard row 0 must contain at most 8 buttons; got: 9"):
        InlineKeyboardMarkup(buttons=[row])


def test_inline_keyboard_rejects_more_than_64_buttons():
    keyboard = [[InlineKeyboardButton(text="Кнопка", command="action") for _ in range(8)] for _ in range(7)]
    keyboard.append([InlineKeyboardButton(text="Кнопка", command="action") for _ in range(9)])

    with pytest.raises(ValueError, match="Inline keyboard must contain at most 64 buttons; got: 65"):
        InlineKeyboardMarkup(buttons=keyboard)


def test_send_message_payload_contains_inline_keyboard():
    keyboard = InlineKeyboardMarkup(
        buttons=[
            [InlineKeyboardButton(text="Подтвердить", command="confirm")],
        ]
    )
    method = SendMessage(
        chat_id="chat-1",
        text="Выберите действие",
        parse_mode="text",
        buttons=keyboard,
    )

    assert method.payload() == {
        "chatId": "chat-1",
        "replyMessageId": None,
        "content": {
            "text": "Выберите действие",
            "parseMode": "text",
            "buttons": [
                [
                    {
                        "type": "command",
                        "label": "Подтвердить",
                        "command": "confirm",
                    }
                ]
            ],
        },
    }


def test_bot_send_message_accepts_inline_keyboard():
    class CapturingBot(Bot):
        async def __call__(self, method):
            self.captured_method = method
            return SendMessageResponse(chat_id="chat-1", message_id="message-1", timestamp=1)

    bot = object.__new__(CapturingBot)
    keyboard = InlineKeyboardMarkup(
        buttons=[
            [InlineKeyboardButton(text="Подтвердить", command="confirm")],
        ]
    )

    asyncio.run(
        bot.send_message(
            chat_id="chat-1",
            text="Выберите действие",
            buttons=keyboard,
        )
    )

    assert isinstance(bot.captured_method, SendMessage)
    assert bot.captured_method.payload()["content"]["buttons"] == [
        [
            {
                "type": "command",
                "label": "Подтвердить",
                "command": "confirm",
            }
        ]
    ]


def test_bot_send_message_completes_short_button_recipient_with_server_name():
    class CapturingBot(Bot):
        @property
        def server_name(self):
            async def resolve_server_name():
                return "local.example.com"

            return resolve_server_name()

        async def __call__(self, method):
            self.captured_method = method
            return SendMessageResponse(chat_id="chat-1", message_id="message-1", timestamp=1)

    bot = object.__new__(CapturingBot)
    button = InlineKeyboardButton(
        text="Передать команду",
        command="process_order",
        to="orders_bot",
    )
    keyboard = InlineKeyboardMarkup(buttons=[[button]])

    asyncio.run(
        bot.send_message(
            chat_id="chat-1",
            text="Выберите действие",
            buttons=keyboard,
        )
    )

    assert isinstance(bot.captured_method, SendMessage)
    assert bot.captured_method.payload()["content"]["buttons"][0][0]["to"] == "orders_bot@local.example.com"
    assert button.to == "orders_bot"


def test_bot_send_message_keeps_full_button_recipient_without_resolving_server_name():
    class CapturingBot(Bot):
        @property
        def server_name(self):
            raise AssertionError("server_name must not be resolved for a full TrueConf ID")

        async def __call__(self, method):
            self.captured_method = method
            return SendMessageResponse(chat_id="chat-1", message_id="message-1", timestamp=1)

    bot = object.__new__(CapturingBot)
    keyboard = InlineKeyboardMarkup(
        buttons=[
            [
                InlineKeyboardButton(
                    text="Передать команду",
                    command="process_order",
                    to="orders_bot@remote.example.com",
                )
            ]
        ]
    )

    asyncio.run(
        bot.send_message(
            chat_id="chat-1",
            text="Выберите действие",
            buttons=keyboard,
        )
    )

    assert isinstance(bot.captured_method, SendMessage)
    assert bot.captured_method.payload()["content"]["buttons"][0][0]["to"] == ("orders_bot@remote.example.com")


def _bound_text_message(bot) -> Message:
    message = Message.from_dict(
        {
            "messageId": "message-1",
            "chat": {"chatId": "chat-1", "chatTitle": "Chat 1", "chatType": 1},
            "timestamp": 1_725_000_000,
            "replyMessageId": None,
            "isEdited": False,
            "type": 200,
            "author": {"id": "alice@example.com", "type": 1},
            "box": {"id": 1, "position": "incoming"},
            "content": {"text": "Исходное сообщение", "parseMode": "html"},
        }
    )
    return message.bind(bot)


@pytest.mark.parametrize(
    ("shortcut", "expected_reply_message_id"),
    [
        pytest.param("answer", None, id="answer"),
        pytest.param("reply", "message-1", id="reply"),
    ],
)
def test_message_shortcuts_accept_inline_keyboard(shortcut: str, expected_reply_message_id: str | None):
    class CapturingBot:
        async def send_message(self, **kwargs):
            self.send_message_kwargs = kwargs
            return SendMessageResponse(chat_id="chat-1", message_id="message-2", timestamp=1)

    bot = CapturingBot()
    message = _bound_text_message(bot)
    keyboard = InlineKeyboardMarkup(buttons=[[InlineKeyboardButton(text="Подтвердить", command="confirm")]])

    asyncio.run(getattr(message, shortcut)("Выберите действие", buttons=keyboard))

    assert bot.send_message_kwargs["buttons"] is keyboard
    assert bot.send_message_kwargs.get("reply_message_id") == expected_reply_message_id


def test_inline_keyboard_types_are_available_from_public_package():
    from trueconf import ButtonStyle as PublicButtonStyle
    from trueconf import ButtonType as PublicButtonType
    from trueconf import InlineKeyboardButton as PublicInlineKeyboardButton
    from trueconf import InlineKeyboardMarkup as PublicInlineKeyboardMarkup

    assert PublicButtonStyle is ButtonStyle
    assert PublicButtonType.__module__ == "trueconf.enums.button"
    assert PublicInlineKeyboardButton is InlineKeyboardButton
    assert PublicInlineKeyboardMarkup is InlineKeyboardMarkup


def test_edit_message_accepts_inline_keyboard():
    keyboard = InlineKeyboardMarkup(buttons=[[InlineKeyboardButton(text="Подтвердить", command="confirm")]])

    with_markup = EditMessage(
        message_id="message-1",
        text="Новый текст",
        parse_mode="html",
        buttons=keyboard,
    )
    without_markup = EditMessage(message_id="message-1", text="Новый текст", parse_mode="html")

    assert with_markup.payload() == {
        "messageId": "message-1",
        "content": {
            "text": "Новый текст",
            "parseMode": "html",
            "buttons": [[{"type": "command", "label": "Подтвердить", "command": "confirm"}]],
        },
    }
    assert without_markup.payload() == {
        "messageId": "message-1",
        "content": {"text": "Новый текст", "parseMode": "html"},
    }
