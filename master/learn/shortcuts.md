# Shortcuts⚓︎

## Working with the Message Object⚓︎

When handling an incoming message, a `Message` object is typically passed to the handler function:

```
from trueconf import Router
from trueconf.types import Message

r = Router()

@r.message()
async def on_message(message: Message):
await message.answer("Message received")
```

The `Message` object is injected into the handler automatically and contains the context of the current event: information about the sender, chat, message type, content, message ID, and other parameters.

In addition, the message object provides access to the bot instance that is processing the current event:

```
@r.message()
async def on_message(message: Message):
result = await message.bot.get_something()
```

This is useful when the bot instance is defined in another module or declared later in the code, making it unavailable as a direct variable (`bot`) inside the handler.

In such cases, you can access the current bot instance via the message object: `message.bot`.

## Message Shortcuts⚓︎

The `Message` class provides shortcuts — helper methods that allow you to perform common actions without explicitly passing `chat_id`, `message_id`, and other parameters. These values are automatically taken from the current message.

Note

Currently, shortcuts are implemented only for the `Message` type. Support for other event types may be added in future releases.

For example, instead of calling the bot method directly:

```
@r.message()
async def on_message(message: Message):
await message.bot.send_message(
chat_id=message.chat_id,
text="Hello!"
)
```

you can use a shortcut:

```
@r.message()
async def on_message(message: Message):
await message.answer("Hello!")
```

Shortcuts are especially useful in handlers where actions are tied to the current message or chat. They make the code more concise and reduce repetition.

For example, `message.answer(...)` automatically uses the chat where the message was received, while `message.reply(...)` also links the response to the original message.

Tip

You can find the full list of available shortcuts in the Message class reference.

June 30, 2026

May 5, 2026
