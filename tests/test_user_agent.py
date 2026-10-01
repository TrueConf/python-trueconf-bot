from __future__ import annotations

import asyncio
import json
import re
from types import SimpleNamespace

import httpx2
import pytest
import websockets

from trueconf import _version
from trueconf.client.bot import Bot
from trueconf.exceptions import PasswordAuthDisabledError, WSConnectionError
from trueconf.types.input_file import URLInputFile
from trueconf.utils._auth._token import _get_auth_token
from trueconf.utils._user_agent import get_user_agent

pytestmark = pytest.mark.anyio


@pytest.fixture
def anyio_backend():
    return "asyncio"


# ---------- get_user_agent() ----------


def test_user_agent_matches_expected_format():
    ua = get_user_agent()
    assert re.match(r"^python-trueconf-bot/\d+\.\d+\.\d+(\.dev\d+)? \(Python/\d+\.\d+(\.\d+)?; [^)]+\)$", ua)


def test_user_agent_falls_back_to_generated_version(monkeypatch):
    import importlib.metadata as md

    def _raise(_name):
        raise md.PackageNotFoundError(_name)

    monkeypatch.setattr("trueconf.utils._user_agent.metadata.version", _raise)
    get_user_agent.cache_clear()
    try:
        ua = get_user_agent()
    finally:
        get_user_agent.cache_clear()

    assert ua.startswith(f"python-trueconf-bot/{_version.__version__} ")


# ---------- httpx2.AsyncClient in bot.py (file download) ----------


async def test_download_client_sends_user_agent(monkeypatch):
    captured = {}

    class FakeResponse:
        def raise_for_status(self):
            pass

        async def aiter_bytes(self):
            yield b"payload"

    class FakeStream:
        async def __aenter__(self):
            return FakeResponse()

        async def __aexit__(self, *exc):
            return False

    class FakeClient:
        def stream(self, method, url):
            return FakeStream()

        async def __aenter__(self):
            return self

        async def __aexit__(self, *exc):
            return False

    def factory(**kwargs):
        captured.update(kwargs)
        return FakeClient()

    monkeypatch.setattr(httpx2, "AsyncClient", factory)

    bot = object.__new__(Bot)
    bot.ssl_context = True
    bot.timeout = 5

    await bot._Bot__download_file_from_server("https://example.com/file.bin", "file.bin")

    assert captured["headers"]["User-Agent"] == get_user_agent()


# ---------- aiohttp.ClientSession in bot.py (file upload) ----------


class _File:
    file_name = "file.txt"
    file_size = 4
    mime_type = "text/plain"

    async def read(self):
        return b"data"


class _Response:
    def __init__(self, payload):
        self.payload = payload

    async def __aenter__(self):
        return self

    async def __aexit__(self, *_args):
        return False

    def raise_for_status(self):
        pass

    async def json(self):
        return self.payload


class _Session:
    def __init__(self, response):
        self.response = response

    async def __aenter__(self):
        return self

    async def __aexit__(self, *_args):
        return False

    def post(self, *_args, **_kwargs):
        return self.response


async def test_upload_client_sends_user_agent(monkeypatch):
    captured = {}

    def factory(**kwargs):
        captured.update(kwargs)
        return _Session(_Response({"temporalFileId": "temporary-id"}))

    monkeypatch.setattr("trueconf.client.bot.ClientSession", factory)

    bot = object.__new__(Bot)
    bot.server = "example.com"
    bot.port = 443
    bot._protocol = "https"
    bot.ssl_context = None
    bot.timeout = 10

    async def create_upload_task(_self, _method):
        return SimpleNamespace(upload_task_id="task-id")

    monkeypatch.setattr(Bot, "__call__", create_upload_task)

    result = await bot._Bot__upload_file_to_server(_File())

    assert result == "temporary-id"
    assert captured["headers"]["User-Agent"] == get_user_agent()


# ---------- websockets.connect (WS handshake) ----------


async def test_websocket_connect_sends_user_agent(monkeypatch):
    captured = {}

    def connect(**kwargs):
        captured.update(kwargs)
        raise OSError("network unavailable")

    monkeypatch.setattr(websockets, "connect", connect)

    bot = object.__new__(Bot)
    bot.https = False
    bot.server = "example.com"
    bot.port = 4309
    bot._ws_max_retries = 1
    bot._ws_max_delay = 1
    bot._stop = False
    bot._session = None
    bot._ws = None
    bot.connected_event = asyncio.Event()
    bot.authorized_event = asyncio.Event()

    with pytest.raises(WSConnectionError):
        await bot._Bot__connect_and_listen()

    assert captured["user_agent_header"] == get_user_agent()


# ---------- httpx2.Client (sync) in _token.py ----------


def test_auth_token_client_sends_user_agent(monkeypatch):
    captured = {}

    class FakeResponse:
        def raise_for_status(self):
            pass

        def json(self):
            return {"access_token": "token-value"}

    class FakeClient:
        def __init__(self, **kwargs):
            captured.update(kwargs)

        def __enter__(self):
            return self

        def __exit__(self, *_exc):
            return False

        def post(self, *_args, **_kwargs):
            return FakeResponse()

    monkeypatch.setattr("trueconf.utils._auth._token.Client", FakeClient)

    token = _get_auth_token("example.com", "user", "pass", ssl_context=True)

    assert token == "token-value"
    assert captured["headers"]["User-Agent"] == get_user_agent()


