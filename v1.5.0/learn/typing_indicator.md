# Chat activity indicator⚓︎

While the bot processes a request, you can show its status in the chat: for example, that it is typing a message.

## One-shot activity⚓︎

Use `bot.send_chat_activity(...)` to send a single activity event:

```
from trueconf.enums import ChatActivity

await bot.send_chat_activity(
chat_id="chat_id",
activity_type=ChatActivity.TYPING,
)
```

Available activity types are listed in the `ChatActivity` enum:

- `ChatActivity.TYPING` — the bot is typing;

- `ChatActivity.CHOOSING_STICKER` — the bot is choosing a sticker;

- `ChatActivity.UPLOADING_FILE` — the bot is uploading a file.

The indicator expires

The server shows the indicator only for a short time. For long operations, re-send the activity periodically — use `ChatActivitySender` described below.

## Keeping the indicator visible⚓︎

`ChatActivitySender` is an async context manager that periodically re-sends the activity in the background while the operation runs:

```
from trueconf.utils.chat_activity import ChatActivitySender

async with ChatActivitySender.typing(bot=bot, chat_id=chat_id):
result = await generate_text_answer()
```

The sender re-sends the activity at the cadence returned by the server: each response carries `retryAfter` in milliseconds, and the sender waits that long before the next send.

`ChatActivitySender` also accepts the generic `activity` argument, so you can use any value from the `ChatActivity` enum:

```
from trueconf.enums import ChatActivity

async with ChatActivitySender(bot=bot, chat_id=chat_id, activity=ChatActivity.UPLOADING_FILE):
await upload_large_file()
```

October 1, 2026

October 1, 2026
