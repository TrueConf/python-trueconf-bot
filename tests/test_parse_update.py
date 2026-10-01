from copy import deepcopy

import pytest

from trueconf.enums.message_type import MessageType
from trueconf.types.callback_query import CallbackQuery
from trueconf.types.chat import Chat
from trueconf.types.content.chat_created import ParticipantRoleContent
from trueconf.types.content.edit_chat_avatar import EditChatAvatarContent
from trueconf.types.content.edit_chat_title import EditChatTitleContent
from trueconf.types.content.location import Location
from trueconf.types.content.remove_participant import RemoveParticipant
from trueconf.types.content.text import TextContent
from trueconf.types.message import Message
from trueconf.types.parser import parse_update
from trueconf.types.requests.cleared_chat_history import ClearedChatHistory
from trueconf.types.requests.uploading_progress import UploadingProgress
from trueconf.types.system_message import SystemMessage
from trueconf.types.update import Update


def _raw(method, payload, *, update_type=1):
    return {"type": update_type, "method": method, "id": 42, "payload": payload}


def _text_message(message_id: str, text: str) -> dict:
    return {
        "chat": {"chatId": "chat-1", "chatTitle": "Chat 1", "chatType": 1},
        "chatId": "chat-1",
        "messageId": message_id,
        "timestamp": 1_725_000_000,
        "author": {"id": "alice@example.com", "type": 1},
        "box": {"id": 1, "position": "incoming"},
        "type": MessageType.PLAIN_MESSAGE.value,
        "content": {"text": text, "parseMode": "html"},
        "isEdited": False,
    }


def test_simple_event_parses_via_map():
    result = parse_update(_raw("uploadFileProgress", {"fileId": "f1", "progress": 50}))
    assert isinstance(result, UploadingProgress)
    assert result.file_id == "f1"
    assert result.progress == 50


def test_command_with_command_id_parses_as_callback_query():
    payload = {
        "commandId": "command-1",
        "commandSource": {
            "type": "inlineKeyboard",
            "buttonId": "button-1",
            "message": _text_message("message-1", "Choose an action"),
        },
        "commandPayload": {
            "type": "userCommand",
            "command": "add_to_cart",
            "customData": "item:42",
        },
    }

    result = parse_update(_raw("command", payload))

    assert isinstance(result, CallbackQuery)
    assert result.command_id == "command-1"
    assert result.command_source.type == "inlineKeyboard"
    assert result.command_source.button_id == "button-1"
    assert isinstance(result.command_source.message, Message)
    assert result.command_source.message.message_id == "message-1"
    assert result.command_payload.type == "userCommand"
    assert result.command_payload.command == "add_to_cart"
    assert result.command_payload.custom_data == "item:42"


def test_command_without_command_id_exposes_callback_shortcuts():
    payload = {
        "commandSource": {
            "type": "inlineKeyboard",
            "message": _text_message("message-2", "Choose an action"),
        },
        "commandPayload": {
            "type": "userCommand",
            "command": "show_cart",
            "customData": "корзина:🛒",
        },
    }

    result = parse_update(_raw("command", payload))

    assert isinstance(result, CallbackQuery)
    assert result.command_id is None
    assert result.command == "show_cart"
    assert result.custom_data == "корзина:🛒"
    assert result.message is result.command_source.message
    assert result.chat is result.message.chat


def test_callback_query_bind_binds_nested_message():
    payload = {
        "commandSource": {
            "type": "inlineKeyboard",
            "message": _text_message("message-3", "Choose an action"),
        },
        "commandPayload": {"type": "userCommand", "command": "details"},
    }
    bot = object()

    result = parse_update(_raw("command", payload)).bind(bot)

    assert result.bot is bot
    assert result.message.bot is bot


def test_callback_query_is_exported_from_types_package():
    from trueconf.types import CallbackQuery as ExportedCallbackQuery

    assert ExportedCallbackQuery is CallbackQuery


def test_callback_query_without_source_message_is_safe_to_bind():
    payload = {
        "commandSource": {"type": "inlineKeyboard"},
        "commandPayload": {"type": "userCommand", "command": "dismiss"},
    }

    result = parse_update(_raw("command", payload)).bind(object())

    assert result.message is None
    assert result.chat is None


def test_callback_query_preserves_unknown_command_payload_type():
    payload = {
        "commandSource": {"type": "inlineKeyboard"},
        "commandPayload": {"type": "futureCommand", "command": "future"},
    }

    result = parse_update(_raw("command", payload))

    assert result.command_payload.type == "futureCommand"
    assert result.command == "future"


def test_callback_query_deserialization_does_not_mutate_payload():
    payload = {
        "commandId": "command-2",
        "commandSource": {
            "type": "inlineKeyboard",
            "message": _text_message("message-4", "Choose an action"),
        },
        "commandPayload": {
            "type": "userCommand",
            "command": "checkout",
            "customData": "заказ:📦",
        },
    }
    original = deepcopy(payload)

    parse_update(_raw("command", payload))

    assert payload == original


def test_response_update_returns_none():
    assert parse_update(_raw("sendMessage", {}, update_type=2)) is None


def test_non_dict_payload_returns_none():
    assert parse_update(_raw("uploadFileProgress", "not-a-dict")) is None


def test_message_with_unsupported_content_returns_none():
    result = parse_update(_raw("sendMessage", {"type": 999}))
    assert result is None


