from __future__ import annotations

import pytest

from trueconf.enums.message_type import MessageType
from trueconf.types.content.clear_chat_history import ClearChatHistoryContent
from trueconf.types.content.parser import UnsupportedMessageType
from trueconf.types.content.remove_participant import RemoveParticipant
from trueconf.types.content.text import TextContent
from trueconf.types.last_message import LastMessage
from trueconf.types.responses.get_chat_by_id_response import GetChatByIdResponse
from trueconf.types.responses.get_chats_response import GetChatsResponse


def _last_message(message_type: int, content: dict) -> dict:
    return {
        "messageId": "last-1",
        "timestamp": 1_789_486_204_571,
        "author": {"id": "trueconf.server", "type": 0},
        "type": message_type,
        "content": content,
        "chat": {"chatId": "chat-1", "chatTitle": "Chat 1", "chatType": 1},
    }


def _chat(raw_last_message: dict | None) -> dict:
    return {
        "title": "Chat 1",
        "chatId": "chat-1",
        "chatTitle": "Chat 1",
        "chatType": 2,
        "unreadMessages": 0,
        "lastMessage": raw_last_message,
    }


def test_cleared_chat_history_last_message_parses():
    message = LastMessage.from_dict(_last_message(MessageType.CLEAR_CHAT_HISTORY.value, {"forAll": True}))

    assert isinstance(message.content, ClearChatHistoryContent)
    assert message.content.for_all is True


def test_get_chats_survives_cleared_chat_history_last_message():
    response = GetChatsResponse.from_dict(
        {
            "chats": [
                _chat(
                    _last_message(
                        MessageType.PLAIN_MESSAGE.value,
                        {"text": "still here", "parseMode": "html"},
                    )
                ),
                _chat(
                    _last_message(
                        MessageType.CLEAR_CHAT_HISTORY.value,
                        {"forAll": True},
                    )
                ),
            ]
        }
    )

    assert len(response.chats) == 2
    assert isinstance(response.chats[0].last_message.content, TextContent)
    assert response.chats[0].last_message.text == "still here"
    assert isinstance(response.chats[1].last_message.content, ClearChatHistoryContent)
    assert response.chats[1].last_message.content.for_all is True


def test_get_chat_by_id_survives_cleared_chat_history_last_message():
    response = GetChatByIdResponse.from_dict(_chat(_last_message(23, {"forAll": True})))

    assert isinstance(response.last_message.content, ClearChatHistoryContent)


def test_text_last_message_still_parses():
    message = LastMessage.from_dict(_last_message(200, {"text": "hi", "parseMode": "html"}))

    assert isinstance(message.content, TextContent)
    assert message.text == "hi"


def test_remove_participant_last_message_parses():
    message = LastMessage.from_dict(_last_message(2, {"userId": "user@example.com"}))

    assert isinstance(message.content, RemoveParticipant)


def test_unknown_last_message_type_raises_unsupported():
    with pytest.raises(UnsupportedMessageType):
        LastMessage.from_dict(_last_message(999, {"foo": "bar"}))
