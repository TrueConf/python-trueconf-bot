# FSM Implementation Plan

Spec: `docs/superpowers/specs/2026-05-25-fsm-design.md`

## Overview

11 steps. Bottom-up: storage → state → key → context → manager → filter → middleware → dispatcher/router integration → exports → tests → verify.

---

## Step 1: Create `trueconf/fsm/storage/base.py` — BaseStorage ABC

**File**: `trueconf/fsm/storage/base.py` (new)

```python
from abc import ABC, abstractmethod
from typing import Any
from trueconf.fsm.key_builder import StorageKey


class BaseStorage(ABC):
    @abstractmethod
    async def get_state(self, key: StorageKey) -> str | None: ...

    @abstractmethod
    async def set_state(self, key: StorageKey, state: str | None) -> None: ...

    @abstractmethod
    async def get_data(self, key: StorageKey) -> dict[str, Any]: ...

    @abstractmethod
    async def set_data(self, key: StorageKey, data: dict[str, Any]) -> None: ...

    @abstractmethod
    async def update_data(self, key: StorageKey, updates: dict[str, Any]) -> dict[str, Any]: ...

    @abstractmethod
    async def clear(self, key: StorageKey) -> None: ...

    async def close(self) -> None:
        pass
```

**Note**: Imports `StorageKey` from `key_builder` which doesn't exist yet. To avoid circular imports, use `TYPE_CHECKING` guard or create key_builder first. Since key_builder has no dependencies on storage, create key_builder first (Step 3) or use a forward reference.

Actually — create `key_builder.py` first (Step 3) since it has no dependencies. Then `storage/base.py` can import from it.

**Revised order**: Steps 1 and 3 swap — key_builder before storage/base.

---

## Step 2: Create `trueconf/fsm/key_builder.py` — StorageKey + KeyBuilder + DefaultKeyBuilder

**File**: `trueconf/fsm/key_builder.py` (new)

```python
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
```

No external dependencies. Pure dataclass + protocol.

**Note**: `chat_id` and `user_id` are always strings. In TrueConf API, IDs are strings like `"user@server"`. `DefaultKeyBuilder` converts to `str` to normalize input types.

---

## Step 3: Create `trueconf/fsm/storage/base.py` — BaseStorage ABC

**File**: `trueconf/fsm/storage/base.py` (new)

```python
from abc import ABC, abstractmethod
from typing import Any
from trueconf.fsm.key_builder import StorageKey


class BaseStorage(ABC):
    @abstractmethod
    async def get_state(self, key: StorageKey) -> str | None: ...

    @abstractmethod
    async def set_state(self, key: StorageKey, state: str | None) -> None: ...

    @abstractmethod
    async def get_data(self, key: StorageKey) -> dict[str, Any]: ...

    @abstractmethod
    async def set_data(self, key: StorageKey, data: dict[str, Any]) -> None: ...

    @abstractmethod
    async def update_data(self, key: StorageKey, updates: dict[str, Any]) -> dict[str, Any]: ...

    @abstractmethod
    async def clear(self, key: StorageKey) -> None: ...

    async def close(self) -> None:
        pass
```

Depends on: `key_builder.StorageKey` (Step 2).

---

## Step 4: Create `trueconf/fsm/storage/memory.py` — MemoryStorage

**File**: `trueconf/fsm/storage/memory.py` (new)

```python
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any
from trueconf.fsm.key_builder import StorageKey
from trueconf.fsm.storage.base import BaseStorage


@dataclass
class _Record:
    state: str | None = None
    data: dict[str, Any] = field(default_factory=dict)


class MemoryStorage(BaseStorage):
    def __init__(self) -> None:
        self._records: dict[StorageKey, _Record] = {}

    def _get_or_create(self, key: StorageKey) -> _Record:
        if key not in self._records:
            self._records[key] = _Record()
        return self._records[key]

    async def get_state(self, key: StorageKey) -> str | None:
        record = self._records.get(key)
        return record.state if record else None

    async def set_state(self, key: StorageKey, state: str | None) -> None:
        self._get_or_create(key).state = state

    async def get_data(self, key: StorageKey) -> dict[str, Any]:
        record = self._records.get(key)
        return record.data.copy() if record else {}

    async def set_data(self, key: StorageKey, data: dict[str, Any]) -> None:
        self._get_or_create(key).data = data.copy()

    async def update_data(self, key: StorageKey, updates: dict[str, Any]) -> dict[str, Any]:
        record = self._get_or_create(key)
        record.data.update(updates)
        return record.data.copy()

    async def clear(self, key: StorageKey) -> None:
        self._records.pop(key, None)
```

