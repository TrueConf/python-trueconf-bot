from __future__ import annotations

from inspect import signature
from pathlib import Path
from types import SimpleNamespace

import pytest

from trueconf.client.bot import Bot
from trueconf.enums.file_ready_state import FileReadyState
from trueconf.exceptions import InMemoryDownloadLimitExceededError

pytestmark = pytest.mark.anyio


@pytest.fixture
def anyio_backend():
    return "asyncio"


def info(size, ready_state=FileReadyState.READY):
    return SimpleNamespace(
        size=size,
        ready_state=ready_state,
        name="file.bin",
        download_url="https://example.com/file.bin",
    )


def test_default_in_memory_limit_is_100_mib():
    parameter = signature(Bot.__init__).parameters["max_in_memory_download_size"]
    assert parameter.default == 100 * 1024 * 1024


async def test_oversized_in_memory_download_is_rejected(monkeypatch):
    bot = object.__new__(Bot)
    bot.max_in_memory_download_size = 100

    async def get_file_info(_file_id):
        return info(101)

    monkeypatch.setattr(bot, "get_file_info", get_file_info)

    with pytest.raises(InMemoryDownloadLimitExceededError) as caught:
        await bot.download_file_by_id("file-id")

    assert caught.value.actual_value == 101
    assert caught.value.limit == 100


async def test_disk_download_is_not_limited(monkeypatch):
    bot = object.__new__(Bot)
    bot.max_in_memory_download_size = 100

    async def get_file_info(_file_id):
        return info(101)

    async def download(url, file_name, file_path):
        assert url == "https://example.com/file.bin"
        assert file_name == "file.bin"
        assert file_path == Path("downloads/file.bin")
        return "downloads/file.bin"

    monkeypatch.setattr(bot, "get_file_info", get_file_info)
    monkeypatch.setattr(bot, "_Bot__download_file_from_server", download)

    with pytest.warns(DeprecationWarning, match="dest_path.*deprecated"):
        result = await bot.download_file_by_id("file-id", dest_path="downloads")
    assert result == "downloads/file.bin"


async def test_file_path_is_exact_destination(monkeypatch):
    bot = object.__new__(Bot)
    bot.max_in_memory_download_size = 100

    async def get_file_info(_file_id):
        return info(101)

    async def download(url, file_name, file_path):
        assert url == "https://example.com/file.bin"
        assert file_name == "file.bin"
        assert file_path == Path("downloads/custom-name.bin")
        return file_path

    monkeypatch.setattr(bot, "get_file_info", get_file_info)
    monkeypatch.setattr(bot, "_Bot__download_file_from_server", download)

    result = await bot.download_file_by_id("file-id", file_path="downloads/custom-name.bin")
    assert result == Path("downloads/custom-name.bin")


async def test_positional_dest_path_remains_a_deprecated_directory(monkeypatch):
    bot = object.__new__(Bot)
    bot.max_in_memory_download_size = 100

    async def get_file_info(_file_id):
        return info(101)

    async def download(url, file_name, file_path):
        return file_path

    monkeypatch.setattr(bot, "get_file_info", get_file_info)
    monkeypatch.setattr(bot, "_Bot__download_file_from_server", download)

    with pytest.warns(DeprecationWarning, match="dest_path.*deprecated"):
        result = await bot.download_file_by_id("file-id", "downloads")

    assert result == Path("downloads/file.bin")


async def test_destination_parameters_are_mutually_exclusive(monkeypatch):
    bot = object.__new__(Bot)

    async def get_file_info(_file_id):
        pytest.fail("get_file_info must not be called for invalid arguments")

    monkeypatch.setattr(bot, "get_file_info", get_file_info)

    with pytest.raises(ValueError, match="only one destination parameter"):
        await bot.download_file_by_id("file-id", dest_path="downloads", file_path="downloads/file.bin")


async def test_limit_uses_file_info_after_upload_completes(monkeypatch):
    bot = object.__new__(Bot)
    bot.max_in_memory_download_size = 100
    states = iter(
        [
            info(50, FileReadyState.UPLOADING),
            info(101),
        ]
    )

    async def get_file_info(_file_id):
        return next(states)

    async def wait_upload_complete(_file_id, expected_size):
        assert expected_size == 50
        return True

    monkeypatch.setattr(bot, "get_file_info", get_file_info)
    monkeypatch.setattr(bot, "_Bot__wait_upload_complete", wait_upload_complete)

    with pytest.raises(InMemoryDownloadLimitExceededError):
        await bot.download_file_by_id("file-id")
