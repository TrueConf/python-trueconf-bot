---
title: Индикатор активности
description: Показываем в чате статус набора текста или записи голосового сообщения
icon: material/keyboard-outline
---

# Индикатор активности в чате

Пока бот обрабатывает запрос, можно показывать в чате его статус: например, что он набирает сообщение.

## Разовое событие активности

Используйте [`bot.send_chat_activity(...)`](../reference/Bot.md/#trueconf.Bot.send_chat_activity), чтобы отправить одно событие активности:

```python
from trueconf.enums import ChatActivity

await bot.send_chat_activity(
    chat_id="chat_id",
    activity_type=ChatActivity.TYPING,
)
```

Доступные типы активности перечислены в enum [`ChatActivity`](../reference/Enums.md):

- `ChatActivity.TYPING` — бот набирает текст;
- `ChatActivity.CHOOSING_STICKER` — бот выбирает стикер;
- `ChatActivity.UPLOADING_FILE` — бот загружает файл.

!!! note "Индикатор истекает"
    Сервер показывает индикатор лишь короткое время. Для длительных операций отправку нужно повторять — используйте [`ChatActivitySender`](../reference/chat_activity.md), описанный ниже.

## Удержание индикатора видимым

[`ChatActivitySender`](../reference/chat_activity.md) — это асинхронный контекст-менеджер, который периодически переотправляет активность в фоне, пока выполняется операция:

```python
from trueconf.utils.chat_activity import ChatActivitySender

async with ChatActivitySender.typing(bot=bot, chat_id=chat_id):
    result = await generate_text_answer()
```

Сендер переотправляет активность с темпом, который возвращает сервер: каждый ответ содержит
`retryAfter` в миллисекундах, и сендер ждёт не меньше этого времени перед следующей отправкой.

`ChatActivitySender` также принимает универсальный аргумент `activity`, поэтому можно использовать любое значение из enum [`ChatActivity`](../reference/Enums.md):

```python
from trueconf.enums import ChatActivity

async with ChatActivitySender(bot=bot, chat_id=chat_id, activity=ChatActivity.UPLOADING_FILE):
    await upload_large_file()
```
