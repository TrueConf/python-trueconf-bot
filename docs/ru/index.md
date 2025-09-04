# Python-библиотека для работы с TrueConf Chatbot Connector

<img src="img/head.png" alt="">

**{{product_name}}** — это асинхронная Python-библиотека для API чат-ботов TrueConf Server, вдохновлённая философией aiogram.
Если вы когда-то писали бота для Telegram на aiogram — переход на TrueConf будет максимально простым и безболезненным.

## Установка

### Требования
- Python **3.10+**
- Поддерживаются ОС: Linux, macOS, Windows
- Рекомендуется использовать [virtualenv](https://docs.python.org/3/library/venv.html) или [poetry](https://python-poetry.org/) для изоляции зависимостей

### Установка через pip
```bash
pip install git+https://github.com/TrueConf/{{product_name}}
```

## Сравнение с aiogram

| Возможность             | aiogram (Telegram)                             | {{product_name}} (TrueConf)                                                               |
|-------------------------|------------------------------------------------|-------------------------------------------------------------------------------------------|
| Асинхронность           | asyncio                                        | asyncio                                                                                   |
| Декораторы для роутинга | `@router.message(...)`                         | `@router.message(...)`                                                                    |
| Фильтрация сообщений    | `F.text`, `F.photo`, `F.document`              | `F.text`, `F.photo`, `F.document`                                                         |
| Magic-filter            | ✅                                              | ✅                                                                                         |
| Алиасы (шорткаты)       | `message.answer()`, `message.reply()`          | `message.answer()`, `message.reply()`                                                     |
| Инициализация бота      | `Bot(token="...")`                             | `Bot(server,token="...")` или `Bot.from_credentials(server, login, password)`             |
| JSON → Python           | Pydantic models                                | Mashumaro dataclasses                                                                     |
| Транспорт               | HTTPS + long polling / webhook                 | Асинхронный WebSocket                                                                     |
| Работа с файлами        | `bot.get_file(...)` + `bot.download_file(...)` | `message.photo.download()`, `message.document.download()`, `bot.download_file_by_id(...)` |

- Если у вас уже есть опыт с aiogram — код переносится почти без изменений.
- TrueConf API становится «человеческим»: вместо JSON-словарей вы работаете с Python-классами.
- Вы получаете удобный инструмент для интеграции ботов в корпоративные чаты TrueConf.


