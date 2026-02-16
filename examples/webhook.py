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