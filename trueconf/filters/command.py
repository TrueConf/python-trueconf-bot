from __future__ import annotations
from dataclasses import dataclass, field, replace
from re import Match, Pattern
from typing import Any
from trueconf.enums.message_type import MessageType
from trueconf.types.message import Message
from magic_filter import F
from magic_filter import MagicFilter

Event = Any  # позже можно заменить на типизированные модели

class Command:
    """
    /start, /help, /echo hi
    Command("start")   == Command("/start")  # оба варианта валидны
    Command(("start", "join")) — строго '/start join'
    Command("echo", with_param=True) — '/echo <любой текст>'
    """

    def __init__(
        self,
        *commands: str | Pattern[str],
        prefix: str = "/",
        ignore_case: bool = False,
        magic: MagicFilter | None = None,
    ):
        if not commands:
            raise ValueError("At least one command is required")
        self.commands = tuple(
            cmd.casefold() if isinstance(cmd, str) and ignore_case else cmd
            for cmd in commands
        )
        self.prefix = prefix
        self.ignore_case = ignore_case
        self.magic = magic

    async def __call__(self, event: Event) -> bool | dict[str, Any]:
        if not isinstance(event, Message):
            return False
        if event.type != MessageType.PLAIN_MESSAGE:
            return False
        text = event.content.text or ""
        if not text.startswith(self.prefix):
            return False

        try:
            command_obj = self.extract_command(text)
        except ValueError:
            return False

        try:
            self.validate_command(command_obj)
        except ValueError:
            return False

        if self.magic:
            result = self.magic.resolve(command_obj)
            if not result:
                return False
            if isinstance(result, dict):
                return {"command": replace(command_obj, magic_result=result)}
            return {"command": command_obj}

        return {"command": command_obj}

    def extract_command(self, text: str) -> CommandObject:
        try:
            full_command, *args = text.split(maxsplit=1)
        except ValueError:
            raise ValueError("Command format invalid")

        prefix, (command, _, _) = full_command[0], full_command[1:].partition("@")
        return CommandObject(
            prefix=prefix,
            command=command,
            args=args[0] if args else None,
        )

    def validate_command(self, command: CommandObject) -> None:
        name = command.command
        if self.ignore_case:
            name = name.casefold()
        for pattern in self.commands:
            if isinstance(pattern, str) and name == pattern:
                return
            if isinstance(pattern, Pattern) and pattern.match(name):
                return
        raise ValueError("Command not matched")

@dataclass(frozen=True)
class CommandObject:
    prefix: str = "/"
    command: str = ""
    args: str | None = field(repr=False, default=None)
    regexp_match: Match[str] | None = field(repr=False, default=None)
    magic_result: Any | None = field(repr=False, default=None)

    @property
    def text(self) -> str:
        line = self.prefix + self.command
        if self.args:
            line += " " + self.args
        return line