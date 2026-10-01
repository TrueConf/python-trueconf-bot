from __future__ import annotations

import pytest

from trueconf.enums.button import ButtonType
from trueconf.types.content.location import Location
from trueconf.types.content.text import TextContent
from trueconf.types.message import Message
from trueconf.types.responses.get_chat_history_response import GetChatHistoryResponse
from trueconf.types.responses.get_message_by_id_response import GetMessageByIdResponse
from trueconf.types.system_message import SystemMessage


class FakeBot:
    me_id = "bot@example.com"


def _text_raw(message_id: str, text: str, parse_mode: str = "html") -> dict:
    return {
        "messageId": message_id,
        "chat": {"chatId": "chat-1", "chatTitle": "Chat 1", "chatType": 1},
        "timestamp": 1_725_000_000,
        "replyMessageId": None,
        "isEdited": False,
        "type": 200,
        "author": {"id": "alice@example.com", "type": 1},
        "box": {"id": 1, "position": "incoming"},
        "content": {"text": text, "parseMode": parse_mode},
    }


def _voice_raw(message_id: str) -> dict:
    return {
        "messageId": message_id,
        "chat": {"chatId": "chat-1", "chatTitle": "Chat 1", "chatType": 1},
        "timestamp": 1_725_000_000,
        "replyMessageId": None,
        "isEdited": False,
        "type": 205,
        "author": {"id": "alice@example.com", "type": 1},
        "box": {"id": 1, "position": "incoming"},
        "content": {"fileId": "voice-1", "size": 12_345, "mimeType": "audio/ogg", "duration": 7},
    }


def _location_raw(message_id: str) -> dict:
    return {
        "messageId": message_id,
        "chat": {"chatId": "chat-1", "chatTitle": "Chat 1", "chatType": 1},
        "timestamp": 1_725_000_000,
        "replyMessageId": None,
        "isEdited": False,
        "type": 203,
        "author": {"id": "alice@example.com", "type": 1},
        "box": {"id": 1, "position": "incoming"},
        "content": {"latitude": 47.227204, "longitude": 39.704168, "title": "Rostov"},
    }


def _history_raw(messages: list[dict]) -> dict:
    return {"count": len(messages), "chatId": "chat-1", "messages": messages}


def _clear_history_raw(message_id: str) -> dict:
    return {
        "messageId": message_id,
        "chatId": "chat-1",
        "chat": {"chatId": "chat-1", "chatTitle": "Chat 1", "chatType": 2},
        "timestamp": 1_725_000_001,
        "type": 23,
        "author": {"id": "alice@example.com", "type": 1},
        "box": {"id": 2, "position": "incoming"},
        "content": {"forAll": True},
    }


def test_unbound_message_raises_runtime_error():
    message = Message.from_dict(_text_raw("m1", "hello"))

    with pytest.raises(RuntimeError, match="bound to ChatBot"):
        assert message.bot


def test_unbound_message_mention_raises_runtime_error():
    message = Message.from_dict(_text_raw("m1", '<a href="trueconf:bot@example.com">Bot</a>'))

    with pytest.raises(RuntimeError, match="bound to ChatBot"):
        assert message.mention


def test_bound_message_exposes_bot():
    bot = FakeBot()
    message = Message.from_dict(_text_raw("m1", "hello"))

    assert message.bind(bot) is message
    assert message.bot is bot


def test_mention_self_link_is_true():
    message = Message.from_dict(_text_raw("m1", '<a href="trueconf:bot@example.com">Bot</a>'))
    message.bind(FakeBot())

    assert message.mention is True


def test_mention_other_user_link_is_none():
    message = Message.from_dict(_text_raw("m1", '<a href="trueconf:other@example.com">Other</a>'))
    message.bind(FakeBot())

    assert message.mention is None


def test_mention_plain_text_is_none():
    message = Message.from_dict(_text_raw("m1", "hello"))
    message.bind(FakeBot())

    assert message.mention is None


