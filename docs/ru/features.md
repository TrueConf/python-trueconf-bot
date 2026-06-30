---
title: Возможности
description: 'Что умеет библиотека: асинхронность, API в стиле aiogram, WebSocket и другое'
icon: material/feather
---

# Возможности

### Асинхронность на основе asyncio

Всё построено на async/await. Высокая производительность и отсутствие блокировок. 

### Похожесть на aiogram

Используются знакомые концепции: Router, декораторы, шорткаты (message.answer, message.reply), фильтры и даже magic-filter (F.text, F.document, F.photo). 

### Удобная обработка входящих событий

Все входящие JSON автоматически трансформируются в классы Python (Message, AttachmentContent, UploadingProgress и др.), поэтому работа с данными проста и безопасна. 

### Декораторы для роутинга

Роутер позволяет элегантно обрабатывать события:

```python
from trueconf import Router, Message
from trueconf.enums import MessageType
from trueconf.filters import F

router = Router()

@router.message(F.text.startswith("/start"))
async def on_start(msg: Message):
  await msg.answer("Привет! Я TrueConf бот 👋")

@router.message(F.document.mime_type == "application/pdf")
async def on_pdf(msg: Message):
  await msg.reply("Спасибо за PDF!")
```

### Два варианта подключения

1. Используя заранее полученный JWT-токен:
    ```python
    bot = Bot(server="video.example.com", token="...")
    ```

2. или авторизацию с помощью логина и пароля:
    ```python
    bot = Bot.from_credentials(server, username, password)
    ```
  
### Алиасы и шорткаты в стиле aiogram

Для сообщений доступны привычные методы:

```python
await msg.answer("Текст в чат")
await msg.reply("Ответ на сообщение")
await msg.copy_to(chat_id="other_chat")
```

### Многоботность

Вы можете запустить несколько ботов одновременно и маршрутизировать события отдельно для каждого.

### Асинхронный транспорт — WebSocket

Всё общение с сервером происходит через WebSocket. Это быстрее и эффективнее классических REST-запросов.

### Magic-filter, как в aiogram

Точно так же, как в aiogram:

```python
@router.message(F.photo)
async def on_photo(msg: Message): ...

@router.message(F.document.mime_type.in_(["application/pdf", "application/msword"]))
async def on_doc(msg: Message): ...
```

### Файлы и загрузки

Поддержана асинхронная отправка и скачивание файлов. Можно скачивать файл во временную директории или по указанному пути.

```python
path = await bot.download_file_by_id(file_id)
await msg.answer(f"Файл скачан в {path}")
```

### Все публичные методы API

В библиотеке реализованы все основные методы TrueConf API: отправка сообщений, загрузка/скачивание файлов, опросы, конференции, управление участниками и пр.