<p align="center">
  <a href="https://trueconf.com" target="_blank" rel="noopener noreferrer">
    <picture>
      <source media="(prefers-color-scheme: dark)" srcset="assets/logo-cyrillic.svg" type="image/svg">
      <img width="150" src="assets/logo-cyrillic.svg" type="image/svg">
    </picture>
  </a>
</p>

<h1 align="center">python-trueconf-bot</h1>

<p align="center">Это легкая и мощная обертка для <a href="hhttps://trueconf.ru/docs/chatbot-connector/ru/overview/">API чат-ботов TrueConf Server</a>, позволяющая быстро интегрировать чат-ботов с API TrueConf.</p>

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
  <img src="/assets/head_ru.png" alt="Example Bot in TrueConf" width="600" height="auto">
</p>

<p align="center">
  <a href="./README.md">English</a> /
  <a href="./README-ru.md">Русский</a>
</p>

> [!TIP]
> При разработке мы вдохновлялись популярной библиотекой [aiogram](https://github.com/aiogram/aiogram/), поэтому разработчикам,
> знакомым с ней, переход будет **простым** и **безболезненным**.

## Ключевые возможности

- Простая интеграция с [API чат-ботов TrueConf Server](https://trueconf.ru/docs/chatbot-connector/ru/overview/);
- Быстрый старт с пакетом `python-trueconf-bot`;
- Современный и понятный Python API (`from trueconf import Bot`);
- Поддержка всех основных функций чат-ботов TrueConf Server.

> [!IMPORTANT]
> Функционал чат-ботов поддерживается начиная с версии TrueConf Server 5.5, а также в TrueConf Enterprise и TrueConf Server Free.

## Пример бота

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

## Документация и поддержка

1. [Документация API чат-ботов TrueConf Server](https://trueconf.ru/docs/chatbot-connector/ru/overview/)
2. [Документация python-trueconf-bot](https://trueconf.github.io/python-trueconf-bot/ru/)

Все обновления и релизы доступны в репозитории. Следите за статусом сборок и покрытием тестами.

---

Начните создавать умных и надежных ботов для TrueConf уже сегодня с **python-trueconf-bot**!