def test_mention_at_all_is_true():
    message = Message.from_dict(_text_raw("m1", "@all"))
    message.bind(FakeBot())

    assert message.mention is True


def test_mention_non_text_content_is_none():
    message = Message.from_dict(_voice_raw("m1"))
    message.bind(FakeBot())

    assert message.mention is None


def test_location_shortcut_returns_content():
    message = Message.from_dict(_location_raw("m1"))

    assert isinstance(message.location, Location)
    assert message.location.latitude == 47.227204
    assert message.location.longitude == 39.704168
    assert message.location.title == "Rostov"


def test_location_shortcut_none_for_text():
    message = Message.from_dict(_text_raw("m1", "hello"))

    assert message.location is None


def test_location_shortcut_none_for_voice():
    message = Message.from_dict(_voice_raw("m1"))

    assert message.location is None


def test_history_response_bind_binds_every_message():
    bot = FakeBot()
    response = GetChatHistoryResponse.from_dict(_history_raw([_text_raw("m1", "one"), _text_raw("m2", "two")]))

    response.bind(bot)

    assert all(message.bot is bot for message in response.messages)


def test_message_bind_binds_reply_message():
    bot = FakeBot()
    raw = _text_raw("outer", "answer")
    raw["replyMessageId"] = "inner"
    raw["replyMessage"] = _text_raw("inner", "question")
    message = Message.from_dict(raw)

    message.bind(bot)

    assert message.reply_message is not None
    assert message.reply_message.bot is bot


def test_history_deserializes_and_binds_user_and_system_messages():
    bot = FakeBot()
    response = GetChatHistoryResponse.from_dict(_history_raw([_text_raw("m1", "one"), _clear_history_raw("s1")]))

    response.bind(bot)

    assert isinstance(response.messages[0], Message)
    assert isinstance(response.messages[1], SystemMessage)
    assert response.messages[0].bot is bot
    assert response.messages[1].bot is bot
    assert response.messages[1].content.for_all is True


def test_history_binds_nested_reply_message():
    bot = FakeBot()
    raw = _text_raw("outer", "answer")
    raw["replyMessage"] = _text_raw("inner", "question")
    response = GetChatHistoryResponse.from_dict(_history_raw([raw]))

    response.bind(bot)

    message = response.messages[0]
    assert isinstance(message, Message)
    assert message.reply_message is not None
    assert message.reply_message.bot is bot


def test_get_message_by_id_response_deserializes_and_binds_reply_message():
    bot = FakeBot()
    raw = _text_raw("outer", "answer")
    raw["chatId"] = "chat-1"
    raw["replyMessageId"] = "inner"
    raw["replyMessage"] = _text_raw("inner", "question")
    response = GetMessageByIdResponse.from_dict(raw)

    response.bind(bot)

    assert isinstance(response.content, TextContent)
    assert isinstance(response.reply_message, Message)
    assert response.reply_message.message_id == "inner"
    assert response.reply_message.bot is bot


def test_get_message_by_id_response_parses_buttons_into_content_buttons():
    raw = _text_raw("message-1", "Старый текст")
    raw["chatId"] = "chat-1"
    raw["content"]["buttons"] = [
        [{"type": "command", "label": "Нажми меня", "command": "btn:simple", "waitReply": False}]
    ]
    response = GetMessageByIdResponse.from_dict(raw)

    assert isinstance(response.content, TextContent)
    assert response.content.buttons is not None
    button = response.content.buttons.buttons[0][0]
    assert button.text == "Нажми меня"
    assert button.command == "btn:simple"
    assert button.type == ButtonType.COMMAND


def test_get_message_by_id_response_without_buttons_has_none_buttons():
    raw = _text_raw("message-2", "Просто текст")
    raw["chatId"] = "chat-1"
    response = GetMessageByIdResponse.from_dict(raw)

    assert isinstance(response.content, TextContent)
    assert response.content.buttons is None
