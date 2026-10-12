from __future__ import annotations

import json

import pytest

from trueconf.enums.message_type import MessageType
from trueconf.methods.get_chat_history import GetChatHistory
from trueconf.types.content.attachment import AttachmentContent
from trueconf.types.content.forward_message import ForwardMessage
from trueconf.types.content.location import Location
from trueconf.types.content.survey import SurveyContent
from trueconf.types.content.text import TextContent
from trueconf.types.content.voice import Voice
from trueconf.types.envelope_parser import deserialize_envelope
from trueconf.types.last_message import LastMessage
from trueconf.types.message import Message
from trueconf.types.parser import parse_update


class FakeBot:
    me_id = "bot@example.com"


# Real payload captured from TrueConf Server (forwards of forwards).
_REAL_FORWARD_RAW = json.loads(
    '{"method":"sendMessage","type":1,"id":2,"payload":{'
    '"chat":{"chatId":"818f295b8c37f8a226c063ffcec63b4fcab88299","chatTitle":"baadzhi@team.trueconf.com","chatType":1},'
    '"chatId":"818f295b8c37f8a226c063ffcec63b4fcab88299",'
    '"messageId":"00f60c68-563a-45ab-9458-7cc1572eff91",'
    '"timestamp":1791364172317,'
    '"author":{"id":"baadzhi@team.trueconf.com","type":1},'
    '"box":{"id":4,"position":"0"},'
    '"type":201,'
    '"content":{'
    '"chat":{"chatType":1,"chatTitle":"Алексей Нахошкин","chatId":"254db5dd8d7900deecc9068c4f0f1f0ca8a6c9dd"},'
    '"chatId":"254db5dd8d7900deecc9068c4f0f1f0ca8a6c9dd",'
    '"messageId":"8717f0de-5e42-4d59-b208-bfc9a1a844dd",'
    '"author":{"id":"nakhoshkin@team.trueconf.com","type":1},'
    '"type":201,'
    '"timestamp":1791362942904,'
    '"content":{"text":"все, кайфы, пасиб","parseMode":"html"},'
    '"isEdited":false},'
    '"isEdited":false}}'
)["payload"]


def _forward_raw(inner_type: int, inner_content: dict) -> dict:
    """A forwarded message (type 201) whose content is the original's envelope."""
    return {
        "chat": {"chatId": "chat-1", "chatTitle": "Chat 1", "chatType": 1},
        "chatId": "chat-1",
        "messageId": "forward-envelope-1",
        "timestamp": 1_725_000_000,
        "author": {"id": "bob@example.com", "type": 1},
        "box": {"id": 5, "position": "0"},
        "type": 201,
        "isEdited": False,
        "content": {
            # The inner envelope of the forwarded original, without `box`.
            "chat": {"chatId": "chat-2", "chatTitle": "Source Chat", "chatType": 1},
            "chatId": "chat-2",
            "messageId": "original-1",
            "timestamp": 1_724_999_000,
            "author": {"id": "alice@example.com", "type": 1},
            "type": inner_type,
            "isEdited": False,
            "content": inner_content,
        },
    }


_CANONICAL_CONTENTS: list[tuple[int, dict, type]] = [
    (200, {"text": "оригинал", "parseMode": "html"}, TextContent),
    (202, {"name": "image.webp", "mimeType": "image/webp", "fileId": "8e75", "size": 37856}, AttachmentContent),
    (203, {"latitude": 47.227208, "longitude": 39.70418, "title": "Ростов-на-Дону"}, Location),
    (
        204,
        {
            "url": "https://video.example.net/webtools/survey?id=FVx",
            "title": "📊 Опрос",
            "path": "FVx",
            "description": "{{Survey}}",
            "buttonText": "{{Go to survey}}",
            "appVersion": 1,
            "secret": "xPlNHP1Okj",
            "alt": "📊 Опрос",
        },
        SurveyContent,
    ),
    (205, {"fileId": "voice-1", "size": 20277, "mimeType": "voice/m4a", "duration": 5043}, Voice),
]


