# List of Changes⚓︎

## 1.4.0⚓︎

Added:

- FSM (Finite State Machine) — a finite state machine mechanism. It allows you to implement step-by-step dialogs, such as questionnaires, forms, and setup wizards.
States are declared declaratively using `StatesGroup`/`State`, while data is stored in `FSMContext`. It supports nested groups, multiple storage strategies, and state-based filtering via `StateFilter`. Learn more: FSM.

- Middleware — a layer for processing events before and after handlers.
It allows you to log events, block them, check access, and modify data.
It supports two types: outer middleware, which runs before filters, and inner middleware, which runs after filters. Learn more: Middleware.

- The `skip_self_messages` parameter in `Bot()`. By default, it is set to `True`, so the bot automatically ignores messages sent by itself.
It can be disabled with `skip_self_messages=False`.

## 1.3.0⚓︎

Added:

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

Changed:

- Updated the `verify_ssl` behavior:

- `verify_ssl=True` uses the system trusted certificate store through `truststore`;

- `verify_ssl=False` disables certificate verification;

- `verify_ssl="/path/to/ca.pem"` uses a custom CA bundle;

- `verify_ssl=ssl.SSLContext(...)` uses the provided SSL context.

- Updated the SSL logic for WebSocket connections: a single `self.ssl_context`, created via `build_ssl_context(...)`, is now used.

- Updated bot initialization logging: logs now include human-readable information about the SSL context.

Fixed:

- Fixed failures caused by incomplete certificate chains. Certificate chains can now be verified successfully by using the system trusted certificate store through `truststore` or by passing a custom SSL context.

Deprecated:

- The asynchronous `bot.me` property, which returns the `chat_id` of the "Favorites" chat, is now deprecated. Use `await bot.me_chat` instead.

Documentation:

- Added Context7 AI Assistant: interactive support for code and documentation.

- Added a new Sending messages documentation section covering:

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

- Added new sections: Shortcuts, Restrictions, Formatting, Exceptions.

## 1.2.3⚓︎

Added:

