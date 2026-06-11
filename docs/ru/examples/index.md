---
title: Примеры кода
icon: material/console
---

# Примеры

## Эхо-бот (базовый пример)

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

## Webhook (например, для Zabbix)

В этом примере вы можете увидеть, насколько просто настроить webhook с помощью FastAPI для приёма запросов от внешних систем, таких как Zabbix.

Вы также можете защитить свой webhook с помощью авторизации или разрешить приём запросов только с определённых IP-адресов. Всё это настраивается в  [FastAPI](https://fastapi.tiangolo.com/).

```python
import asyncio
import logging
import os
from typing import Any
from trueconf import Bot
from contextlib import asynccontextmanager
from fastapi import FastAPI
import uvicorn

os.makedirs("logs", exist_ok=True)

logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    filename="logs/bot.log",
    encoding="utf-8",
)

@asynccontextmanager
async def lifespan(app: FastAPI):
    bot_task = asyncio.create_task(bot.run())
    yield

app = FastAPI(lifespan=lifespan)
bot = Bot.from_credentials(
    server="10.140.1.255",
    username="echo_bot",
    password="123tr",
    verify_ssl=False)


@app.post("/send")
async def read_root(data: dict[str, Any]):
    r = await bot.create_personal_chat(user_id="user")
    r = await bot.send_message(chat_id = r.chat_id, text=str(data))
    print(r.message_id)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
```

## Добавление большого списка пользователей в канал

```python
from trueconf import Bot
from trueconf.exceptions import ApiErrorException
import asyncio
import logging
from pathlib import Path

SERVER_ADDR = ""
BOT_USERNAME = ""
BOT_PASSWORD = ""
PATH_LIST_USERS = ""
CHANNEL_NAME = ""

bot = Bot.from_credentials(
    server=SERVER_ADDR,
    username=BOT_USERNAME,
    password=BOT_PASSWORD,
    verify_ssl=False,
)

Path("logs").mkdir(parents=True, exist_ok=True)

logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    filename="logs/bot.log",
    encoding="utf-8",
)

async def main():
    await bot.start()
    await bot.connected_event.wait()
    await bot.authorized_event.wait()

    resp = await bot.create_channel(title=CHANNEL_NAME)
    with open(PATH_LIST_USERS, "r") as file:
        for line in file:
            user_id = line.strip()
            if user_id:
                try:
                    await bot.add_participant_to_chat(resp.chat_id, user_id=user_id, display_history=True)
                except ApiErrorException as e:
                    if e.code == 309:
                        continue

    await bot.shutdown()

if __name__ == "__main__":
    asyncio.run(main())
```

## Мультибот

Команда TrueConf подготовила пример использования сразу 4 ботов (all-in-one):

- эхо-бот;
- больничный-бот, корый пересылает сообщения в группу с HR;
- мониторинг-бот статистики внешнего сервиса (TrueConf Server);
- gpt-бот, который в фоне запускает локальную LLM-модель.

[View repository :fontawesome-solid-arrow-right:](https://github.com/TrueConf/trueconf-chatbot-example){ .md-button }

## Бот для написания обращений в поддержку

```python
"""
Below is the initial scaffold for a bot that collects support reports.

- /report creates a router/state to capture and parse messages from a specific user.
- /cancel cancels the ticket and removes the user from this state.
- /send emails the collected messages — this is where you implement the logic to assemble the email (body + attachments) and send it.
You can use built-in modules, and third-party libraries if needed.
"""

import asyncio
import uuid
import trueconf
from trueconf import *
from trueconf.filters import Command

r1 = Router()
dp = Dispatcher()
dp.include_router(r1)

router_list_for_report = {}
list_message_for_report = {}

bot = trueconf.Bot.from_credentials(
    server="10.110.2.241",
    username="report_bot",
    password="123tr",
    dispatcher=dp,
    https=True,
    verify_ssl=False)

async def handle_report(msg: Message):
    if msg.from_user.id in router_list_for_report.keys():
        list_message_for_report[msg.from_user.id].append(msg)
        await msg.answer("The message has been added to the report.")


@r1.message(Command("report"))
async def on_report(msg: Message):
    number = uuid.uuid4() # генерация номера обращения с помощью uuid
    await msg.answer(f"Your ticket number is {number}. All subsequent messages will be added to this ticket.")
    r = Router(name=str(number))
    dp.include_router(r)
    r.message(F.from_user.id == msg.from_user.id)(handle_report)
    router_list_for_report.update({msg.from_user.id: r})
    list_message_for_report.update({msg.from_user.id: []})


@r1.message(Command("cancel"))
async def on_cancel(msg: Message):
    if msg.from_user.id in router_list_for_report.keys():
        for router in dp.routers:
            if router.name == router_list_for_report[msg.from_user.id].name:
                dp.routers.remove(router)
                router_list_for_report.pop(msg.from_user.id)
                list_message_for_report.pop(msg.from_user.id)
                await msg.answer("The report has been cancelled.")
                break
    else:
        await msg.answer("You don’t have an active report.")


def build_message_and_send_email(messages:list):
    """
    In Python, there are built-in libraries for working with email messages:
    https://docs.python.org/3/library/email.examples.html

    Here, you need to take the data from list_message_for_report[msg.from_user.id]
    and build an email-ready representation:

    for msg in message:
        match msg.content_type:
            case MessageType.TEXT:
                # You can put the text into the email body
            case MessageType.ATTACHMENT:
                # Download the files from TrueConf Server via:
                # msg.download(dest_path="path/to/file")

    Once the email is assembled correctly, send it using the smtplib module:
    https://docs.python.org/3/library/smtplib.html#smtp-example
    """

@r1.message(Command("send"))
async def send_report(msg: Message):
    if msg.from_user.id in router_list_for_report.keys():
        if build_message_and_send_email(list_message_for_report[msg.from_user.id]):
            await msg.answer("Your request has been successfully submitted to Technical Support.")
        else:
            await msg.answer("An error occurred. Please contact the bot developer.")
    else:
        await msg.answer("You don’t have an active report.")
        return

if __name__ == "__main__":
    asyncio.run(bot.run())
```

## Анкета (пример реализации FSM)

```python
import asyncio
from trueconf import Bot, Dispatcher, Router, F, Message
from trueconf.filters import Command
from trueconf.fsm import FSMContext, State, StatesGroup
from trueconf.fsm.storage.memory import MemoryStorage


class Survey(StatesGroup):
    name = State()
    age = State()
    city = State()
    confirm = State()


storage = MemoryStorage()
dp = Dispatcher(storage=storage)
router = Router()
dp.include_router(router)


@router.message(Command("cancel"))
async def cmd_cancel(msg: Message, state: FSMContext):
    current = await state.get_state()
    if current is None:
        await msg.answer("Нечего отменять.")
        return
    await state.clear()
    await msg.answer("Анкета отменена.")


@router.message(Command("start"))
async def cmd_start(msg: Message, state: FSMContext):
    await state.set_state(Survey.name)
    await msg.answer("Как вас зовут?")


@router.message(Survey.name)
async def process_name(msg: Message, state: FSMContext):
    if len(msg.text) < 2:
        await msg.answer("Имя слишком короткое. Попробуйте ещё раз:")
        return
    await state.update_data(name=msg.text)
    await state.set_state(Survey.age)
    await msg.answer("Сколько вам лет?")


@router.message(Survey.age)
async def process_age(msg: Message, state: FSMContext):
    if not msg.text.isdigit() or not (1 <= int(msg.text) <= 150):
        await msg.answer("Введите корректный возраст (1–150):")
        return
    await state.update_data(age=int(msg.text))
    await state.set_state(Survey.city)
    await msg.answer("В каком городе вы живёте?")


@router.message(Survey.city)
async def process_city(msg: Message, state: FSMContext):
    await state.update_data(city=msg.text)
    await state.set_state(Survey.confirm)
    data = await state.get_data()
    await msg.answer(
        f"Проверьте данные:\n\n"
        f"Имя: {data['name']}\n"
        f"Возраст: {data['age']}\n"
        f"Город: {data['city']}\n\n"
        f"Всё верно? (да/нет)"
    )


@router.message(Survey.confirm)
async def process_confirm(msg: Message, state: FSMContext):
    text = msg.text.lower().strip()
    if text == "да":
        data = await state.get_data()
        await state.clear()
        await msg.answer(f"Спасибо, {data['name']}! Анкета заполнена.")
    elif text == "нет":
        await state.clear()
        await msg.answer("Анкета отменена. Начните заново: /start")
    else:
        await msg.answer("Ответьте 'да' или 'нет'.")


bot = Bot.from_credentials(
    server="your-server",
    username="your-bot",
    password="your-password",
    dispatcher=dp,
)

if __name__ == "__main__":
    asyncio.run(bot.run())
```

## Middleware

```python
import logging
import time
from trueconf import Bot, Dispatcher, Router, F
from trueconf.types import Message
from trueconf.filters import Command
from trueconf.middleware import BaseMiddleware

logger = logging.getLogger("bot")


class LoggingMiddleware(BaseMiddleware):
    async def __call__(self, handler, event, data):
        logger.info(f"Event: {type(event).__name__}")
        await handler(event, data)


class AntiFloodMiddleware(BaseMiddleware):
    def __init__(self, limit: float = 1.0):
        self.limit = limit
        self.last: dict[str, float] = {}

    async def __call__(self, handler, event, data):
        if not isinstance(event, Message):
            await handler(event, data)
            return

        user_id = event.author.id
        now = time.monotonic()

        if user_id in self.last and now - self.last[user_id] < self.limit:
            return

        self.last[user_id] = now
        await handler(event, data)


dp = Dispatcher()
dp.outer_middleware(LoggingMiddleware())

router = Router()
router.outer_middleware(AntiFloodMiddleware(limit=0.5))
dp.include_router(router)


@router.message(Command("start"))
async def cmd_start(msg: Message):
    await msg.answer("Привет!")


@router.message(F.text)
async def echo(msg: Message):
    await msg.answer(msg.text)


bot = Bot.from_credentials(
    server="your-server",
    username="your-bot",
    password="your-password",
    dispatcher=dp,
)

import asyncio
if __name__ == "__main__":
    asyncio.run(bot.run())
```

Порядок выполнения для каждого сообщения:

```
1. LoggingMiddleware (Dispatcher)     — логирует событие
2. AntiFloodMiddleware (Router)       — проверяет частоту
3. Проверка фильтров                  — Command("start") или F.text
4. Обработчик                         — cmd_start или echo
```