Depends on: `storage.base.BaseStorage`, `key_builder.StorageKey`.

---

## Step 5: Create `trueconf/fsm/storage/__init__.py`

**File**: `trueconf/fsm/storage/__init__.py` (new)

```python
from trueconf.fsm.storage.base import BaseStorage
from trueconf.fsm.storage.memory import MemoryStorage

__all__ = ("BaseStorage", "MemoryStorage")
```

---

## Step 6: Create `trueconf/fsm/state.py` — State + StatesGroup

**File**: `trueconf/fsm/state.py` (new)

```python
from __future__ import annotations
from typing import Any


class State:
    def __init__(self, state: str | None = None) -> None:
        self._custom_state = state
        self._name: str | None = None
        self._group: type[StatesGroup] | None = None

    def bind(self, group: type[StatesGroup], name: str) -> None:
        if self._group is not None or self._name is not None:
            raise RuntimeError(
                f"State '{self._name}' is already bound to {self._group}. "
                f"Cannot rebind to {group.__name__}:{name}."
            )
        self._group = group
        self._name = name

    def __str__(self) -> str:
        if self._custom_state is not None:
            return self._custom_state
        if self._group is None or self._name is None:
            raise RuntimeError(
                "State is not bound to a StatesGroup. "
                "Use State inside a StatesGroup class definition, "
                "or pass a custom string: State('my:state')."
            )
        return f"{self._group.__name__}:{self._name}"

    def __repr__(self) -> str:
        return f"State({str(self)!r})"

    def __eq__(self, other: object) -> bool:
        if isinstance(other, State):
            return str(self) == str(other)
        if isinstance(other, str):
            return str(self) == other
        return NotImplemented

    def __hash__(self) -> int:
        return hash(str(self))


class _StatesGroupMeta(type):
    def __new__(
        mcs,
        name: str,
        bases: tuple[type, ...],
        namespace: dict[str, Any],
    ) -> _StatesGroupMeta:
        state_names = [
            key for key, value in namespace.items()
            if isinstance(value, State)
        ]
        cls = super().__new__(mcs, name, bases, namespace)
        states: list[State] = []
        for key in state_names:
            state = getattr(cls, key)
            state.bind(cls, key)
            states.append(state)
        cls.__states__ = tuple(states)
        return cls


class StatesGroup(metaclass=_StatesGroupMeta):
    __states__: tuple[State, ...] = ()
```

No external dependencies.

---

## Step 7: Create `trueconf/fsm/context.py` — FSMContext

**File**: `trueconf/fsm/context.py` (new)

```python
from __future__ import annotations
from typing import Any
from trueconf.fsm.key_builder import StorageKey
from trueconf.fsm.state import State
from trueconf.fsm.storage.base import BaseStorage


class FSMContext:
    def __init__(self, storage: BaseStorage, key: StorageKey) -> None:
        self._storage = storage
        self._key = key

    @property
    def key(self) -> StorageKey:
        return self._key

    async def get_state(self) -> str | None:
        return await self._storage.get_state(self._key)

    async def set_state(self, state: State | str | None) -> None:
        value = str(state) if isinstance(state, State) else state
        await self._storage.set_state(self._key, value)

    async def get_data(self) -> dict[str, Any]:
        return await self._storage.get_data(self._key)

    async def set_data(self, data: dict[str, Any]) -> None:
        await self._storage.set_data(self._key, data)

    async def update_data(self, **kwargs: Any) -> dict[str, Any]:
        return await self._storage.update_data(self._key, kwargs)

    async def clear(self) -> None:
        await self._storage.clear(self._key)
```

Depends on: `storage.base.BaseStorage`, `key_builder.StorageKey`, `state.State`.

---

## Step 8: Create `trueconf/fsm/manager.py` — FSMManager

**File**: `trueconf/fsm/manager.py` (new)

```python
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
```

Depends on: `context.FSMContext`, `key_builder.*`, `storage.*`.

---

## Step 9: Create `trueconf/fsm/middleware.py` — FSMMiddleware

**File**: `trueconf/fsm/middleware.py` (new)

