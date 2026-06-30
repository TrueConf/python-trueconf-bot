---
title: Middleware
description: Как перехватывать и изменять события до попадания в обработчик
icon: material/layers-triple
---

# Middleware

Middleware — это прослойка, которая перехватывает события **до** того, как они попадут в обработчик. Middleware может логировать, фильтровать, модифицировать данные или полностью блокировать события.

## Зачем нужен middleware

- **Логирование** — записывать каждое входящее событие
- **Проверка доступа** — блокировать события от определённых пользователей
- **Модификация данных** — добавлять дополнительную информацию в контекст события
- **Anti-flood** — ограничивать частоту запросов

## Два типа middleware

В **python-trueconf-bot** существуют два типа middleware, которые выполняются на разных этапах обработки:

### Outer middleware (внешний)

Выполняется **до** проверки фильтров. Позволяет заблокировать событие до того, как оно дойдёт до любого обработчика.

```python
router.outer_middleware(my_middleware)
```

### Inner middleware (внутренний)

Выполняется **после** совпадения фильтров, но **до** вызова самого обработчика. Полезен для проверок, которые нужны только для конкретных хендлеров.

```python
router.inner_middleware(my_middleware)
```

## Порядок выполнения

```
Входящее событие
  → Outer middleware (Dispatcher)
    → Outer middleware (Router)
      → Проверка фильтров
        → Inner middleware (Router)
          → Обработчик (handler)
```

Outer middleware выполняется раньше фильтров. Если outer middleware не вызовет `await handler(event, data)`, событие будет полностью заблокировано — ни фильтры, ни обработчики не запустятся.

## Создание своего middleware

Любой middleware — это класс с методом `__call__`, наследующийся от `BaseMiddleware`:

```python
from trueconf.middleware import BaseMiddleware

class MyMiddleware(BaseMiddleware):
    async def __call__(self, handler, event, data):
        # Код ДО обработчика
        print(f"Получено событие: {event}")

        await handler(event, data)  # ← передаём управление дальше

        # Код ПОСЛЕ обработчика
        print(f"Обработка завершена")
```

!!! note "Важно"
    - Если **не вызвать** `await handler(event, data)`, событие будет заблокировано
    - Код **до** `await handler(...)` выполняется перед обработчиком
    - Код **после** `await handler(...)` выполняется после обработчика

### Пример: логирование всех событий

```python
import logging
from trueconf.middleware import BaseMiddleware

logger = logging.getLogger("bot")

class LoggingMiddleware(BaseMiddleware):
    async def __call__(self, handler, event, data):
        logger.info(f"Входящее событие: {type(event).__name__}")
        await handler(event, data)
        logger.info(f"Событие обработано")

router.outer_middleware(LoggingMiddleware())
```

### Пример: проверка доступа

```python
from trueconf.middleware import BaseMiddleware
from trueconf.types import Message

ALLOWED_USERS = {"admin_user", "moderator_user"}

class AccessMiddleware(BaseMiddleware):
    async def __call__(self, handler, event, data):
        # Проверяем только сообщения
        if not isinstance(event, Message):
            await handler(event, data)
            return

        if event.author.id not in ALLOWED_USERS:
            # Не вызываем handler — событие блокируется
            return

        await handler(event, data)

router.outer_middleware(AccessMiddleware())
```

### Пример: anti-flood

```python
import time
from trueconf.middleware import BaseMiddleware
from trueconf.types import Message

class AntiFloodMiddleware(BaseMiddleware):
    def __init__(self, limit: float = 1.0):
        self.limit = limit
        self.last_message: dict[str, float] = {}

    async def __call__(self, handler, event, data):
        if not isinstance(event, Message):
            await handler(event, data)
            return

        user_id = event.author.id
        now = time.monotonic()

        if user_id in self.last_message:
            elapsed = now - self.last_message[user_id]
            if elapsed < self.limit:
                return  # Блокируем — слишком часто

        self.last_message[user_id] = now
        await handler(event, data)

router.outer_middleware(AntiFloodMiddleware(limit=0.5))
```

## Доступ к данным в middleware

Параметр `data` — это словарь с контекстом события. В нём доступны:

