# Class `Router`⚓︎

Here is the reference information for the `Router` class, including all its parameters, attributes, and methods.
You can import the `Router` class directly from the `trueconf` package:

```
from trueconf import Router
```

## `` trueconf.Router ⚓︎

```
Router(name=None, allow_child_on_event=False, _parent=None)
```

Event router for handling incoming events in a structured and extensible way.

A `Router` allows you to register event handlers with specific filters, such as message types, chat events, or custom logic.

You can also include nested routers using `include_router()` to build modular and reusable event structures.

Handlers can be registered for:

- Messages (`@.message(...)`)

- Chat creation events (`@.created_personal_chat()`, `@.created_group_chat()`, `@.created_channel()`)

- Participant events (`@.added_chat_participant()`, `@.removed_chat_participant()`)

- Message lifecycle events (`@.edited_message()`, `@.removed_message()`)

- File upload events (`@.uploading_progress()`)

- Removed chats (`@.removed_chat()`)

Example:

```
router = Router()

@router.message(F.text == "hello")
async def handle_hello(msg: Message):
await msg.answer("Hi there!")
```

If you have multiple routers, use `.include_router()` to add them to a parent router.

### `` allow_child_on_event `instance-attribute` ⚓︎

```
allow_child_on_event = allow_child_on_event
```

### `` name `instance-attribute` ⚓︎

```
name = name or hex(id(self))
```

### `` added_chat_participant ⚓︎

```
added_chat_participant(*filters)
```

Register a handler when a participant is added to a chat.

### `` changed_file_upload_limits ⚓︎

```
changed_file_upload_limits(*filters)
```

Requires TrueConf Server 5.5.3+ Registers a handler for file upload limits change events.

This handler is triggered when the server's file upload restrictions are updated. The event is represented by the `ChangedFileUploadLimits` type and may include:

- `max_size` — the maximum allowed file size in bytes (`1 MB = 1000 bytes`). If the size limit is disabled, the value is `None`.

- `extensions` — file extension restrictions. If extension filtering is disabled, the value is `None`.

If `extensions` is provided, it contains: - `mode` — restriction mode: - `block` — blocked extensions (blacklist) - `allow` — allowed extensions (whitelist) - `list` — list of file extensions.

### Source

trueconf.com/docs/chatbot-connector/en/files/#newFileUploadLimits

Parameters:

| Name | Type | Description | Default |
| --- | --- | --- | --- |
| `*filters` | `FilterLike` | Optional filters to apply to the event. Multiple filters can be specified. | `()` |

Returns:

| Name | Type | Description |
| --- | --- | --- |
| `Callable` | | A decorator function for registering the handler. |

### Example

```
from trueconf.types import ChangedFileUploadLimits
@router.changed_file_upload_limits()
async def on_limits_changed(event: ChangedFileUploadLimits):
print(f"Max file size: {event.max_size}")
if event.extensions:
print(f"Mode: {event.extensions.mode}")
print(f"Extensions: {event.extensions.list}")
```

### `` changed_participant_role ⚓︎

```
changed_participant_role(*filters)
```

Requires TrueConf Server 5.5.2+ Registers a handler for participant role change events in chats.

This handler is triggered when a user's role is changed in a personal chat, group chat, channel, or conference chat. Used with the `ChangedParticipantRole` event type.

### Source

trueconf.com/docs/chatbot-connector/en/chats/#changedParticipantRole

Parameters:

| Name | Type | Description | Default |
| --- | --- | --- | --- |
| `*filters` | `FilterLike` | Optional filters to apply to the event. Multiple filters can be specified. | `()` |

Returns:

| Name | Type | Description |
| --- | --- | --- |
| `Callable` | | A decorator function for registering the handler. |

### Example

```
from trueconf.enums import ChatParticipantRole as role
from trueconf.types import ChangedParticipantRole

@router.changed_participant_role()
async def on_role_changed(event: ChangedParticipantRole):
if event.role == role.admin:
print(f"{event.user_id} has been promoted to admin in chat {event.chat_id}")
```

### `` cleared_chat_history ⚓︎

```
cleared_chat_history(*filters)
```

Requires TrueConf Server 5.5.3+ Registers a handler for chat history clearing events.

This handler is triggered when the message history of a chat is cleared. Used with the `ClearedChatHistory` event type.

