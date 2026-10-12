# Chat activity

## `` trueconf.utils.chat_activity ⚓︎

### `` DEFAULT_INITIAL_SLEEP `module-attribute` ⚓︎

```
DEFAULT_INITIAL_SLEEP = 0.0
```

### `` ChatActivitySender ⚓︎

```
ChatActivitySender(
*,
bot,
chat_id,
activity= TYPING

class-attribute
instance-attribute
(trueconf.enums.chat_activity.ChatActivity.TYPING)' href=../Enums/#trueconf.enums.ChatActivity.TYPING>TYPING,
initial_sleep= DEFAULT_INITIAL_SLEEP

module-attribute
(trueconf.utils.chat_activity.DEFAULT_INITIAL_SLEEP)' href=#trueconf.utils.chat_activity.DEFAULT_INITIAL_SLEEP>DEFAULT_INITIAL_SLEEP,
)
```

Sends a chat activity (for example, typing) in the background until a long operation finishes.

The TrueConf server shows the activity indicator only for a short time, so it needs to be re-sent periodically. This utility starts a background task that re-sends the activity while the context is active. The cadence is taken from the server: each response carries `retryAfter` in milliseconds, and the sender waits that long before the next send.

Examples:

```
>>> async with ChatActivitySender.typing(bot=bot, chat_id=chat_id):
>>> await generate_text_answer()
```

Parameters:

| Name | Type | Description | Default |
| --- | --- | --- | --- |
| `bot` | `` trueconf.Bot (`trueconf.client.bot.Bot`)' href=../Bot/#trueconf.Bot>Bot | Instance of the bot used to send activities. | required |
| `chat_id` | `str` | Identifier of the target chat. | required |
| `activity` | `` ChatActivity (`trueconf.enums.chat_activity.ChatActivity`)' href=../Enums/#trueconf.enums.ChatActivity>ChatActivity | str | Activity type to show. Defaults to typing. | `` TYPING

`class-attribute`
`instance-attribute`
(`trueconf.enums.chat_activity.ChatActivity.TYPING`)' href=../Enums/#trueconf.enums.ChatActivity.TYPING>TYPING |
| `initial_sleep` | `float` | Delay before the first send in seconds. Defaults to 0.0. | `` DEFAULT_INITIAL_SLEEP

`module-attribute`
(`trueconf.utils.chat_activity.DEFAULT_INITIAL_SLEEP`)' href=#trueconf.utils.chat_activity.DEFAULT_INITIAL_SLEEP>DEFAULT_INITIAL_SLEEP |

#### `` activity `instance-attribute` ⚓︎

```
activity = activity
```

#### `` bot `instance-attribute` ⚓︎

```
bot = bot
```

#### `` chat_id `instance-attribute` ⚓︎

```
chat_id = chat_id
```

#### `` initial_sleep `instance-attribute` ⚓︎

```
initial_sleep = initial_sleep
```

#### `` running `property` ⚓︎

```
running
```

#### `` typing `classmethod` ⚓︎

```
typing(bot, chat_id, **kwargs)
```

Create an instance of the sender with the `typing` activity.

October 1, 2026

October 1, 2026
