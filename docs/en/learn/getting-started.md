---
title: Getting Started
description: How to install the library and create your first bot
icon: material/run
---

# Getting Started

Before getting started, we recommend creating and activating a virtual environment to isolate your project dependencies:

```shell
python -m venv .venv
source .venv/bin/activate   # Linux / macOS
.venv\Scripts\activate      # Windows PowerShell
```

## Installing {{product_name}}

To begin working with {{product_name}}, install the package from the global PyPI repository:

```shell
pip install {{product_name}}
```

!!! info
    Upon installation, dependencies will be automatically pulled in: `websockets`, `httpx`, `mashumaro`, `pillow`, `aiofiles`, `magic-filter`.

## Creating a Basic Echo Bot

First, import the required classes:

```python
from trueconf import Bot, Dispatcher, Router, F
from trueconf.types import Message
```

Next, create instances of `Router` and `Dispatcher` and connect them:

```python
r = Router()
dp = Dispatcher()
# dp.include_router(r)
```

The bot supports two types of authentication: token-based or login/password. You can choose the most convenient method.

### Token-Based Authentication

If you're using token-based connection, obtain the token as described in the [official API documentation](https://trueconf.ru/docs/chatbot-connector/ru/connect-and-auth/#access-token).

It is recommended to store the token in an environment variable or `.env` file. Don’t forget to add `.env` to `.gitignore` if working with public repositories.

```python
from os import getenv

TOKEN = getenv("TOKEN")
bot = Bot(server="video.example.com", token=TOKEN, dispatcher=dp)
```

!!! Note
    The token is valid for one month from the moment it is created.
    However, an already authorized connection remains active until it is closed, even after the token has expired.
    In theory, such a connection can persist for years.

### Login/Password Authentication

Use the `.from_credentials` method:

```python
bot = Bot.from_credentials(
    username="echo_bot",
    password="123tr",
    server="10.110.2.240",
    dispatcher=dp
)
```

!!! info
    Each time **from\_credentials()** is called, the bot requests a new token from the server.
    The token lifespan is 1 month.

### Message Handler

Now let’s create a simple handler for incoming messages. It will reply with the same text (a classic "echo bot"):

```python
@r.message(F.text)
async def echo(message: Message):
    await message.answer(message.text)
```

### Running the Bot

Run the bot inside an asynchronous `main()` function passed to `asyncio.run()`:

```python
async def main():
    await bot.run()
    
import asyncio

if __name__ == "__main__":
    asyncio.run(main())
```

!!! question "Why async/await?"
    The **{{product_name}}** library is built on asyncio.

This means that all network operations (connecting to the server, receiving and sending messages) are asynchronous and non-blocking. Therefore:

* handlers are written as `async def`,
* method calls use `await`,
* the launch is managed via `asyncio.run(...)`.

This approach allows handling multiple events and messages in parallel — without delays or blocking.

### Automatic Connection Recovery

If the WebSocket connection to the server is interrupted, the bot will not stop immediately. Instead, it will automatically attempt to reconnect and continue receiving events.

Reconnection uses an exponential backoff strategy: after each failed attempt, the delay increases but does not exceed the `ws_max_delay` value. This helps prevent excessive requests to the server during temporary network issues.

By default, the following reconnection parameters are used:

```python hl_lines="5-6"
bot = Bot(
    server="video.example.com",
    token=TOKEN,
    dispatcher=dp,
    ws_max_retries=5,
    ws_max_delay=60,
)
```

| Parameter        | Type  | Default | Description                                                                 |
| ---------------- | ----- | ------- | --------------------------------------------------------------------------- |
| `ws_max_retries` | `int` | `5`     | Maximum number of connection attempts on network/IP errors before giving up |
| `ws_max_delay`   | `int` | `60`    | Maximum delay between reconnection attempts (in seconds)                    |

If your bot runs in an unstable network environment or the server may be temporarily unavailable, you can increase these values:

```python hl_lines="5-6"
bot = Bot(
    server="video.example.com",
    token=TOKEN,
    dispatcher=dp,
    ws_max_retries=10,
    ws_max_delay=120,
)
```

!!! note
    In case of a normal WebSocket disconnection, the bot will attempt to reconnect using exponential backoff.

    If the server address is incorrect, the bot will not be able to establish a connection. In this case, the number of retry attempts is limited by `ws_max_retries`, after which a connection error will be raised.

## Health-check

{{product_name}} supports two approaches for checking bot state:

- **push model** — the bot calls a callback function when the connection state changes;
- **pull model** — the application manually requests the current state via `bot.health_check()`.

### Push: callback on state changes

The callback is passed via the `on_health_check` parameter when creating the bot.
The function must be asynchronous and accept a dictionary with the current status:

```python
async def on_health_check(status: dict):
    print("Bot status changed:", status)


bot = Bot.from_credentials(
    server="video.example.com",
    username="echo_bot",
    password="123tr",
    dispatcher=dp,
    on_health_check=on_health_check,
)
```

The callback is triggered whenever the WebSocket connection or authorization state changes.
For example, the bot may emit the following statuses:

- `connected` — the WebSocket connection is established, but the bot is not authorized yet;
- `authorized` — the bot has successfully authenticated;
- `disconnected` — the connection has been lost.

Example payload:

```json
{
    "status": "authorized",
    "websocket_connected": true,
    "authorized": true,
    "user_id": "echo_bot@video.example.com",
    "server": "video.example.com",
    "port": 443,
    "protocol": "https",
    "timestamp": "2026-05-06T12:00:00+00:00",
}
```

The push model is useful when you need to react immediately to state changes: write logs, notify monitoring systems, update application state, or alert administrators.

### Pull: manual health check

The `bot.health_check()` method returns the current bot state at the moment it is called:

```python
status = bot.health_check()
print(status)
```

Example response:

```json
{
    "status": "authorized",
    "websocket_connected": true,
    "authorized": true,
    "server": "video.example.com",
    "port": 443,
    "protocol": "https",
    "timestamp": "2026-05-06T12:00:00+00:00",
}
```

The pull model is useful for HTTP health-check endpoints, such as FastAPI, Zabbix, Kubernetes probes, or other monitoring systems:

```python
from fastapi import FastAPI

app = FastAPI()


@app.get("/health")
def health():
    return bot.health_check()
```

### Combining push and pull

In practice, it is often convenient to use both approaches together.
The callback updates the latest known state, while the HTTP endpoint exposes it to monitoring systems:

```python
from fastapi import FastAPI

app = FastAPI()
bot_status = {"status": "disconnected"}


async def on_health_check(status: dict):
    bot_status.update(status)


bot = Bot.from_credentials(
    server="video.example.com",
    username="echo_bot",
    password="123tr",
    dispatcher=dp,
    on_health_check=on_health_check,
)


@app.get("/health")
def health():
    return bot_status
```

In this setup, the bot reports state changes through the callback, while external monitoring systems retrieve the current status through HTTP requests.
