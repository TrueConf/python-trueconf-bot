# Начало работы

Перед началом работы рекомендуем создать и активировать виртуальное окружение, чтобы изолировать зависимости проекта:

```shell
python -m venv .venv
source .venv/bin/activate   # Linux / macOS
.venv\Scripts\activate      # Windows PowerShell
```

## Установка {{product_name}}

Чтобы начать работу с {{product_name}}, установите библиотеку одним из способов:

1. Из глобального репозитория PyPI:

    ```shell
    pip install {{product_name}}
    ```
2. Из локального собранного пакета (.whl)

    ```shell
    pip install {{product_name}}.whl
    ```

!!! info
    После установки будут автоматически подтянуты зависимости: `websockets`, `httpx`, `mashumaro`, `pillow`, `aiofiles`, `magic-filter`.

## Первое создание простого эхо-бота

Для начала импортируйте нужные классы:

```python
from trueconf import Bot, Dispatcher, Router, F
from trueconf.types import Message
```

Далее создайте экземпляры Router и Dispatcher и подключите их:

```python
r = Router()
dp = Dispatcher()
# dp.include_router(r)
```

Бот поддерживает два типа авторизации: по токену или по логину и паролю. Вы можете выбрать наиболее удобный способ.

### Авторизация по токену

Если вы используете подключение по токену, сначала получите его, как описано в [официальной документации API](https://trueconf.ru/docs/chatbot-connector/ru/connect-and-auth/#access-token).

Рекомендуется хранить токен в переменной окружения или в .env-файле. Не забудьте добавить .env в .gitignore, если работаете с публичными репозиториями.

```python
from os import getenv

TOKEN = getenv("TOKEN")
bot = Bot(server="video.example.com", token=TOKEN, dispatcher=dp)
```

### Авторизация по логину и паролю

Для этого используйте метод `.from_credentials`:

```python
bot = Bot.from_credentials(
    username="echo_bot",
    password="123tr",
    server="10.110.2.240",
    dispatcher=dp
)
```

!!! info
    При каждом вызове **from_credentials()** бот обращается к серверу за получением нового токена.
    Срок жизни каждого токена — 1 месяц.

### Обработчик сообщений

Теперь создадим простую функцию-обработчик входящих сообщений. Она будет отвечать пользователю тем же текстом (классический «эхо-бот»):

```python
@r.message(F.text)
async def echo(message: Message):
    await message.answer(message.text)
```

### Запуск бота

Запуск бота происходит внутри асинхронной функции main, которая передаётся в asyncio.run():

```python
async def main():
    await bot.run()
    
import asyncio

if __name__ == "__main__":
    asyncio.run(main())
```

!!! question "Почему async/await?"
    Библиотека **{{product_name}}** основана на asyncio.

Это значит, что все сетевые операции (подключение к серверу, приём и отправка сообщений) выполняются асинхронно — не блокируя основной поток. Поэтому:

- обработчики пишутся как `async def`,
- для вызовов методов используется `await`,  
- запуск организуется через `asyncio.run(...)`.  

Такой подход позволяет обрабатывать сразу несколько событий и сообщений параллельно, без задержек и подвисаний.

