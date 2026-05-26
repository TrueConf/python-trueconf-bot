# FSM (Finite State Machine) Design Spec

## Overview

Implement a declarative FSM system for `python-trueconf-bot`. Handlers are filtered by conversation state; per-user/per-chat data persists across messages via pluggable storage.

## Goals

- Declarative `StatesGroup` + `State` definitions
- `FSMContext` as async facade over pluggable storage
- `StateFilter` for routing handlers by current state
- `FSMMiddleware` injects `FSMContext` into `data["state"]` before filters run
- `MemoryStorage` as first implementation; `RedisStorage`/`PostgresStorage` possible later without API changes

## Non-Goals (v1)

- Sugar syntax `@router.message(Form.name)` — explicit `StateFilter` only
- Redis/Postgres/SQLite implementations
- State transition graphs / validation
- Nested `StatesGroup`

---

## Architecture

### Pipeline integration

Current pipeline:
```
Dispatcher._feed_update(event, {"bot": self})
  → dispatcher outer middleware
    → router._feed()
      → router outer middleware
        → filter matching  (currently: filters get only `event`, not `data`)
          → router inner middleware
            → handler(event, **filter_kwargs)
```

Two changes required:

1. **FSMMiddleware as outer middleware** — runs before filters, creates `FSMContext`, places in `data["state"]`
2. **`_apply_filter` signature expansion** — filters receive `data` kwargs via signature inspection (backward-compatible)

### Ownership

```
Dispatcher
  └── FSMMiddleware (outer middleware, registered first)
        └── FSMManager
              ├── Storage (owns the data)
              └── KeyBuilder (builds StorageKey from bot + event)
```

- `Dispatcher` connects FSM to pipeline. Does not store states or know storage details.
- `FSMManager` owns `Storage` + `KeyBuilder`. Creates `FSMContext` instances.
- `FSMContext` — per-request facade. Holds reference to storage + key, no state of its own.
- `Storage` — owns data. Knows nothing about `State`/`StatesGroup`.

---

## File Structure

```
trueconf/
  fsm/
    __init__.py           # Public re-exports
    state.py              # State, StatesGroup, _StatesGroupMeta
    context.py            # FSMContext
    manager.py            # FSMManager
    key_builder.py        # StorageKey, KeyBuilder protocol, DefaultKeyBuilder
    middleware.py          # FSMMiddleware
    filters.py            # StateFilter
    storage/
      __init__.py         # Re-exports BaseStorage, MemoryStorage
      base.py             # BaseStorage (ABC)
      memory.py           # MemoryStorage
```

---

## Component Specifications

### 1. State and StatesGroup

```python
class State:
    def __init__(self, state: str | None = None):
        self._custom_state = state
        self._name: str | None = None
        self._group: type[StatesGroup] | None = None

    def bind(self, group: type["StatesGroup"], name: str) -> None:
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

    def __eq__(self, other):
        if isinstance(other, State): return str(self) == str(other)
        if isinstance(other, str): return str(self) == other
        return NotImplemented

    def __hash__(self): return hash(str(self))


class _StatesGroupMeta(type):
    def __new__(mcs, name, bases, namespace):
        state_names = [k for k, v in namespace.items() if isinstance(v, State)]
        cls = super().__new__(mcs, name, bases, namespace)
        states = []
        for key in state_names:
            state = getattr(cls, key)
            state.bind(cls, key)
            states.append(state)
        cls.__states__ = tuple(states)
        return cls


class StatesGroup(metaclass=_StatesGroupMeta):
    __states__: tuple[State, ...] = ()
```

```python
class Form(StatesGroup):
    name = State()
    age = State()
    confirm = State()

str(Form.name)    # "Form:name"
str(Form.age)     # "Form:age"
Form.__states__   # (State("Form:name"), State("Form:age"), State("Form:confirm"))
```

### 2. StorageKey and KeyBuilder

