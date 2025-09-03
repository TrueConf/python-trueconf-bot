# Использование перечеслений

В библиотеке {{product_name}} многие параметры методов и объектов определены через **enums** (перечисления).
Это делается для удобства разработчика и чтобы избежать ошибок при передаче «магических строк» или числовых кодов.

Вы можете импортировать сразу всё:

```python
from trueconf.enums import *
```

Или точечно использовать только нужные перечисления:

```python
from trueconf.enums import ParseMode, FileReadyState
```

Для чего нужны **enums**?

- повышают читаемость кода;
- исключают опечатки в строковых значениях;
- дают подсказки в IDE (автодополнение);
- явно показывают, какие значения доступны.

!!! Tip
    Подробнее со всеми перечислениями вы можете ознакомиться с [соответствующем разделе](../../en/reference/Enums.md).

### Примеры использования

#### Форматирование текста

```python
from trueconf.enums import ParseMode

@r.message()
async def on_message(message: Message):
    await message.answer(
        "Hello, *world*!",
        parse_mode=ParseMode.MARKDOWN
)
```

Вместо того чтобы вручную писать строку `"Markdown"`, используется `ParseMode.MARKDOWN`.

#### Работа с файлами

```python
from trueconf.enums import FileReadyState

info = await bot.get_file_info(file_id="abc123")

if info.ready_state == FileReadyState.READY:
    await bot.download_file_by_id(info.file_id, "./downloads")
elif info.ready_state == FileReadyState.NOT_AVAILABLE:
    print("File is not available")
```

#### Типы чатов

```python
from trueconf.enums import ChatType

if chat_type == ChatType.GROUP:
    await bot.send_message("This is a group chat")
```

---

Таким образом, **enums** помогают писать код чище и безопаснее.