# ── Canonical: forward of every content type ────────────────────────────


@pytest.mark.parametrize(("inner_type", "inner_content", "expected"), _CANONICAL_CONTENTS)
def test_forward_of_every_content_type(inner_type, inner_content, expected):
    msg = deserialize_envelope(_forward_raw(inner_type, inner_content))

    assert isinstance(msg, Message)
    assert msg.type is MessageType.FORWARDED_MESSAGE
    assert isinstance(msg.content, ForwardMessage)

    forwarded = msg.forwarded_message
    assert forwarded is not None
    assert MessageType(forwarded.type) is MessageType(inner_type)
    assert isinstance(forwarded.content, expected)


def test_forwarded_original_envelope_fields():
    msg = deserialize_envelope(_forward_raw(205, _CANONICAL_CONTENTS[4][1]))

    forwarded = msg.forwarded_message
    assert forwarded.message_id == "original-1"
    assert forwarded.author.id == "alice@example.com"
    assert forwarded.chat.chat_id == "chat-2"
    assert forwarded.chat.chat_title == "Source Chat"
    assert forwarded.box is None


def test_forwarded_chat_id_deprecated_property_still_works():
    msg = deserialize_envelope(_forward_raw(205, _CANONICAL_CONTENTS[4][1]))

    with pytest.warns(DeprecationWarning, match="chat_id is deprecated"):
        assert msg.forwarded_message.chat_id == "chat-2"


# ── Real payload: the server flattens forwards of forwards ──────────────


def test_real_forward_payload_parses():
    msg = deserialize_envelope(_REAL_FORWARD_RAW)

    assert isinstance(msg, Message)
    assert msg.type is MessageType.FORWARDED_MESSAGE
    assert isinstance(msg.content, ForwardMessage)


def test_real_payload_forwarded_fields():
    msg = deserialize_envelope(_REAL_FORWARD_RAW)

    forwarded = msg.forwarded_message
    assert forwarded.message_id == "8717f0de-5e42-4d59-b208-bfc9a1a844dd"
    assert forwarded.author.id == "nakhoshkin@team.trueconf.com"
    assert forwarded.chat.chat_title == "Алексей Нахошкин"


def test_real_payload_flattened_forward_content():
    # The forwarded original was itself a forward: the server flattens it,
    # so the inner envelope is marked with the forward's own type (201) and
    # carries the deepest original's flat content.
    msg = deserialize_envelope(_REAL_FORWARD_RAW)

    forwarded = msg.forwarded_message
    assert MessageType(forwarded.type) is MessageType.FORWARDED_MESSAGE
    assert isinstance(forwarded.content, TextContent)
    assert forwarded.content.text == "все, кайфы, пасиб"


def test_real_payload_box_is_none():
    msg = deserialize_envelope(_REAL_FORWARD_RAW)

    assert msg.forwarded_message.box is None


# ── Hypothetical: envelope form of the inner content ─────────────────────


def test_envelope_form_content_falls_back_to_message():
    # If the server ever nests a full envelope as the content (as the
    # `ForwardMessageContent` interface literally describes), the union
    # resolves it to a `Message` fallback.
    inner_envelope = _forward_raw(200, {"text": "глубокий оригинал", "parseMode": "html"})["content"]

    msg = deserialize_envelope(_forward_raw(201, inner_envelope))

    forwarded = msg.forwarded_message
    assert isinstance(forwarded.content, Message)
    assert isinstance(forwarded.content.content, TextContent)


# ── Voice shortcuts through a forward ───────────────────────────────────


def test_forwarded_voice_shortcut():
    msg = deserialize_envelope(_forward_raw(205, _CANONICAL_CONTENTS[4][1]))
    msg.bind(FakeBot())

    assert msg.forwarded_message.voice is not None
    assert msg.forwarded_message.voice.file_id == "voice-1"


