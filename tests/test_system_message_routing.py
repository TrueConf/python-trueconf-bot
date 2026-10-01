import pytest

from trueconf import F, Router, SkipSelfMessages
from trueconf.enums.message_type import MessageType
from trueconf.types.parser import parse_update
from trueconf.types.system_message import SystemMessage

pytestmark = pytest.mark.anyio


@pytest.fixture
def anyio_backend():
    return "asyncio"


def _clear_history_update() -> dict:
    return {
        "method": "sendMessage",
        "type": 1,
        "id": 5,
        "payload": {
            "chat": {"chatId": "chat-1", "chatTitle": "Chat 1", "chatType": 2},
            "messageId": "system-1",
            "timestamp": 1_789_486_204_571,
            "author": {"id": "bot@example.com", "type": 1},
            "box": {"id": 16, "position": "0"},
            "type": MessageType.CLEAR_CHAT_HISTORY.value,
            "content": {"forAll": True},
        },
    }


async def test_system_message_handler_receives_system_envelope_not_message_handler():
    router = Router()
    received = []

    @router.message()
    async def handle_message(message):
        received.append(("message", message))

    @router.system_message(F.type == MessageType.CLEAR_CHAT_HISTORY)
    async def handle_system_message(message):
        received.append(("system", message))

    event = parse_update(_clear_history_update())
    handled = await router._feed(event, {})

    assert handled is True
    assert len(received) == 1
    assert received[0][0] == "system"
    assert isinstance(received[0][1], SystemMessage)


async def test_skip_self_messages_does_not_drop_system_message():
    event = parse_update(_clear_history_update())
    middleware = SkipSelfMessages()
    received = []

    async def handler(message, data):
        received.append(message)

    class Bot:
        me_id = "bot@example.com"

    await middleware(handler, event, {"bot": Bot()})

    assert received == [event]
