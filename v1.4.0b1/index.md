# Python Library for TrueConf Chatbot Connector⚓︎

Welcome to the documentation of python-trueconf-bot — a library that allows you to create and manage chatbots for the TrueConf platform using WebSocket and asyncio.

This library is designed to simplify the development of chatbots by providing ready-made tools for connecting, processing incoming events, and sending responses. With it, you can create bots for automating tasks, integrating with external services, and enhancing communication within your organization.

## Key features⚓︎

- Asynchronous operation using asyncio

- Support for WebSocket connections

- Convenient routing of incoming messages

- Built-in filters for processing different types of updates

- Easy integration with external Python libraries

## Installation⚓︎

### Requirements⚓︎

- Python 3.10+

- Installed dependencies: `websockets`, `httpx`, `mashumaro`, `pillow`, `aiofiles`, `magic-filter`

- It is recommended to use virtualenv or poetry for dependency isolation.

### Installation using pip⚓︎

```
pip install python-trueconf-bot
```

## Comparison with aiogram⚓︎

| Feature | aiogram (Telegram) | python-trueconf-bot (TrueConf) |
| --- | --- | --- |
| Asynchronous | asyncio | asyncio |
| Routing decorators | `@router.message(...)` | `@router.message(...)` |
| Message filtering | `F.text`, `F.photo`, `F.document` | `F.text`, `F.photo`, `F.document` |
| Magic-filter | ✅ | ✅ |
| Aliases (shortcuts) | `message.answer()`, `message.reply()` | `message.answer()`, `message.reply()` |
| Bot initialization | `Bot(token="...")` | `Bot(server, token="...")` or `Bot.from_credentials(server, login, password)` |
| JSON → Python | Pydantic models | Mashumaro dataclasses |
| Transport | HTTPS + long polling / webhook | Asynchronous WebSocket |
| Working with files | `bot.get_file(...)` + `bot.download_file(...)` | `message.photo.download()`, `message.document.download()`, `bot.download_file_by_id(...)` |

## LLM Files⚓︎

- llms.txt

- llms-full.txt
