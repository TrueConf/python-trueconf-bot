---
title: Начало работы
icon: material/run
---

#  Начало работы

Перед началом работы рекомендуем создать и активировать виртуальное окружение, чтобы изолировать зависимости проекта:

```shell
python -m venv .venv
source .venv/bin/activate   # Linux / macOS
.venv\Scripts\activate      # Windows PowerShell
```

## Установка {{product_name}}

Чтобы начать работу с {{product_name}}, установите библиотеку из глобального репозитория PyPI:

```shell
pip install {{product_name}}
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

!!! Note
    Токен действителен в течение одного месяца с момента создания. 
    При этом уже авторизованное соединение продолжает работать до момента разрыва соединения, даже после истечения срока действия токена.
    Теоретически такое соединение может существовать годами.
    
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

## Автоматическое восстановление соединения

Если WebSocket-соединение с сервером будет разорвано, бот не завершит работу сразу. Он автоматически попытается восстановить соединение и продолжить получать события.

При повторном подключении используется экспоненциальная задержка: после каждой неудачной попытки время ожидания увеличивается, но не превышает значение параметра `ws_max_delay`. Это помогает избежать слишком частых запросов к серверу при временных сетевых проблемах.

По умолчанию используются следующие параметры реконнекта:

```python hl_lines="5-6"
bot = Bot(
    server="video.example.com",
    token=TOKEN,
    dispatcher=dp,
    ws_max_retries=5,
    ws_max_delay=60,
)
```

| Параметр | Тип | Значение по умолчанию | Описание |
| --- | --- | --- | --- |
| `ws_max_retries` | `int` | `5` | Максимальное количество попыток подключения при сетевых ошибках или ошибках IP-адреса перед остановкой. |
| `ws_max_delay` | `int` | `60` | Максимальная задержка между попытками повторного подключения в секундах. |

Если бот работает в нестабильной сети или сервер может быть временно недоступен, эти параметры можно увеличить:

```python hl_lines="5-6"
bot = Bot(
    server="video.example.com",
    token=TOKEN,
    dispatcher=dp,
    ws_max_retries=10,
    ws_max_delay=120,
)
```

!!! Note
    При обычном разрыве WebSocket-соединения бот будет пытаться подключиться повторно с экспоненциальной задержкой.

    Если адрес сервера указан неправильно, бот не сможет установить соединение. В этом случае количество повторных попыток ограничивается параметром `ws_max_retries`, после чего будет вызвана ошибка подключения.

## Health-check

{{product_name}} поддерживает два подхода к проверке состояния бота:

- **push-модель** — бот сам вызывает callback-функцию при изменении состояния подключения;
- **pull-модель** — приложение само запрашивает текущее состояние через `bot.health_check()`.

### Push: callback при изменении состояния

Callback передаётся в параметр `on_health_check` при создании бота. Функция должна быть асинхронной и принимать словарь со статусом:

```python
async def on_health_check(status: dict):
    print("Bot status changed:", status)


bot = Bot.from_credentials(
    server="video.example.com",
    username="echo_bot",
    password="123tr",
    dispatcher=dp,
    on_health_check=on_health_check,
)
```

Callback вызывается при изменении состояния WebSocket-подключения и авторизации. Например, бот может передать статусы:

- `connected` — WebSocket-соединение установлено, но бот ещё не авторизован;
- `authorized` — бот успешно авторизован;
- `disconnected` — соединение разорвано.

Пример payload:

```json
{
    "status": "authorized",
    "websocket_connected": true,
    "authorized": true,
    "user_id": "echo_bot@video.example.com",
    "server": "video.example.com",
    "port": 443,
    "protocol": "https",
    "timestamp": "2026-05-06T12:00:00+00:00",
}
```

Push-модель удобна, если нужно сразу реагировать на изменение состояния: записывать статус в лог, отправлять событие в мониторинг, обновлять переменную приложения или уведомлять администратора.

### Pull: ручная проверка состояния

Метод `bot.health_check()` возвращает текущее состояние бота в момент вызова:

```python
status = bot.health_check()
print(status)
```

Пример ответа:

```json
{
    "status": "authorized",
    "websocket_connected": true,
    "authorized": true,
    "server": "video.example.com",
    "port": 443,
    "protocol": "https",
    "timestamp": "2026-05-06T12:00:00+00:00",
}
```

Pull-модель удобна для HTTP health-check endpoint'ов, например в FastAPI, Zabbix, Kubernetes probes или других системах мониторинга:

```python
from fastapi import FastAPI

app = FastAPI()


@app.get("/health")
def health():
    return bot.health_check()
```

### Совместное использование push и pull

На практике часто удобно использовать оба подхода одновременно. Callback обновляет последний известный статус, а HTTP endpoint возвращает его системе мониторинга:

```python
from fastapi import FastAPI

app = FastAPI()
bot_status = {"status": "disconnected"}


async def on_health_check(status: dict):
    bot_status.update(status)


bot = Bot.from_credentials(
    server="video.example.com",
    username="echo_bot",
    password="123tr",
    dispatcher=dp,
    on_health_check=on_health_check,
)


@app.get("/health")
def health():
    return bot_status
```

В такой схеме бот сообщает об изменениях через callback, а внешняя система мониторинга получает актуальный статус через HTTP-запрос.