```python
@dataclass(frozen=True, slots=True)
class StorageKey:
    bot_id: str | None
    chat_id: str
    user_id: str
    destiny: str = "default"


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

- `bot_id` is optional — some deployments may not need it in the key.
- `chat_id` and `user_id` are required — missing them is a configuration error, not a silent fallback.
- `destiny` allows partitioning within the same user/chat.

### 3. BaseStorage and MemoryStorage

```python
class BaseStorage(ABC):
    """Contract:
      - set_state(None) resets state but keeps data.
      - clear() removes both state and data for the key.
    """

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
        pass  # For Redis/Postgres — release connections
```

```python
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

    async def get_state(self, key):
        r = self._records.get(key)
        return r.state if r else None

    async def set_state(self, key, state):
        self._get_or_create(key).state = state

    async def get_data(self, key):
        r = self._records.get(key)
        return r.data.copy() if r else {}

    async def set_data(self, key, data):
        self._get_or_create(key).data = data.copy()

    async def update_data(self, key, updates):
        r = self._get_or_create(key)
        r.data.update(updates)
        return r.data.copy()

    async def clear(self, key):
        self._records.pop(key, None)
```

| Operation | Effect on state | Effect on data |
|-----------|----------------|----------------|
| `set_state("X")` | sets to `"X"` | unchanged |
| `set_state(None)` | clears state | unchanged |
| `set_data({...})` | unchanged | replaces entirely |
| `update_data(k=v)` | unchanged | merges keys |
| `clear()` | removes key | removes key |

### 4. FSMContext

```python
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

### 5. FSMManager

```python
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

### 6. FSMMiddleware

```python
class FSMMiddleware(BaseMiddleware):
    def __init__(self, fsm_manager: FSMManager) -> None:
        self._manager = fsm_manager

    async def __call__(self, handler, event, data):
        bot = data.get("bot")
        if bot is not None:
            data["state"] = self._manager.get_context(bot, event)
        return await handler(event, data)
```

Does not store state, does not choose handlers, does not know about `StatesGroup`.

### 7. StateFilter

```python
class StateFilter:
    def __init__(self, *states: State | str | None) -> None:
        self._states: set[str | None] = {
            str(s) if isinstance(s, State) else s for s in states
        }

    async def __call__(self, event, *, state: FSMContext | None = None) -> bool:
        if state is None:
            raise RuntimeError(
                "StateFilter requires FSMContext in data['state'], but it was not found. "
                "Make sure FSMMiddleware is registered as outer middleware "
                "before any StateFilter is evaluated."
            )
        current = await state.get_state()
        return current in self._states
```

- `state is None` (middleware not registered) → `RuntimeError`. Config errors must be explicit.
- `StateFilter(None)` matches when `await state.get_state()` returns `None`.

### 8. Dispatcher Integration

```python
class Dispatcher(Router):
    def __init__(
        self,
        *,
        storage: BaseStorage | None = None,
        fsm_manager: FSMManager | None = None,
        key_builder: KeyBuilder | None = None,
    ):
        super().__init__(name="dispatcher")
        self.routers: list[Router] = []
        self.fsm: FSMManager | None = None

        if fsm_manager is not None and storage is not None:
            raise ValueError("Pass either fsm_manager or storage, not both")
        if fsm_manager is not None:
            self.setup_fsm(fsm_manager=fsm_manager)
        elif storage is not None:
            self.setup_fsm(storage=storage, key_builder=key_builder)

    def setup_fsm(
        self,
        *,
        fsm_manager: FSMManager | None = None,
        storage: BaseStorage | None = None,
        key_builder: KeyBuilder | None = None,
    ) -> FSMManager:
        if fsm_manager is None:
            fsm_manager = FSMManager(
                storage=storage or MemoryStorage(),
                key_builder=key_builder or DefaultKeyBuilder(),
            )
        self.fsm = fsm_manager
        self._outer_middlewares.insert(0, FSMMiddleware(fsm_manager))
        return fsm_manager
