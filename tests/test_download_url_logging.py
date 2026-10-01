from __future__ import annotations

import logging
from types import SimpleNamespace

import httpx2
import pytest

from trueconf import loggers
from trueconf.client.bot import Bot
from trueconf.enums.file_ready_state import FileReadyState
from trueconf.utils._url import _sanitize_url_for_log

pytestmark = pytest.mark.anyio


@pytest.fixture
def anyio_backend():
    return "asyncio"


@pytest.fixture
def captured_chatbot_logs():
    records = []

    class _Handler(logging.Handler):
        def emit(self, record):
            records.append(record.getMessage())

    handler = _Handler()
    loggers.chatbot.addHandler(handler)
    try:
        yield records
    finally:
        loggers.chatbot.removeHandler(handler)


def test_sanitize_strips_token_query_and_fragment():
    url = "https://video.example.com/bridge/api/client/v1/files/abc?token=SUPERSECRET#frag"
    assert _sanitize_url_for_log(url) == ("https://video.example.com/bridge/api/client/v1/files/abc")


def test_sanitize_keeps_url_without_secrets():
    url = "https://video.example.com/files/file.bin"
    assert _sanitize_url_for_log(url) == url


def test_sanitize_handles_none():
    assert _sanitize_url_for_log(None) == ""


def _file_info(download_url, size=10, ready_state=FileReadyState.READY):
    return SimpleNamespace(
        size=size,
        ready_state=ready_state,
        name="file.bin",
        download_url=download_url,
    )


async def test_download_file_by_id_does_not_log_token(monkeypatch, captured_chatbot_logs):
    token = "SUPERSECRETTOKEN"
    bot = object.__new__(Bot)
    bot.max_in_memory_download_size = 1024

    async def get_file_info(_file_id):
        return _file_info(f"https://example.com/files/abc?token={token}")

    async def download(url, file_name, file_path):
        return b"payload"

    monkeypatch.setattr(bot, "get_file_info", get_file_info)
    monkeypatch.setattr(bot, "_Bot__download_file_from_server", download)

    result = await bot.download_file_by_id("file-id")

    assert result == b"payload"
    log_text = "\n".join(captured_chatbot_logs)
    assert token not in log_text
    assert "https://example.com/files/abc" in log_text


async def test_download_from_server_does_not_log_token(monkeypatch, captured_chatbot_logs):
    token = "SUPERSECRETTOKEN"
    url = f"https://example.com/files/abc?token={token}"

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

    monkeypatch.setattr(httpx2, "AsyncClient", lambda **kwargs: FakeClient())

    bot = object.__new__(Bot)
    bot.ssl_context = True
    bot.timeout = 5

    result = await bot._Bot__download_file_from_server(url, "file.bin")

    assert result == b"payload"
    log_text = "\n".join(captured_chatbot_logs)
    assert token not in log_text
    assert "https://example.com/files/abc" in log_text


async def test_download_from_server_saves_to_exact_file_path(monkeypatch, tmp_path):
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

    monkeypatch.setattr(httpx2, "AsyncClient", lambda **kwargs: FakeClient())

    bot = object.__new__(Bot)
    bot.ssl_context = True
    bot.timeout = 5
    file_path = tmp_path / "nested" / "custom-name.bin"

    result = await bot._Bot__download_file_from_server(
        "https://example.com/file.bin",
        "server-name.bin",
        file_path=file_path,
    )

    assert result == file_path
    assert file_path.read_bytes() == b"payload"
    assert not (file_path / "server-name.bin").exists()


async def test_download_error_does_not_log_token(monkeypatch, captured_chatbot_logs):
    token = "SUPERSECRETTOKEN"
    url = f"https://example.com/files/abc?token={token}"

    class FakeStream:
        async def __aenter__(self):
            raise Exception("boom")

        async def __aexit__(self, *exc):
            return False

    class FakeClient:
        def stream(self, method, url):
            return FakeStream()

        async def __aenter__(self):
            return self

        async def __aexit__(self, *exc):
            return False

    monkeypatch.setattr(httpx2, "AsyncClient", lambda **kwargs: FakeClient())

    bot = object.__new__(Bot)
    bot.ssl_context = True
    bot.timeout = 5

    result = await bot._Bot__download_file_from_server(url, "file.bin")

    assert result is None
    log_text = "\n".join(captured_chatbot_logs)
    assert token not in log_text
    assert "Failed to download file from https://example.com/files/abc" in log_text
