# Middleware⚓︎

Middleware is a layer that intercepts events before they reach a handler. Middleware can log, filter, modify data, or completely block events.

## Why middleware is needed⚓︎

- Logging — record every incoming event

- Access control — block events from specific users

- Data modification — add additional information to the event context

- Anti-flood — limit request frequency

## Two types of middleware⚓︎

In python-trueconf-bot, there are two types of middleware that run at different stages of event processing:

### Outer middleware⚓︎

Runs before filters are checked. It allows you to block an event before it reaches any handler.

```
router.outer_middleware(my_middleware)
```

### Inner middleware⚓︎

Runs after filters match, but before the handler itself is called. It is useful for checks that are needed only for specific handlers.

```
router.inner_middleware(my_middleware)
```

## Execution order⚓︎

```
Incoming event
→ Outer middleware (Dispatcher)
→ Outer middleware (Router)
→ Filter checks
→ Inner middleware (Router)
→ Handler
```

Outer middleware runs before filters. If an outer middleware does not call `await handler(event, data)`, the event will be completely blocked — neither filters nor handlers will run.

## Creating custom middleware⚓︎

Any middleware is a class with a `__call__` method that inherits from `BaseMiddleware`:

```
from trueconf.middleware import BaseMiddleware

class MyMiddleware(BaseMiddleware):
async def __call__(self, handler, event, data):
# Code BEFORE the handler
print(f"Event received: {event}")

await handler(event, data) # ← pass control further down the chain

# Code AFTER the handler
print(f"Processing completed")
```

Important

- If you do not call `await handler(event, data)`, the event will be blocked

- Code before `await handler(...)` runs before the handler

- Code after `await handler(...)` runs after the handler

### Example: logging all events⚓︎

```
import logging
from trueconf.middleware import BaseMiddleware

logger = logging.getLogger("bot")

class LoggingMiddleware(BaseMiddleware):
async def __call__(self, handler, event, data):
logger.info(f"Incoming event: {type(event).__name__}")
await handler(event, data)
logger.info(f"Event processed")

router.outer_middleware(LoggingMiddleware())
```

### Example: access control⚓︎

```
from trueconf.middleware import BaseMiddleware
from trueconf.types import Message

ALLOWED_USERS = {"admin_user", "moderator_user"}

class AccessMiddleware(BaseMiddleware):
async def __call__(self, handler, event, data):
# Check only messages
if not isinstance(event, Message):
await handler(event, data)
return

if event.author.id not in ALLOWED_USERS:
# Do not call handler — the event is blocked
return

await handler(event, data)

router.outer_middleware(AccessMiddleware())
```

### Example: anti-flood⚓︎

```
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
if elapsed before middleware from child routers.

### Middleware inheritance⚓︎

In a nested router structure, middleware is inherited from a parent router by child routers:

```
parent = Router()
parent.outer_middleware(LoggingMiddleware())

child = Router()
parent.include_router(child)
```

In this case, `child` inherits `LoggingMiddleware` from `parent`. Execution chain:

```
LoggingMiddleware (parent) → middleware (child) → filters → handler
```

Dispatcher is a special case

`Dispatcher` inherits from `Router`, but its middleware is not inherited by child routers via `include_router()`. The dispatcher applies its middleware separately before passing the event to child routers.

## Differences between middleware and filters⚓︎

Middleware and filters solve different problems. Here are the key differences:

| | Filters | Middleware |
| --- | --- | --- |
| Purpose | Routing — direct an event to the appropriate handler | Global processing — logging, blocking, data modification |
| Scope | One specific handler | All events at once |
| If it does not match | Router looks for the next handler | The event is fully blocked — no handler receives it |
| Where it lives | In the handler decorator | Registered separately on Router/Dispatcher |

### Example: blocking with a filter vs blocking with middleware⚓︎

Filter — the event simply does not reach this handler, but it may reach another one:

```
# If the text is not "ping", this handler will not run,
# but Router will check the next handlers
@router.message(F.text == "ping")
async def ping(msg: Message):
await msg.answer("pong")

# This handler will run for ALL other messages
@router.message(F.text)
async def echo(msg: Message):
await msg.answer(msg.text)
```

Middleware — the event is blocked completely; no handler receives it:

```
class BanMiddleware(BaseMiddleware):
async def __call__(self, handler, event, data):
if isinstance(event, Message) and event.author.id == "spammer":
return # ← do not call handler — the event dies here
await handler(event, data)

router.outer_middleware(BanMiddleware())
```

### When to use which⚓︎

Use filters when you need to:

- Route the `/start` command to one handler and text messages to another

- Check a specific message field, such as type, content, or author

- Respond only to certain events

Use middleware when you need to:

- Block a user or event before filters are checked

- Log all incoming events

- Limit request frequency (anti-flood)

- Add shared data to the context, such as user information from a database

- Check access to all handlers at once

June 30, 2026

June 11, 2026
