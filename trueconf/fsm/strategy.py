from __future__ import annotations

from enum import Enum, auto


class FSMStrategy(Enum):
    """FSM strategy for storage key generation.

    Determines how chat_id and user_id are combined to form the storage key.
    """

    USER_IN_CHAT = auto()
    """State is stored per user per chat. Default behavior."""

    CHAT = auto()
    """State is stored per chat (all users in a chat share the same state)."""

    GLOBAL_USER = auto()
    """State is stored per user globally (across all chats)."""


def apply_strategy(
    strategy: FSMStrategy,
    chat_id: str,
    user_id: str,
) -> tuple[str, str]:
    """Apply FSM strategy to chat_id and user_id.

    Returns (effective_chat_id, effective_user_id) for StorageKey construction.
    """
    if strategy == FSMStrategy.CHAT:
        return chat_id, chat_id
    if strategy == FSMStrategy.GLOBAL_USER:
        return user_id, user_id
    # USER_IN_CHAT (default)
    return chat_id, user_id
