from __future__ import annotations
from typing import Any
from trueconf.enums.message_type import MessageType
from trueconf.types.message import Message

Event = Any  # позже можно заменить на типизированные модели

class Command:
    """
    /start, /help, /echo hi
    Command("start")   == Command("/start")  # оба варианта валидны
    Command(("start", "join")) — строго '/start join'
    Command("echo", with_param=True) — '/echo <любой текст>'
    """

    def __init__(self, cmd: str, with_param: bool = False):
        self.cmd = cmd[1:] if cmd.startswith("/") else cmd
        self.with_param = with_param

    async def __call__(self, event: Event) -> bool:
        if not isinstance(event, Message):
            return False
        if event.type != MessageType.PLAIN_MESSAGE:
            return False
        text = (event.content.text or "")
        if not text.startswith("/"):
            return False
        no_slash = text[1:]
        parts = no_slash.split(maxsplit=1)
        if not parts or parts[0] != self.cmd:
            return False
        return (len(parts) == 2 and bool(parts[1].strip())) if self.with_param else True