from __future__ import annotations

import asyncio

import pytest
import websockets
from websockets.exceptions import InvalidURI

from trueconf.client.bot import Bot
from trueconf.exceptions import TrueConfChatBotError, WSConnectionError

pytestmark = pytest.mark.anyio


@pytest.fixture
def anyio_backend():
    return "asyncio"


def make_bot(*, max_retries: int = 2, max_delay: float = 1.5) -> Bot:
    bot = object.__new__(Bot)
    bot.https = False
    bot.server = "example.com"
    bot.port = 4309
    bot._ws_max_retries = max_retries
    bot._ws_max_delay = max_delay
    bot._stop = False
    bot._session = None
    bot._ws = None
    bot.connected_event = asyncio.Event()
    bot.authorized_event = asyncio.Event()
    return bot


class FailingConnection:
    def __init__(self, error: Exception):
        self.error = error

    async def __aenter__(self):
        raise self.error

    async def __aexit__(self, exc_type, exc_value, traceback):
        return False


@pytest.mark.parametrize(
    "error, expected_detail",
    [
        (OSError("network unavailable"), "network unavailable"),
        (InvalidURI("ws://example.com", "invalid URI"), "invalid URI"),
    ],
)
async def test_connection_retries_are_exhausted_at_configured_limit(
    monkeypatch,
    error,
    expected_detail,
):
    bot = make_bot()
    connect_calls = 0
    sleep_delays = []

    def connect(**_kwargs):
        nonlocal connect_calls
        connect_calls += 1
        return FailingConnection(error)

    async def sleep(delay):
        sleep_delays.append(delay)

    monkeypatch.setattr(websockets, "connect", connect)
    monkeypatch.setattr(asyncio, "sleep", sleep)
    monkeypatch.setattr("trueconf.client.bot.random.uniform", lambda _start, _end: 1)

    with pytest.raises(WSConnectionError) as caught:
        await bot._Bot__connect_and_listen()

    assert connect_calls == 2
    assert sleep_delays == [1.5]
    assert isinstance(caught.value, TrueConfChatBotError)
    assert isinstance(caught.value, ConnectionError)
    assert caught.value.__cause__ is error
    assert "Failed to connect to ws://example.com:4309 after 2 attempts" in str(caught.value)
    assert expected_detail in str(caught.value)


def test_websocket_retry_settings_are_validated_before_use(monkeypatch):
    monkeypatch.setattr("trueconf.client.bot._validate_token", lambda _token: True)

    with pytest.raises(ValueError, match="ws_max_retries"):
        Bot("example.com", "token", ws_max_retries=0)

    with pytest.raises(ValueError, match="ws_max_delay"):
        Bot("example.com", "token", ws_max_delay=0)
