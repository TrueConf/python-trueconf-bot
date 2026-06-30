---
title: Sending messages
description: How to send, reply, forward, and format messages
icon: material/message-text-fast-outline
---

# Sending messages

To send a message, the bot must know the `chat_id` of the target chat: a personal chat, group chat, or channel.

## How to get `chat_id`?

### Personal chats (P2P)

To get the `chat_id` of a personal chat, use [`bot.create_personal_chat(user_id)`](../reference/Bot.md/#trueconf.Bot.create_personal_chat).
If a personal chat with the user does not exist yet, the server will create it.
If the chat already exists, the server will return the existing `chat_id`.

```python
chat = await bot.create_personal_chat(user_id="john_doe@video.example.com")

await bot.send_message(
    chat_id=chat.chat_id,
    text="Hello!",
)
```

### Group chats and channels

Be careful with [group chats](../reference/Bot.md/#trueconf.Bot.create_group_chat) and [channels](../reference/Bot.md/#trueconf.Bot.create_channel). Methods that create group chats and channels always create a new chat:

```python
chat = await bot.create_group_chat(title="Support")
channel = await bot.create_channel(title="News")
```

If you call such a method again with the same title, another chat or channel with the same `title` will be created.
Therefore, after creating a group chat or channel, it is better to save its `chat_id` in a database, configuration file, or another persistent storage.

!!! Question "What if the chat already exists? How do I get its `chat_id`?"

### Finding an existing chat

You can get the list of available chats with [`bot.get_chats()`](../reference/Bot.md/#trueconf.Bot.get_chats):

```python
response = await bot.get_chats(count=10, page=1)
```

The method returns [`GetChatsResponse`](../reference/Responses.md/#trueconf.types.responses.GetChatsResponse) with the `list` parameter containing the list of chats.
You can find the required chat, for example by its title, and get its `chat_id`:

=== "Using a generator"
    ```python
    response = await bot.get_chats(count=100, page=1)
    
    chat = next(
        (chat for chat in response.list if chat.title == "Support"),
        None,
    )
    
    if chat is not None:
        print(chat.chat_id)
    ```

=== "Using a loop"
    ```python
    response = await bot.get_chats(count=100, page=1)
    chat = None

    for item in response.list:
        if item.title == "Support":
            chat = item
            break
    
    if chat is not None:
        print(chat.chat_id)
    ```

After you find the required `chat_id`, it is also recommended to save it so that you do not have to search for the chat again on every application start.

### Getting `chat_id` from an incoming message

Another simple way is to send a message to the target chat and handle it with the bot. In the handler, you can print `message.chat_id`:

```python
from trueconf import Router
from trueconf.types import Message

router = Router()


@router.message()
async def print_chat_id(message: Message):
    print(message.chat_id)
```

This approach is convenient for group chats and channels: add the bot to the required chat, send a message, and check the `chat_id` in the console.

## Text messages

To send a text message, use [`bot.send_message(...)`](../reference/Bot.md/#trueconf.Bot.send_message):

```python
await bot.send_message(
    chat_id="chat_id",
    text="Hello!",
)
```

If you send a message from an incoming message handler, you can use `Message` shortcut methods, such as `message.answer(...)` or `message.reply(...)`.
They automatically use `message.chat_id`, so you do not need to pass it manually. For details, see the [Shortcuts](shortcuts.md) section.

### Replying to a message

If you need to reply to a specific message, pass the source message identifier in the `reply_message_id` parameter:

```python
await bot.send_message(
    chat_id="chat_id",
    text="This is a reply",
    reply_message_id="message_id",
)
```

This approach allows you to send regular messages and replies through a single API.

### Forwarding messages

To forward an existing message, use [`bot.forward_message(...)`](../reference/Bot.md/#trueconf.Bot.forward_message):

```python
await bot.forward_message(
    chat_id="target_chat_id",
    message_id="source_message_id",
)
```

Where:

- `chat_id` is the identifier of the chat where the message should be forwarded;
- `message_id` is the identifier of the message to forward.

### Text formatting

Messages can be sent as plain text, HTML, or Markdown by passing `parse_mode`:

```python
from trueconf.enums import ParseMode

await bot.send_message(
    chat_id="chat_id",
    text="<b>Important</b>",
    parse_mode=ParseMode.HTML,
)
```

For convenient formatted text construction, the library provides the [`trueconf.utils.formatting`](../reference/Formatting.md) module.
It lets you build a message from classes instead of writing HTML or Markdown manually:

```python
from trueconf.enums import ParseMode
from trueconf.utils.formatting import (
    Bold,
    Italic,
    Link,
    Mention,
    Text,
)

content = Text(
    Bold("Important"),
    " message for ",
    Mention("John Doe", user_id="john_doe@video.example.com"),
    "\n",
    Link("Open website", url="https://trueconf.com"),
)

await bot.send_message(
    chat_id="chat_id",
    text=content.as_html(),
    parse_mode=ParseMode.HTML,
)
```

The module supports:

- [`Bold(...)`](../reference/Formatting.md/#trueconf.utils.formatting.Bold)
- [`Italic(...)`](../reference/Formatting.md/#trueconf.utils.formatting.Italic)
- [`Underline(...)`](../reference/Formatting.md/#trueconf.utils.formatting.Underline)
- [`Strikethrough(...)`](../reference/Formatting.md/#trueconf.utils.formatting.Strikethrough)
- [`Link(...)`](../reference/Formatting.md/#trueconf.utils.formatting.Link)
- [`Mention(...)`](../reference/Formatting.md/#trueconf.utils.formatting.Mention)
- [`AllMention()`](../reference/Formatting.md/#trueconf.utils.formatting.AllMention)
- [`Text(...)`](../reference/Formatting.md/#trueconf.utils.formatting.Text)

### Message length limits

TrueConf Server limits text messages to `4096` characters.

If a message exceeds this limit, use the `safe_split_text(...)` helper function.
It safely splits long text while preserving HTML/Markdown markup:

```python
from trueconf.utils import safe_split_text

chunks = safe_split_text(long_text)

for chunk in chunks:
    await bot.send_message(
        chat_id="chat_id",
        text=chunk,
        parse_mode=ParseMode.HTML,
    )
```

For more information about limits, see the [Restrictions](restrictions.md) section.

!!! Tip "Shortcut methods"
    In message handlers, it is often more convenient to use `message.answer(...)`, `message.reply(...)`, and other shortcut methods instead of calling `bot.send_message(...)` directly.
    For details, see the [Shortcuts](shortcuts.md) section.

!!! Tip "Sending files"
    This section covers text messages.
    To send documents, images, videos, voice messages, and other attachments, see the [Working with files](files.md) section.
