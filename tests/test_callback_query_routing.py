import pytest

from trueconf import BaseMiddleware, Dispatcher, F, Router
from trueconf.types import CallbackQuery
from trueconf.types.parser import parse_update

pytestmark = pytest.mark.anyio


@pytest.fixture
def anyio_backend():
    return "asyncio"


def _callback_update(command: str = "add_to_cart", custom_data: str | None = "item:42") -> dict:
    command_payload = {"type": "userCommand", "command": command}
    if custom_data is not None:
        command_payload["customData"] = custom_data
    return {
        "method": "command",
        "type": 1,
        "id": 42,
        "payload": {
            "commandSource": {"type": "inlineKeyboard"},
            "commandPayload": command_payload,
        },
    }


class RecordingMiddleware(BaseMiddleware):
    def __init__(self, name, calls):
        self.name = name
        self.calls = calls

    async def __call__(self, handler, event, data):
        self.calls.append(f"{self.name}:before")
        await handler(event, data)
        self.calls.append(f"{self.name}:after")


async def test_callback_query_handler_receives_command_event_not_message_handler():
    router = Router()
    received = []

    @router.message()
    async def handle_message(event):
        received.append(("message", event))

    @router.callback_query()
    async def handle_callback(callback):
        received.append(("callback", callback))

    event = parse_update(_callback_update())
    handled = await router._feed(event, {})

    assert handled is True
    assert received == [("callback", event)]
    assert isinstance(received[0][1], CallbackQuery)


async def test_callback_query_magic_filter_matches_command():
    router = Router()
    received = []

    @router.callback_query(F.command == "add_to_cart")
    async def handle_callback(callback):
        received.append(callback.command)

    ignored = await router._feed(parse_update(_callback_update("show_cart")), {})
    handled = await router._feed(parse_update(_callback_update("add_to_cart")), {})

    assert ignored is False
    assert handled is True
    assert received == ["add_to_cart"]


async def test_callback_query_callable_filters_inject_data_into_handler():
    router = Router()
    received = []

    def has_custom_data(callback):
        return callback.custom_data is not None

    async def unpack_item(callback):
        _, item_id = callback.custom_data.split(":")
        return {"item_id": int(item_id)}

    @router.callback_query(has_custom_data, unpack_item)
    async def handle_callback(callback, item_id):
        received.append((callback.command, item_id))

    handled = await router._feed(parse_update(_callback_update()), {})

    assert handled is True
    assert received == [("add_to_cart", 42)]


async def test_callback_query_runs_outer_and_inner_middleware_in_order():
    router = Router()
    calls = []
    router.outer_middleware(RecordingMiddleware("outer", calls))
    router.inner_middleware(RecordingMiddleware("inner", calls))

    @router.callback_query()
    async def handle_callback(callback):
        calls.append(f"handler:{callback.command}")

    handled = await router._feed(parse_update(_callback_update()), {})

    assert handled is True
    assert calls == [
        "outer:before",
        "inner:before",
        "handler:add_to_cart",
        "inner:after",
        "outer:after",
    ]


async def test_callback_query_reaches_each_independent_root_router():
    dispatcher = Dispatcher()
    first = Router()
    second = Router()
    dispatcher.include_router(first)
    dispatcher.include_router(second)
    received = []

    @first.callback_query()
    async def handle_first(callback):
        received.append(("first", callback.command))

    @second.callback_query()
    async def handle_second(callback):
        received.append(("second", callback.command))

    await dispatcher._feed_update(parse_update(_callback_update()), {})

    assert received == [
        ("first", "add_to_cart"),
        ("second", "add_to_cart"),
    ]


async def test_callback_query_falls_back_to_next_sibling_router():
    dispatcher = Dispatcher()
    root = Router()
    first_child = Router()
    second_child = Router()
    root.include_router(first_child)
    root.include_router(second_child)
    dispatcher.include_router(root)
    received = []

    @first_child.callback_query(F.command == "other")
    async def handle_first(callback):
        received.append(("first", callback.command))

    @second_child.callback_query(F.command == "add_to_cart")
    async def handle_second(callback):
        received.append(("second", callback.command))

    await dispatcher._feed_update(parse_update(_callback_update()), {})

    assert received == [("second", "add_to_cart")]


@pytest.mark.parametrize(
    ("allow_child_on_event", "expected"),
    [
        (False, ["parent"]),
        (True, ["parent", "child"]),
    ],
)
async def test_callback_query_child_propagation_is_configurable(allow_child_on_event, expected):
    dispatcher = Dispatcher()
    parent = Router(allow_child_on_event=allow_child_on_event)
    child = Router()
    parent.include_router(child)
    dispatcher.include_router(parent)
    received = []

    @parent.callback_query()
    async def handle_parent(callback):
        received.append("parent")

    @child.callback_query()
    async def handle_child(callback):
        received.append("child")

    await dispatcher._feed_update(parse_update(_callback_update()), {})

    assert received == expected


async def test_callback_query_stops_at_first_matching_sibling_router():
    dispatcher = Dispatcher()
    root = Router()
    first_child = Router()
    second_child = Router()
    root.include_router(first_child)
    root.include_router(second_child)
    dispatcher.include_router(root)
    received = []

    @first_child.callback_query()
    async def handle_first(callback):
        received.append("first")

    @second_child.callback_query()
    async def handle_second(callback):
        received.append("second")

    await dispatcher._feed_update(parse_update(_callback_update()), {})

    assert received == ["first"]
