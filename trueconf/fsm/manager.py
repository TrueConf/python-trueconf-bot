from __future__ import annotations

from typing import Any

from trueconf.fsm.context import FSMContext
from trueconf.fsm.key_builder import DefaultKeyBuilder, KeyBuilder, StorageKey
from trueconf.fsm.storage.base import BaseStorage
from trueconf.fsm.storage.memory import MemoryStorage
from trueconf.fsm.strategy import FSMStrategy, apply_strategy


class FSMManager:
    def __init__(
        self,
        storage: BaseStorage | None = None,
        key_builder: KeyBuilder | None = None,
        strategy: FSMStrategy = FSMStrategy.USER_IN_CHAT,
    ) -> None:
        self.storage: BaseStorage = storage or MemoryStorage()
        self.key_builder: KeyBuilder = key_builder or DefaultKeyBuilder()
        self.strategy = strategy

    def get_context(self, bot: Any, event: Any) -> FSMContext:
        key = self.key_builder.build(bot, event)
        chat_id, user_id = apply_strategy(
            self.strategy,
            key.chat_id,
            key.user_id,
        )
        adjusted_key = StorageKey(
            bot_id=key.bot_id,
            chat_id=chat_id,
            user_id=user_id,
            destiny=key.destiny,
        )
        return FSMContext(self.storage, adjusted_key)
