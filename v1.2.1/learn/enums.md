# Using enumerations⚓︎

In the python-trueconf-bot library, many method parameters and object fields are defined through enums (enumerations). This is done for developer convenience and to avoid errors caused by using "magic strings" or numeric codes.

You can import all enums at once:

```
from trueconf.enums import *
```

Or import only the ones you need:

```
from trueconf.enums import ParseMode, FileReadyState
```

### Usage examples⚓︎

#### Text formatting⚓︎

```
from trueconf.enums import ParseMode

await message.answer(
"Hello, *world*!",
parse_mode=ParseMode.MARKDOWN
)
```

Instead of manually typing the string `"Markdown"`, you use `ParseMode.MARKDOWN`.

#### Working with files⚓︎

```
from trueconf.enums import FileReadyState

info = await bot.get_file_info(file_id="abc123")

if info.ready_state == FileReadyState.READY:
await bot.download_file_by_id(info.file_id, "./downloads")
elif info.ready_state == FileReadyState.NOT_AVAILABLE:
print("File is not available")
```

#### Chat types⚓︎

```
from trueconf.enums import ChatType

if chat.chat_type == ChatType.GROUP:
await message.answer("This is a group chat")
```

Thus, `enums` help you write cleaner and safer code.
