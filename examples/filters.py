import asyncio
import sys
import logging
import os
import re
from trueconf import Bot, Dispatcher, Router, Message, F
from trueconf.filters.command import Command, CommandObject

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
    server="10.140.1.255",
    username="echo_bot",
    password="123tr",
    web_port=443,
    verify_ssl=False,
    dispatcher=dp)




@r.message(Command("ping"))
async def handle_ping(message: Message, command: CommandObject):
    await bot.send_message(chat_id=message.chat_id, text="pong")

@r.message(Command("hello"))
async def handle_hello(message: Message, command: CommandObject):
    await bot.send_message(chat_id=message.chat_id, text="Hello there!")

@r.message(Command("time"))
async def handle_time(message: Message, command: CommandObject):
    from datetime import datetime
    await bot.send_message(chat_id=message.chat_id, text=f"Current time: {datetime.now().isoformat()}")

@r.message(Command("echo", magic=F.args))
async def handle_echo(message: Message, command: CommandObject):
    await bot.send_message(chat_id=message.chat_id, text=command.args or "You didn't say anything.")

@r.message(Command("upper", magic=F.args.len() > 3))
async def handle_upper(message: Message, command: CommandObject):
    await bot.send_message(chat_id=message.chat_id, text=(command.args or "").upper())

@r.message(Command("lower"))
async def handle_lower(message: Message, command: CommandObject):
    await bot.send_message(chat_id=message.chat_id, text=(command.args or "").lower())

@r.message(Command("reverse"))
async def handle_reverse(message: Message, command: CommandObject):
    await bot.send_message(chat_id=message.chat_id, text=(command.args or "")[::-1])

@r.message(Command("repeat", magic=F.args.func(lambda x: isinstance(x, str) and len(x.split()) == 1)))
async def handle_repeat(message: Message, command: CommandObject):
    await bot.send_message(chat_id=message.chat_id, text=f"{command.args or ''} {command.args or ''}")

@r.message(Command("args", magic=F.args.len() > 0))
async def handle_args(message: Message, command: CommandObject):
    await bot.send_message(chat_id=message.chat_id, text=f"Args: {command.args}")


# Новый хендлер для нескольких команд сразу: /info, /about, /whoami
@r.message(Command("info", "about", "whoami"))
async def handle_multi_command(message: Message, command: CommandObject):
    await bot.send_message(chat_id=message.chat_id, text=f"You're {message.author.id}, used /{command.command}")

@r.message(Command(re.compile(r"cap[s]?"), magic=F.args))
async def handle_caps(message: Message, command: CommandObject):
    await bot.send_message(chat_id=message.chat_id, text=(command.args or "").capitalize())

# Ещё один хендлер с magic, принимающий несколько команд: /check, /verify, если аргументов больше двух
@r.message(Command("check", "verify", magic=F.args.len() > 2))
async def handle_check_commands(message: Message, command: CommandObject):
    await bot.send_message(chat_id=message.chat_id, text=f"Check passed for: /{command.command} with args: {command.args}")

# Новый хендлер с magic фильтром для /start demo
@r.message(Command("start", magic=F.args.func(lambda x: x and x.startswith("demo"))))
async def handle_start_demo(message: Message, command: CommandObject):
    await bot.send_message(chat_id=message.chat_id, text=f"Demo mode: {command.args}")

# Новый хендлер с regexp командой
@r.message(Command(re.compile(r"echo_\d+")))
async def handle_echo_numbered(message: Message, command: CommandObject):
    await bot.send_message(chat_id=message.chat_id, text=f"Special echo: {command.command} {command.args or ''}")

@r.message(Command("len"))
async def handle_len(message: Message, command: CommandObject):
    await bot.send_message(chat_id=message.chat_id, text=str(len(command.args or "")))

@r.message(Command("words"))
async def handle_words(message: Message, command: CommandObject):
    words = (command.args or "").split()
    await bot.send_message(chat_id=message.chat_id, text=f"Words: {len(words)}")

@r.message(Command("help"))
async def handle_help(message: Message, command: CommandObject):
    await bot.send_message(chat_id=message.chat_id, text="Available commands: /ping, /hello, /time, /echo, /upper, /lower, /reverse, /repeat, /args, /whoami, /caps, /len, /words, /help, /id")

@r.message(Command("id"))
async def handle_id(message: Message):
    await bot.send_message(chat_id=message.chat_id, text=f"Your ID: {message.author.id}")

try:
    asyncio.run(bot.start())
except KeyboardInterrupt:
    sys.exit(0)
except asyncio.CancelledError:
    print("🛑 Задача была отменена.")