def test_auth_token_403_auth_method_disabled_raises_password_auth_disabled(monkeypatch):
    class FakeResponse:
        def __init__(self):
            self.request = httpx2.Request("POST", "https://example.com")

        def raise_for_status(self):
            raise httpx2.HTTPStatusError(
                "error 403",
                request=self.request,
                response=httpx2.Response(403, request=self.request),
            )

        def json(self):
            return {
                "error": "auth_method_disabled",
                "error_description": "Password-based authentication is disabled for the current authorization zone",
                "reason": "auth method disabled",
            }

    class FakeClient:
        def __init__(self, **kwargs):
            pass

        def __enter__(self):
            return self

        def __exit__(self, *_exc):
            return False

        def post(self, *_args, **_kwargs):
            return FakeResponse()

    monkeypatch.setattr("trueconf.utils._auth._token.Client", FakeClient)

    with pytest.raises(PasswordAuthDisabledError, match="from_oauth"):
        _get_auth_token("example.com", "user", "pass", ssl_context=True)


def test_auth_token_403_other_error_re_raises_http_status_error(monkeypatch):
    class FakeResponse:
        def __init__(self):
            self.request = httpx2.Request("POST", "https://example.com")

        def raise_for_status(self):
            raise httpx2.HTTPStatusError(
                "error 403",
                request=self.request,
                response=httpx2.Response(403, request=self.request),
            )

        def json(self):
            return {"error": "some_other_error"}

    class FakeClient:
        def __init__(self, **kwargs):
            pass

        def __enter__(self):
            return self

        def __exit__(self, *_exc):
            return False

        def post(self, *_args, **_kwargs):
            return FakeResponse()

    monkeypatch.setattr("trueconf.utils._auth._token.Client", FakeClient)

    with pytest.raises(httpx2.HTTPStatusError):
        _get_auth_token("example.com", "user", "pass", ssl_context=True)


def test_auth_token_403_non_json_body_re_raises_http_status_error(monkeypatch):
    class FakeResponse:
        def __init__(self):
            self.request = httpx2.Request("POST", "https://example.com")

        def raise_for_status(self):
            raise httpx2.HTTPStatusError(
                "error 403",
                request=self.request,
                response=httpx2.Response(403, request=self.request),
            )

        def json(self):
            raise json.JSONDecodeError("Expecting value", "<html>403</html>", 0)

    class FakeClient:
        def __init__(self, **kwargs):
            pass

        def __enter__(self):
            return self

        def __exit__(self, *_exc):
            return False

        def post(self, *_args, **_kwargs):
            return FakeResponse()

    monkeypatch.setattr("trueconf.utils._auth._token.Client", FakeClient)

    with pytest.raises(httpx2.HTTPStatusError):
        _get_auth_token("example.com", "user", "pass", ssl_context=True)


# ---------- httpx2.AsyncClient in URLInputFile ----------


def test_url_input_file_constructs_without_file_name():
    # Regression: InputFile.__init__ crashed with TypeError when file_name is
    # None (guess_type(None) / Path(None)) — URLInputFile resolves the name
    # later in prepare(), so file_name must be allowed to stay None.
    f = URLInputFile("https://example.com/file.bin")

    assert f.file_name is None
    assert f.extension == ""


class _FakeUrlResponse:
    headers = {"Content-Length": "10", "Content-Type": "text/plain"}

    async def aiter_bytes(self):
        yield b"data"


class _FakeUrlStream:
    async def __aenter__(self):
        return _FakeUrlResponse()

    async def __aexit__(self, *_exc):
        return False


class _FakeUrlClient:
    def __init__(self, **kwargs):
        self.kwargs = kwargs

    def stream(self, *_args, **_kwargs):
        return _FakeUrlStream()

    async def __aenter__(self):
        return self

    async def __aexit__(self, *_exc):
        return False


async def test_url_input_file_sends_library_user_agent(monkeypatch):
    fake_client = _FakeUrlClient()

    def factory(**kwargs):
        fake_client.kwargs = kwargs
        return fake_client

    monkeypatch.setattr("trueconf.types.input_file.AsyncClient", factory)

    f = URLInputFile("https://example.com/file.bin")
    await f.prepare()

    assert fake_client.kwargs["headers"]["User-Agent"] == get_user_agent()


async def test_url_input_file_respects_explicit_user_agent(monkeypatch):
    fake_client = _FakeUrlClient()

    def factory(**kwargs):
        fake_client.kwargs = kwargs
        return fake_client

    monkeypatch.setattr("trueconf.types.input_file.AsyncClient", factory)

    f = URLInputFile("https://example.com/file.bin", headers={"User-Agent": "custom-agent"})
    await f.prepare()

    assert fake_client.kwargs["headers"]["User-Agent"] == "custom-agent"