### Source

trueconf.com/docs/chatbot-connector/en/chats/#clearedHistory

Parameters:

| Name | Type | Description | Default |
| --- | --- | --- | --- |
| `*filters` | `FilterLike` | Optional filters to apply to the event. Multiple filters can be specified. | `()` |

Returns:

| Name | Type | Description |
| --- | --- | --- |
| `Callable` | | A decorator function for registering the handler. |

### Example

```
from trueconf.types import ClearedChatHistory
@router.cleared_chat_history()
async def on_history_cleared(event: ClearedChatHistory):
print(f"History was cleared in chat {event.chat_id}. For all: {event.for_all}")
```

### `` created_channel ⚓︎

```
created_channel(*filters)
```

Register a handler for channel creation events.

### `` created_favorites_chat ⚓︎

```
created_favorites_chat(*filters)
```

Requires TrueConf Server 5.5.2+. Register a handler for favorites chat creation events.

### `` created_group_chat ⚓︎

```
created_group_chat(*filters)
```

Register a handler for group chat creation events.

### `` created_personal_chat ⚓︎

```
created_personal_chat(*filters)
```

Register a handler for personal chat creation events.

### `` edited_chat_avatar ⚓︎

```
edited_chat_avatar(*filters)
```

Requires TrueConf Server 5.5.3+ Registers a handler for chat avatar edit events.

This handler is triggered when a chat avatar is changed. Used with the `EditedChatAvatar` event type.

### Source

trueconf.com/docs/chatbot-connector/en/chats/#editedChatAvatar

Parameters:

| Name | Type | Description | Default |
| --- | --- | --- | --- |
| `*filters` | `FilterLike` | Optional filters to apply to the event. Multiple filters can be specified. | `()` |

Returns:

| Name | Type | Description |
| --- | --- | --- |
| `Callable` | | A decorator function for registering the handler. |

### Example

```
from trueconf.types import EditedChatAvatar
@router.edited_chat_avatar()
async def on_avatar_changed(event: EditedChatAvatar):
print(f"Avatar was updated in chat {event.chat_id}")
print(f"New avatar: {event.avatar_url}")
```

### `` edited_chat_title ⚓︎

```
edited_chat_title(*filters)
```

Requires TrueConf Server 5.5.3+ Registers a handler for chat title edit events.

This handler is triggered when a chat title is changed. Used with the `EditedChatTitle` event type.

### Source

trueconf.com/docs/chatbot-connector/en/chats/#editedChatTitle

Parameters:

| Name | Type | Description | Default |
| --- | --- | --- | --- |
| `*filters` | `FilterLike` | Optional filters to apply to the event. Multiple filters can be specified. | `()` |

Returns:

| Name | Type | Description |
| --- | --- | --- |
| `Callable` | | A decorator function for registering the handler. |

### Example

```
from trueconf.types import EditedChatTitle
@router.edited_chat_title()
async def on_title_changed(event: EditedChatTitle):
print(f"Chat {event.chat_id} has a new title: {event.title}")
```

### `` edited_message ⚓︎

```
edited_message(*filters)
```

Register a handler for message edit events.

### `` event ⚓︎

```
event(method, *filters)
```

Register a handler for a generic event type, filtered by method name.

Examples:

```
>>> @r.event(F.method == "SendMessage")
>>> async def handle_message(msg: Message): ...
```

### `` include_router ⚓︎

```
include_router(router)
```

Include a child router for hierarchical event routing.

### `` inner_middleware ⚓︎

```
inner_middleware(middleware)
```

Register inner middleware (runs after filter match, before handler).

### `` message ⚓︎

```
message(*filters)
```

Register a handler for incoming `Message` events.

### `` outer_middleware ⚓︎

```
outer_middleware(middleware)
```

Register outer middleware (runs before filter/handler matching).

### `` removed_chat ⚓︎

```
removed_chat(*filters)
```

Register a handler when a chat is removed.

### `` removed_chat_participant ⚓︎

```
removed_chat_participant(*filters)
```

Register a handler when a participant is removed from a chat.

### `` removed_message ⚓︎

```
removed_message(*filters)
```

Register a handler for message deletion events.

### `` uploading_progress ⚓︎

```
uploading_progress(*filters)
```

Register a handler for file uploading progress events.

June 30, 2026

September 3, 2025
