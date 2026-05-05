---
title: Ограничения
icon: material/alert-octagon-outline
---

# Ограничения

Библиотека заранее проверяет часть ограничений TrueConf Server и вызывает исключение до отправки запроса, если значение превышает допустимый лимит.

#### Название чата

Максимальная длина названия чата — `255` символов. Если передать более длинное название, будет вызвано исключение [`GroupTitleTooLongError`](../reference/Exceptions.md/#trueconf.exceptions.GroupTitleTooLongError) или [`ChannelTitleTooLongError`](../reference/Exceptions.md/#trueconf.exceptions.ChannelTitleTooLongError).

#### Длина сообщения

Максимальная длина текстового сообщения — `4096` видимых символов. Если превысить этот лимит, будет вызвано исключение [`TextMessageTooLongError`](../reference/Exceptions.md/#trueconf.exceptions.TextMessageTooLongError).

Если нужно отправить длинный текст, например ответ от LLM, его можно разделить на несколько частей с помощью `safe_split_text`:

```python
from trueconf.utils import safe_split_text

for chunk in safe_split_text(long_text):
    await bot.send_message(
        chat_id=chat_id,
        text=chunk,
    )
```

Функция `safe_split_text(text)` возвращает список чанков, которые можно отправлять по очереди.

#### Ограничения файлов

Ограничения на размер файлов и допустимые расширения задаются администратором TrueConf Server. Бот получает эти параметры от сервера и обновляет их при изменении настроек:

```python
bot.max_file_size: int | None
bot.file_extension_filter_mode: str | None
bot.file_extensions_list: set | None 
```

При отправке файла библиотека проверяет его размер и расширение. Если файл превышает допустимый размер, будет вызвано исключение [`FileSizeTooLargeError`](../reference/Exceptions.md/#trueconf.exceptions.FileSizeTooLargeError). Если расширение файла запрещено настройками сервера, будет вызвано исключение [`InvalidFileExtensionError`](../reference/Exceptions.md/#trueconf.exceptions.InvalidFileExtensionError).

!!! Note
    Файловые ограничения зависят от настроек конкретного TrueConf Server. Если администратор изменит максимальный размер файла или список разрешенных расширений, бот автоматически получит обновленные значения при следующем событии изменения лимитов.

