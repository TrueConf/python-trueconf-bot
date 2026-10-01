from __future__ import annotations

import asyncio

import pytest

from trueconf.client.bot import Bot
from trueconf.client.session import WebSocketSession
from trueconf.dispatcher.router import Router

pytestmark = pytest.mark.anyio


@pytest.fixture
def anyio_backend():
    return "asyncio"


class Session:
    def __init__(self):
        self.closed = False

    async def close(self):
        self.closed = True


class WebSocket:
    def __init__(self):
        self.closed = False

    async def close(self):
        self.closed = True


def make_bot() -> Bot:
    bot = object.__new__(Bot)
    bot._stop = False
    bot._accept_updates = True
    bot._update_tasks = set()
    bot._protocol_tasks = set()
    bot._futures = {}
    bot._connect_task = None
    bot._session = None
    bot._ws = None
    bot.connected_event = asyncio.Event()
    bot.authorized_event = asyncio.Event()
    bot.stopped_event = asyncio.Event()
    return bot


async def test_websocket_session_close_closes_attached_socket():
    session = WebSocketSession()
    websocket = WebSocket()
    session.ws = websocket

    await session.close()

    assert websocket.closed
    assert session.ws is None


async def test_raw_message_task_is_tracked_until_update_finishes(monkeypatch):
    bot = make_bot()
    started = asyncio.Event()
    release = asyncio.Event()

    async def process_message(_bot, _data):
        started.set()
        await release.wait()

    monkeypatch.setattr(Bot, "_Bot__process_message", process_message)

    await bot._Bot__on_raw_message('{"type": 0}')
    await started.wait()

    assert len(bot._update_tasks) == 1

    release.set()
    await asyncio.wait(tuple(bot._update_tasks))
    await asyncio.sleep(0)

    assert not bot._update_tasks


async def test_raw_message_does_not_start_update_during_shutdown(monkeypatch):
    bot = make_bot()
    bot._accept_updates = False
    called = False

    async def process_message(_bot, _data):
        nonlocal called
        called = True

    monkeypatch.setattr(Bot, "_Bot__process_message", process_message)

    await bot._Bot__on_raw_message('{"type": 0}')
    await asyncio.sleep(0)

    assert not called
    assert not bot._update_tasks


async def test_router_waits_for_matched_handler():
    router = Router()
    started = asyncio.Event()
    release = asyncio.Event()

    @router._register(())
    async def handler(_event):
        started.set()
        await release.wait()

    feed_task = asyncio.create_task(router._feed(object(), {}))
    await started.wait()

    assert not feed_task.done()

    release.set()
    assert await feed_task is True


async def test_shutdown_waits_for_active_update_before_closing_connection():
    bot = make_bot()
    session = Session()
    bot._session = session
    release = asyncio.Event()

    async def update():
        await release.wait()
        assert not session.closed

    async def connection():
        await asyncio.Event().wait()

    update_task = asyncio.create_task(update())
    bot._update_tasks.add(update_task)
    bot._connect_task = asyncio.create_task(connection())

    shutdown_task = asyncio.create_task(bot.shutdown())
    await asyncio.sleep(0)

    assert not shutdown_task.done()
    assert not session.closed
    assert not bot._connect_task.cancelled()

    release.set()
    await shutdown_task

    assert session.closed
    assert bot.stopped_event.is_set()


async def test_handler_can_request_shutdown_without_waiting_for_itself():
    bot = make_bot()
    start_shutdown = asyncio.Event()

    async def update():
        await start_shutdown.wait()
        await bot.shutdown()

    update_task = asyncio.create_task(update())
    bot._update_tasks.add(update_task)
    start_shutdown.set()

    await asyncio.wait_for(update_task, timeout=1)

    assert bot.stopped_event.is_set()


async def test_external_timeout_does_not_cancel_active_update():
    bot = make_bot()
    session = Session()
    bot._session = session

    async def update():
        await asyncio.Event().wait()

    update_task = asyncio.create_task(update())
    bot._update_tasks.add(update_task)

    with pytest.raises(asyncio.TimeoutError):
        await asyncio.wait_for(bot.shutdown(), timeout=0.01)

    assert not update_task.cancelled()
    assert session.closed
    assert bot.stopped_event.is_set()

    update_task.cancel()
    with pytest.raises(asyncio.CancelledError):
        await update_task


async def test_shutdown_timeout_proceeds_without_cancelling_handlers():
    bot = make_bot()
    session = Session()
    bot._session = session

    async def update():
        await asyncio.Event().wait()

    update_task = asyncio.create_task(update())
    bot._update_tasks.add(update_task)

    await bot.shutdown(timeout=0.01)

    assert not update_task.cancelled()
    assert not update_task.done()
    assert session.closed
    assert bot.stopped_event.is_set()

    update_task.cancel()
    with pytest.raises(asyncio.CancelledError):
        await update_task


async def test_shutdown_timeout_waits_when_handlers_finish_in_time():
    bot = make_bot()
    session = Session()
    bot._session = session
    release = asyncio.Event()

    async def update():
        await release.wait()

    update_task = asyncio.create_task(update())
    bot._update_tasks.add(update_task)

    shutdown_task = asyncio.create_task(bot.shutdown(timeout=1))
    await asyncio.sleep(0)

    assert not shutdown_task.done()
    assert not session.closed

    release.set()
    await shutdown_task

    assert session.closed
    assert bot.stopped_event.is_set()


async def test_shutdown_default_waits_forever():
    bot = make_bot()
    session = Session()
    bot._session = session

    async def update():
        await asyncio.Event().wait()

    update_task = asyncio.create_task(update())
    bot._update_tasks.add(update_task)

    shutdown_task = asyncio.create_task(bot.shutdown())
    await asyncio.sleep(0)

    assert not shutdown_task.done()
    assert not session.closed

    update_task.cancel()
    with pytest.raises(asyncio.CancelledError):
        await update_task

    await shutdown_task

    assert session.closed
    assert bot.stopped_event.is_set()
