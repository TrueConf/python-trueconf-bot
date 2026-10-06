"""Smoke tests for the public httpx2 API surface used by trueconf.

The library depends on a specific subset of httpx2's public API. These tests
import every symbol the package relies on so that a future httpx2 release
removing or renaming any of them fails fast here instead of breaking user
code at runtime.
"""

import httpx2


def test_httpx2_minimum_version():
    assert tuple(int(part) for part in httpx2.__version__.split(".")[:2]) >= (2, 7)


def test_package_modules_import_httpx2():
    # Every trueconf module that touches httpx2 must import cleanly.
    import importlib

    for module_name in (
        "trueconf.types.input_file",
        "trueconf.utils._auth._token",
        "trueconf.client.bot",
    ):
        importlib.import_module(module_name)


def test_symbols_used_by_bot_module():
    # trueconf/client/bot.py uses these via `httpx2.<name>`
    for name in ("AsyncClient", "Timeout", "TimeoutException", "RequestError", "HTTPStatusError"):
        assert hasattr(httpx2, name), f"httpx2 is missing {name!r} required by trueconf.client.bot"


def test_symbols_used_by_auth_token():
    # trueconf/utils/_auth/_token.py imports these directly
    from httpx2 import Client, ConnectTimeout, HTTPStatusError  # noqa: F401


def test_symbols_used_by_input_file():
    # trueconf/types/input_file.py imports AsyncClient directly
    from httpx2 import AsyncClient  # noqa: F401


def test_client_constructor_signature():
    # Keywords used by trueconf when creating clients
    client = httpx2.Client(timeout=1.0, verify=True, headers={"User-Agent": "test"})
    try:
        assert client.timeout.read == 1.0
    finally:
        client.close()


def test_async_client_constructor_signature():
    client = httpx2.AsyncClient(timeout=httpx2.Timeout(5.0), verify=True, headers={"User-Agent": "test"})
    assert client.timeout.read == 5.0


def test_request_and_response_roundtrip():
    request = httpx2.Request("POST", "https://example.com")
    response = httpx2.Response(403, request=request)
    error = httpx2.HTTPStatusError("forbidden", request=request, response=response)
    assert error.response.status_code == 403
    assert isinstance(error, httpx2.RequestError) is False


def test_exception_hierarchy():
    # trueconf catches these exception types separately
    assert issubclass(httpx2.ConnectTimeout, httpx2.TimeoutException)
    assert issubclass(httpx2.TimeoutException, httpx2.RequestError)
    assert issubclass(httpx2.HTTPStatusError, httpx2.HTTPError)
