---
title: Release notes
---

# List of Changes

## 1.1.1

**Added:**

- New classes for working with files: `FSInputFile`, `BufferedInputFile`,
`URLInputFile`. More details can be found in the
[documentation](learn/files.md).
- Support for displaying message history `display_history = True` when [adding a
user](reference/Bot.md/#trueconf.Bot.add_participant_to_chat) to a group chat
or channel.
- Support for request and event for:
   - role changes in a group chat or channel
([request](reference/Bot.md/#trueconf.Bot.change_participant_role),
[notification](reference/Router.md/#trueconf.Router.changed_participant_role));
   - creation of the “Favorites” chat
([request](reference/Bot.md/#trueconf.Bot.create_favorites_chat),
[notification](reference/Router.md/#trueconf.Router.created_favorites_chat)).
- Ability to send files with a caption.
- Shortcut `.save_to_favorites()` for quickly saving a message to the "Favorites"
chat.
- The asynchronous property `await bot.me`, which returns the `chat_id` of the
"Saved Messages" chat.

**Fixed:**

- Stickers sent via `bot.send_sticker()` were displayed with a background due to
an incorrect MIME type.
- The method `.remove_participant_from_chat()` did not work when an incomplete
TrueConf ID was specified.
- Error unpacking the participant list due to an incorrect alias.
- Sometimes, when obtaining a token using `.from_credentials()`, a
`400 Bad Requests` error would occur when using a digit password.

**Modified:**

- The `bot.server_name` property has become asynchronous. Use it as
`await bot.server_name`.

## 1.0.0

🎉 **First Release!**

- Stable version of the python-trueconf-bot library.
- Support for all major TrueConf ChatBot API methods.
- Aliases and keyboard shortcuts in the aiogram style (message.answer,
message.reply, etc.).
- Asynchronous data transmission via the WebSocket protocol.
- Working with files (sending and uploading).
- Documentation: trueconf.github.io/python-trueconf-bot/
- PyPI: https://pypi.org/project/python-trueconf-bot/
