from __future__ import annotations

import asyncio
import base64
import json
import threading
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

import pytest
import websockets

from trueconf import Bot, Dispatcher, Router
from trueconf.enums.message_type import MessageType
from trueconf.exceptions import WSConnectionError
from trueconf.types.system_message import SystemMessage

pytestmark = pytest.mark.anyio


@pytest.fixture
def anyio_backend():
    return "asyncio"


def make_token() -> str:
    def encode(value: dict) -> str:
        return base64.urlsafe_b64encode(json.dumps(value).encode()).decode().rstrip("=")

    return f"{encode({'alg': 'none'})}.{encode({'exp': int(time.time()) + 3600})}.signature"


class OAuthHandler(BaseHTTPRequestHandler):
    requests: list[str] = []

    def do_POST(self):
        type(self).requests.append(self.path)
        length = int(self.headers["Content-Length"])
        self.rfile.read(length)
        body = json.dumps({"access_token": make_token()}).encode()
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, _format, *_args):
        pass


class OAuth2Handler(BaseHTTPRequestHandler):
    requests: list[str] = []

    def do_POST(self):
        type(self).requests.append(self.path)
        length = int(self.headers["Content-Length"])
        self.rfile.read(length)
        if self.path == "/api/v4/oauth2/token":
            payload = {"access_token": "oauth-access-token", "expires_in": 3600}
        elif self.path == "/bridge/api/client/v1/auth/web_rest_api_token":
            payload = {"authorization_code": "auth-code-123", "expires_in": 1790175912634}
        elif self.path == "/bridge/api/client/v1/auth/token":
            payload = {"access_token": make_token(), "token_type": "JWT", "expires_in": 1792764433973}
        else:
            self.send_response(404)
            self.end_headers()
            return
        body = json.dumps(payload).encode()
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, _format, *_args):
        pass


