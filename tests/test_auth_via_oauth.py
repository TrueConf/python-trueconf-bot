import httpx2
import pytest

from trueconf.exceptions import InvalidGrantError, OAuthMissingScopeError
from trueconf.utils._auth._token import _get_auth_token_via_oauth
from trueconf.utils._user_agent import get_user_agent

STEP_1_URL = "https://example.com:443/api/v4/oauth2/token"
STEP_2_URL = "https://example.com:443/bridge/api/client/v1/auth/web_rest_api_token"
STEP_3_URL = "https://example.com:443/bridge/api/client/v1/auth/token"


class FakeResponse:
    def __init__(self, payload, status_code=200):
        self.payload = payload
        self.status_code = status_code
        self.request = httpx2.Request("POST", "https://example.com")

    def raise_for_status(self):
        if self.status_code >= 400:
            response = httpx2.Response(self.status_code, request=self.request)
            raise httpx2.HTTPStatusError(f"error {self.status_code}", request=self.request, response=response)

    def json(self):
        return self.payload


class FakeClient:
    instances: list = []
    responses: list = []

    def __init__(self, **kwargs):
        self.captured = []
        self.kwargs = kwargs
        type(self).instances.append(self)

    def __enter__(self):
        return self

    def __exit__(self, *_exc):
        return False

    def post(self, url, json=None):
        self.captured.append((url, json))
        return type(self).responses.pop(0)


def test_via_oauth_happy_path_uses_three_requests_in_order(monkeypatch):
    FakeClient.instances = []
    FakeClient.responses = [
        FakeResponse({"access_token": "oauth-access-token", "expires_in": 3600}),
        FakeResponse({"authorization_code": "auth-code-123", "expires_in": 1790175912634}),
        FakeResponse({"access_token": "jwt-value", "token_type": "JWT", "expires_in": 1792764433973}),
    ]
    monkeypatch.setattr("trueconf.utils._auth._token.Client", FakeClient)

    token = _get_auth_token_via_oauth("example.com", "elisa", "123tr", "client-id-1", ssl_context=True)

    fake = FakeClient.instances[0]
    assert token == "jwt-value"
    assert fake.captured == [
        (STEP_1_URL, {"client_id": "client-id-1", "grant_type": "password", "username": "elisa", "password": "123tr"}),
        (STEP_2_URL, {"client_id": "elisa", "token": "oauth-access-token"}),
        (STEP_3_URL, {"client_id": "user", "grant_type": "authorization_code", "code": "auth-code-123"}),
    ]
    assert fake.kwargs["headers"]["User-Agent"] == get_user_agent()


def test_via_oauth_returns_none_when_authorization_code_missing(monkeypatch):
    FakeClient.instances = []
    FakeClient.responses = [
        FakeResponse({"access_token": "oauth-access-token"}),
        FakeResponse({"expires_in": 1790175912634}),
    ]
    monkeypatch.setattr("trueconf.utils._auth._token.Client", FakeClient)

    assert _get_auth_token_via_oauth("example.com", "elisa", "123tr", "client-id-1", ssl_context=True) is None


def test_via_oauth_401_raises_invalid_grant(monkeypatch):
    FakeClient.instances = []
    FakeClient.responses = [FakeResponse({"error": "invalid_grant"}, status_code=401)]
    monkeypatch.setattr("trueconf.utils._auth._token.Client", FakeClient)

    with pytest.raises(InvalidGrantError):
        _get_auth_token_via_oauth("example.com", "elisa", "wrong", "client-id-1", ssl_context=True)


def test_via_oauth_connect_timeout_raises_connection_error(monkeypatch):
    FakeClient.instances = []
    FakeClient.responses = []

    class TimeoutClient(FakeClient):
        def post(self, url, json=None):
            raise httpx2.ConnectTimeout("boom")

    monkeypatch.setattr("trueconf.utils._auth._token.Client", TimeoutClient)

    with pytest.raises(ConnectionError, match="Server may be down or unreachable"):
        _get_auth_token_via_oauth("example.com", "elisa", "123tr", "client-id-1", ssl_context=True)


def test_via_oauth_400_invalid_scope_raises_oauth_missing_scope_error(monkeypatch):
    FakeClient.instances = []
    FakeClient.responses = [
        FakeResponse(
            {
                "error": {
                    "code": 400,
                    "message": "Bad Request",
                    "trace_id": "5034013532",
                    "errors": [{"reason": "invalidScope", "location": "scope"}],
                }
            },
            status_code=400,
        ),
    ]
    monkeypatch.setattr("trueconf.utils._auth._token.Client", FakeClient)

    with pytest.raises(OAuthMissingScopeError, match="scope"):
        _get_auth_token_via_oauth("example.com", "elisa", "123tr", "client-id-1", ssl_context=True)


def test_via_oauth_400_other_reason_re_raises_http_status_error(monkeypatch):
    FakeClient.instances = []
    FakeClient.responses = [
        FakeResponse(
            {"error": {"code": 400, "errors": [{"reason": "invalid_client"}]}},
            status_code=400,
        ),
    ]
    monkeypatch.setattr("trueconf.utils._auth._token.Client", FakeClient)

    with pytest.raises(httpx2.HTTPStatusError):
        _get_auth_token_via_oauth("example.com", "elisa", "123tr", "client-id-1", ssl_context=True)
