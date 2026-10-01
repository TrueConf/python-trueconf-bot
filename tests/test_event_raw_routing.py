import pytest

from trueconf import Dispatcher, Router
from trueconf.types import CallbackQuery, Update
from trueconf.types.parser import parse_update

pytestmark = pytest.mark.anyio


@pytest.fixture
def anyio_backend():
    return "asyncio"


def _command_update():
    return {
        "type": 1,
        "id": 42,
        "method": "command",
        "payload": {
            "commandSource": {"type": "inlineKeyboard"},
            "commandPayload": {"type": "userCommand", "command": "btn:simple"},
        },
    }


async def test_event_method_command_gets_raw_update_and_callback_query_fires():
    dp = Dispatcher()
    raw_router = Router()
    cb_router = Router()
    dp.include_router(raw_router)
    dp.include_router(cb_router)
    raw_received, cb_received = [], []

    @raw_router.event(method="command")
    async def raw_handler(event):
        raw_received.append(event)

    @cb_router.callback_query()
    async def cb_handler(cb: CallbackQuery):
        cb_received.append(cb)

    raw_dict = _command_update()
    typed = parse_update(raw_dict)

    await dp._feed_update(typed, {"bot": object(), "update": Update.from_dict(raw_dict)})

    assert len(raw_received) == 1
    assert isinstance(raw_received[0], Update)
    assert raw_received[0].method == "command"
    assert raw_received[0].payload["commandPayload"]["command"] == "btn:simple"
    assert len(cb_received) == 1
    assert isinstance(cb_received[0], CallbackQuery)


async def test_event_catch_all_matches_without_method():
    dp = Dispatcher()
    r = Router()
    dp.include_router(r)
    received = []

    @r.event()
    async def raw_all(event):
        received.append(event.method)

    raw_dict = _command_update()
    await dp._feed_update(parse_update(raw_dict), {"bot": object(), "update": Update.from_dict(raw_dict)})

    assert received == ["command"]


async def test_event_method_filter_ignores_other_methods():
    dp = Dispatcher()
    r = Router()
    dp.include_router(r)
    received = []

    @r.event(method="command")
    async def raw_handler(event):
        received.append(event)

    send_message = {"type": 1, "id": 7, "method": "sendMessage", "payload": {}}
    await dp._feed_update(None, {"bot": object(), "update": Update.from_dict(send_message)})

    assert received == []