def test_from_credentials_honors_http_and_custom_web_port():
    OAuthHandler.requests = []
    server = ThreadingHTTPServer(("127.0.0.1", 0), OAuthHandler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()

    try:
        bot = Bot.from_credentials(
            "127.0.0.1",
            "bot",
            "secret",
            https=False,
            web_port=server.server_port,
            timeout=0.5,
        )
    finally:
        server.shutdown()
        server.server_close()
        thread.join()

    assert OAuthHandler.requests == ["/bridge/api/client/v1/oauth/token"]
    assert bot.port == server.server_port
    assert bot.https is False


def test_from_oauth_honors_http_and_custom_web_port():
    OAuth2Handler.requests = []
    server = ThreadingHTTPServer(("127.0.0.1", 0), OAuth2Handler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()

    try:
        bot = Bot.from_oauth(
            "127.0.0.1",
            "elisa",
            "secret",
            "client-id-1",
            https=False,
            web_port=server.server_port,
            timeout=0.5,
        )
    finally:
        server.shutdown()
        server.server_close()
        thread.join()

    assert OAuth2Handler.requests == [
        "/api/v4/oauth2/token",
        "/bridge/api/client/v1/auth/web_rest_api_token",
        "/bridge/api/client/v1/auth/token",
    ]
    assert bot.port == server.server_port
    assert bot.https is False


def test_from_oauth_raises_runtime_error_when_token_missing(monkeypatch):
    monkeypatch.setattr(
        "trueconf.client.bot._get_auth_token_via_oauth",
        lambda *args, **kwargs: None,
    )

    with pytest.raises(RuntimeError, match="Failed to obtain token"):
        Bot.from_oauth("example.com", "elisa", "secret", "client-id-1", timeout=0.5)


class ContractBot(Bot):
    async def check_version(self):
        pass


class FakeWebSocket:
    def __init__(self):
        self.incoming: asyncio.Queue[str | None] = asyncio.Queue()
        self.closed = asyncio.Event()
        self.fail_requests = False
        self.ack_started = asyncio.Event()
        self.release_ack = asyncio.Event()
        self.ack_settled = asyncio.Event()

    async def send(self, raw: str):
        message = json.loads(raw)
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
        if message.get("method") == "getChatHistory":
            await self.incoming.put(
                json.dumps(
                    {
                        "type": 2,
                        "id": message["id"],
                        "payload": {
                            "count": 2,
                            "chatId": "chat-1",
                            "messages": [
                                {
                                    "messageId": "message-1",
                                    "chat": {
                                        "chatId": "chat-1",
                                        "chatTitle": "Chat 1",
                                        "chatType": 1,
                                    },
                                    "timestamp": 1_725_000_000,
                                    "replyMessageId": None,
                                    "isEdited": False,
                                    "type": 200,
                                    "author": {"id": "alice@example.com", "type": 1},
                                    "box": {"id": 1, "position": "incoming"},
                                    "content": {
                                        "text": '<a href="trueconf:bot@example.com">Bot</a>',
                                        "parseMode": "html",
                                    },
                                },
                                {
                                    "messageId": "message-2",
                                    "chat": {
                                        "chatId": "chat-1",
                                        "chatTitle": "Chat 1",
                                        "chatType": 1,
                                    },
                                    "timestamp": 1_725_000_001,
                                    "replyMessageId": None,
                                    "isEdited": False,
                                    "type": 200,
                                    "author": {"id": "alice@example.com", "type": 1},
                                    "box": {"id": 1, "position": "incoming"},
                                    "content": {
                                        "text": "plain message",
                                        "parseMode": "html",
                                    },
                                },
                            ],
                        },
                    }
                )
            )
            return
        if message == {"type": 2, "id": 9001}:
            self.ack_started.set()
            try:
                await self.release_ack.wait()
            finally:
                self.ack_settled.set()
            return
        if self.fail_requests:
            raise OSError("transport unavailable")

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
        timeout=0.01,
    )
    return bot, socket, router


async def start_authorized(bot: Bot) -> asyncio.Task:
    run_task = asyncio.create_task(bot.run(handle_signals=False))
    await asyncio.wait_for(bot.authorized_event.wait(), timeout=1)
    return run_task


async def test_external_run_cancellation_propagates(connected_bot):
    bot, _socket, _router = connected_bot
    run_task = await start_authorized(bot)

    run_task.cancel()

    with pytest.raises(asyncio.CancelledError):
        await run_task
    await bot.shutdown()


async def test_shutdown_settles_protocol_ack_work(connected_bot):
    bot, socket, _router = connected_bot
    run_task = await start_authorized(bot)
    await socket.incoming.put(json.dumps({"type": 1, "id": 9001, "method": "event"}))
    await asyncio.wait_for(socket.ack_started.wait(), timeout=1)

    await bot.shutdown()

    assert socket.ack_settled.is_set()
    await run_task


async def test_public_send_preserves_transport_failure(connected_bot):
    bot, socket, _router = connected_bot
    run_task = await start_authorized(bot)
    socket.fail_requests = True

    with pytest.raises(WSConnectionError) as caught:
        await bot.send_message("chat-id", "hello")

    assert isinstance(caught.value.__cause__, OSError)
    await bot.shutdown()
    await run_task


async def test_get_chat_history_messages_are_bound_to_bot(connected_bot):
    bot, _socket, _router = connected_bot
    run_task = await start_authorized(bot)

    response = await bot.get_chat_history("chat-1", count=2)

    assert response.messages[0].bot is bot
    assert response.messages[0].mention is True
    assert response.messages[1].bot is bot
    assert response.messages[1].mention is None
    await bot.shutdown()
    await run_task


async def test_native_voice_reaches_public_message_handler(connected_bot):
    bot, socket, router = connected_bot
    received = asyncio.get_running_loop().create_future()

    @router.message()
    async def handle(message):
        received.set_result(message)

    run_task = await start_authorized(bot)
    await socket.incoming.put(
        json.dumps(
            {
                "type": 1,
                "id": 9002,
                "method": "sendMessage",
                "payload": {
                    "messageId": "message-1",
                    "chatId": "chat-1",
                    "chat": {
                        "chatId": "chat-1",
                        "chatTitle": "Alice & Bot",
                        "chatType": 1,
                    },
                    "timestamp": 1_725_000_000,
                    "replyMessageId": "message-0",
                    "isEdited": False,
                    "type": 205,
                    "author": {"id": "alice@example.com", "type": 1},
                    "box": {"id": 42, "position": "incoming"},
                    "content": {
                        "fileId": "voice-file-1",
                        "size": 12_345,
                        "mimeType": "audio/ogg",
                        "duration": 7,
                    },
                },
            }
        )
    )

    message = await asyncio.wait_for(received, timeout=1)

    assert message.message_id == "message-1"
    assert message.reply_message_id == "message-0"
    assert message.author.id == "alice@example.com"
    assert message.voice.file_id == "voice-file-1"
    assert message.voice.file_size == 12_345
    assert message.voice.mime_type == "audio/ogg"
    assert message.voice.duration == 7
    assert message.voice.bot is bot
    await bot.shutdown()
    await run_task


async def test_system_envelope_reaches_public_system_message_handler(connected_bot):
    bot, socket, router = connected_bot
    received = asyncio.get_running_loop().create_future()

    @router.system_message()
    async def handle(message):
        received.set_result(message)

    run_task = await start_authorized(bot)
    await socket.incoming.put(
        json.dumps(
            {
                "type": 1,
                "id": 9003,
                "method": "sendMessage",
                "payload": {
                    "messageId": "system-1",
                    "chatId": "chat-1",
                    "chat": {"chatId": "chat-1", "chatTitle": "Chat 1", "chatType": 2},
                    "timestamp": 1_789_486_204_571,
                    "type": MessageType.CLEAR_CHAT_HISTORY.value,
                    "author": {"id": "alice@example.com", "type": 1},
                    "box": {"id": 16, "position": "0"},
                    "content": {"forAll": True},
                },
            }
        )
    )

    message = await asyncio.wait_for(received, timeout=1)

    assert isinstance(message, SystemMessage)
    assert message.content.for_all is True
    assert message.bot is bot
    await bot.shutdown()
    await run_task