```

**Order guarantee:** `insert(0, ...)` puts FSMMiddleware first. User middlewares are appended via `.outer_middleware()` → `.append()`. FSMMiddleware always runs before any user middleware.

### 9. `_apply_filter` Expansion

```python
async def _apply_filter(self, f, event, data=None):
    data = data or {}

    if isinstance(f, MagicFilter):
        try: return bool(f.resolve(event))
        except Exception: return False

    kwargs = {}
    try:
        sig = inspect.signature(f)
        for name, param in sig.parameters.items():
            if name in data and param.kind in (
                inspect.Parameter.POSITIONAL_OR_KEYWORD,
                inspect.Parameter.KEYWORD_ONLY,
            ):
                kwargs[name] = data[name]
    except (ValueError, TypeError):
        pass

    try:
        res = f(event, **kwargs) if kwargs else f(event)
    except Exception:
        return False

    if inspect.isawaitable(res):
        try: res = await res
        except Exception: return False

    if isinstance(res, (bool, dict)):
        return res
    return bool(res)
```

**Backward compatible:** existing filters accepting only `(event)` get no extra kwargs.

**Handler kwargs injection** — merge `data` into filter kwargs in `_core()`:

```python
# In _core(), when filter matched:
all_kwargs = {**ctx, **kwargs}  # data + filter-returned dicts
```

This allows `state: FSMContext` and `bot: Bot` to be injected into handlers via the existing signature-inspection in `_register`.

**Call site change:**
```python
# CURRENT
result = await self._apply_filter(f, evt)
# NEW
result = await self._apply_filter(f, evt, ctx)
```

---

## User-Facing API

### Basic usage

```python
from trueconf import Bot, Dispatcher, Router, F, Message
from trueconf.fsm import FSMContext, State, StatesGroup
from trueconf.fsm.storage.memory import MemoryStorage
from trueconf.filters import Command

class Form(StatesGroup):
    name = State()
    age = State()
    confirm = State()

dp = Dispatcher(storage=MemoryStorage())
router = Router()
dp.include_router(router)

@router.message(Command("start"))
async def cmd_start(msg: Message, state: FSMContext):
    await state.set_state(Form.name)
    await msg.answer("What is your name?")

@router.message(StateFilter(Form.name))
async def process_name(msg: Message, state: FSMContext):
    await state.update_data(name=msg.text)
    await state.set_state(Form.age)
    await msg.answer("How old are you?")

@router.message(StateFilter(Form.age))
async def process_age(msg: Message, state: FSMContext):
    await state.update_data(age=msg.text)
    data = await state.get_data()
    await state.set_state(Form.confirm)
    await msg.answer(f"You are {data['age']}, name {data['name']}. Correct? (yes/no)")

@router.message(StateFilter(Form.confirm), F.text.lower() == "yes")
async def process_confirm(msg: Message, state: FSMContext):
    await state.clear()
    await msg.answer("Thank you!")

@router.message(Command("cancel"))
async def cmd_cancel(msg: Message, state: FSMContext):
    await state.clear()
    await msg.answer("Cancelled.")
```

### Custom KeyBuilder

```python
class TenantKeyBuilder:
    def build(self, bot, event) -> StorageKey:
        return StorageKey(
            bot_id=bot.me_id,
            chat_id=f"{event.tenant_id}:{event.chat_id}",
            user_id=event.author.id,
        )

dp = Dispatcher(storage=MemoryStorage(), key_builder=TenantKeyBuilder())
```

### Explicit FSMManager

```python
fsm = FSMManager(storage=MemoryStorage(), key_builder=DefaultKeyBuilder())
dp = Dispatcher(fsm_manager=fsm)
```

### Matching no state

```python
@router.message(StateFilter(None))
async def handle_no_state(msg: Message, state: FSMContext):
    await msg.answer("You have no active conversation.")
```

---

## Migration Path for Future Storage Backends

```python
# Before
dp = Dispatcher(storage=MemoryStorage())

# After — one line change
from trueconf_fsm_redis import RedisStorage
dp = Dispatcher(storage=RedisStorage(redis_url="redis://localhost"))
```

No changes to `FSMContext`, `FSMMiddleware`, `StateFilter`, `State`, `StatesGroup`.

---

## Open Questions

None.
