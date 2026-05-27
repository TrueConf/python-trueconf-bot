---
title: FSM (Машина состояний)
icon: material/transit-connection-variant
---

# FSM — Конечный автомат состояний

## Что это такое

**FSM** (Finite State Machine) — конечный автомат состояний. Это механизм, который позволяет боту «запоминать», на каком этапе разговора находится пользователь, и реагировать на сообщения в зависимости от этого этапа.

Представьте анкету из нескольких шагов:

1. Бот спрашивает имя → пользователь вводит имя
2. Бот спрашивает возраст → пользователь вводит возраст
3. Бот спрашивает город → пользователь вводит город
4. Бот выводит итог

Без FSM бот не понимает, какой ответ он сейчас ждёт. Если пользователь введёт «25» — бот не поймёт, это возраст или что-то другое. **FSM решает эту проблему**: бот точно знает, что на шаге `age` любое сообщение от пользователя — это возраст.

## Зачем это нужно

FSM полезен везде, где нужен **пошаговый диалог**:

- **Анкеты и формы** — регистрация, опросы, сбор данных
- **Мастер настройки** — пошаговая настройка параметров
- **Поддержка** — заявка → описание проблемы → прикрепление файлов → подтверждение
- **Меню с разделами** — навигация с помощью команд или текста

## Основные концепции

| Концепция | Что это | Пример |
|-----------|---------|--------|
| **State** | Одно конкретное состояние (шаг) | `name`, `age`, `confirm` |
| **StatesGroup** | Группа связанных состояний | `Form` с состояниями `name`, `age`, `confirm` |
| **FSMContext** | Объект для чтения и записи состояния и данных | `await state.get_state()`, `await state.set_state(...)` |
| **StateFilter** | Фильтр, который пропускает хендлер только в нужном состоянии | `@router.message(StateFilter(Form.name))` |
| **Storage** | Хранилище состояний (в памяти) | `MemoryStorage()` |

## Быстрый старт

### Шаг 1. Импорты

```python
from trueconf import Bot, Dispatcher, Router, F
from trueconf.types import Message
from trueconf.filters import Command
from trueconf.fsm import FSMContext, State, StatesGroup, StateFilter
from trueconf.fsm.storage.memory import MemoryStorage
```

### Шаг 2. Создание хранилища и диспетчера

```python
storage = MemoryStorage()
dp = Dispatcher(storage=storage)
router = Router()
dp.include_router(router)
```

