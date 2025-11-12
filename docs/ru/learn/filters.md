---
title: Фильтры
icon: 
---

# Фильтры

Фильтры необходимы для маршрутизации входящих событий (апдейтов) к правильным обработчикам.
Поиск обработчика всегда останавливается при первом совпадении с набором фильтров. 
По умолчанию все обработчики имеют пустой набор фильтров, поэтому все обновления будут переданы первому обработчику с пустым набором фильтров.
В текущей реализации доступны два основных подхода для фильтрации текстовых сообщений:

- **Command** — фильтр для обработки команд вида /команда \[аргументы].
- **MagicFilter** — универсальный декларативный фильтр (из библиотеки magic-filter) для проверки полей события.

Эти два подхода часто используются вместе: **Command** проверяет форму команды и выделяет аргументы, а **MagicFilter** — накладывает дополнительные условия на аргументы или другие поля сообщения.

!!! Tip
    Ниже вы сможете найти примеры использования фильтров, но если этого окажется недостаточно, то смотрите [примеры в репозитории](https://github.com/TrueConf/python-trueconf-bot/tree/master/examples).

## Command

**Command** — удобный фильтр для парсинга и обработки команд в тексте сообщения.

```python
Command(*commands: str | Pattern[str],
        prefix: str = "/",
        ignore_case: bool = False,
        magic: MagicFilter | None = None)
```

!!! note "Что умеет?"
    - Принимать одну или несколько команд: `Command("start")`, `Command("info", "about")`.
	- Поддерживать регулярные шаблоны: `Command(re.compile(r"echo_\d+"))`.
	- Поддерживать разные префиксы (по умолчанию `/`), например `prefix="!/"` — тогда будут валидны `!cmd` и `/cmd`.
	- Игнорировать регистр для строковых команд (`ignore_case=True`).
	- Принимать опциональный `magic` — **MagicFilter**, который дополнительно валидирует `CommandObject` (см. ниже).

Фильтр **Command** работает следующим образом:

1. Проверяет, что сообщение — это `Message`, и что оно имеет тип `PLAIN_MESSAGE`.
2. Проверяет, начинается ли текст с указанного префикса (по умолчанию `/`).
3. Делит строку на команду и аргументы (если есть).
4. Сравнивает команду с заданными (включая поддержку `re.Pattern`).
5. Если передан `magic`, применяется `MagicFilter` к `CommandObject`.
6. Если `magic`-фильтр сработал, возвращает словарь `{"command": command_obj}`.

### CommandObject

Если фильтр срабатывает, в хендлер можно получить объект **CommandObject** (передаётся как параметр `command`):

```python
@dataclass(frozen=True)
class CommandObject:
    prefix: str
    command: str
    args: str | None
    regexp_match: Match[str] | None = None
    magic_result: Any | None = None
```

!!! Note "Поля"
	- `prefix` — символ префикса (`/` или `!` и т.п.).
	- `command` — имя команды без префикса.
	- `args` — строка аргументов (всё, что после пробела).
	- `regexp_match` — результат `re.Match`, если команда была задана как регулярка.
	- `magic_result` — опциональные данные, которые вернёт `magic` (если применимо).

### Примеры

**Простейший хендлер:**

```python
@r.message(Command("ping"))
async def handle_ping(message: Message):
    await bot.send_message(chat_id=message.chat_id, text="pong")
```

**Несколько команд:**

```python
@r.message(Command("info", "about", "whoami"))
async def handle_info(message: Message, command: CommandObject):
    await bot.send_message(chat_id=message.chat_id, text=f"Used /{command.command}")
```

**Команда с префиксом:**

```python
@r.message(Command(re.compile(r"echo_\d+")))
async def handle_echo_numbered(message: Message, command: CommandObject):
    await bot.send_message(chat_id=message.chat_id, text=f"Echo: {command.command} {command.args or ''}")
```

## MagicFilter

**MagicFilter** — декларативный, цепочечный фильтр из пакета **magic-filter**. 
Позволяет выражать проверки над полями события в виде цепочек и операторов.
Вместо того чтобы вручную проверять поля апдейта внутри обработчика, условия можно задать прямо в декораторе.

Фильтр работает «лениво»: при объявлении обработчика сохраняется сама цепочка проверок, а не её результат. 
Проверка выполняется только в момент, когда приходит новое событие, поэтому фильтры легко комбинируются и остаются читаемыми. 
Такой подход делает код короче и понятнее: сразу видно, какие именно апдейты пройдут через конкретный обработчик.

Идея **MagicFilter** проста: вы описываете цепочку атрибутов и условие, а затем применяете её к объекту. 
Представьте, что у вас есть объект с вложенными полями. Вместо ручной проверки вида `if obj.foo.bar.baz == "spam": ...` можно собрать фильтр декларативно:

```python
F.foo.bar.baz == "spam"
```

Получившийся фильтр — это не мгновенная проверка, а объект, который «запоминает» условие. 
При обработке апдейта этот фильтр автоматически применяется к объекту (роутер сам выполняет проверку под капотом). 
Технически для этого используется метод `.resolve(obj)`, 
но напрямую вызывать его в коде не требуется — достаточно описать условие в декораторе, и оно будет выполнено при маршрутизации.

```python
@r.message(F.text == "ping")
async def ping_handler(message):
    await message.answer("pong")
```

Здесь фильтр `F.text == "ping"` будет автоматически проверен для каждого входящего сообщения. Если условие совпадает, сработает обработчик.

### Примеры

Объект **MagicFilter** поддерживает базовые логические операции над атрибутами объектов.

**Проверка существования:**

```python
F.photo  # message.photo
```

**Равенство:**

```python
F.text == "hello"        # message.text == "hello"
F.from_user.id == 42     # message.from_user.id == 42
F.text != "spam"         # message.text != "spam"
```

**Принадлежность множеству:**

```python
# query.from_user.id in {42, 1000, 123123}
F.from_user.id.in_({42, 1000, 123123})

# query.data in {"foo", "bar", "baz"}
F.data.in_({"foo", "bar", "baz"})       
```

**Содержит:**

```python
F.text.contains("foo")  # "foo" in message.text
```

**Начинается/заканчивается строкой:**

```python
F.text.startswith("foo")  # message.text.startswith("foo")
F.text.endswith("bar")    # message.text.endswith("bar")
```

**Регулярные выражения:**

```python
F.text.regexp(r"Hello, .+")  # re.match(r"Hello, .+", message.text)
```

**Пользовательская функция:**

```python
# (lambda chat: chat.id == -42)(message.chat)
F.chat.func(lambda chat: chat.id == -42)  
```

**Инверсия результата:**

```python
~F.text                     # not message.text
~F.text.startswith("spam")  # not message.text.startswith("spam")
```

**Комбинирование условий:**

```python
(F.from_user.id == 42) & (F.text == "admin")

F.text.startswith("a") | F.text.endswith("b")

(F.from_user.id.in_({42, 777, 911})) & (F.text.startswith("!") | F.text.startswith("/")) & F.text.contains("ban")   
```

**Модификаторы атрибутов (строки):**

```python
F.text.lower() == "test"           # message.text.lower() == "test"
F.text.upper().in_({"FOO", "BAR"}) # message.text.upper() in {"FOO", "BAR"}
F.text.len() == 5                  # len(message.text) == 5
```

## Объединение фильтров

Комбинирование **Command** и **MagicFilter** — частая и рекомендованная практика: **Command** парсит команду и формирует **CommandObject**, а `magic` позволяет наложить дополнительные условия на `args` или другие части **CommandObject**.

**Фильтрация команды /echo только если есть аргументы:**

```python
@r.message(Command("echo", magic=F.args.is_not(None)))
async def handle_echo(message: Message, command: CommandObject):
    await bot.send_message(chat_id=message.chat_id, text=command.args)
```

**Дополнительная проверка длины аргумента:**

```python
@r.message(Command("upper", magic=F.args.len() > 3))
async def handle_upper(message: Message, command: CommandObject):
    await bot.send_message(chat_id=message.chat_id, text=(command.args or "").upper())
```

**Проверка с func — единичное слово:**

```python
@r.message(Command("repeat", magic=F.args.func(lambda x: isinstance(x, str) and len(x.split()) == 1)))
async def handle_repeat(message: Message, command: CommandObject):
    await bot.send_message(chat_id=message.chat_id, text=f"{command.args} {command.args}")
```

**Комбинирование regexp и magic:**

```python
@r.message(Command(re.compile(r"echo_\\d+"), magic=F.args))
async def handle_special_echo(message: Message, command: CommandObject):
    await bot.send_message(chat_id=message.chat_id, text=f"Special: {command.command} -> {command.args}")
```