def test_forwarded_voice_survives_parse_update():
    raw = {"method": "sendMessage", "type": 1, "id": 7, "payload": _forward_raw(205, _CANONICAL_CONTENTS[4][1])}

    data = parse_update(raw)
    data.bind(FakeBot())

    assert isinstance(data, Message)
    assert data.forwarded_message.voice.file_id == "voice-1"


# ── Binding ──────────────────────────────────────────────────────────────


def test_bind_reaches_forwarded_message():
    bot = FakeBot()
    msg = deserialize_envelope(_forward_raw(205, _CANONICAL_CONTENTS[4][1]))

    msg.bind(bot)

    assert msg.forwarded_message.bot is bot
    assert msg.forwarded_message.voice.bot is bot


def test_bind_reaches_nested_reply_message_inside_forward():
    bot = FakeBot()
    raw = _forward_raw(200, {"text": "оригинал", "parseMode": "html"})
    raw["content"]["replyMessageId"] = "reply-target-1"
    raw["content"]["replyMessage"] = {
        "chat": {"chatId": "chat-2", "chatTitle": "Source Chat", "chatType": 1},
        "chatId": "chat-2",
        "messageId": "reply-target-1",
        "timestamp": 1_724_998_000,
        "author": {"id": "alice@example.com", "type": 1},
        "type": 200,
        "isEdited": False,
        "content": {"text": "реплика", "parseMode": "html"},
    }

    msg = deserialize_envelope(raw)
    msg.bind(bot)

    forwarded = msg.forwarded_message
    assert forwarded.reply_message is not None
    assert forwarded.reply_message.message_id == "reply-target-1"
    assert forwarded.reply_message.bot is bot


def test_forwarded_message_none_for_plain_message():
    plain = {
        "chat": {"chatId": "chat-1", "chatTitle": "Chat 1", "chatType": 1},
        "chatId": "chat-1",
        "messageId": "m-1",
        "timestamp": 1_725_000_000,
        "author": {"id": "bob@example.com", "type": 1},
        "box": {"id": 5, "position": "0"},
        "type": 200,
        "isEdited": False,
        "content": {"text": "hi", "parseMode": "html"},
    }

    msg = deserialize_envelope(plain)

    assert isinstance(msg.content, TextContent)
    assert msg.forwarded_message is None


# ── GetChatHistory payload ──────────────────────────────────────────────
def test_get_chat_history_payload_omits_from_message_id_when_none():
    call = GetChatHistory(chat_id="chat-1", count=10)

    assert call.payload() == {"chatId": "chat-1", "count": 10}


def test_get_chat_history_payload_keeps_from_message_id_when_set():
    call = GetChatHistory(chat_id="chat-1", count=10, from_message_id="m-1")

    assert call.payload() == {"chatId": "chat-1", "count": 10, "fromMessageId": "m-1"}


# ── Examples from the official docs ─────────────────────────────────────


def test_docs_objects_forward_content_example():
    # https://trueconf.ru/docs/chatbot-connector/ru/objects/#ForwardMessageContent
    # Inner envelope: type 200, no `box`.
    msg = deserialize_envelope(
        {
            "chat": {"chatId": "chat-1", "chatTitle": "Chat 1", "chatType": 1},
            "messageId": "outer",
            "timestamp": 1,
            "author": {"id": "elisa@video.example.net", "type": 1},
            "box": {"id": 1, "position": "0"},
            "type": 201,
            "isEdited": False,
            "content": {
                "chat": {"chatId": "55f9", "chatTitle": "elisa@video.example.net", "chatType": 1},
                "messageId": "2969b905",
                "timestamp": 1790085027947,
                "author": {"id": "elisa@video.example.net", "type": 1},
                "type": 200,
                "content": {"text": "Пересланное сообщение", "parseMode": "html"},
                "isEdited": False,
            },
        }
    )

    forwarded = msg.forwarded_message
    assert isinstance(forwarded, ForwardMessage)
    assert MessageType(forwarded.type) is MessageType.PLAIN_MESSAGE
    assert isinstance(forwarded.content, TextContent)
    assert forwarded.content.text == "Пересланное сообщение"
    assert forwarded.box is None


