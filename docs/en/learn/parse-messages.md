# Handling Requests

## Router

Whenever a user interacts with the bot — for example, via a direct message, or when the bot is added to a group chat or channel — the bot receives an **update** from the server.

To process these events, the `Router` is used. It defines which functions should be triggered upon receiving a specific type of update. This allows you to centrally manage the logic for handling various types of messages:

```python
from trueconf import Router

r = Router()
```

To handle an update with the [`SendMessage` method](https://trueconf.com/docs/chatbot-connector/en/server-requests/#new-message-in-chat), the handler function is wrapped with a decorator:

```python
@r.message()
async def on_message(message): ...
```

## Filter Support

Routers support filters based on the [magic-filter](https://github.com/aiogram/magic-filter) library using the `F` object:

```python
from trueconf import F
```

Filters allow you to process only those updates that match specific conditions. For example:

```python
# Messages that contain text
@r.message(F.text)
async def on_message(message): ...

# Messages that contain images
@r.message(F.photo)
async def on_photo(message): ...

# Messages from a specific user
@r.message(F.from_user.id == "elisa")
async def on_elisa(message): ...
```

!!! Tip
    You can find more detailed examples of filter usage in the [Filter section](filters.md).

## Dispatcher

All created routers must be added to the dispatcher (`Dispatcher`).
It combines all handlers and manages update routing:

```python
from trueconf import Dispatcher

dp = Dispatcher()
dp.include_router(r)
```

## Handler Priorities

* Routers and their handlers are checked in the order they were added via `Dispatcher.include_router()`.
* Inside a single router, handlers are evaluated in the order they are declared.
* Upon the first filter match, the handler is executed and no further handlers are checked (default behavior).

This means that if you have multiple handlers with the same filter:

```python
@r.message(F.text == "Hello")
async def handler1(message):
    await message.answer("First")

@r.message(F.text == "Hello")
async def handler2(message):
    await message.answer("Second")
```

Then **only `handler1`** will be triggered, and `handler2` will be ignored.

To trigger both handlers, use different filters or combine the logic inside a single handler function.

!!! Tip
    For better logic separation, it's recommended to create multiple routers (e.g., `commands_router`, `messages_router`, `admin_router`) and include them in the dispatcher in the desired order. This helps organize your code and simplifies bot maintenance.

## Code Organization Best Practices

* Typically, routers are placed in separate modules (e.g., `handlers/messages.py`) and included in the main bot module via `include_router`.
* This helps separate handlers by responsibility: messages, photos, commands, etc.
* The dispatcher (`Dispatcher`) can be viewed as the central managing component that coordinates the logic for handling all incoming events.