def test_message_reply_is_deserialized_as_message():
    payload = _text_message("outer", "answer")
    payload["replyMessageId"] = "inner"
    payload["replyMessage"] = _text_message("inner", "/new")

    result = parse_update(_raw("sendMessage", payload))

    assert isinstance(result, Message)
    assert isinstance(result.reply_message, Message)
    assert result.reply_message.message_id == "inner"
    assert isinstance(result.reply_message.content, TextContent)
    assert result.reply_message.content.text == "/new"


@pytest.mark.parametrize("reply_message", [None, pytest.param("missing", id="missing")])
def test_message_without_reply_has_none(reply_message):
    payload = _text_message("outer", "answer")
    if reply_message != "missing":
        payload["replyMessage"] = reply_message

    result = parse_update(_raw("sendMessage", payload))

    assert isinstance(result, Message)
    assert result.reply_message is None


def test_message_deserialization_does_not_mutate_payload():
    payload = _text_message("outer", "answer")
    payload["replyMessage"] = _text_message("inner", "question")
    original = deepcopy(payload)

    parse_update(_raw("sendMessage", payload))

    assert payload == original


def test_clear_history_envelope_is_deserialized_as_system_message():
    payload = {
        "chat": {"chatId": "chat-1", "chatTitle": "Chat 1", "chatType": 2},
        "chatId": "chat-1",
        "messageId": "system-1",
        "timestamp": 1_789_486_204_571,
        "author": {"id": "danilov@example.com", "type": 1},
        "box": {"id": 16, "position": "0"},
        "type": MessageType.CLEAR_CHAT_HISTORY.value,
        "content": {"forAll": True},
    }

    result = parse_update(_raw("sendMessage", payload))

    assert isinstance(result, SystemMessage)
    assert result.message_id == "system-1"
    assert result.content.for_all is True
    assert not hasattr(result, "reply")
    assert not hasattr(result, "forward")


@pytest.mark.parametrize(
    ("message_type", "content", "content_type"),
    [
        (MessageType.ADD_PARTICIPANT, {"userId": "bob", "role": "user"}, ParticipantRoleContent),
        (MessageType.REMOVE_PARTICIPANT, {"userId": "bob"}, RemoveParticipant),
        (MessageType.EDIT_CHAT_TITLE, {"title": "New title"}, EditChatTitleContent),
        (MessageType.EDIT_CHAT_AVATAR, {"avatarUrl": "https://example.com/a"}, EditChatAvatarContent),
        (MessageType.PARTICIPANT_ROLE, {"userId": "bob", "role": "admin"}, ParticipantRoleContent),
    ],
)
def test_known_system_envelopes_are_deserialized_by_message_type(message_type, content, content_type):
    payload = {
        "chat": {"chatId": "chat-1", "chatTitle": "Chat 1", "chatType": 2},
        "messageId": "system-1",
        "timestamp": 1_789_486_204_571,
        "author": {"id": "alice@example.com", "type": 1},
        "box": {"id": 16, "position": "0"},
        "type": message_type.value,
        "content": content,
    }

    result = parse_update(_raw("sendMessage", payload))

    assert isinstance(result, SystemMessage)
    assert isinstance(result.content, content_type)


def test_clear_history_notification_preserves_boolean_for_all():
    result = parse_update(_raw("clearHistory", {"chatId": "chat-1", "forAll": True}))

    assert isinstance(result, ClearedChatHistory)
    assert result.for_all is True


def test_unknown_method_returns_generic_update():
    result = parse_update(_raw("someUnknownMethod", {"foo": "bar"}))
    assert isinstance(result, Update)
    assert result.method == "someUnknownMethod"
    assert result.type == 1
    assert result.id == 42
    assert result.payload == {"foo": "bar"}


def test_location_message_is_deserialized():
    payload = {
        "chat": {
            "chatId": "d7b69ccdeb2dbab9440f86a76bdfcae0f76b1d90",
            "chatTitle": None,
            "chatType": 5,
        },
        "chatId": "d7b69ccdeb2dbab9440f86a76bdfcae0f76b1d90",
        "messageId": "948d0d76-c599-4be9-8934-36a0be902579",
        "timestamp": 1_789_992_728_122,
        "author": {"id": "danilov@video.example.net", "type": 1},
        "box": {"id": 711, "position": "0"},
        "type": MessageType.LOCATION.value,
        "content": {
            "latitude": 47.227204,
            "longitude": 39.704168,
            "title": "Будённовский просп., 61, Ростов-на-Дону, Ростовская обл., Россия, 344011",
        },
        "isEdited": False,
    }

    result = parse_update(_raw("sendMessage", payload))

    assert isinstance(result, Message)
    assert result.type == MessageType.LOCATION
    assert result.message_id == "948d0d76-c599-4be9-8934-36a0be902579"
    assert result.chat.chat_id == "d7b69ccdeb2dbab9440f86a76bdfcae0f76b1d90"
    assert result.chat.chat_type == 5
    assert isinstance(result.content, Location)
    assert result.content.latitude == 47.227204
    assert result.content.longitude == 39.704168
    assert result.content.title == "Будённовский просп., 61, Ростов-на-Дону, Ростовская обл., Россия, 344011"
    assert result.text is None


def test_chat_title_null_is_preserved_as_none():
    chat = Chat.from_dict({"chatId": "chat-1", "chatTitle": None, "chatType": 1})

    assert chat.chat_title is None


def test_location_is_exported_from_content_package():
    from trueconf.types.content import Location as ExportedLocation

    assert ExportedLocation is Location


def test_message_filter_is_exported_from_filters_package():
    from trueconf.filters import MessageFilter as ExportedMessageFilter
    from trueconf.filters.message import MessageFilter

    assert ExportedMessageFilter is MessageFilter
