import base64
import json
from datetime import datetime
from functools import lru_cache
from typing import Optional

from httpx import AsyncClient, Client, HTTPStatusError

from ..exceptions import TokenValidationError, InvalidGrantError


def get_auth_token(
    server: str,
    username: str,
    password: str,
    verify: bool,
    *,
    protocol: str = "https",
    port: int = 443,
    timeout: float = 5.0,
) -> Optional[str]:
    url = f"{protocol}://{server}:{port}/bridge/api/client/v1/oauth/token"
    params = {
        "client_id": "chat_bot",
        "grant_type": "password",
        "username": username,
        "password": password,
    }
    with Client(timeout=timeout, verify=verify) as client:
        r = client.post(url, json=params)

        try:
            r.raise_for_status()
        except HTTPStatusError as e:
            if e.response.status_code == 401:
                if r.json().get("error_description", False):
                    raise InvalidGrantError("Invalid username or password!") from e
            else:
                raise

        return r.json().get("access_token", None)


@lru_cache()
def validate_token(token: str) -> bool:
    """
    Validate TrueConf Chatbot Connector token

    :param token:
    :return:
    """
    if not isinstance(token, str):
        message = (
            f"Token is invalid! It must be 'str' type instead of {type(token)} type."
        )
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
        message = f"Token is invalid!"
        raise TokenValidationError(message)

    return True
