from __future__ import annotations

import pytest

from trueconf.enums.parse_mode import ParseMode
from trueconf.types.callback_query import CallbackQuery
from trueconf.types.keyboard import InlineKeyboardMarkup
from trueconf.types.responses.edit_message_response import EditMessageResponse
from trueconf.types.responses.get_message_by_id_response import GetMessageByIdResponse

pytestmark = pytest.mark.anyio


@pytest.fixture
def anyio_backend():
    return "asyncio"


class RecordingBot:
    """Fake-бот: отдаёт фиксированный getMessageById, записывает edit_message вызовы."""

    def __init__(self, current_raw: dict):
        self.current = GetMessageByIdResponse.from_dict(current_raw)
        self.calls: list[tuple] = []

    async def get_message_by_id(self, message_id: str) -> GetMessageByIdResponse:
        self.calls.append(("get_message_by_id", message_id))
        return self.current

    async def edit_message(self, message_id, text, parse_mode, *, buttons=None):
        self.calls.append(("edit_message", message_id, text, parse_mode, buttons))
        return EditMessageResponse(message_id=message_id, timestamp=0)


def _text_raw(message_id: str, text: str, parse_mode: str = "html") -> dict:
    return {
        "messageId": message_id,
        "chat": {"chatId": "chat-1", "chatTitle": "Chat 1", "chatType": 1},
        "timestamp": 1_725_000_000,
        "replyMessageId": None,
        "isEdited": False,
        "type": 200,
        "author": {"id": "button_bot@example.com", "type": 1},
        "box": {"id": 1, "position": "incoming"},
        "content": {"text": text, "parseMode": parse_mode},
    }


def _current_raw(message_id: str = "message-1") -> dict:
    raw = _text_raw(message_id, "Старый текст", "html")
    raw["chatId"] = "chat-1"  # GetMessageByIdResponse требует chatId на верхнем уровне
    raw["content"]["buttons"] = [
        [{"type": "command", "label": "Нажми меня", "command": "btn:simple", "waitReply": False}]
    ]
    return raw


def _callback_query(message_id: str = "message-1") -> CallbackQuery:
    raw = {
        "commandSource": {
            "type": "inlineKeyboard",
            "message": _text_raw(message_id, "Выберите действие"),
        },
        "commandPayload": {"type": "userCommand", "command": "next", "customData": ""},
    }
    return CallbackQuery.from_dict(raw)


async def test_edit_message_text_only_keeps_buttons_from_server():
    # buttons не передан → кнопки берём из getMessageById (в событии их нет)
    bot = RecordingBot(_current_raw())
    callback = _callback_query().bind(bot)

    result = await callback.edit_message(text="Новый текст")

    assert result.message_id == "message-1"
    assert bot.calls[0] == ("get_message_by_id", "message-1")
    edit_call = bot.calls[1]
    assert edit_call[0] == "edit_message"
    assert edit_call[1] == "message-1"
    assert edit_call[2] == "Новый текст"
    assert edit_call[3] == "html"  # parse_mode из события нажатия
    assert edit_call[4] is not None  # кнопки из getMessageById
    assert edit_call[4].buttons[0][0].command == "btn:simple"


async def test_edit_message_text_only_keeps_server_buttons_in_payload():
    # проверить, что в editMessage уходят именно кнопки из getMessageById
    bot = RecordingBot(_current_raw())
    callback = _callback_query().bind(bot)

    await callback.edit_message(text="Новый текст")

    edit_call = bot.calls[-1]
    assert edit_call[0] == "edit_message"
    assert edit_call[4] is not None
    assert edit_call[4].buttons[0][0].command == "btn:simple"


async def test_edit_message_buttons_only_skips_get_message_by_id():
    # buttons передан явно → getMessageById НЕ нужен; текст и parse_mode из события
    bot = RecordingBot(_current_raw())
    callback = _callback_query().bind(bot)
    kb = InlineKeyboardMarkup.from_dict({"buttons": [[{"type": "command", "label": "Далее", "command": "next"}]]})

    await callback.edit_message(buttons=kb)

    assert bot.calls == [
        ("edit_message", "message-1", "Выберите действие", "html", kb),
    ]


async def test_edit_message_text_and_buttons_skips_get_message_by_id():
    bot = RecordingBot(_current_raw())
    callback = _callback_query().bind(bot)
    kb = InlineKeyboardMarkup.from_dict({"buttons": [[{"type": "command", "label": "Далее", "command": "next"}]]})

    await callback.edit_message(text="Новый текст", parse_mode=ParseMode.HTML, buttons=kb)

    assert bot.calls == [("edit_message", "message-1", "Новый текст", "html", kb)]


async def test_edit_message_buttons_none_removes_buttons_keeps_text():
    # buttons=None явный → кнопки удаляются, getMessageById не нужен
    bot = RecordingBot(_current_raw())
    callback = _callback_query().bind(bot)

    await callback.edit_message(buttons=None)

    assert bot.calls == [
        ("edit_message", "message-1", "Выберите действие", "html", None),
    ]


async def test_edit_message_text_and_buttons_none_changes_text_removes_buttons():
    bot = RecordingBot(_current_raw())
    callback = _callback_query().bind(bot)

    await callback.edit_message(text="Новый текст", buttons=None)

    assert bot.calls == [
        ("edit_message", "message-1", "Новый текст", "html", None),
    ]


async def test_edit_message_requires_message():
    bot = RecordingBot(_current_raw())
    callback = _callback_query().bind(bot)
    callback.command_source.message = None

    with pytest.raises(ValueError, match="callback query has no message"):
        await callback.edit_message(text="Новый текст")


async def test_edit_message_non_text_event_content_raises_when_text_omitted():
    # text не передан → берём из события; событие нетекстовое → ValueError
    bot = RecordingBot(_current_raw())
    raw = _text_raw("message-1", "Выберите действие")
    raw["type"] = 205  # VOICE_MESSAGE
    raw["content"] = {"fileId": "voice-1", "size": 12_345, "mimeType": "audio/ogg", "duration": 7}
    callback = CallbackQuery.from_dict(
        {
            "commandSource": {"type": "inlineKeyboard", "message": raw},
            "commandPayload": {"type": "userCommand", "command": "next", "customData": ""},
        }
    ).bind(bot)

    with pytest.raises(ValueError, match="no text content"):
        await callback.edit_message()  # text и parse_mode оба UNSET → из события


async def test_edit_message_non_text_server_content_raises_when_buttons_needed():
    # buttons не передан → getMessageById; ответ нетекстовый → ValueError
    raw = _text_raw("message-1", "Старый текст")
    raw["chatId"] = "chat-1"
    raw["type"] = 205
    raw["content"] = {"fileId": "voice-1", "size": 12_345, "mimeType": "audio/ogg", "duration": 7}
    bot = RecordingBot(raw)
    callback = _callback_query().bind(bot)

    with pytest.raises(ValueError, match="no text content"):
        await callback.edit_message(text="Новый текст")