- Added a 10-second server response timeout. If no response is received within the timeout, an `asyncio.TimeoutError` is raised: `Request to {self.__api_method__} timed out after {timeout}s` (#12).

Fixed:

- Fixed cases where Mashumaro failed to parse a response, which could cause the application to crash (#8, #11).

## 1.2.2⚓︎

Fixed:

- Fixed a missing dependency: the `packaging` package, which is required to check the library version at bot startup.

## 1.2.1⚓︎

Added:

- Added support for TrueConf Server 5.5.4.

- Added the `receive_system_messages` flag to `Bot()` and `Bot.from_credentials()` to enable or disable receiving system messages.

- Added the new `bot.get_chat_participant()` method, which replaces `bot.has_chat_participant()`.

Fixed:

- Fixed support for TrueConf Server 5.5.3+. Removed an unnecessary version check that prevented the code from running with library version 1.2.0.

- Fixed documentation links to `llms.txt` and `llms-full.txt`.

Changed:

- When retrieving file information via `bot.get_file_info(file_id=...)`, the response now returns the `file_id` field instead of `info_hash`.

Deprecated:

- The `bot.has_chat_participant()` method has been deprecated. Use `bot.get_chat_participant()` instead.

## 1.2.0⚓︎

Added:

- Added support for TrueConf Server 5.5.3, including:

- chat title editing with `bot.edit_chat_title(...)`;

- chat avatar editing with `bot.edit_chat_avatar(...)`;

- chat history clearing with `bot.clear_chat_history(...)`;

- retrieving file storage limits with `bot.get_file_info_upload_limits(...)`;

- a new file transfer approach where the `file_name` parameter is now required for `FSInputFile(...)` and other file upload methods.

- Added caching for file storage limit settings. These settings are now used for pre-upload validation, and the library raises an exception if a file does not meet the configured constraints.

- Added `python-magic` and `filetype` libraries for more reliable file type detection based on magic numbers (byte signatures).

- Added automatic file extension appending when a filename does not contain an extension.

- Improved WebSocket connection stability with exponential backoff and a configurable retry strategy. You can control the maximum number of reconnection attempts with `ws_max_retries` and the maximum delay between attempts with `ws_max_delay` (#6).

- Added TrueConf Server version validation. The library now raises a `RuntimeError` with upgrade instructions if an incompatible server version is detected.

- Added the `safe_split_text` utility for safely splitting long messages exceeding 4096 characters into chunks of up to 4096 characters. This is especially useful for AI agents that generate long responses.

- Added AI-friendly documentation builds: `llms.txt` and `llms-full.txt`.

- Added and expanded logging.

Fixed:

- Fixed an issue with sending stickers in TrueConf Server 5.5.3+.

- Fixed issue #7.

- Fixed various minor bugs and made general improvements.

Deprecated:

- The `filename` and `mimetype` parameters are now deprecated.

- Please migrate to the new `snake_case` parameter naming, as the old parameters will be removed in future versions.

## 1.1.10⚓︎

Fixed:

- Fixed the missing `file_id` parameter in `SendFileResponse`.

## 1.1.9⚓︎

Added:

- Added TrueConf Server version validation. The library now raises a `RuntimeError` with update instructions if an incompatible server version is detected.

## 1.1.8⚓︎

Fixed:

- Added `verify_ssl` support for WSS connections. Previously, SSL verification was unconditionally bypassed when `https` was enabled; it is now correctly controlled by the configuration flag.

## 1.1.7⚓︎

Added:

- Added `reply_photo`, `reply_document`, and `reply_sticker` shortcut methods to the `Message` class.

- Added `reply_message_id` support to multiple methods and to the `SendFile` class.

Fixed:

- Fixed `quote_fields` being set to `False` in `aiohttp.FormData`.

- Set the default value of `last_message` to `None` in `GetChatByIdResponse` (fixes #4).

Deprecated:

- `reply_message` is now deprecated. Use `reply_message_id` instead.

## 1.1.6⚓︎

Refactored:

- Replaced local `verify_ssl` usage with `self.verify_ssl` in class methods.

## 1.1.5⚓︎

Fixed:

- Prevented `run()` from hanging when the connect task fails.

- Properly propagate `ApiErrorException` and other errors to the caller.

## 1.1.4⚓︎

Fixed:

- Removed the `chat_id` field from `RemoveChatResponse` (#1).

## 1.1.3⚓︎

Fixed:

- Fixed event propagation for multiple routers and subrouters.

## 1.1.2⚓︎

Added:

- Bumped the development status.

- Added `typing_extensions` to dependencies.

- Added and updated the downloads badge.

- Added imports for `Self` and `Unpack` from `typing_extensions`.

Fixed:

- Fixed `Message` shortcuts not working.

## 1.1.1⚓︎

Added:

- New classes for working with files: `FSInputFile`, `BufferedInputFile`, `URLInputFile`. More details can be found in the documentation.

- Support for displaying message history `display_history = True` when adding a user to a group chat or channel.

- Support for request and event for:

- role changes in a group chat or channel (request, notification);

- creation of the “Favorites” chat (request, notification).

- Ability to send files with a caption.

- Shortcut `.save_to_favorites()` for quickly saving a message to the "Favorites" chat.

- The asynchronous property `await bot.me`, which returns the `chat_id` of the "Saved Messages" chat.

Fixed:

- Stickers sent via `bot.send_sticker()` were displayed with a background due to an incorrect MIME type.

- The method `.remove_participant_from_chat()` did not work when an incomplete TrueConf ID was specified.

- Error unpacking the participant list due to an incorrect alias.

- Sometimes, when obtaining a token using `.from_credentials()`, a `400 Bad Requests` error would occur when using a digit password.

Modified:

- The `bot.server_name` property has become asynchronous. Use it as `await bot.server_name`.

## 1.0.0⚓︎

🎉 First Release!

- Stable version of the python-trueconf-bot library.

- Support for all major TrueConf ChatBot API methods.

- Aliases and keyboard shortcuts in the aiogram style (message.answer, message.reply, etc.).

- Asynchronous data transmission via the WebSocket protocol.

- Working with files (sending and uploading).

- Documentation: trueconf.github.io/python-trueconf-bot/

- PyPI: pypi.org/project/python-trueconf-bot/