```python
from __future__ import annotations
from typing import Any
from trueconf.middleware import BaseMiddleware
from trueconf.fsm.manager import FSMManager


class FSMMiddleware(BaseMiddleware):
    def __init__(self, fsm_manager: FSMManager) -> None:
        self._manager = fsm_manager

    async def __call__(
        self,
        handler: Any,
        event: Any,
        data: dict[str, Any],
    ) -> None:
        bot = data.get("bot")
        if bot is not None:
            data["state"] = self._manager.get_context(bot, event)
        return await handler(event, data)
```

Depends on: `middleware.BaseMiddleware`, `manager.FSMMiddleware`.

---

## Step 10: Create `trueconf/fsm/filters.py` — StateFilter

**File**: `trueconf/fsm/filters.py` (new)

```python
from __future__ import annotations
from typing import Any
from trueconf.fsm.context import FSMContext
from trueconf.fsm.state import State


class StateFilter:
    def __init__(self, *states: State | str | None) -> None:
        self._states: set[str | None] = {
            str(s) if isinstance(s, State) else s for s in states
        }

    async def __call__(
        self,
        event: Any,
        *,
        state: FSMContext | None = None,
    ) -> bool:
        if state is None:
            raise RuntimeError(
                "StateFilter requires FSMContext in data['state'], but it was not found. "
                "Make sure FSMMiddleware is registered as outer middleware "
                "before any StateFilter is evaluated."
            )
        current = await state.get_state()
        return current in self._states
```

Depends on: `context.FSMContext`, `state.State`.

---

## Step 11: Create `trueconf/fsm/__init__.py` — public exports

**File**: `trueconf/fsm/__init__.py` (new)

```python
from trueconf.fsm.state import State, StatesGroup
from trueconf.fsm.context import FSMContext
from trueconf.fsm.filters import StateFilter
from trueconf.fsm.manager import FSMManager
from trueconf.fsm.key_builder import StorageKey, KeyBuilder, DefaultKeyBuilder

__all__ = (
    "State",
    "StatesGroup",
    "FSMContext",
    "StateFilter",
    "FSMManager",
    "StorageKey",
    "KeyBuilder",
    "DefaultKeyBuilder",
)
```

---

## Step 12: Modify `trueconf/dispatcher/dispatcher.py` — Dispatcher integration

**File**: `trueconf/dispatcher/dispatcher.py` (modify)

Changes:
1. Add imports for FSM types
2. Extend `__init__` with `storage`, `fsm_manager`, `key_builder` keyword args
3. Add `setup_fsm()` method
4. FSMMiddleware is inserted at position 0 of `_outer_middlewares`

```python
from __future__ import annotations
from typing import TYPE_CHECKING, Any, Awaitable, Callable, Dict, List
from trueconf.filters.base import Event
from trueconf.dispatcher.router import Router

if TYPE_CHECKING:
    from trueconf.fsm.manager import FSMManager
    from trueconf.fsm.key_builder import KeyBuilder
    from trueconf.fsm.storage.base import BaseStorage

MiddlewareHandler = Callable[[Event, Dict[str, Any]], Awaitable[None]]


class Dispatcher(Router):
    def __init__(
        self,
        *,
        storage: "BaseStorage | None" = None,
        fsm_manager: "FSMManager | None" = None,
        key_builder: "KeyBuilder | None" = None,
    ):
        super().__init__(name="dispatcher")
        self.routers: List[Router] = []
        self.fsm: "FSMManager | None" = None

        if fsm_manager is not None and storage is not None:
            raise ValueError("Pass either fsm_manager or storage, not both")

        if fsm_manager is not None:
            self.setup_fsm(fsm_manager=fsm_manager)
        elif storage is not None:
            self.setup_fsm(storage=storage, key_builder=key_builder)

    def setup_fsm(
        self,
        *,
        fsm_manager: "FSMManager | None" = None,
        storage: "BaseStorage | None" = None,
        key_builder: "KeyBuilder | None" = None,
    ) -> "FSMManager":
        from trueconf.fsm.manager import FSMManager
        from trueconf.fsm.storage.memory import MemoryStorage
        from trueconf.fsm.key_builder import DefaultKeyBuilder
        from trueconf.fsm.middleware import FSMMiddleware

        if self.fsm is not None:
            raise RuntimeError(
                "FSM is already configured for this Dispatcher. "
                "Call setup_fsm() only once, or create a new Dispatcher."
            )

        if fsm_manager is None:
            fsm_manager = FSMManager(
                storage=storage or MemoryStorage(),
                key_builder=key_builder or DefaultKeyBuilder(),
            )

        self.fsm = fsm_manager
        self._outer_middlewares.insert(0, FSMMiddleware(fsm_manager))
        return fsm_manager

    # ... include_router and _feed_update unchanged ...
```