| Ключ | Тип | Описание |
|------|-----|----------|
| `bot` | `Bot` | Экземпляр бота |
| `state` | `FSMContext` | Контекст FSM (если подключён) |
| `raw_state` | `str \| None` | Текущее состояние как строка (если FSM подключён) |

```python
class StateLoggingMiddleware(BaseMiddleware):
    async def __call__(self, handler, event, data):
        state = data.get("raw_state")
        if state:
            print(f"Пользователь в состоянии: {state}")
        await handler(event, data)
```

## SkipSelfMessages

Встроенное middleware, которое игнорирует сообщения, отправленные самим ботом. Предотвращает эхо-циклы при запуске нескольких сессий бота.

```python
from trueconf.middleware import SkipSelfMessages

router.outer_middleware(SkipSelfMessages())
```

!!! info
    При использовании `Bot(skip_self_messages=True)` (по умолчанию) это middleware регистрируется автоматически. Отключить можно параметром `skip_self_messages=False`:

    ```python
    bot = Bot.from_credentials(
        server="your-server",
        username="your-bot",
        password="your-password",
        dispatcher=dp,
        skip_self_messages=False,  # отключить автофильтр
    )
    ```

## Регистрация middleware

### На Router

```python
router = Router()
router.outer_middleware(LoggingMiddleware())
router.inner_middleware(AccessMiddleware())
```

### На Dispatcher

Так как `Dispatcher` наследуется от `Router`, middleware можно регистрировать напрямую на диспетчере:

```python
dp = Dispatcher()
dp.outer_middleware(LoggingMiddleware())
```

Middleware, зарегистрированный на `Dispatcher`, выполняется **до** middleware дочерних роутеров.

### Наследование middleware

При вложенной структуре роутеров middleware **наследуется** от родительского роутера к дочернему:

```python
parent = Router()
parent.outer_middleware(LoggingMiddleware())

child = Router()
parent.include_router(child)
```

В этом случае `child` унаследует `LoggingMiddleware` от `parent`. Цепочка выполнения:

```
LoggingMiddleware (parent) → middleware (child) → фильтры → handler
```

!!! warning "Dispatcher — особый случай"
    `Dispatcher` наследуется от `Router`, но его middleware **не наследуется** дочерними роутерами через `include_router()`. Dispatcher применяет свои middleware отдельно, перед тем как передать событие дочерним роутерам.

## Отличия middleware от фильтров

Middleware и фильтры решают разные задачи. Вот ключевые отличия:

| | Фильтры | Middleware |
|---|---------|-----------|
| **Задача** | Маршрутизация — направить событие к нужному хендлеру | Глобальная обработка — логирование, блокировка, модификация данных |
| **Область действия** | Один конкретный хендлер | Все события сразу |
| **Если не совпал** | Router ищет следующий хендлер | Событие блокируется полностью — ни один хендлер его не получит |
| **Где живёт** | В декораторе хендлера | Регистрируется на Router/Dispatcher отдельно |

### Пример: блокировка фильтром vs блокировка middleware

**Фильтр** — событие просто не попадает в этот хендлер, но может попасть в другой:

```python
# Если текст не "ping" — этот хендлер не сработает,
# но Router проверит следующие хендлеры
@router.message(F.text == "ping")
async def ping(msg: Message):
    await msg.answer("pong")

# Этот хендлер сработает на ВСЕ остальные сообщения
@router.message(F.text)
async def echo(msg: Message):
    await msg.answer(msg.text)
```

**Middleware** — событие блокируется полностью, ни один хендлер его не получит:

```python
class BanMiddleware(BaseMiddleware):
    async def __call__(self, handler, event, data):
        if isinstance(event, Message) and event.author.id == "spammer":
            return  # ← не вызываем handler — событие умирает
        await handler(event, data)

router.outer_middleware(BanMiddleware())
```

### Когда что использовать

**Используйте фильтры**, когда нужно:

- Направить команду `/start` в один хендлер, а текст — в другой
- Проверить конкретное поле сообщения (тип, содержимое, автор)
- Реагировать только на определённые события

**Используйте middleware**, когда нужно:

- Заблокировать пользователя или событие **до** проверки фильтров
- Логировать **все** входящие события
- Ограничить частоту запросов (anti-flood)
- Добавить общие данные в контекст (например, информацию о пользователе из БД)
- Проверить доступ ко **всем** хендлерам сразу
