# Python Library for TrueConf Chatbot Connector

<img src="img/head.png" alt="">

Welcome to the documentation of **{{product_name}}** — a library that allows you to create and manage chatbots for the TrueConf platform using WebSocket and asyncio.

This library is designed to simplify the development of chatbots by providing ready-made tools for connecting, processing incoming events, and sending responses. With it, you can create bots for automating tasks, integrating with external services, and enhancing communication within your organization.

## Key features

* Asynchronous operation using **asyncio**
* Support for WebSocket connections
* Convenient routing of incoming messages
* Built-in filters for processing different types of updates
* Easy integration with external Python libraries

## Installation

### Requirements

* Python **3.10+**
* Installed dependencies: `websockets`, `httpx`, `mashumaro`, `pillow`, `aiofiles`, `magic-filter`
* It is recommended to use [virtualenv](https://docs.python.org/3/library/venv.html) or [poetry](https://python-poetry.org/) for dependency isolation.

### Installation using pip

```shell
pip install git+https://github.com/TrueConf/{{product_name}}
```

## Comparison with aiogram

| Feature             | aiogram (Telegram)                             | {{product_name}} (TrueConf)                                                               |
|---------------------|------------------------------------------------|-------------------------------------------------------------------------------------------|
| Asynchronous        | asyncio                                        | asyncio                                                                                   |
| Routing decorators  | `@router.message(...)`                         | `@router.message(...)`                                                                    |
| Message filtering   | `F.text`, `F.photo`, `F.document`              | `F.text`, `F.photo`, `F.document`                                                         |
| Magic-filter        | ✅                                              | ✅                                                                                         |
| Aliases (shortcuts) | `message.answer()`, `message.reply()`          | `message.answer()`, `message.reply()`                                                     |
| Bot initialization  | `Bot(token="...")`                             | `Bot(server, token="...")` or `Bot.from_credentials(server, login, password)`             |
| JSON → Python       | Pydantic models                                | Mashumaro dataclasses                                                                     |
| Transport           | HTTPS + long polling / webhook                 | Asynchronous WebSocket                                                                    |
| Working with files  | `bot.get_file(...)` + `bot.download_file(...)` | `message.photo.download()`, `message.document.download()`, `bot.download_file_by_id(...)` |