**Lazy imports** in `setup_fsm()` avoid circular import issues and keep FSM optional — if user never calls `setup_fsm()` or passes `storage=`, the FSM modules are never loaded.

---

## Step 13: Modify `trueconf/dispatcher/router.py` — `_apply_filter` expansion + kwargs merge + State sugar

**File**: `trueconf/dispatcher/router.py` (modify)

### Change 1: `_register` — auto-wrap `State` with `StateFilter`

Add sugar so `@router.message(Form.name)` works as shorthand for `@router.message(StateFilter(Form.name))`:

```python
# CURRENT (line 116):
def _register(self, filters: Tuple[FilterLike, ...]):

# NEW:
def _register(self, filters: Tuple[FilterLike, ...]):
    # Sugar: State instances are auto-wrapped with StateFilter
    from trueconf.fsm.state import State
    from trueconf.fsm.filters import StateFilter
    filters = tuple(
        StateFilter(f) if isinstance(f, State) else f
        for f in filters
    )
    # ... rest unchanged
```

This is backward-compatible — existing filter tuples without `State` are unchanged.

### Change 2: `_apply_filter` signature and body

```python
# CURRENT (line 232):
async def _apply_filter(self, f: Filter | Any, event: Event) -> bool:

# NEW:
async def _apply_filter(self, f: Filter | Any, event: Event, data: dict[str, Any] | None = None) -> bool:
```

Full new body:

```python
async def _apply_filter(self, f: Filter | Any, event: Event, data: dict[str, Any] | None = None) -> bool:
    """Evaluate a filter against the event, passing matching kwargs from data."""
    data = data or {}

    if isinstance(f, MagicFilter):
        try:
            return bool(f.resolve(event))
        except Exception:
            return False

    # Resolve which kwargs from data the filter accepts
    kwargs: dict[str, Any] = {}
    has_var_kwargs = False
    try:
        sig = inspect.signature(f)
        for name, param in sig.parameters.items():
            if param.kind == inspect.Parameter.VAR_KEYWORD:
                has_var_kwargs = True
                continue
            if name in data and param.kind in (
                inspect.Parameter.POSITIONAL_OR_KEYWORD,
                inspect.Parameter.KEYWORD_ONLY,
            ):
                kwargs[name] = data[name]
    except (ValueError, TypeError):
        pass

    # If filter accepts **kwargs, pass all remaining data
    if has_var_kwargs:
        kwargs.update({k: v for k, v in data.items() if k not in kwargs})

    # Regular filters: let exceptions propagate (config errors must be explicit)
    res = f(event, **kwargs) if kwargs else f(event)

    if inspect.isawaitable(res):
        res = await res

    if isinstance(res, (bool, dict)):
        return res
    return bool(res)
```

**Key changes from original plan:**
- Regular filter exceptions are **NOT caught** — `RuntimeError` from `StateFilter` (missing FSMContext) propagates explicitly
- Only `MagicFilter` catches exceptions (attribute resolution failures are normal)
- `has_var_kwargs` check — filters with `**kwargs` receive all of `data`

### Change 3: `_core()` — pass `ctx` to `_apply_filter` and merge data into handler kwargs

In `_core()` (around lines 151-192), two changes:

```python
# CURRENT line 162:
result = await self._apply_filter(f, evt)

# NEW:
result = await self._apply_filter(f, evt, ctx)
```

```python
# CURRENT lines 175-184:
if matched:
    handler_found = True
    # ...
    async def _inner_base(ievt: Event, ictx: Dict[str, Any]) -> None:
        self._spawn(handler, ievt, filters_str, **kwargs)

# NEW:
if matched:
    handler_found = True
    # Merge data dict (bot, state, etc.) with filter-returned kwargs
    all_kwargs: dict[str, Any] = {**ctx, **kwargs}
    # ...
    async def _inner_base(ievt: Event, ictx: Dict[str, Any]) -> None:
        self._spawn(handler, ievt, filters_str, **all_kwargs)
```

This allows `state: FSMContext` and `bot: Bot` to reach handlers via the existing signature-inspection in `_register`'s `async_wrapper`.

---

## Step 14: Update `trueconf/__init__.py` — export FSM types

**File**: `trueconf/__init__.py` (modify)

No changes needed to top-level `__init__.py` — FSM types live under `trueconf.fsm` and are imported by users directly:

