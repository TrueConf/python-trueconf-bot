from trueconf.types.responses.send_file_response import SendFileResponse


def _raw(*, caption_message_id=None) -> dict:
    payload = {
        "chatId": "chat-1",
        "messageId": "file-message-1",
        "timestamp": 1_725_000_000,
        "fileId": "file-1",
    }
    if caption_message_id is not None:
        payload["captionMessageId"] = caption_message_id
    return payload


def test_send_file_response_with_caption_parses_caption_message_id():
    response = SendFileResponse.from_dict(_raw(caption_message_id="caption-message-1"))

    assert response.chat_id == "chat-1"
    assert response.message_id == "file-message-1"
    assert response.timestamp == 1_725_000_000
    assert response.file_id == "file-1"
    assert response.caption_message_id == "caption-message-1"


def test_send_file_response_without_caption_has_none_caption_message_id():
    response = SendFileResponse.from_dict(_raw())

    assert response.caption_message_id is None
    assert response.chat_id == "chat-1"
    assert response.message_id == "file-message-1"
    assert response.file_id == "file-1"


def test_send_file_response_round_trip_preserves_caption_message_id():
    response = SendFileResponse.from_dict(_raw(caption_message_id="caption-message-1"))

    serialized = response.to_dict()

    # `to_dict()` serializes by field name (snake_case), same as the other fields.
    assert serialized["caption_message_id"] == "caption-message-1"
