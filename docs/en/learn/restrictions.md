---
title: Restrictions
description: What limits apply to messages, files, and chat titles
icon: material/alert-octagon-outline
---

# Restrictions

The library performs pre-validation of certain TrueConf Server limits and raises exceptions before sending a request if a value exceeds the allowed threshold.

#### Chat Title

The maximum chat title length is `255` characters. If a longer title is provided, a [`GroupTitleTooLongError`](../reference/Exceptions.md/#trueconf.exceptions.GroupTitleTooLongError) or [`ChannelTitleTooLongError`](../reference/Exceptions.md/#trueconf.exceptions.ChannelTitleTooLongError) will be raised.

#### Message Length

The maximum length of a text message is `4096` visible characters. If this limit is exceeded, a [`TextMessageTooLongError`](../reference/Exceptions.md/#trueconf.exceptions.TextMessageTooLongError) will be raised.

If you need to send a long message, for example an LLM-generated response, you can split it into multiple parts using `safe_split_text`:

```python
from trueconf.utils import safe_split_text

for chunk in safe_split_text(long_text):
    await bot.send_message(
        chat_id=chat_id,
        text=chunk,
    )
```

The `safe_split_text(text)` function returns a list of chunks that can be sent sequentially.

#### File Restrictions

Limits on file size and allowed extensions are configured by the TrueConf Server administrator. The bot retrieves these parameters from the server and updates them when the settings change:

```python
bot.max_file_size: int | None
bot.file_extension_filter_mode: str | None
bot.file_extensions_list: set | None
```

When sending a file, the library checks its size and extension. If the file exceeds the allowed size, a [`FileSizeTooLargeError`](../reference/Exceptions.md/#trueconf.exceptions.FileSizeTooLargeError) will be raised. If the file extension is not allowed by server settings, an [`InvalidFileExtensionError`](../reference/Exceptions.md/#trueconf.exceptions.InvalidFileExtensionError) will be raised.

!!! Note
    File restrictions depend on the configuration of the specific TrueConf Server. If the administrator changes the maximum file size or the list of allowed extensions, the bot will automatically receive updated values on the next limits update event.
