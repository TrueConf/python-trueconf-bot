from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Protocol, runtime_checkable


@dataclass(frozen=True, slots=True)
class StorageKey:
    bot_id: str | None
    chat_id: str
    user_id: str
    destiny: str = "default"


@runtime_checkable
class KeyBuilder(Protocol):
    def build(self, bot: Any, event: Any) -> StorageKey: ...


class DefaultKeyBuilder:
    def build(self, bot: Any, event: Any) -> StorageKey:
        bot_id = getattr(bot, "me_id", None) or getattr(bot, "id", None)

        chat_id = (
            getattr(event, "chat_id", None)
            or getattr(getattr(event, "chat", None), "id", None)
        )

        user = getattr(event, "from_user", None) or getattr(event, "author", None)
        user_id = getattr(user, "id", None) if user else None

        if chat_id is None or user_id is None:
            raise RuntimeError(
                f"Cannot build FSM StorageKey: event of type {type(event).__name__} "
                f"has no chat_id ({chat_id}) or user_id ({user_id}). "
                f"Provide a custom KeyBuilder to Dispatcher.setup_fsm()."
            )

        return StorageKey(bot_id=bot_id, chat_id=str(chat_id), user_id=str(user_id))
