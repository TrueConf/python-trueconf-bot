from __future__ import annotations

from typing import Any

from trueconf.fsm.context import FSMContext
from trueconf.fsm.key_builder import DefaultKeyBuilder, KeyBuilder
from trueconf.fsm.storage.base import BaseStorage
from trueconf.fsm.storage.memory import MemoryStorage


class FSMManager:
    def __init__(
        self,
        storage: BaseStorage | None = None,
        key_builder: KeyBuilder | None = None,
    ) -> None:
        self.storage: BaseStorage = storage or MemoryStorage()
        self.key_builder: KeyBuilder = key_builder or DefaultKeyBuilder()

    def get_context(self, bot: Any, event: Any) -> FSMContext:
        key = self.key_builder.build(bot, event)
        return FSMContext(self.storage, key)