```python
from trueconf.fsm import FSMContext, State, StatesGroup, StateFilter
```

However, if we want to make `StateFilter` available from `trueconf.filters`, add to `trueconf/filters/__init__.py`:

```python
# Optional: re-export for convenience
from trueconf.fsm.filters import StateFilter
```

**Decision**: Do NOT pollute `trueconf.filters` with FSM types. Users import from `trueconf.fsm`. Keep boundaries clean.

---

## Step 15: Create `tests/test_fsm.py` — comprehensive tests

**File**: `tests/test_fsm.py` (new)

Tests covering:

1. **State declaration** — `str(Form.name) == "Form:name"`, custom state, unbound error, `__states__`
2. **MemoryStorage** — get/set state, set_state(None) keeps data, clear removes all, update_data merges, different keys independent
3. **FSMContext** — full lifecycle: get_state → set_state → update_data → get_data → clear; set_state with State object
4. **StateFilter** — matches current state, rejects wrong state, matches None, multiple states, raises without FSMContext, State object as arg
5. **FSMMiddleware** — injects state into data, no bot skips injection
6. **Dispatcher integration** — setup_fsm registers middleware, middleware is first in chain, StateFilter works in pipeline, rejects wrong state
7. **DefaultKeyBuilder** — builds key from Message event, raises on missing fields
8. **StorageKey** — equality, hashing, frozen

Use existing test patterns from `tests/test_middleware.py` (pytest.mark.anyio, `_make_message` helper).

---

## Step 16: Run tests and lint

```bash
cd /Users/baadzianton/TrueConf/python-trueconf-bot
python -m pytest tests/test_fsm.py -v
python -m pytest tests/ -v  # ensure no regressions
```

If the project has a lint/typecheck command (check pyproject.toml), run it too.

---

## Execution Order Summary

| Step | File | Action |
|------|------|--------|
| 1 | `trueconf/fsm/__init__.py` | create (empty initially) |
| 2 | `trueconf/fsm/key_builder.py` | create |
| 3 | `trueconf/fsm/storage/base.py` | create |
| 4 | `trueconf/fsm/storage/memory.py` | create |
| 5 | `trueconf/fsm/storage/__init__.py` | create |
| 6 | `trueconf/fsm/state.py` | create |
| 7 | `trueconf/fsm/context.py` | create |
| 8 | `trueconf/fsm/manager.py` | create |
| 9 | `trueconf/fsm/middleware.py` | create |
| 10 | `trueconf/fsm/filters.py` | create |
| 11 | `trueconf/fsm/__init__.py` | update with exports |
| 12 | `trueconf/dispatcher/dispatcher.py` | modify |
| 13 | `trueconf/dispatcher/router.py` | modify |
| 14 | `tests/test_fsm.py` | create |
| 15 | run tests | verify |

---

## Risk Areas

1. **Circular imports**: `fsm/storage/base.py` imports from `fsm/key_builder.py`. Both are in `trueconf.fsm.*`. No issue — `key_builder` has no imports from `fsm`. `fsm/middleware.py` imports `BaseMiddleware` from `trueconf.middleware` — no issue. `dispatcher.py` uses lazy imports in `setup_fsm()` to avoid circular deps.

2. **`_apply_filter` backward compatibility**: Existing filters (`Command`, `InstanceOfFilter`, `MethodFilter`, `MessageFilter`, `MagicFilter`) accept only `(event)`. The new signature inspection will find no matching kwargs in `data` for them, so `f(event)` is called — identical to current behavior. Exception: existing filters that raise exceptions will now propagate instead of being swallowed. This is intentional — configuration errors must be explicit.

3. **Handler kwargs collision**: If `data` contains `"bot"` and a filter also returns `{"bot": ...}`, the filter value wins (`{**ctx, **kwargs}`). This is correct — filter-returned values are more specific.

4. **`asyncio.create_task` in `_spawn`**: Handlers run as fire-and-forget tasks. Middleware post-processing runs after task creation, not completion. This is existing behavior and doesn't change with FSM.

5. **Thread safety of MemoryStorage**: MemoryStorage uses a plain dict. In a single asyncio event loop (which is the intended usage), this is safe. No thread safety needed for v1.

6. **`setup_fsm()` idempotency**: Guard prevents double-registration of FSMMiddleware. Calling `setup_fsm()` twice raises `RuntimeError`. This is intentional for v1 — if dynamic reconfiguration is needed later, it can be added.
