---
title: Shortcuts
description: How to use shortcut methods on the Message object
icon: material/knife
---

# Shortcuts

## Working with the Message Object

When handling an incoming message, a `Message` object is typically passed to the handler function:

```python
from trueconf import Router
from trueconf.types import Message

r = Router()


@r.message()
async def on_message(message: Message):
    await message.answer("Message received")
```

The `Message` object is injected into the handler automatically and contains the context of the current event: information about the sender, chat, message type, content, message ID, and other parameters.

In addition, the message object provides access to the bot instance that is processing the current event:

```python
@r.message()
async def on_message(message: Message):
    result = await message.bot.get_something()
```

This is useful when the bot instance is defined in another module or declared later in the code, making it unavailable as a direct variable (`bot`) inside the handler.

In such cases, you can access the current bot instance via the message object: `message.bot`.

## Message Shortcuts

The `Message` class provides shortcuts — helper methods that allow you to perform common actions without explicitly passing `chat_id`, `message_id`, and other parameters. These values are automatically taken from the current message.

!!! Note
    Currently, shortcuts are implemented only for the `Message` type.
    Support for other event types may be added in future releases.

For example, instead of calling the bot method directly:

```python hl_lines="3-5"
@r.message()
async def on_message(message: Message):
    await message.bot.send_message(chat_id=message.chat_id, text="Hello!")
```

you can use a shortcut:

```python hl_lines="3"
@r.message()
async def on_message(message: Message):
    await message.answer("Hello!")
```

Shortcuts are especially useful in handlers where actions are tied to the current message or chat.
They make the code more concise and reduce repetition.

For example, `message.answer(...)` automatically uses the chat where the message was received,
while `message.reply(...)` also links the response to the original message.

!!! Tip
    You can find the full list of available shortcuts in the [Message class reference](../reference/Types.md/#trueconf.types.Message).

## Contacts

`Message.contact` returns the contact of the current message as a
[`Contact`](../reference/Types.md/#trueconf.types.contact.Contact) object, or `None` if the
message is not a contact. The result is cached on the message, so a vCard file
is downloaded from the server only once:

```python
contact = await message.contact
```

Two contact formats are recognized:

- **vCard attachment** — a `.vcf` file (`mimeType: text/vcard`). The file is
  downloaded from the server and parsed: the structured `N` field gives the
  first/last name, `TEL` gives the phone number, and the raw vCard text is
  available as `Contact.vcard`.
- **TrueConf contact link** — a text message whose entire content is exactly one
  `<a href="trueconf:login&do=profile">Name</a>` link. `Contact.user_id` holds the
  login and `Contact.first_name` holds the display name fetched from the server
  (falling back to the link text if the user no longer exists).

```python
@r.message()
async def on_message(message: Message):
    contact = await message.contact
    if contact is not None:
        await message.answer(f"{contact.first_name}: {contact.phone_number}")
```

The display name is never split into first/last name: the server-side name
convention (surname-first, given-first, full name) varies per installation, so
`Contact.last_name` stays `None` for TrueConf contacts.

## Geolocation

`Message.location` returns a [`Location`](../reference/Types.md/#trueconf.types.content.location.Location) object for a geolocation message, or `None` for other message types:

```python
@r.message()
async def on_message(message: Message):
    if message.location is not None:
        print(location.latitude, location.longitude, location.title)
```

## Quote

`Message.quote` returns the quoted part of a reply, while `Message.text` contains the message text without the quote block. You can pass the quoted fragment to the `quote` parameter of `message.reply(...)` or `bot.send_message(...)`:

```python
@r.message()
async def on_message(message: Message):
    if message.quote is not None:
        await message.reply("Thank you for the quote!", quote=message.quote)
```

## Voice Messages

`Message.voice` returns a [`Voice`](../reference/Types.md/#trueconf.types.content.voice.Voice) object for a voice message, or `None` for other message types. It provides the same file shortcuts as other attachments: `download()`, `url`, and `preview_url`:

```python
@r.message()
async def on_message(message: Message):
    if message.voice is not None:
        await voice.download(file_path="voice.ogg")
```
