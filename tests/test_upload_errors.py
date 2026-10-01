from __future__ import annotations

from types import SimpleNamespace

import pytest

from trueconf.client.bot import Bot
from trueconf.exceptions import FileUploadError

pytestmark = pytest.mark.anyio


@pytest.fixture
def anyio_backend():
    return "asyncio"


class File:
    file_name = "file.txt"
    file_size = 4
    mime_type = "text/plain"

    async def read(self):
        return b"data"


class Response:
    def __init__(self, payload, error=None):
        self.payload = payload
        self.error = error

    async def __aenter__(self):
        return self

    async def __aexit__(self, *_args):
        return False

    def raise_for_status(self):
        if self.error:
            raise self.error

    async def json(self):
        return self.payload


class Session:
    def __init__(self, response):
        self.response = response

    async def __aenter__(self):
        return self

    async def __aexit__(self, *_args):
        return False

    def post(self, *_args, **_kwargs):
        return self.response


@pytest.fixture
def bot(monkeypatch):
    bot = object.__new__(Bot)
    bot.server = "example.com"
    bot.port = 443
    bot._protocol = "https"
    bot.ssl_context = None
    bot.timeout = 10

    async def create_upload_task(_self, _method):
        return SimpleNamespace(upload_task_id="task-id")

    monkeypatch.setattr(Bot, "__call__", create_upload_task)
    return bot


async def test_upload_returns_temporal_file_id(bot, monkeypatch):
    response = Response({"temporalFileId": "temporary-id"})
    monkeypatch.setattr("trueconf.client.bot.ClientSession", lambda **_kwargs: Session(response))

    result = await bot._Bot__upload_file_to_server(File())

    assert result == "temporary-id"


async def test_http_error_is_wrapped_and_preserved(bot, monkeypatch):
    error = RuntimeError("HTTP 500")
    response = Response({}, error=error)
    monkeypatch.setattr("trueconf.client.bot.ClientSession", lambda **_kwargs: Session(response))

    with pytest.raises(FileUploadError) as caught:
        await bot._Bot__upload_file_to_server(File())

    assert caught.value.__cause__ is error


async def test_missing_temporal_file_id_raises_typed_error(bot, monkeypatch):
    response = Response({})
    monkeypatch.setattr("trueconf.client.bot.ClientSession", lambda **_kwargs: Session(response))

    with pytest.raises(FileUploadError, match="temporalFileId") as caught:
        await bot._Bot__upload_file_to_server(File())

    assert caught.value.__cause__ is None
