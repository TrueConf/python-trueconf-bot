import asyncio
import logging
import os
import sys

from trueconf import Bot, Dispatcher, Message, Router

os.makedirs("logs", exist_ok=True)

logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    filename="logs/bot.log",
    encoding="utf-8",
)

r = Router()
dp = Dispatcher()
dp.include_router(r)

bot = Bot.from_credentials(
    server="10.140.1.255", username="echo_bot", password="123tr", web_port=443, verify_ssl=False, dispatcher=dp
)


@r.message()
async def handle_contact(message: Message):
    contact = await message.contact
    if contact is None:
        await message.answer("Send me a .vcf file or a TrueConf contact to see its details.")
        return

    lines = [f"Name: {contact.first_name}"]
    if contact.last_name:
        lines.append(f"Last name: {contact.last_name}")
    if contact.phone_number:
        lines.append(f"Phone: {contact.phone_number}")
    if contact.user_id:
        lines.append(f"User ID: {contact.user_id}")
    await message.answer("\n".join(lines))


try:
    asyncio.run(bot.run())
except KeyboardInterrupt:
    sys.exit(0)
except asyncio.CancelledError:
    print("🛑 Задача была отменена.")