!!! info
    `MemoryStorage` хранит состояния в оперативной памяти. После перезапуска бота все состояния сбрасываются. 
    Для разработки и тестирования этого достаточно. Для продакшена вы можете реализовать [свое постоянное хранилище](#создание-кастомного-хранилища).

### Шаг 3. Объявление состояний

Создайте класс, наследующийся от `StatesGroup`, и объявите в нём состояния как атрибуты:

```python
class Form(StatesGroup):
    name = State()     # "Form:name"
    age = State()      # "Form:age"
    city = State()     # "Form:city"
```

Каждое состояние автоматически получает строковый идентифиатор в формате `ИмяГруппы:ИмяСостояния`. 
Вы не задаёте его вручную — он формируется из имени класса и имени атрибута.

### Шаг 4. Обработчики

```python
@router.message(Command("start"))
async def cmd_start(msg: Message, state: FSMContext):
    await state.set_state(Form.name)
    await msg.answer("Как вас зовут?")


@router.message(Form.name)
async def process_name(msg: Message, state: FSMContext):
    await state.update_data(name=msg.text)
    await state.set_state(Form.age)
    await msg.answer("Сколько вам лет?")


@router.message(Form.age)
async def process_age(msg: Message, state: FSMContext):
    await state.update_data(age=msg.text)
    data = await state.get_data()
    await state.clear()
    await msg.answer(f"Приятно познакомиться, {data['name']}!\nВам {data['age']} лет.")


@router.message(Command("cancel"))
async def cmd_cancel(msg: Message, state: FSMContext):
    await state.clear()
    await msg.answer("Отменено.")
```

### Шаг 5. Запуск

```python
bot = Bot.from_credentials(
    server="your-server",
    username="your-bot",
    password="your-password",
    dispatcher=dp,
)

async def main():
    await bot.run()

import asyncio
if __name__ == "__main__":
    asyncio.run(main())
```

!!! Tip
    Обратите внимание: `state: FSMContext` передаётся как параметр в хендлер автоматически. 
    Вам не нужно создавать его вручную — библиотека сама подставит нужный объект.

## Объявление состояний

### StatesGroup и State

```python
from trueconf.fsm import State, StatesGroup

class OrderForm(StatesGroup):
    product = State()    # "OrderForm:product"
    quantity = State()   # "OrderForm:quantity"
    address = State()    # "OrderForm:address"
    confirm = State()    # "OrderForm:confirm"
```

!!! note "Правила"
    - Класс **обязательно** должен наследоваться от `StatesGroup`.
    - Каждое состояние — это атрибут класса, созданный через `State()`
    - Имена состояний формируются **автоматически** из имени группы и имени атрибута
    - Не используйте один и тот же `State()` в разных группах — каждый `State` привязывается к одной группе

### Несколько групп

Можно создавать сколько угодно групп для разных сценариев:

```python
class FeedbackForm(StatesGroup):
    rating = State()
    comment = State()

class SupportTicket(StatesGroup):
    topic = State()
    description = State()
    priority = State()
```

### Вложенные группы

Группы могут быть вложенными друг в друга — это удобно для сложных многошаговых форм:

```python
class Registration(StatesGroup):
    name = State()                       # "Registration:name"
    age = State()                        # "Registration:age"

    class Address(StatesGroup):          # вложенная группа
        city = State()                   # "Registration.Address:city"
        street = State()                 # "Registration.Address:street"
        zip_code = State()               # "Registration.Address:zip_code"

    confirm = State()                    # "Registration:confirm"
```

Идентификаторы вложенных состояний формируются через точку: `Registration.Address:city`.

## Установка и чтение состояния

### set_state — установить состояние

```python
await state.set_state(Form.name)
```

Устанавливает текущее состояние пользователя. Все последующие сообщения от этого пользователя будут обрабатываться хендлерами, привязанными к `Form.name`.

### get_state — получить текущее состояние

```python
current = await state.get_state()
# "Form:name" или None, если состояния нет
```

### clear — сбросить состояние

```python
await state.clear()
```

Сбрасывает текущее состояние **и** все сохранённые данные. После вызова `clear()` пользователь считается «без состояния» — хендлеры с `StateFilter` его больше не поймают.

!!! warning "Разница между clear и set_state(None)"
    - `await state.clear()` — сбрасывает состояние и **удаляет все данные**
    - `await state.set_state(None)` — сбросит состояние, но **данные сохранятся**

    Используйте `clear()` когда диалог полностью завершён и данные больше не нужны.

## Хранение и чтение данных

Помимо состояния (на каком шаге пользователь), FSM позволяет сохранять произвольные данные (что именно пользователь ввёл на каждом шаге).

### update_data — сохранить данные

```python
# Через именованные аргументы:
await state.update_data(name="Иван", age=25)

# Через словарь:
await state.update_data({"name": "Иван", "age": 25})

# Комбинация (словарь перезаписывает kwargs при конфликте):
await state.update_data({"name": "Иван"}, age=25)
```

!!! note
    `update_data` **объединяет** новые данные с уже существующими. Чтобы заменить все данные целиком, используйте `set_data`.

### get_data — получить все данные

```python
data = await state.get_data()
# {"name": "Иван", "age": 25}
```

### get_value — получить одно значение

```python
name = await state.get_value("name")
# "Иван"

name = await state.get_value("name", "Не указано")
# "Иван" (или "Не указано", если ключа нет)
```

Это удобный шорткат — не нужно получать весь словарь ради одного поля.

### set_data — заменить все данные

```python
await state.set_data({"name": "Пётр"})
```

Полностью заменяет хранимые данные. Предыдущие данные теряются.

## Фильтрация по состоянию

### StateFilter

`StateFilter` — фильтр, который пропускает хендлер **только** когда текущее состояние пользователя совпадает с одним из указанных:

```python
from trueconf.fsm import StateFilter

@router.message(StateFilter(Form.name))
async def process_name(msg: Message, state: FSMContext):
    ...
```

### Несколько состояний

Фильтр принимает несколько состояний — хендлер сработает, если текущее состояние совпадёт с **любым** из них:

```python
@router.message(StateFilter(Form.name, Form.age))
async def process_name_or_age(msg: Message, state: FSMContext):
    ...
```

### Отсутствие состояния

`StateFilter(None)` пропускает хендлер только когда у пользователя **нет** активного состояния:

```python
@router.message(StateFilter(None))
async def no_active_state(msg: Message, state: FSMContext):
    await msg.answer("У вас нет активного диалога. Введите /start.")
```

### Любой_state (wildcard)

Импортируйте `any_state` для обработки сообщений **в любом состоянии**:

```python
from trueconf.fsm import any_state

@router.message(any_state)
async def catch_all(msg: Message, state: FSMContext):
    await msg.answer("Я не понимаю. Введите /cancel для отмены.")
```

### Сахар: State вместо StateFilter

Для краткости можно передавать `State` напрямую в декоратор — библиотека автоматически обернёт его в `StateFilter`:

```python
# Эти два варианта эквивалентны:

@router.message(StateFilter(Form.name))
async def process_name(msg: Message, state: FSMContext): ...

@router.message(Form.name)
async def process_name(msg: Message, state: FSMContext): ...
```

### Команды внутри состояний

Можно комбинировать `StateFilter` с `Command` — хендлер сработает только если пользователь **в нужном состоянии** И отправил **конкретную команду**:

```python
# /skip работает ТОЛЬКО в состоянии Form.name
@router.message(Form.name, Command("skip"))
async def skip_name(msg: Message, state: FSMContext):
    await state.update_data(name="Аноним")
    await state.set_state(Form.age)
    await msg.answer("Имя пропущено. Сколько вам лет?")
```

Несколько команд в одном состоянии:

```python
@router.message(Form.confirm, Command("yes"))
async def confirm_yes(msg: Message, state: FSMContext):
    data = await state.get_data()
    await state.clear()
    await msg.answer(f"Готово, {data['name']}!")

@router.message(Form.confirm, Command("no"))
async def confirm_no(msg: Message, state: FSMContext):
    await state.clear()
    await msg.answer("Отменено.")
```

!!! warning "Порядок хендлеров важен!"
    Router проверяет хендлеры **в порядке регистрации** и останавливается на первом совпавшем. 
    
    Если у вас есть хендлер с `Command("cancel")` и хендлер с `Form.name` — **регистрируйте команды первыми**, 
    иначе `/cancel` попадёт в хендлер состояния и не сработает как отмена:

    ```python
    # Правильно:
    @router.message(Command("cancel"))
    async def cmd_cancel(msg: Message, state: FSMContext):
        await state.clear()
        await msg.answer("Отменено.")

    @router.message(Form.name)
    async def process_name(msg: Message, state: FSMContext):
        ...
    ```

## Валидация ввода

Если пользователь ввёл некорректные данные — **не вызывайте** `set_state()`. Пользователь останется в текущем состоянии и сможет повторить ввод:

```python
@router.message(Form.age)
async def process_age(msg: Message, state: FSMContext):
    if not msg.text.isdigit():
        await msg.answer("Пожалуйста, введите число. Сколько вам лет?")
        return  # ← остаёмся в Form.age

    await state.update_data(age=int(msg.text))
    await state.set_state(Form.city)
    await msg.answer("В каком городе вы живёте?")
```

## Полный пример: анкета с валидацией

```python
import asyncio
from trueconf import Bot, Dispatcher, Router, F, Message
from trueconf.filters import Command
from trueconf.fsm import FSMContext, State, StatesGroup
from trueconf.fsm.storage.memory import MemoryStorage


class Survey(StatesGroup):
    name = State()
    age = State()
    city = State()
    confirm = State()


storage = MemoryStorage()
dp = Dispatcher(storage=storage)
router = Router()
dp.include_router(router)


@router.message(Command("cancel"))
async def cmd_cancel(msg: Message, state: FSMContext):
    current = await state.get_state()
    if current is None:
        await msg.answer("Нечего отменять.")
        return
    await state.clear()
    await msg.answer("Анкета отменена.")


@router.message(Command("start"))
async def cmd_start(msg: Message, state: FSMContext):
    await state.set_state(Survey.name)
    await msg.answer("Как вас зовут?")


@router.message(Survey.name)
async def process_name(msg: Message, state: FSMContext):
    if len(msg.text) < 2:
        await msg.answer("Имя слишком короткое. Попробуйте ещё раз:")
        return
    await state.update_data(name=msg.text)
    await state.set_state(Survey.age)
    await msg.answer("Сколько вам лет?")


@router.message(Survey.age)
async def process_age(msg: Message, state: FSMContext):
    if not msg.text.isdigit() or not (1 <= int(msg.text) <= 150):
        await msg.answer("Введите корректный возраст (1–150):")
        return
    await state.update_data(age=int(msg.text))
    await state.set_state(Survey.city)
    await msg.answer("В каком городе вы живёте?")


@router.message(Survey.city)
async def process_city(msg: Message, state: FSMContext):
    await state.update_data(city=msg.text)
    await state.set_state(Survey.confirm)
    data = await state.get_data()
    await msg.answer(
        f"Проверьте данные:\n\n"
        f"Имя: {data['name']}\n"
        f"Возраст: {data['age']}\n"
        f"Город: {data['city']}\n\n"
        f"Всё верно? (да/нет)"
    )


@router.message(Survey.confirm)
async def process_confirm(msg: Message, state: FSMContext):
    text = msg.text.lower().strip()
    if text == "да":
        data = await state.get_data()
        await state.clear()
        await msg.answer(f"Спасибо, {data['name']}! Анкета заполнена.")
    elif text == "нет":
        await state.clear()
        await msg.answer("Анкета отменена. Начните заново: /start")
    else:
        await msg.answer("Ответьте 'да' или 'нет'.")


bot = Bot.from_credentials(
    server="your-server",
    username="your-bot",
    password="your-password",
    dispatcher=dp,
)

if __name__ == "__main__":
    asyncio.run(bot.run())
```

## Стратегии FSM

По умолчанию состояние хранится **отдельно для каждого пользователя в каждом чате**. Это подходит для большинства ботов. Но иногда нужно иное поведение.

### FSMStrategy

```python
from trueconf.fsm import FSMStrategy

dp = Dispatcher(storage=MemoryStorage(), strategy=FSMStrategy.CHAT)
```

| Стратегия | Поведение | Когда использовать |
|-----------|-----------|-------------------|
| `USER_IN_CHAT` | Каждый пользователь в каждом чате — отдельное состояние | **По умолчанию.** Личные сообщения, анкеты |
| `CHAT` | Весь чат — одно состояние (все пользователи разделяют) | Голосования, совместные игры |
| `GLOBAL_USER` | Пользователь — одно состояние во всех чатах | Глобальные настройки пользователя |

## Создание кастомного хранилища

`MemoryStorage` подходит для разработки, но данные теряются при перезапуске. Для продакшена можно реализовать своё хранилище.

!!! Tip
    Если вам нужно своё сохранять данные в хранилище, чтобы они сохранялись при перезапуске бота — реализуйте абстрактный класс `BaseStorage`:

```python
from trueconf.fsm.storage.base import BaseStorage
from trueconf.fsm.key_builder import StorageKey

class MyCustomStorage(BaseStorage):
    async def get_state(self, key: StorageKey) -> str | None: ...
    async def set_state(self, key: StorageKey, state: str | None) -> None: ...
    async def get_data(self, key: StorageKey) -> dict: ...
    async def set_data(self, key: StorageKey, data: dict) -> None: ...
    async def update_data(self, key: StorageKey, updates: dict) -> dict: ...
    async def clear(self, key: StorageKey) -> None: ...
    async def close(self) -> None: ...
```

Подключается так же просто:

```python
dp = Dispatcher(storage=MyCustomStorage())
```

Весь пользовательский код (`state.set_state()`, `state.get_data()` и т.д.) работает **без изменений** — меняется только хранилище.