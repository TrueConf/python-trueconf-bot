import base64
import json
from datetime import datetime
from functools import lru_cache

from httpx2 import Client, ConnectTimeout, HTTPStatusError

from ...exceptions import InvalidGrantError, OAuthMissingScopeError, PasswordAuthDisabledError, TokenValidationError
from .._ssl import SSLVerify
from .._user_agent import get_user_agent


def _get_auth_token(
    server: str,
    username: str,
    password: str,
    ssl_context: SSLVerify,
    *,
    protocol: str = "https",
    port: int = 443,
    timeout: float = 5.0,
) -> str | None:
    url = f"{protocol}://{server}:{port}/bridge/api/client/v1/oauth/token"
    params = {"client_id": "chat_bot", "grant_type": "password", "username": str(username), "password": str(password)}
    with Client(timeout=timeout, verify=ssl_context, headers={"User-Agent": get_user_agent()}) as client:
        try:
            r = client.post(url, json=params)
            r.raise_for_status()
        except ConnectTimeout:
            raise ConnectionError(f"Cannot connect to {server}:{port}. Server may be down or unreachable.") from None
        except HTTPStatusError as e:
            if e.response.status_code == 401:
                if r.json().get("error_description", False):
                    raise InvalidGrantError("Invalid username or password!") from e
            elif e.response.status_code == 403:
                try:
                    payload = r.json()
                except json.JSONDecodeError:
                    payload = {}
                if payload.get("error") == "auth_method_disabled":
                    raise PasswordAuthDisabledError() from e
            raise

        return r.json().get("access_token", None)


def _get_auth_token_via_oauth(
    server: str,
    username: str,
    password: str,
    client_id: str,
    ssl_context: SSLVerify,
    *,
    protocol: str = "https",
    port: int = 443,
    timeout: float = 5.0,
) -> str | None:
    base_url = f"{protocol}://{server}:{port}"
    with Client(timeout=timeout, verify=ssl_context, headers={"User-Agent": get_user_agent()}) as client:
        try:
            r1 = client.post(
                f"{base_url}/api/v4/oauth2/token",
                json={
                    "client_id": str(client_id),
                    "grant_type": "password",
                    "username": str(username),
                    "password": str(password),
                },
            )
            r1.raise_for_status()
            access_token = r1.json().get("access_token", None)
            if not access_token:
                return None

            r2 = client.post(
                f"{base_url}/bridge/api/client/v1/auth/web_rest_api_token",
                json={"client_id": str(username), "token": access_token},
            )
            r2.raise_for_status()
            authorization_code = r2.json().get("authorization_code", None)
            if not authorization_code:
                return None

            r3 = client.post(
                f"{base_url}/bridge/api/client/v1/auth/token",
                json={
                    "client_id": "user",
                    "grant_type": "authorization_code",
                    "code": authorization_code,
                },
            )
            r3.raise_for_status()
            return r3.json().get("access_token", None)
        except ConnectTimeout:
            raise ConnectionError(f"Cannot connect to {server}:{port}. Server may be down or unreachable.") from None
        except HTTPStatusError as e:
            if e.response.status_code == 401:
                raise InvalidGrantError("Invalid username, password or client_id!") from e
            elif e.response.status_code == 400:
                try:
                    payload = r1.json()
                except json.JSONDecodeError:
                    payload = {}
                if any(item.get("reason") == "invalidScope" for item in payload.get("error", {}).get("errors", [])):
                    raise OAuthMissingScopeError() from e
            raise


@lru_cache()
def _validate_token(token: str) -> bool:
    """
    Validate TrueConf Chatbot Connector token

    :param token:
    :return:
    """
    if not isinstance(token, str):
        message = f"Token is invalid! It must be 'str' type instead of {type(token)} type."
        raise TokenValidationError(message)

    if any(x.isspace() for x in token):
        message = "Token is invalid! It can't contains spaces."
        raise TokenValidationError(message)

    header_encoded, payload_encoded, signature = token.split(".")

    if (not header_encoded) or (not payload_encoded):
        message = f"Token is invalid! It can't contain any of the following characters: {token}"
        raise TokenValidationError(message)

    header_decoded = base64.urlsafe_b64decode(header_encoded + "==").decode("utf-8")
    payload_decoded = base64.urlsafe_b64decode(payload_encoded + "==").decode("utf-8")

    header = json.loads(header_decoded)
    payload = json.loads(payload_decoded)

    if int(datetime.now().timestamp()) > payload["exp"]:
        message = "Token is invalid!"
        raise TokenValidationError(message)

    return True
