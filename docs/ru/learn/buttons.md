---
title: Интерактивные кнопки
description: Как добавить к сообщению inline-кнопки и обработать команды от них
icon: material/gesture-tap-button
---

# Интерактивные кнопки

Inline-кнопки отображаются под сообщением и помогают пользователю взаимодействовать с ботом без ручного ввода: выбрать команду, открыть ссылку, отправить подготовленный текст или скопировать данные.

Начнём с одной кнопки, а затем соберём из них меню и добавим обработку нажатий.

!!! info "Требования"
    - TrueConf Server 5.5.6 или новее;
    - TrueConf для Windows, macOS и Linux 8.6.0 или новее;
    - TrueConf для Android 3.3.0 или новее;
    - TrueConf для iOS 4.2.0 или новее.

!!! caution
    Кнопки можно прикреплять только к обычным текстовым сообщениям. Отправлять сообщения с кнопками могут только чат-боты.

Полное описание формата кнопок на уровне WebSocket API приведено в [документации TrueConf Server API](https://trueconf.ru/docs/chatbot-connector/ru/buttons/).

## Первая кнопка

Кнопка создаётся с помощью `InlineKeyboardButton`, а клавиатура — с помощью `InlineKeyboardMarkup`:

```python
from trueconf import InlineKeyboardButton, InlineKeyboardMarkup

keyboard = InlineKeyboardMarkup(
    buttons=[
        [InlineKeyboardButton(text="Помощь", command="menu:help")],
    ]
)
```

Здесь `text` — надпись на кнопке, а `command` — команда, которую бот получит после нажатия.

Параметр `buttons` содержит список рядов. Поэтому даже для одной кнопки нужны два вложенных списка: внешний задаёт клавиатуру, внутренний — первый ряд.

Передайте готовую клавиатуру в параметр `buttons` метода отправки сообщения:

```python
await bot.send_message(
    chat_id="chat_id",
    text="Выберите действие:",
    buttons=keyboard,
)
```

Клавиатуру также можно передать в `message.answer(...)` и `message.reply(...)`.

!!! tip
    Если одна клавиатура используется в нескольких обработчиках, создайте её один раз на уровне модуля и передавайте в нужные методы.

## Действия кнопок

В предыдущем примере использовалась кнопка `command`, которая отправляет команду боту. Всего библиотека поддерживает четыре действия. Для каждой кнопки нужно указать ровно одно из них:

| Параметр | Что происходит при нажатии |
| --- | --- |
| `command` | Боту приходит событие `CallbackQuery`; сообщение в чат не отправляется |
| `url` | Открывается ссылка с протоколом `http`, `https`, `mailto` или `trueconf` |
| `message` | От имени пользователя отправляется заданное сообщение |
| `copy_data` | Заданные данные копируются в буфер обмена |

Кнопки можно объединять в несколько рядов:

```python
from trueconf import ButtonStyle, InlineKeyboardButton, InlineKeyboardMarkup

keyboard = InlineKeyboardMarkup(
    buttons=[
        [
            InlineKeyboardButton(
                text="Помощь",
                command="menu:help",
                style=ButtonStyle.PRIMARY,
            ),
            InlineKeyboardButton(
                text="Открыть сайт",
                url="https://trueconf.com",
            ),
        ],
        [
            InlineKeyboardButton(
                text="Подготовить вопрос",
                message="Расскажите подробнее",
                draft=True,
            ),
            InlineKeyboardButton(
                text="Скопировать код",
                copy_data="code-42",
            ),
        ],
    ]
)
```

В этом примере:

- `Помощь` отправляет боту команду `menu:help`;
- `Открыть сайт` открывает ссылку;
- `Подготовить вопрос` помещает текст в поле ввода благодаря `draft=True`;
- `Скопировать код` копирует строку `code-42`.

Если у кнопки `message` не указывать `draft=True`, подготовленный текст будет сразу отправлен в чат от имени пользователя.

!!! tip
    Параметр `text` обязателен для всех действий, кроме `url`. Если не задать надпись кнопки-ссылки, клиент отобразит саму ссылку.

!!! caution
    Только кнопка `command` отправляет событие боту. Нажатия кнопок `url`, `message` и `copy_data` обрабатываются клиентским приложением и не создают `CallbackQuery`.

## Дополнительные параметры

Когда базового действия недостаточно, поведение и внешний вид кнопки можно уточнить дополнительными параметрами:

| Параметр | Для каких кнопок | Назначение |
| --- | --- | --- |
| `style` | Для всех | Задаёт стиль `ButtonStyle.DEFAULT`, `ButtonStyle.PRIMARY`, `ButtonStyle.DANGER` или `ButtonStyle.SUCCESS` |
| `button_id` | Для всех | Задаёт идентификатор кнопки; для `command` он приходит в событии нажатия |
| `draft` | Только `message` | Помещает текст в поле ввода вместо немедленной отправки |
| `custom_data` | Только `command` | Передаёт боту дополнительные данные вместе с командой |
| `to` | Только `command` | Направляет команду другому боту |

Например, в `custom_data` можно передать идентификатор выбранного объекта отдельно от команды:

```python
button = InlineKeyboardButton(
    text="Добавить в корзину",
    command="cart:add",
    custom_data="product-42",
    button_id="add-product",
)
```

!!! warning
    Параметр `wait_reply=True` и метод `CallbackQuery.answer()` пока нельзя использовать, поскольку клиентские приложения TrueConf ещё не поддерживают этот сценарий. Поэтому при их использовании библиотека вызывает `NotImplementedError`.

## Обработка команды

После нажатия кнопки `command` бот получает объект `CallbackQuery`. Для обработки события зарегистрируйте `@router.callback_query()` и добавьте фильтр по значению команды:

```python
from trueconf import CallbackQuery, F, Router

router = Router()


@router.callback_query(F.command == "menu:help")
async def show_help(callback: CallbackQuery):
    await callback.edit_message(text="Раздел помощи", buttons=help_keyboard)
```

Фильтр `F.command == "menu:help"` позволяет обработчику реагировать только на нужную кнопку. Для группы связанных команд удобно использовать общий префикс и фильтр `F.command.startswith(...)`:

```python
@router.callback_query(F.command.startswith("menu:"))
async def handle_menu(callback: CallbackQuery):
    ...
```

Данные о нажатии доступны через свойства объекта `CallbackQuery`:

- `callback.command` — команда нажатой кнопки;
- `callback.custom_data` — данные из `custom_data`;
- `callback.message` — сообщение с кнопкой;
- `callback.chat` — чат, в котором нажали кнопку;
- `callback.command_source.button_id` — значение `button_id`, если оно было задано.

## Изменение меню после нажатия

Кнопки часто используются для навигации: пользователь открывает раздел, а бот изменяет текст сообщения и показывает новый набор действий. Из обработчика для этого удобно вызывать `callback.edit_message(...)`:

```python
@router.callback_query(F.command == "menu:catalog")
async def show_catalog(callback: CallbackQuery):
    await callback.edit_message(
        text="Выберите категорию:",
        buttons=catalog_keyboard,
    )
```

Текст и клавиатуру можно изменять независимо друг от друга:

```python
# Изменить только текст и сохранить текущие кнопки
await callback.edit_message(text="Новый текст")

# Изменить только кнопки и сохранить текущий текст
await callback.edit_message(buttons=new_keyboard)

# Изменить текст и кнопки одновременно
await callback.edit_message(
    text="Новый текст",
    buttons=new_keyboard,
)

# Удалить кнопки и сохранить текущий текст
await callback.edit_message(buttons=None)
```

Если параметр `buttons` не указан, текущие кнопки сохраняются. Чтобы удалить их, нужно явно передать `buttons=None`.

Если сообщение изменяется не из обработчика `CallbackQuery`, используйте `bot.edit_message(...)`. В этом случае нужно обязательно передать текст сообщения:

```python
await bot.edit_message(
    message_id="message_id",
    text="Обновлённый текст",
    buttons=new_keyboard,
)
```

## Получение клавиатуры сообщения

Клавиатура полученного текстового сообщения доступна через `TextContent.buttons`:

```python
message = await bot.get_message_by_id(message_id)

if message.content.buttons is not None:
    keyboard = message.content.buttons
```

## Ограничения

При создании клавиатуры соблюдайте следующие ограничения:

- не более 8 рядов и 8 кнопок в каждом ряду;
- не более 64 кнопок во всей клавиатуре;
- `text` — от 1 до 32 символов, если надпись задана;
- `command` — от 1 до 255 ASCII-символов;
- `custom_data` — от 1 до 4096 ASCII-символов;
- `copy_data` — от 1 до 4095 символов Unicode;
- `url` — от 8 до 8095 ASCII-символов. 
- HTML- и Markdown-разметка в тексте кнопки не обрабатывается, а переносы строк заменяются пробелами.

## Полный пример

!!! tip "Готовые боты"
    Больше готовых сценариев использования кнопок доступно в [примерах на GitHub](https://github.com/TrueConf/python-trueconf-bot/tree/master/examples/buttons_bot.py).

Этот бот отправляет меню в ответ на команду `/menu`, а затем обрабатывает кнопку `Поздороваться`:

```python
import asyncio

from trueconf import (
    Bot,
    CallbackQuery,
    Dispatcher,
    F,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    Message,
    Router,
)
from trueconf.filters import Command

router = Router()
dispatcher = Dispatcher()

MAIN_MENU = InlineKeyboardMarkup(
    buttons=[
        [
            InlineKeyboardButton(text="Поздороваться", command="menu:hello"),
            InlineKeyboardButton(text="Открыть сайт", url="https://trueconf.com"),
        ],
        [InlineKeyboardButton(text="Скопировать", copy_data="trueconf")],
    ]
)


@router.message(Command("menu"))
async def show_menu(message: Message):
    await message.answer("Выберите действие:", buttons=MAIN_MENU)


@router.callback_query(F.command == "menu:hello")
async def say_hello(callback: CallbackQuery):
    await callback.edit_message(text="Здравствуйте!", buttons=MAIN_MENU)


async def main():
    dispatcher.include_router(router)

    bot = Bot.from_credentials(
        username="echo_bot",
        password="123tr",
        server="video.example.com",
        dispatcher=dispatcher,
    )
    await bot.run()


if __name__ == "__main__":
    asyncio.run(main())
```