def test_docs_objects_envelope_forward_example():
    # https://trueconf.ru/docs/chatbot-connector/ru/objects/#envelope-examples
    # Inner envelope: type 201 (a forwarded original) with the deepest flat text.
    msg = deserialize_envelope(
        {
            "chat": {"chatId": "c1", "chatTitle": "elisa@video.example.net", "chatType": 1},
            "chatId": "c1",
            "messageId": "03a9a955",
            "timestamp": 1790781149722,
            "author": {"id": "elisa@video.example.net", "type": 1},
            "box": {"id": 124, "position": "0"},
            "type": 201,
            "isEdited": False,
            "content": {
                "chat": {"chatType": 2, "chatTitle": "12", "chatId": "cc1f6a2f"},
                "chatId": "cc1f6a2f",
                "messageId": "2969b905",
                "author": {"id": "elisa@video.example.net", "type": 1},
                "type": 201,
                "timestamp": 1790085027947,
                "content": {"text": "как дела?", "parseMode": "html"},
                "isEdited": False,
            },
        }
    )

    forwarded = msg.forwarded_message
    assert isinstance(forwarded, ForwardMessage)
    assert forwarded.chat.chat_title == "12"
    assert isinstance(forwarded.content, TextContent)
    assert forwarded.content.text == "как дела?"


def test_docs_messages_forward_example_with_inner_box():
    # https://trueconf.ru/docs/chatbot-connector/ru/messages/#newForwardMessage
    # Inner envelope: type 202 (attachment) and, unlike the objects page, it
    # carries a `box`. (The published example omits the outer `chat`; we add it,
    # since `chat` is mandatory in the Envelope contract.)
    msg = deserialize_envelope(
        {
            "chat": {"chatId": "d0b99ed2", "chatTitle": "Group", "chatType": 2},
            "chatId": "d0b99ed2",
            "messageId": "b5feca9f",
            "timestamp": 1776460454738,
            "author": {"id": "echo_bot@video.example.net", "type": 1},
            "isEdited": False,
            "box": {"id": 14, "position": "0"},
            "type": 201,
            "content": {
                "chat": {"chatType": 2, "chatTitle": "Групповой чат", "chatId": "e2cf0a56"},
                "chatId": "e2cf0a56",
                "messageId": "73cc1e8b",
                "author": {"id": "echo_bot@video.example.net", "type": 1},
                "type": 202,
                "isEdited": False,
                "timestamp": 1776460454738,
                "content": {
                    "name": "bot.log",
                    "mimeType": "text/plain",
                    "fileId": "c324bb13",
                    "size": 186543,
                },
                "box": {"id": 14, "position": "0"},
            },
        }
    )

    forwarded = msg.forwarded_message
    assert MessageType(forwarded.type) is MessageType.ATTACHMENT
    assert isinstance(forwarded.content, AttachmentContent)
    assert forwarded.content.file_name == "bot.log"
    assert forwarded.box is not None
    assert forwarded.box.id == 14


def test_last_message_forward_does_not_raise():
    # Regression: lastMessage may itself be a forwarded message.
    last_message = {
        "messageId": "o",
        "timestamp": 1,
        "author": {"id": "bob@example.com", "type": 1},
        "type": 201,
        "chat": {"chatId": "c1", "chatTitle": "Chat", "chatType": 1},
        "content": {
            "chat": {"chatId": "c2", "chatTitle": "Source", "chatType": 1},
            "chatId": "c2",
            "messageId": "orig",
            "timestamp": 2,
            "author": {"id": "alice@example.com", "type": 1},
            "type": 205,
            "isEdited": False,
            "content": {"fileId": "voice-1", "size": 20277, "mimeType": "voice/m4a", "duration": 5043},
        },
    }

    parsed = LastMessage.from_dict(last_message)

    assert isinstance(parsed.content, ForwardMessage)
    assert isinstance(parsed.content.content, Voice)
