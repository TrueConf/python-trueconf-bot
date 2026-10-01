---
title: Release notes
description: Changelog — features, fixes, and deprecations
icon: material/note-text
---

# List of Changes

## 1.5.0

🚀 **Major release!** This is not only a set of new features, but also extensive work on stability.

!!! Tip
    Support for Python 3.10 ends on 31.10.2026, together with the end of its official support by the Python Software Foundation.

**Added:**

- Support for incoming voice messages with the `MessageType.VOICE_MESSAGE` (`205`) type
- Support for inline buttons via `InlineKeyboardMarkup`/`InlineKeyboardButton` (actions: command, URL, message, copy). Requires TrueConf Server 5.5.6 and TrueConf client apps for Windows, macOS and Linux version 8.6.0, TrueConf for Android 3.3.0, TrueConf for iOS 4.2.0
- Callback queries for handling button presses: the `@router.callback_query()` handler, `callback_query.edit_message(...)` and `callback_query.answer(...)` shortcuts
- Buttons with `wait_reply=True` and the `answerCommand` method temporarily raise `NotImplementedError`: the functionality is supported by TrueConf Server but awaits support from client applications. Once it becomes available, a new release will be published that removes this limitation
- Chat object: the `chat` field with the `Chat` model in `Message` and `LastMessage`
- Message replies: incoming reply messages now include `Message.reply_message` with the content of the original message being replied to
- System messages: the `SystemMessage` model and the `@router.system_message()` handler
- Reply with a quote via the `quote` parameter in `Message.reply()` and `Bot.send_message()`, as well as the `Message.quote` property
- Chat activity indicator: the `Bot.send_chat_activity()` method, the `ChatActivity` enum and the `ChatActivitySender.typing(...)` context manager
- In-memory file download size limit via the `max_in_memory_download_size` parameter
- The `LineBreak` node in `trueconf.utils.formatting` (`<br>` for HTML, `\n` for Markdown)
- The `message.location` and `message.contact` shortcuts for geolocation and contacts (vCard files and trueconf links)
- OAuth2 authentication via `Bot.from_oauth()` for servers with login/password authentication disabled. Requires TrueConf Server 5.5.3+
- New exceptions: `WSConnectionError`, `InMemoryDownloadLimitExceededError`, `FileUploadError`, `OAuthMissingScopeError`, `PasswordAuthDisabledError`
- Text descriptions for API error codes (399, 400–408) in `ApiError.message()`. Codes 400–408 relate to files and replace the single generic code 310 (“error while sending”) — now it is clear what exactly went wrong during the send
- The `caption_message_id` field in `SendFileResponse` — the ID of the caption message sent with a file; allows changing the file caption via `edit_message(...)`
- A custom `User-Agent` on all library requests in the format `python-trueconf-bot/<version> (Python/<version>; <OS>/<release>)`, e.g.: `python-trueconf-bot/1.5.0 (Python/3.12.4; Darwin/24.0.0)`

**Changed:**

- The `Underline` node in `trueconf.utils.formatting` now also renders in Markdown (`__text__`) — previously underline worked only in HTML markup
- File download: the `file_path` parameter sets the exact output path, parent directories are created automatically
- The `mimetype` parameter was renamed to `mime_type`
- `ws_max_retries`/`ws_max_delay` behavior: once the attempts are exhausted, the connection ends with `WSConnectionError`
- Bot shutdown now waits for running handlers and closes the WebSocket transport; a `timeout` parameter was added to `shutdown()`
- The HTTP client was migrated from `httpx` to `httpx2`

**Fixed:**

- Parsing of system messages in chat history and API responses
- File upload errors: the caller now receives `FileUploadError` with the original cause
- Infinite WebSocket reconnection after the retry limit is exhausted
- The WebSocket connection was not closed on bot shutdown — the session now properly closes the attached socket
- Download URLs and tokens no longer appear in logs in full: the query string is stripped from URLs (`https://server/.../files/download?token=...` → `https://server/.../files/download`), and tokens in debug logs are truncated to the last 30 characters
- Token acquisition in `Bot.from_credentials()` now respects the `https` and `web_port` parameters — previously the token was always requested via https:443, even if the server runs on http or a non-standard port

**Deprecated:**

- The `Message.chat_id` property — use `message.chat.chat_id` instead
- The `dest_path` parameter — use `file_path` instead (will be removed in version 2.0)
- The `mimetype` parameter — use `mime_type` instead

## 1.4.4

**Fixed:**

