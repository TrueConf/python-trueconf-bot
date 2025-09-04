from __future__ import annotations
from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .bot import Bot

@dataclass
class BoundToBot:
    __slots__ = ('_bot',)

    def __init__(self) -> None:
        self._bot = None

    def bind(self, bot: "Bot"):
        self._bot = bot
        return self

    if TYPE_CHECKING:
        @property
        def bot(self) -> "Bot": ...
    else:
        @property
        def bot(self) :
            if not self._bot  or self._bot is None:
                raise RuntimeError("Object isn’t bound to ChatBot. Bind via bind(bot) before using shortcuts.")
            return self._bot