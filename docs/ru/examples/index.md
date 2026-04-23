# Examples

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