- Fixed a library (bot) crash occurring when the LastMessage contained a notification about a chat avatar change [#15](https://github.com/TrueConf/python-trueconf-bot/issues/15).

## 1.4.3

**Fixed:**

- Checking server version. Currently, the check is performed via the API first; if an error occurs, the check is based on the TrueConf service status.

## 1.4.2

**Fixed:**

- Bot crash when server version field is empty

## 1.4.1

**Added:**

- New parameter `timeout` in class `Bot` and `Bot.from_credentials()` method

**Fixed:**

- System events like `ChangedFileUploadLimits` don't have chat_id or author, which caused `DefaultKeyBuilder` to raise `RuntimeError`. Now `FSMMiddleware` checks for `chat_id/user_id` before building FSM context. System events pass through without FSM context.

**Refactor:**

- Improve network timeout logic for file download and upload:
    - Remove hardcoded `chunk_size` from `httpx.stream` to prevent false ReadTimeout on slow networks.
    - Configure `aiohttp.ClientTimeout` using `sock_read` instead of `total` to allow long file uploads without socket freezes.
    - Enforce strict `int | float` types for timeouts, removing redundant `None` checks
    - Update method docstrings to clearly reflect adaptive timeout behavior.

## 1.4.0

**Added:**

- **FSM (Finite State Machine)** — a finite state machine mechanism. It allows you to implement step-by-step dialogs, such as questionnaires, forms, and setup wizards.  
States are declared declaratively using `StatesGroup`/`State`, while data is stored in `FSMContext`. It supports nested groups, multiple storage strategies, and state-based filtering via `StateFilter`. Learn more: [FSM](learn/fsm.md).
- **Middleware** — a layer for processing events before and after handlers.  
It allows you to log events, block them, check access, and modify data.  
It supports two types: outer middleware, which runs before filters, and inner middleware, which runs after filters. Learn more: [Middleware](learn/middleware.md).
- **The `skip_self_messages` parameter** in `Bot()`. By default, it is set to `True`, so the bot automatically ignores messages sent by itself.  
It can be disabled with `skip_self_messages=False`.
- Added `Message.reply_message`, containing the full message being replied to.
- Added the `SystemMessage` model for system Envelopes in live updates and chat history, together with the
  `@router.system_message()` handler.

**Fixed:**

- The history-clearing notification now preserves `for_all` as the server-provided `bool` value.

## 1.3.0

**Added:**

- Added a health-check mechanism for tracking the bot connection state:
    - push model via the `Bot(on_health_check=func_callback)` callback, which is called when the connection status changes;
    - pull model via the `bot.health_check()` method, which returns the current bot state;
    - `connected`, `authorized`, and `disconnected` statuses.
- Added `bot.me_id` support for storing the authorized bot identifier.
- Added the `message.mention` shortcut, which returns `True` if the current bot is mentioned in the message or if `@all` is used.
- Added the `trueconf.utils.formatting` module for convenient HTML/Markdown message construction with classes: `Text`, `Bold`, `Italic`, `Underline`, `Strikethrough`, `Link`, `Mention`, `AllMention`.
- Added the `truststore` dependency for working with the system trusted certificate store.
- Added the `SSLVerify` type for unified typing of the `verify_ssl` parameter: `bool | str | ssl.SSLContext`.
- Added the `bot.me_chat` property as the new name for getting the `chat_id` of the "Favorites" chat.

**Changed:**

- Updated the `verify_ssl` behavior:
    - `verify_ssl=True` uses the system trusted certificate store through `truststore`;
    - `verify_ssl=False` disables certificate verification;
    - `verify_ssl="/path/to/ca.pem"` uses a custom CA bundle;
    - `verify_ssl=ssl.SSLContext(...)` uses the provided SSL context.
- Updated the SSL logic for WebSocket connections: a single `self.ssl_context`, created via `build_ssl_context(...)`, is now used.
- Updated bot initialization logging: logs now include human-readable information about the SSL context.

**Fixed:**

- Fixed failures caused by incomplete certificate chains. Certificate chains can now be verified successfully by using the system trusted certificate store through `truststore` or by passing a custom SSL context.

**Deprecated:**

- The asynchronous `bot.me` property, which returns the `chat_id` of the "Favorites" chat, is now deprecated. Use `await bot.me_chat` instead.

**Documentation:**

- Added Context7 AI Assistant: interactive support for code and documentation.
- Added a new **Sending messages** documentation section covering:
    - getting `chat_id`;
    - sending text messages via `bot.send_message(...)`;
    - replying with `reply_message_id`;
    - forwarding messages via `bot.forward_message(...)`;
    - text formatting via `trueconf.utils.formatting`;
    - the 4096-character message length limit and using `safe_split_text(...)`.
- Added health-check documentation covering:
    - push model via callback;
    - pull model via `bot.health_check()`;
    - an example of combined usage with an HTTP health endpoint.
- Added and updated docstrings for the formatting module, `Message.mention`, `verify_ssl`, and the health-check API.
- Added new sections: **Shortcuts**, **Restrictions**, **Formatting**, **Exceptions**.



## 1.2.3

**Added:**

- Added a 10-second server response timeout. If no response is received within the timeout, an `asyncio.TimeoutError` is raised: `Request to {self.__api_method__} timed out after {timeout}s` ([#12](https://github.com/TrueConf/python-trueconf-bot/issues/12)).

**Fixed:**

- Fixed cases where Mashumaro failed to parse a response, which could cause the application to crash ([#8](https://github.com/TrueConf/python-trueconf-bot/issues/8), [#11](https://github.com/TrueConf/python-trueconf-bot/issues/11)).

## 1.2.2

**Fixed:**

- Fixed a missing dependency: the `packaging` package, which is required to check the library version at bot startup.

## 1.2.1

**Added:**

- Added support for TrueConf Server 5.5.4.
- Added the `receive_system_messages` flag to `Bot()` and `Bot.from_credentials()` to enable or disable receiving system messages.
- Added the new `bot.get_chat_participant()` method, which replaces `bot.has_chat_participant()`.

**Fixed:**

- Fixed support for TrueConf Server 5.5.3+. Removed an unnecessary version check that prevented the code from running with library version 1.2.0.
- Fixed documentation links to `llms.txt` and `llms-full.txt`.

**Changed:**

- When retrieving file information via `bot.get_file_info(file_id=...)`, the response now returns the `file_id` field instead of `info_hash`.

**Deprecated:**

- The `bot.has_chat_participant()` method has been deprecated. Use `bot.get_chat_participant()` instead.

## 1.2.0

**Added:**

- Added support for TrueConf Server 5.5.3, including:
  - chat title editing with `bot.edit_chat_title(...)`;
  - chat avatar editing with `bot.edit_chat_avatar(...)`;
  - chat history clearing with `bot.clear_chat_history(...)`;
  - retrieving file storage limits with `bot.get_file_info_upload_limits(...)`;
  - a new file transfer approach where the `file_name` parameter is now required for `FSInputFile(...)` and other file upload methods.
- Added caching for file storage limit settings. These settings are now used for pre-upload validation, and the library raises an exception if a file does not meet the configured constraints.
- Added `python-magic` and `filetype` libraries for more reliable file type detection based on magic numbers (byte signatures).
- Added automatic file extension appending when a filename does not contain an extension.
- Improved WebSocket connection stability with exponential backoff and a configurable retry strategy. You can control the maximum number of reconnection attempts with `ws_max_retries` and the maximum delay between attempts with `ws_max_delay` ([#6](https://github.com/TrueConf/python-trueconf-bot/issues/6)).
- Added TrueConf Server version validation. The library now raises a `RuntimeError` with upgrade instructions if an incompatible server version is detected.
- Added the `safe_split_text` utility for safely splitting long messages exceeding 4096 characters into chunks of up to 4096 characters. This is especially useful for AI agents that generate long responses.
- Added AI-friendly documentation builds: `llms.txt` and `llms-full.txt`.
- Added and expanded logging.

**Fixed:**

- Fixed an issue with sending stickers in TrueConf Server 5.5.3+.
- Fixed issue #7.
- Fixed various minor bugs and made general improvements.

**Deprecated:**

- The `filename` and `mimetype` parameters are now deprecated.
- Please migrate to the new `snake_case` parameter naming, as the old parameters will be removed in future versions.

## 1.1.10

**Fixed:**

- Fixed the missing `file_id` parameter in `SendFileResponse`.

## 1.1.9

**Added:**

- Added TrueConf Server version validation. The library now raises a `RuntimeError` with update instructions if an incompatible server version is detected.

## 1.1.8

**Fixed:**

- Added `verify_ssl` support for WSS connections. Previously, SSL verification was unconditionally bypassed when `https` was enabled; it is now correctly controlled by the configuration flag.

## 1.1.7

**Added:**

- Added `reply_photo`, `reply_document`, and `reply_sticker` shortcut methods to the `Message` class.
- Added `reply_message_id` support to multiple methods and to the `SendFile` class.

**Fixed:**

- Fixed `quote_fields` being set to `False` in `aiohttp.FormData`.
- Set the default value of `last_message` to `None` in `GetChatByIdResponse` (fixes [#4](https://github.com/TrueConf/python-trueconf-bot/issues/4)).

**Deprecated:**

- `reply_message` is now deprecated. Use `reply_message_id` instead.

## 1.1.6

**Refactored:**

- Replaced local `verify_ssl` usage with `self.verify_ssl` in class methods.

## 1.1.5

**Fixed:**

- Prevented `run()` from hanging when the connect task fails.
- Properly propagate `ApiErrorException` and other errors to the caller.

## 1.1.4

**Fixed:**

- Removed the `chat_id` field from `RemoveChatResponse` ([#1](https://github.com/TrueConf/python-trueconf-bot/issues/1)).

## 1.1.3

**Fixed:**

- Fixed event propagation for multiple routers and subrouters.

## 1.1.2

**Added:**

- Bumped the development status.
- Added `typing_extensions` to dependencies.
- Added and updated the downloads badge.
- Added imports for `Self` and `Unpack` from `typing_extensions`.

**Fixed:**

- Fixed `Message` shortcuts not working.

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
