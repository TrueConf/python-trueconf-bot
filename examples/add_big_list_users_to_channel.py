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