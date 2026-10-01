---
title: Authentication
description: 'Bot authentication methods: token, login and password, and OAuth2'
icon: material/key
---

# Authentication

The library supports three ways to authenticate a bot on TrueConf Server:

| Method | API | When to use it |
| --- | --- | --- |
| Token | `Bot(server, token=...)` | You already have a token obtained manually or through the API |
| Login and password | `Bot.from_credentials(...)` | Login and password authentication is enabled on the server |
| OAuth2 | `Bot.from_oauth(...)` | Login and password authentication is disabled on the server |

## Token authentication

Obtain a token as described in the [official API documentation](https://trueconf.com/docs/chatbot-connector/en/connect-and-auth/#access-token).

We recommend storing the token in an environment variable or a `.env` file. If you use a public repository, remember to add `.env` to `.gitignore`.

```python
from os import getenv

TOKEN = getenv("TOKEN")
bot = Bot(server="video.example.com", token=TOKEN, dispatcher=dp)
```

!!! note
    A token is valid for one month from the time it is created.
    However, an authenticated connection remains active until it is closed, even after the token expires.
    In theory, such a connection can remain active for years.

## Login and password authentication

The `Bot.from_credentials()` method authenticates the bot with a login and password:

```python
bot = Bot.from_credentials(
    username="echo_bot",
    password="123tr",
    server="video.example.com",
    dispatcher=dp,
)
```

!!! info
    Every call to **from_credentials()** requests a new token from the server.
    Each token is valid for one month.

The main parameters after `password` are keyword-only:

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| `dispatcher` | `Dispatcher` | `None` | Dispatcher used to register handlers |
| `receive_unread_messages` | `bool` | `False` | Whether to receive messages that arrived while the bot was offline |
| `receive_system_messages` | `bool` | `False` | Whether to receive system messages |
| `skip_self_messages` | `bool` | `True` | Whether to ignore messages sent by the bot itself |
| `verify_ssl` | `bool | str | ssl.SSLContext` | `True` | SSL certificate verification settings |
| `https` | `bool` | `True` | Whether to use HTTPS |
| `web_port` | `int` | `None` | WebSocket port (`443` with HTTPS and `4309` without HTTPS by default) |
| `ws_max_retries` | `int` | `5` | Maximum number of connection attempts after network errors |
| `ws_max_delay` | `int` | `60` | Maximum delay between connection attempts, in seconds |
| `timeout` | `float | int` | `10.0` | Server response timeout |
| `on_health_check` | `Callable` | `None` | Callback invoked when the connection state changes |

For the complete parameter list, see the [`Bot.from_credentials()` reference](../reference/Bot.md/#trueconf.Bot.from_credentials).

If login and password authentication is disabled on the server, the method raises `PasswordAuthDisabledError`. Use `Bot.from_oauth()` instead.

## OAuth2 authentication

If login and password authentication is disabled on the server for security reasons, the bot cannot use `from_credentials()`. It does not support authentication through NTLM, Kerberos, other SSO protocols, or MFA.

In this case, create an OAuth application on the server and authenticate the bot with `Bot.from_oauth()`. In addition to the login and password, you need the application's `client_id`:

```python
bot = Bot.from_oauth(
    username="elisa",
    password="123tr",
    client_id="application_client_id",
    server="video.example.com",
    dispatcher=dp,
)
```

Requirements:

- TrueConf Server 5.5.3 or later;
- an OAuth application created on the server;
- at least one scope configured for the application. The `version:read` scope is sufficient and does not expose sensitive information. A token cannot be obtained for an application without a scope.

`Bot.from_oauth()` accepts the same parameters as `from_credentials()` and additionally requires `client_id`. See the [`Bot.from_oauth()` reference](../reference/Bot.md/#trueconf.Bot.from_oauth).

### Authentication errors

| Exception | When it occurs | What to do |
| --- | --- | --- |
| `PasswordAuthDisabledError` | The server rejects the token request with `403 auth_method_disabled` because login and password authentication is disabled | Use `Bot.from_oauth()` |
| `OAuthMissingScopeError` | The server rejects the OAuth token request with `400 invalidScope` because the OAuth application has no configured scope | Add a scope, such as `version:read`, to the application settings on the server |

Both exceptions inherit from `TrueConfChatBotError` and can be imported from `trueconf.exceptions`. For details, see the [exceptions reference](../reference/Exceptions.md).
