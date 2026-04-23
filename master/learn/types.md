# Data Types⚓︎

When developing applications, it is especially important that the IDE provides hints about available methods and class parameters. However, the router (Router) passes different data types to handlers, and the IDE cannot always correctly determine their type. Therefore, it needs a hint about which specific object is being passed.

In python-trueconf-bot, this is handled by the `trueconf.types` package, which describes all incoming server events and requests (notifications). For responses to client requests, a separate module is provided — `trueconf.types.responses`.

Thus:

- when working with events, use types from `trueconf.types`;

- when working with client request results, use types from `trueconf.types.responses`.

This ensures:

- IDE autocompletion (hints for attributes and methods);

- static type checking with mypy or similar tools;

- more convenient code and documentation navigation.

## Example Usage⚓︎

Suppose you want to handle an event about adding a new participant to a chat (1):

- According to the API, this request has `"method": "addChatParticipant"`.

```
from trueconf import Router

r = Router()

@r.added_chat_participant()
async def on_added_user(event): ...
```

To enable the IDE to provide hints about the available attributes of the `event` object, you need to specify the correct data type:

```
from trueconf import Router
from trueconf.types import AddedChatParticipant

r = Router()

@r.added_chat_participant()
async def on_added_user(event: AddedChatParticipant):
who_add = event.added_by
```

In this example:

- `AddedChatParticipant` describes the structure of the incoming event,

- you get convenient IDE autocompletion,

- with static type checking tools (e.g., mypy), the correctness of field access is automatically verified.

## “Raw” event⚓︎

When using the `@.event` decorator, you gain access to all fields of the event object, including those that are usually hidden when converting JSON into a class:

```
{
"method": "name",
"type": 1,
"id": 11,
"payload": {}
}
```

In this case, it is better to use `trueconf.types.Update`, which describes the structure of the full update received from the server.

```
from trueconf import Router
from trueconf.types import Update
from trueconf.enums import IncomingUpdateMethod

r = Router()

@r.event()
async def raw_event(event: Update):
if event.method == IncomingUpdateMethod.MESSAGE:
pass

# Alternatively, without importing enum
if event.method == "SendMessage":
pass
```
