from __future__ import annotations

import threading
from http.server import BaseHTTPRequestHandler, HTTPServer

import httpx2
import pytest

from trueconf.exceptions import FileSizeTooLargeError, FileUploadError
from trueconf.types.input_file import BufferedInputFile, FSInputFile, URLInputFile

pytestmark = pytest.mark.anyio

BODY = b"x" * 250
ERROR_BODY = b"<html>404 Not Found</html>"


@pytest.fixture
def anyio_backend():
    return "asyncio"


class _Handler(BaseHTTPRequestHandler):
    request_count = 0

    def log_message(self, *_args):  # keep test output clean
        return

    def do_HEAD(self):
        self._respond(head=True)

    def do_GET(self):
        self._respond(head=False)

    def _send_headers(self, content_type: str, content_length: int | None) -> None:
        self.send_response(200)
        self.send_header("Content-Type", content_type)
        if content_length is not None:
            self.send_header("Content-Length", str(content_length))
        self.end_headers()

    def _send_dynamic(self, head: bool) -> None:
        # A live source (e.g. a camera): a fresh image with a different size per request.
        size = 23_000 + _Handler.request_count
        body = b"z" * size
        self._send_headers("image/jpeg", len(body))
        if not head:
            self.wfile.write(body)

    def _send_missing(self, head: bool) -> None:
        self.send_response(404)
        self.send_header("Content-Type", "text/html")
        self.send_header("Content-Length", str(len(ERROR_BODY)))
        self.end_headers()
        if not head:
            self.wfile.write(ERROR_BODY)

    def _send_bodyless(self, content_type: str, body: bytes, head: bool) -> None:
        # No Content-Length: the response body ends when the connection closes.
        self._send_headers(content_type, None)
        if not head:
            self.wfile.write(body)

    def _send_file(self, head: bool) -> None:
        self._send_headers("image/png", len(BODY))
        if not head:
            self.wfile.write(BODY)

    def _respond(self, head: bool) -> None:
        _Handler.request_count += 1

        if self.path == "/dynamic":
            self._send_dynamic(head)
        elif self.path == "/redirect":
            self.send_response(302)
            self.send_header("Location", "/file")
            self.end_headers()
        elif self.path == "/missing":
            self._send_missing(head)
        elif self.path == "/nohead" and head:
            self.send_response(405)
            self.end_headers()
        elif self.path == "/big":
            self._send_bodyless("application/octet-stream", b"b" * 1000, head)
        elif self.path == "/chunked":
            self._send_bodyless("text/plain", b"y" * 100, head)
        else:
            # /file and /nohead (GET): a well-formed response with a known size.
            self._send_file(head)


@pytest.fixture
def server_url():
    _Handler.request_count = 0
    server = HTTPServer(("127.0.0.1", 0), _Handler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        yield f"http://127.0.0.1:{server.server_port}"
    finally:
        server.shutdown()
        thread.join()


async def test_prepare_resolves_metadata_for_direct_url(server_url):
    file = URLInputFile(f"{server_url}/file")

    await file.prepare()

    assert file.file_size == len(BODY)
    assert file.mime_type == "image/png"
    assert file.file_name == "file"


async def test_prepare_follows_redirect(server_url):
    # A redirecting URL must yield the metadata of the final resource.
    file = URLInputFile(f"{server_url}/redirect")

    await file.prepare()

    assert file.file_size == len(BODY)
    assert file.mime_type == "image/png"


async def test_prepare_keeps_explicit_size_without_content_length(server_url):
    # Caller-provided size must survive even without Content-Length.
    file = URLInputFile(f"{server_url}/chunked", file_size=100)

    await file.prepare()

    assert file.file_size == 100
    assert file.mime_type == "text/plain"


async def test_prepare_leaves_size_unknown_without_content_length(server_url):
    # Without Content-Length the size is unknown until read() measures the body.
    file = URLInputFile(f"{server_url}/chunked")

    await file.prepare()
    assert file.file_size is None

    data = await file.read()
    assert file.file_size == len(data) == 100


async def test_prepare_raises_on_http_error(server_url):
    # An error page must not be silently treated as the file.
    file = URLInputFile(f"{server_url}/missing")

    with pytest.raises(httpx2.HTTPStatusError):
        await file.prepare()


async def test_prepare_works_when_head_is_not_supported(server_url):
    # prepare() uses a GET, so servers rejecting HEAD still work.
    file = URLInputFile(f"{server_url}/nohead")

    await file.prepare()

    assert file.file_size == len(BODY)
    assert file.mime_type == "image/png"


async def test_read_matches_declared_size_for_dynamic_content(server_url):
    # Regression: a per-request source (camera) must declare the size of the uploaded body.
    file = URLInputFile(f"{server_url}/dynamic")

    await file.prepare()
    declared_hint = file.file_size

    data = await file.read()

    assert file.file_size == len(data)
    assert declared_hint is not None
    assert declared_hint != file.file_size


async def test_read_caches_content(server_url):
    file = URLInputFile(f"{server_url}/file")

    first = await file.read()
    second = await file.read()

    assert first == second == BODY
    assert _Handler.request_count == 1  # single download, second read served from cache


async def test_read_aborts_when_content_exceeds_max_size(server_url):
    file = URLInputFile(f"{server_url}/big")

    with pytest.raises(FileSizeTooLargeError):
        await file.read(max_size=10)


async def test_prepare_raises_when_name_cannot_be_resolved(server_url):
    # A URL without a file name in the path cannot produce valid metadata.
    file = URLInputFile(f"{server_url}/")

    with pytest.raises(FileUploadError, match="file name"):
        await file.prepare()


async def test_prepare_raises_for_missing_name_even_with_full_metadata(server_url):
    # The early-return path (explicit size + mime) must still guarantee a name.
    file = URLInputFile(f"{server_url}/", file_size=250, mime_type="image/png")

    with pytest.raises(FileUploadError, match="file name"):
        await file.prepare()

    assert _Handler.request_count == 0  # no network needed to detect the missing name


def test_buffered_input_file_rejects_empty_name():
    with pytest.raises(TypeError, match="file_name"):
        BufferedInputFile(file=b"data", file_name="")


def test_fs_input_file_rejects_path_without_name(tmp_path):
    with pytest.raises(ValueError, match="file name"):
        FSInputFile(f"{tmp_path}/", file_size=10, mime_type="text/plain")


def test_clone_preserves_metadata(server_url):
    file = URLInputFile(
        f"{server_url}/file",
        file_size=250,
        mime_type="image/png",
    )

    cloned = file.clone()

    assert cloned.file_size == 250
    assert cloned.mime_type == "image/png"
    assert cloned.file_name == file.file_name


async def test_clone_shares_downloaded_content(server_url):
    file = URLInputFile(f"{server_url}/file")
    cloned = file.clone()

    original_data = await file.read()
    clone_data = await cloned.read()

    assert clone_data == original_data == BODY
    assert _Handler.request_count == 1  # the clone must not download again
