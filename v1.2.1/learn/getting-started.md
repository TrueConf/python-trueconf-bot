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
