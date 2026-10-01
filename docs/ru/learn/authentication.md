---
title: Авторизация
description: 'Способы авторизации бота: по токену, по логину и паролю, через OAuth2'
icon: material/key
---

# Авторизация

Библиотека поддерживает три способа авторизации бота на TrueConf Server:

| Способ | Метод | Когда использовать |
| --- | --- | --- |
| По токену | `Bot(server, token=...)` | Токен получен заранее (вручную или через API) |
| По логину и паролю | `Bot.from_credentials(...)` | На сервере включена авторизация по логину и паролю |
| Через OAuth2 | `Bot.from_oauth(...)` | На сервере отключена авторизация по логину и паролю |

## Авторизация по токену

Получите токен, как описано в [официальной документации API](https://trueconf.ru/docs/chatbot-connector/ru/connect-and-auth/#access-token).

Рекомендуется хранить токен в переменной окружения или в `.env`-файле. Не забудьте добавить `.env` в `.gitignore`, если работаете с публичными репозиториями.

```python
from os import getenv

TOKEN = getenv("TOKEN")
bot = Bot(server="video.example.com", token=TOKEN, dispatcher=dp)
```

!!! Note
    Токен действителен в течение одного месяца с момента создания.
    При этом уже авторизованное соединение продолжает работать до момента разрыва соединения, даже после истечения срока действия токена.
    Теоретически такое соединение может существовать годами.

## Авторизация по логину и паролю

Метод `Bot.from_credentials()` авторизует бота с помощью логина и пароля:

```python
bot = Bot.from_credentials(
    username="echo_bot",
    password="123tr",
    server="video.example.com",
    dispatcher=dp,
)
```

!!! info
    При каждом вызове **from_credentials()** бот обращается к серверу за получением нового токена.
    Срок жизни каждого токена — 1 месяц.

Ключевые параметры (после `password` — keyword-only):

| Параметр | Тип | По умолчанию | Описание |
| --- | --- | --- | --- |
| `dispatcher` | `Dispatcher` | `None` | Dispatcher для регистрации обработчиков |
| `receive_unread_messages` | `bool` | `False` | Получать ли непрочитанные сообщения при подключении |
| `receive_system_messages` | `bool` | `False` | Получать ли системные сообщения |
| `skip_self_messages` | `bool` | `True` | Игнорировать сообщения, отправленные самим ботом |
| `verify_ssl` | `bool | str | ssl.SSLContext` | `True` | Проверка SSL-сертификата |
| `https` | `bool` | `True` | Использовать HTTPS-протокол |
| `web_port` | `int` | `None` | WebSocket-порт (по умолчанию `443` при HTTPS, иначе `4309`) |
| `ws_max_retries` | `int` | `5` | Максимум попыток подключения при сетевых ошибках |
| `ws_max_delay` | `int` | `60` | Максимальная задержка между попытками (сек) |
| `timeout` | `float | int` | `10.0` | Таймаут ожидания ответа сервера |
| `on_health_check` | `Callable` | `None` | Callback при изменении состояния подключения |

Полный список параметров — в [справочнике](../reference/Bot.md/#trueconf.Bot.from_credentials).

Если на сервере отключена авторизация по логину и паролю, метод выбросит `PasswordAuthDisabledError` — используйте `Bot.from_oauth()`.

## Авторизация через OAuth2

Если на сервере по требованиям безопасности отключена авторизация по логину и паролю, бот не сможет воспользоваться методом `from_credentials()` — он не умеет авторизовываться по NTLM, Kerberos, другим протоколам SSO или через MFA.

В этом случае на сервере создаётся OAuth-приложение, и бот авторизуется через него методом `Bot.from_oauth()`. Помимо логина и пароля потребуется `client_id` приложения:

```python
bot = Bot.from_oauth(
    username="elisa",
    password="123tr",
    client_id="client_id_приложения",
    server="video.example.com",
    dispatcher=dp,
)
```

Требования:

- TrueConf Server 5.5.3 или новее;
- OAuth-приложение, созданное на сервере;
- у приложения настроен хотя бы один scope — достаточно `version:read`. Такой scope не раскрывает чувствительной информации: получить токен для приложения без scope невозможно.

Параметры `Bot.from_oauth()` совпадают с параметрами `from_credentials()`; дополнительно обязателен `client_id`. См. [справочник](../reference/Bot.md/#trueconf.Bot.from_oauth).

### Ошибки авторизации

| Исключение | Когда возникает | Что делать |
| --- | --- | --- |
| `PasswordAuthDisabledError` | Сервер отклонил запрос токена (403 `auth_method_disabled`) — на сервере отключена авторизация по логину и паролю | Используйте `Bot.from_oauth()` |
| `OAuthMissingScopeError` | Сервер отклонил OAuth-запрос токена (400 `invalidScope`) — у OAuth-приложения не настроен scope | Добавьте scope (например, `version:read`) в настройки приложения на сервере |

Обе ошибки наследуются от `TrueConfChatBotError` и импортируются из `trueconf.exceptions`. Подробнее — в [справочнике](../reference/Exceptions.md).
