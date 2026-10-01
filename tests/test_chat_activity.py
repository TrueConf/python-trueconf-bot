from __future__ import annotations

import asyncio
import base64
import json
import time

import pytest
import websockets

from trueconf import Bot, Dispatcher, Router
from trueconf.enums import ChatActivity
from trueconf.exceptions import ApiErrorException
from trueconf.methods.send_chat_activity import SendChatActivity
from trueconf.types.responses.send_chat_activity_response import (
    SendChatActivityResponse,
)
from trueconf.utils.chat_activity import ChatActivitySender

pytestmark = pytest.mark.anyio


@pytest.fixture
def anyio_backend():
    return "asyncio"


def make_token() -> str:
    def encode(value: dict) -> str:
        return base64.urlsafe_b64encode(json.dumps(value).encode()).decode().rstrip("=")

    return f"{encode({'alg': 'none'})}.{encode({'exp': int(time.time()) + 3600})}.signature"


class FakeWebSocket:
    def __init__(self):
        self.incoming: asyncio.Queue[str | None] = asyncio.Queue()
        self.closed = asyncio.Event()
        self.sent: list[dict] = []
        self.retry_after_ms: int = 0
        self.error_code: int = 0

    async def send(self, raw: str):
        message = json.loads(raw)
        self.sent.append(message)
        if message.get("method") == "auth":
            await self.incoming.put(
                json.dumps(
                    {
                        "type": 2,
                        "id": message["id"],
                        "payload": {
                            "userId": "bot@example.com",
                            "connectionId": "connection-1",
                        },
                    }
                )
            )
            return
        if self.error_code:
            await self.incoming.put(
                json.dumps(
                    {
                        "type": 2,
                        "id": message["id"],
                        "payload": {"errorCode": self.error_code},
                    }
                )
            )
            return
        await self.incoming.put(
            json.dumps(
                {
                    "type": 2,
                    "id": message["id"],
                    "payload": {
                        "chatId": message["payload"]["chatId"],
                        "activityType": message["payload"]["activityType"],
                        "retryAfter": self.retry_after_ms,
                    },
                }
            )
        )

    async def wait_closed(self):
        await self.closed.wait()

    async def close(self):
        self.closed.set()
        await self.incoming.put(None)

    def __aiter__(self):
        return self

    async def __anext__(self):
        item = await self.incoming.get()
        if item is None:
            raise StopAsyncIteration
        return item


class FakeConnection:
    def __init__(self, socket: FakeWebSocket):
        self.socket = socket

    async def __aenter__(self):
        return self.socket

    async def __aexit__(self, _exc_type, _exc_value, _traceback):
        await self.socket.close()


class ContractBot(Bot):
    async def check_version(self):
        pass


@pytest.fixture
def connected_bot(monkeypatch):
    socket = FakeWebSocket()
    monkeypatch.setattr(websockets, "connect", lambda **_kwargs: FakeConnection(socket))
    dispatcher = Dispatcher()
    router = Router()
    dispatcher.include_router(router)
    bot = ContractBot(
        "example.com",
        make_token(),
        dispatcher=dispatcher,
        https=False,
        timeout=0.1,
    )
    return bot, socket, router


async def start_authorized(bot: Bot) -> asyncio.Task:
    run_task = asyncio.create_task(bot.run(handle_signals=False))
    await asyncio.wait_for(bot.authorized_event.wait(), timeout=1)
    return run_task


def test_send_chat_activity_payload():
    call = SendChatActivity(chat_id="chat-1", activity_type=ChatActivity.TYPING)

    assert call.__api_method__ == "sendChatActivity"
    assert call.payload() == {
        "chatId": "chat-1",
        "activityType": "typing",
    }


async def test_send_chat_activity_through_bot(connected_bot):
    bot, socket, _router = connected_bot
    socket.retry_after_ms = 6000
    run_task = await start_authorized(bot)

    result = await bot.send_chat_activity("chat-1", ChatActivity.UPLOADING_FILE)

    assert isinstance(result, SendChatActivityResponse)
    assert result.chat_id == "chat-1"
    assert result.activity_type == "uploading_file"
    assert result.retry_after == 6000
    activity_request = socket.sent[-1]
    assert activity_request["method"] == "sendChatActivity"
    assert activity_request["payload"] == {
        "chatId": "chat-1",
        "activityType": "uploading_file",
    }
    await bot.shutdown()
    await run_task


async def test_chat_activity_sender_sends_periodically(connected_bot):
    bot, socket, _router = connected_bot
    socket.retry_after_ms = 50
    run_task = await start_authorized(bot)

    async with ChatActivitySender.typing(bot=bot, chat_id="chat-1") as sender:
        assert sender.running
        await asyncio.sleep(0.16)

    assert not sender.running

    activity_requests = [m for m in socket.sent if m["method"] == "sendChatActivity"]
    assert len(activity_requests) >= 2
    assert all(m["payload"] == {"chatId": "chat-1", "activityType": "typing"} for m in activity_requests)
    await bot.shutdown()
    await run_task


async def test_chat_activity_sender_respects_retry_after(connected_bot):
    bot, socket, _router = connected_bot
    socket.retry_after_ms = 2000
    run_task = await start_authorized(bot)

    async with ChatActivitySender.typing(bot=bot, chat_id="chat-1") as sender:
        assert sender.running
        await asyncio.sleep(0.12)

    assert not sender.running

    activity_requests = [m for m in socket.sent if m["method"] == "sendChatActivity"]
    assert len(activity_requests) == 1
    await bot.shutdown()
    await run_task


async def test_chat_activity_sender_clears_running_after_worker_crash(connected_bot):
    bot, socket, _router = connected_bot
    socket.error_code = 399
    run_task = await start_authorized(bot)

    sender = ChatActivitySender.typing(bot=bot, chat_id="chat-1", initial_sleep=0.05)
    await sender._run()
    assert sender.running
    task = sender._task
    assert task is not None

    for _ in range(100):
        if not sender.running:
            break
        await asyncio.sleep(0.01)
    assert not sender.running, "running stayed True after worker died"

    assert task.done()
    error = task.exception()
    assert isinstance(error, ApiErrorException)
    assert error.code == 399

    await sender._stop()
    await bot.shutdown()
    await run_task
