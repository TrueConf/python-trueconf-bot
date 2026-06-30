---
title: Отправка сообщений
description: Как отправлять, отвечать, пересылать и форматировать сообщения
icon: material/message-text-fast-outline
---

# Отправка сообщений

Для отправки сообщения боту необходимо знать `chat_id` чата (личный, групповой, канал).

## Как получить `chat_id`?

### Личные чаты (на двоих, P2P)

Для получения `chat_id` личного чата можно использовать метод [`bot.create_personal_chat(user_id)`](../reference/Bot.md/#trueconf.Bot.create_personal_chat)
Если личный чат с пользователем ещё не создан, сервер создаст его.
Если чат уже существует, сервер вернёт существующий `chat_id`.

```python
chat = await bot.create_personal_chat(user_id="john_doe@video.example.com")

await bot.send_message(
    chat_id=chat.chat_id,
    text="Hello!",
)
```

### Групповые чаты и каналы

С [групповыми чатами](../reference/Bot.md/#trueconf.Bot.create_group_chat) и [каналами](../reference/Bot.md/#trueconf.Bot.create_channel) нужно быть осторожнее. Методы создания групповых чатов и каналов каждый раз создают новый чат:

```python
chat = await bot.create_group_chat(title="Support")
channel = await bot.create_channel(title="News")
```

Если вызвать такой метод повторно с тем же названием, будет создан ещё один чат или канал с таким же `title`.
Поэтому после создания группового чата или канала лучше сохранить его `chat_id` в базе данных, файле конфигурации или другом постоянном хранилище.

!!! Question "А что делать, если чат уже существует? Как получить `chat_id`?"

### Поиск существующего чата

Список доступных чатов можно получить методом [`bot.get_chats()`](../reference/Bot.md/#trueconf.Bot.get_chats):

```python
response = await bot.get_chats(count=10, page=1)
```

Метод возвращает [`GetChatsResponse`](../reference/Responses.md/#trueconf.types.responses.GetChatsResponse) с параметром `list` в котором хранится список чатов.
Вы можете найти нужный чат, например по названию, и получить его `chat_id`:

=== "C помощью генератора"
    ```python
    response = await bot.get_chats(count=100, page=1)
    
    chat = next(
        (chat for chat in response.list if chat.title == "Support"),
        None,
    )
    
    if chat is not None:
        print(chat.chat_id)
    ```

=== "С помощью цикла"
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

После того как нужный `chat_id` найден, его также рекомендуется сохранить, чтобы не искать чат повторно при каждом запуске приложения.

### Получение `chat_id` через входящее сообщение

Ещё один простой способ — написать сообщение в нужный чат и обработать его ботом. В обработчике можно вывести `message.chat_id`:

```python
from trueconf import Router
from trueconf.types import Message

router = Router()


@router.message()
async def print_chat_id(message: Message):
    print(message.chat_id)
```

Этот способ удобен для групповых чатов и каналов: достаточно добавить бота в нужный чат, отправить сообщение и посмотреть `chat_id` в консоли.

## Текстовые сообщения

Для отправки текстового сообщения используйте метод [`bot.send_message(...)`](../reference/Bot.md/#trueconf.Bot.send_message):

```python
await bot.send_message(
    chat_id="chat_id",
    text="Hello!",
)
```

Если сообщение отправляется из обработчика входящего сообщения, можно использовать shortcut-методы объекта `Message`, например `message.answer(...)` или `message.reply(...)`. 
Они автоматически используют `message.chat_id`, поэтому его не нужно передавать вручную. Подробнее см. раздел [Шорткаты](shortcuts.md).

### Ответ на сообщение

Если нужно отправить ответ на конкретное сообщение, передайте идентификатор исходного сообщения в параметр `reply_message_id`:

```python
await bot.send_message(
    chat_id="chat_id",
    text="This is a reply",
    reply_message_id="message_id",
)
```

Такой способ позволяет отправлять обычные сообщения и ответы через единый API.

### Пересылка сообщений

Для пересылки уже существующего сообщения используйте [`bot.forward_message(...)`](../reference/Bot.md/#trueconf.Bot.forward_message):

```python
await bot.forward_message(
    chat_id="target_chat_id",
    message_id="source_message_id",
)
```

Где:

- `chat_id` — идентификатор чата, куда нужно переслать сообщение;
- `message_id` — идентификатор сообщения, которое нужно переслать.

### Форматирование текста

Сообщения можно отправлять как обычный текст, HTML или Markdown, передавая `parse_mode`:

```python
from trueconf.enums import ParseMode

await bot.send_message(
    chat_id="chat_id",
    text="<b>Important</b>",
    parse_mode=ParseMode.HTML,
)
```

Для удобного построения форматированного текста в библиотеке есть модуль [`trueconf.utils.formatting`](../reference/Formatting.md).
Он позволяет не писать HTML или Markdown вручную, а собирать сообщение из классов:

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

Модуль поддерживает:

- [`Bold(...)`](../reference/Formatting.md/#trueconf.utils.formatting.Bold)
- [`Italic(...)`](../reference/Formatting.md/#trueconf.utils.formatting.Italic)
- [`Underline(...)`](../reference/Formatting.md/#trueconf.utils.formatting.Underline)
- [`Strikethrough(...)`](../reference/Formatting.md/#trueconf.utils.formatting.Strikethrough)
- [`Link(...)`](../reference/Formatting.md/#trueconf.utils.formatting.Link)
- [`Mention(...)`](../reference/Formatting.md/#trueconf.utils.formatting.Mention)
- [`AllMention()`](../reference/Formatting.md/#trueconf.utils.formatting.AllMention)
- [`Text(...)`](../reference/Formatting.md/#trueconf.utils.formatting.Text)

### Ограничения длины сообщения

TrueConf Server ограничивает длину текстового сообщения до `4096` символов.

Если сообщение превышает лимит, рекомендуется использовать helper-функцию `safe_split_text(...)`,
которая безопасно разбивает длинный текст с учётом HTML/Markdown-разметки:

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

Подробнее об ограничениях см. в разделе [Ограничения](restrictions.md).

!!! Tip "Shortcut-методы"
    В обработчиках сообщений часто удобнее использовать `message.answer(...)`, `message.reply(...)` и другие shortcut-методы вместо прямого вызова `bot.send_message(...)`.
    Подробнее см. раздел [Шорткаты](shortcuts.md).

!!! Tip "Отправка файлов"
    Этот раздел посвящён текстовым сообщениям. 
    Для отправки документов, изображений, видео, голосовых сообщений и других вложений см. раздел [Работа с файлами](files.md).
