---
title: Шорткаты
description: Как использовать удобные методы на объекте Message
icon: material/knife
---

# Шорткаты

## Работа с объектом Message

При обработке входящего сообщения в функцию-обработчик обычно передается объект `Message`:

```python
from trueconf import Router
from trueconf.types import Message

r = Router()


@r.message()
async def on_message(message: Message):
    await message.answer("Сообщение получено")
```
Объект `Message` передается в обработчик автоматически и содержит контекст текущего события: данные об авторе, чате, типе сообщения, содержимом, идентификаторе сообщения и других параметрах.

Кроме того, через объект сообщения можно получить доступ к экземпляру бота, который обрабатывает текущее событие:

```python
@r.message()
async def on_message(message: Message):
    result = await message.bot.get_something()
```

Это удобно, когда экземпляр бота создан в другом файле или объявлен ниже в коде,
и внутри обработчика нельзя напрямую обратиться к переменной `bot`.

В таком случае доступ к текущему экземпляру бота можно получить через объект сообщения: `message.bot`.

## Шорткаты Message

Для `Message` реализованы шорткаты — вспомогательные методы, которые позволяют выполнять частые действия без явной передачи `chat_id`, `message_id` и других параметров. Эти значения автоматически берутся из текущего сообщения.

!!! Note
    На данный момент шорткаты реализованы только для типа `Message`.
    В будущем аналогичные методы могут появиться и для других типов событий.

Например, вместо прямого вызова метода бота:

```python hl_lines="3-5"
@r.message()
async def on_message(message: Message):
    await message.bot.send_message(chat_id=message.chat_id, text="Привет!")
```

можно использовать шорткат:

```python hl_lines="3"
@r.message()
async def on_message(message: Message):
    await message.answer("Привет!")
```

Шорткаты особенно полезны в обработчиках, где действие связано с текущим сообщением или текущим чатом. 
Они делают код короче и уменьшают количество повторяющихся параметров. 

Например, `message.answer(...)` автоматически использует чат, из которого пришло сообщение, 
а `message.reply(...)` дополнительно связывает ответ с исходным сообщением.

!!! Tip
    Список всех доступных шорткатов вы можете изучить в разделе с [описанием класса Message](../reference/Types.md/#trueconf.types.Message).

## Контакты

`Message.contact` возвращает контакт текущего сообщения в виде объекта
[`Contact`](../reference/Types.md/#trueconf.types.contact.Contact) или `None`, если сообщение
не является контактом. Результат кэшируется на сообщении, поэтому vCard-файл
скачивается с сервера только один раз:

```python
contact = await message.contact
```

Распознаются два формата:

- **vCard-вложение** — файл `.vcf` (`mimeType: text/vcard`). Файл скачивается
  с сервера и парсится: структурированное поле `N` даёт имя и фамилию, `TEL` —
  номер телефона, а сырой текст vCard доступен как `Contact.vcard`.
- **Ссылка на контакт TrueConf** — текстовое сообщение, содержимое которого —
  ровно одна ссылка `<a href="trueconf:login&do=profile">Имя</a>`.
  `Contact.user_id` содержит логин, а `Contact.first_name` — отображаемое имя,
  полученное с сервера (если пользователь уже удалён — берётся текст ссылки).

```python
@r.message()
async def on_message(message: Message):
    contact = await message.contact
    if contact is not None:
        await message.answer(f"{contact.first_name}: {contact.phone_number}")
```

Отображаемое имя никогда не разбивается на имя и фамилию: конвенция имени на
сервере (ФИ, ИФ, ФИО) различается от инсталляции к инсталляции, поэтому для
контактов TrueConf `Contact.last_name` всегда `None`.

## Геолокация

`Message.location` возвращает объект [`Location`](../reference/Types.md/#trueconf.types.content.location.Location) для сообщений с геолокацией или `None`:

```python
@r.message()
async def on_message(message: Message):
    if message.location is not None:
        print(location.latitude, location.longitude, location.title)
```

## Цитата

`Message.quote` возвращает процитированную часть сообщения-ответа, а `Message.text` — без блока цитаты. Процитированный фрагмент можно передать в параметр `quote` методов `message.reply(...)` и `bot.send_message(...)`:

```python
@r.message()
async def on_message(message: Message):
    if message.quote is not None:
        await message.reply("Спасибо за цитату!", quote=message.quote)
```

## Голосовые сообщения

`Message.voice` возвращает объект [`Voice`](../reference/Types.md/#trueconf.types.content.voice.Voice) для голосовых сообщений или `None`. Для него доступны те же файловые шорткаты, что и для других вложений: `download()`, `url`, `preview_url`:

```python
@r.message()
async def on_message(message: Message):
    if message.voice is not None:
        await voice.download(file_path="voice.ogg")
```

