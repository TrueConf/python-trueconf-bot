<p align="center">
  <a href="https://trueconf.com" target="_blank" rel="noopener noreferrer">
    <picture>
      <source media="(prefers-color-scheme: dark)" srcset="https://raw.githubusercontent.com/TrueConf/python-trueconf-bot/master/assets/logo.svg" type="image/svg">
      <img width="150" src="https://raw.githubusercontent.com/TrueConf/python-trueconf-bot/master/assets/logo.svg" type="image/svg">
    </picture>
  </a>
</p>

<h1 align="center">python-trueconf-bot</h1>

<p align="center">This is a lightweight and powerful wrapper for the <a href="https://trueconf.com/docs/chatbot-connector/en/overview/">TrueConf Server Chatbot API</a> which enables quick integration of chatbots into TrueConf solutions.</p>

<p align="center">
    <a href="https://t.me/trueconf_chat" target="_blank">
        <img src="https://img.shields.io/badge/telegram-group-blue?style=flat-square&logo=telegram" />
    </a>
    <a href="https://chat.whatsapp.com/GY97WBzSgvD1cJG0dWEiGP">
        <img src="https://img.shields.io/badge/whatsapp-commiunity-gree?style=flat-square&logo=whatsapp" />
    </a>
    <a href="#">
        <img src="https://img.shields.io/github/stars/trueconf/python-trueconf-bot?style=social" />
    </a>
</p>

<p align="center">
  <img src="https://raw.githubusercontent.com/TrueConf/python-trueconf-bot/master/assets/head_en.png" alt="Example Bot in TrueConf" width="600" height="auto">
</p>

> 💡TIP
> 
> We were inspired by the popular [aiogram](https://github.com/aiogram/aiogram/) library, so, the transition will be **simple** for developers already familiar with this library.

## 📌 Key Features

* Easy integration with the [TrueConf Server Chatbot API](https://trueconf.com/docs/chatbot-connector/en/overview/)
* Quick start with the `python-trueconf-bot` package
* Modern and intuitive Python API (`from trueconf import Bot`)
* Support for all major TrueConf Server chatbot features.

> ☝️**IMPORTANT**
> 
> Chatbot features are supported in TrueConf Server 5.5 or above, TrueConf Enterprise, and TrueConf Server Free.

## 🚀 Example Bot

```python
import asyncio
from trueconf import Bot, Dispatcher, Router, Message, F, ParseMode
from os import getenv

router = Router()
dp = Dispatcher()
dp.include_router(router)

TOKEN = getenv("TOKEN")

bot = Bot(server="video.example.com", token=TOKEN, dispatcher=dp)


@router.message(F.text)
async def echo(msg: Message):
    await msg.answer(f"You says: **{msg.text}**", parse_mode=ParseMode.MARKDOWN)


async def main():
    await bot.run()


if __name__ == "__main__":
    asyncio.run(main())
```

## 📚 Documentation

1. [TrueConf Server Chatbot API Documentation](https://trueconf.com/docs/chatbot-connector/en/overview/)
2. [python-trueconf-bot Documentation](https://trueconf.github.io/python-trueconf-bot/)

All updates and releases are available in the repository. Track the build status and test coverage.

---

Start building smart and reliable bots for TrueConf today with **python-trueconf-bot**!
