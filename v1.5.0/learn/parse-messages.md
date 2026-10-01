# Handling Requests⚓︎

## Router⚓︎

Whenever a user interacts with the bot — for example, via a direct message, or when the bot is added to a group chat or channel — the bot receives an update from the server.

To process these events, the `Router` is used. It defines which functions should be triggered upon receiving a specific type of update. This allows you to centrally manage the logic for handling various types of messages:

UnnamedNamed

```
from trueconf import Router

r = Router()
```

```
from trueconf import Router

r = Router(name="Router1")
```

To handle updates, the handler function is wrapped with a decorator. For example, to process the `SendMessage` event, use the `@.message()` decorator:

```
@r.message()
async def on_message(message): ...
```

`@r.message()` receives user messages only. To receive system Envelopes, enable `receive_system_messages` when creating the bot and register a separate handler:

```
from trueconf import Bot, F
from trueconf.enums import MessageType
from trueconf.types import SystemMessage

bot = Bot(
server="video.example.net",
token="JWT-token",
receive_system_messages=True,
)

@r.system_message(F.type == MessageType.CLEAR_CHAT_HISTORY)
async def on_history_cleared(message: SystemMessage):
print(message.content.for_all)
```

System Envelopes may be present in `get_chat_history()` results regardless of the `receive_system_messages` setting.

### Replied-to message⚓︎

When an incoming message is a reply, its `reply_message` field contains the directly referenced `Message` object:

```
@r.message()
async def on_message(message):
if message.reply_message is not None:
print(message.reply_message.text)
```

The server expands only one level of the reply chain. If the referenced message is itself a reply, its `reply_message_id` is populated while its `reply_message` remains `None`. Load the next level explicitly when needed:

```
quoted = message.reply_message

if quoted is not None and quoted.reply_message_id is not None:
previous = await bot.get_message_by_id(quoted.reply_message_id)
```

### Filter support⚓︎

Routers support filters based on the magic-filter library using the `F` object:

```
from trueconf import F
```

Filters allow you to handle only those events (incoming updates) that match specific conditions. For example:

Text messageImageMessage from a specific user

```
from trueconf import Router, F

r = Router()

@r.message(F.text)
async def on_message(message): ...
```

```
from trueconf import Router, F

r = Router()

@r.message(F.photo)
async def on_photo(message): ...
```

```
from trueconf import Router, F

r = Router()

@r.message(F.from_user.id == "elisa")
async def on_elisa(message): ...
```

Tip

You can find more detailed examples of filter usage in the Filter section.

## Registering routers in the dispatcher⚓︎

All created routers must be registered with the main event handler — the `Dispatcher`. It is responsible for объединяет the handlers and manages routing for incoming updates:

```
from trueconf import Dispatcher

dp = Dispatcher()
dp.include_router(r)
```

As a rule, you may have many routers, but only one dispatcher:

```
from trueconf import Bot, Router, Dispatcher

r1 = Router()
r2 = Router()
r3 = Router()
r4 = Router()

dp = Dispatcher()

dp.include_router(r1)
dp.include_router(r2)
dp.include_router(r3)
dp.include_router(r4)

bot = Bot(token="JWT-token", dispatcher=dp)
```

### Dynamic routers⚓︎

We have looked at an example of creating a simple router that is defined in code in advance:

```
from trueconf import Router, F

r = Router()

@r.message(F.from_user.id == "elisa")
async def on_elisa(message): ...
```

But what if you need to handle an event whose condition is not known beforehand? This is where dynamic router registration (or dynamic routers) comes in. As you have already seen, registering a handler is done via a decorator (`@`).

Note

A decorator is a wrapper function that binds your code to a specific event. It “wraps” the handler function and registers it in the system so that when the event (trigger) occurs, the system knows exactly which code to run.

To register a router dynamically, use a functional decorator call — i.e., apply it without the `@decorator` syntax sugar.

```
async def handle_message() ...

@r.message(Command("start"))
async def on_report(msg: Message):
dynamic_r = Router()
dp.include_router(dynamic_r)
dynamic_r.message(F.from_user.id == msg.from_user.id)(handle_message)
```

Example

You can find a detailed example using a dynamic router in our GitHub.

### Removing a router from the dispatcher⚓︎

Removing (deactivating) a router is typically needed when a dynamic router was created for a user and is no longer required. The dispatcher keeps a list of all registered routers in `dp.routers`. Accordingly, if you assigned a name like `Router(name="Cool")`, you can remove it as follows:

```
for router in dp.routers[:]: # (1)!
if router.name == "Cool":
dp.routers.remove(router)
```

- We iterate over a slice (a copy) of the list so the for loop does not break when an element is removed.

### Parallel and child routers⚓︎

Routers can also be:

- independent roots, which receive the same event sequentially regardless of each other's result;

- child routers, which form an ordered tree of fallback routes.

Take a look at the diagram. When a new event arrives from the server, the dispatcher will process it as follows:

- Send it for handling to Router 1.

- Check the condition of the first handler, Handler 1. If it matches, proceed to Router 2. If it does not, check the next handler, Handler 2.

- Regardless of whether any handlers in Router 1 matched, the dispatcher proceeds to execute Router 2.

In Router 2, as shown, there are two child routers: Router 2.3 is a descendant of Router 2.2, and Router 2.2 is a descendant of Router 2.

Here, the event will be processed as follows:

- If nothing matches in Router 2, then move on to Router 2.2.

- If nothing matches in Router 2.2, then move on to Router 2.3.

As a result, Handler 2 from Router 2.3 will run only if no previous handler matched.

If a parent has multiple child routers, they are checked in registration order. Once a child or one of its descendants handles the event, the remaining sibling branches are not checked. By default, children are not visited after their parent handles the event; `Router(allow_child_on_event=True)` enables that propagation.

## Handler priorities⚓︎

- Independent root routers run in the order they were added via `Dispatcher.include_router()`, and every root receives the event.

- Child routers are checked in `Router.include_router()` order until the first tree handles the event.

- Inside a single router, handlers are evaluated in the order they are declared.

- Upon the first filter match, the handler is executed and no further handlers are checked (default behavior).

This means that if you have multiple handlers with the same filter:

```
@r.message(F.text == "Hello")
async def handler1(message):
await message.answer("First")

@r.message(F.text == "Hello")
async def handler2(message):
await message.answer("Second")
```

Then only `handler1` will be triggered, and `handler2` will be ignored.

To trigger both handlers, use different filters or combine the logic inside a single handler function.

Tip

For better logic separation, it's recommended to create multiple routers (e.g., `commands_router`, `messages_router`, `admin_router`) and include them in the dispatcher in the desired order. This helps organize your code and simplifies bot maintenance.

## Code Organization Best Practices⚓︎

- Typically, routers are placed in separate modules (e.g., `handlers/messages.py`) and included in the main bot module via `include_router`.

- This helps separate handlers by responsibility: messages, photos, commands, etc.

- The dispatcher (`Dispatcher`) can be viewed as the central managing component that coordinates the logic for handling all incoming events.

October 1, 2026

September 3, 2025
