# Getting Started⚓︎

Before getting started, we recommend creating and activating a virtual environment to isolate your project dependencies:

```
python -m venv .venv
source .venv/bin/activate # Linux / macOS
.venv\Scripts\activate # Windows PowerShell
```

## Installing python-trueconf-bot⚓︎

To begin working with python-trueconf-bot, install the package from the global PyPI repository:

```
pip install python-trueconf-bot
```

Info

Upon installation, dependencies will be automatically pulled in: `websockets`, `httpx`, `mashumaro`, `pillow`, `aiofiles`, `magic-filter`.

## Creating a Basic Echo Bot⚓︎

First, import the required classes:

```
from trueconf import Bot, Dispatcher, Router, F
from trueconf.types import Message
```

Next, create instances of `Router` and `Dispatcher` and connect them:

```
r = Router()
dp = Dispatcher()
# dp.include_router(r)
```

The bot supports two types of authentication: token-based or login/password. You can choose the most convenient method.

### Token-Based Authentication⚓︎

If you're using token-based connection, obtain the token as described in the official API documentation.

It is recommended to store the token in an environment variable or `.env` file. Don’t forget to add `.env` to `.gitignore` if working with public repositories.

```
from os import getenv

TOKEN = getenv("TOKEN")
bot = Bot(server="video.example.com", token=TOKEN, dispatcher=dp)
```

Note

The token is valid for one month from the moment it is created. However, an already authorized connection remains active until it is closed, even after the token has expired. In theory, such a connection can persist for years.

### Login/Password Authentication⚓︎

Use the `.from_credentials` method:

```
bot = Bot.from_credentials(
username="echo_bot",
password="123tr",
server="10.110.2.240",
dispatcher=dp
)
```

Info

Each time from_credentials() is called, the bot requests a new token from the server. The token lifespan is 1 month.

### Message Handler⚓︎

Now let’s create a simple handler for incoming messages. It will reply with the same text (a classic "echo bot"):

```
@r.message(F.text)
async def echo(message: Message):
await message.answer(message.text)
```

### Running the Bot⚓︎

Run the bot inside an asynchronous `main()` function passed to `asyncio.run()`:

```
async def main():
await bot.run()

import asyncio

if __name__ == "__main__":
asyncio.run(main())
```

Why async/await?

The python-trueconf-bot library is built on asyncio.

This means that all network operations (connecting to the server, receiving and sending messages) are asynchronous and non-blocking. Therefore:

- handlers are written as `async def`,

- method calls use `await`,

- the launch is managed via `asyncio.run(...)`.

This approach allows handling multiple events and messages in parallel — without delays or blocking.

### Automatic Connection Recovery⚓︎

If the WebSocket connection to the server is interrupted, the bot will not stop immediately. Instead, it will automatically attempt to reconnect and continue receiving events.

Reconnection uses an exponential backoff strategy: after each failed attempt, the delay increases but does not exceed the `ws_max_delay` value. This helps prevent excessive requests to the server during temporary network issues.

By default, the following reconnection parameters are used:

```
bot = Bot(
server="video.example.com",
token=TOKEN,
dispatcher=dp,
ws_max_retries=5,
ws_max_delay=60,
)
```

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| `ws_max_retries` | `int` | `5` | Maximum number of connection attempts on network/IP errors before giving up |
| `ws_max_delay` | `int` | `60` | Maximum delay between reconnection attempts (in seconds) |

If your bot runs in an unstable network environment or the server may be temporarily unavailable, you can increase these values:

```
bot = Bot(
server="video.example.com",
token=TOKEN,
dispatcher=dp,
ws_max_retries=10,
ws_max_delay=120,
)
```

Note

In case of a normal WebSocket disconnection, the bot will attempt to reconnect using exponential backoff.

If the server address is incorrect, the bot will not be able to establish a connection. In this case, the number of retry attempts is limited by `ws_max_retries`, after which a connection error will be raised.
