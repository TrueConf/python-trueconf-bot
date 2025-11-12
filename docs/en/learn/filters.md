---
title: Filters
icon:
---

# Filters

Filters are necessary for routing incoming events (updates) to the correct
handlers. The search for a handler always stops at the first match with a set of
filters. By default, all handlers have an empty set of filters, so all updates
will be passed to the first handler with an empty set of filters. In the current
implementation, two main approaches for filtering text messages are available:

- **Command** — a filter for processing commands in the format /command
\[arguments].
- **MagicFilter** is a universal declarative filter (from the magic-filter
library) for event field validation.

These two approaches are often used together: **Command** checks the command
format and extracts arguments, while **MagicFilter** imposes additional
conditions on arguments or other message fields.

!!! Tip 
	Below you can find examples of using filters, but if that's not enough, check out [examples in the repository](https://github.com/TrueConf/python-trueconf-bot/tree/master/examples).

## Command

**Command** — a convenient filter for parsing and processing commands in message
text.

```python
Command(*commands: str | Pattern[str], prefix: str = "/", ignore_case: bool = False, magic: MagicFilter | None = None)
```

!!! note "Capabilities" 
	- Accept one or more commands: `Command("start")`, `Command("info", "about")`. 
	- Support regular expression patterns: `Command(re.compile(r"echo_\d+"))`. 
	- Support different prefixes (default is `/`), for example `prefix="!/"` — then `!cmd` and `/cmd` will be valid. 
	- Ignore case for string commands (`ignore_case=True`). 
	- Accept optional `magic` — **MagicFilter**, which additionally validates the `CommandObject` (see [below](#commandobject)).

The **Command** filter operates as follows:

1. Checks that the message is a `Message` and that it is of type `PLAIN_MESSAGE`.
1. Checks if the text begins with the specified prefix (default is `/`).
1. Splits the string into a command and arguments (if any).
1. Compares the command with the specified ones (including support for
`re.Pattern`).
1. If `magic` is passed, `MagicFilter` is applied to the `CommandObject`.
1. If the `magic` filter is triggered, it returns a dictionary
`{"command": command_obj}`.

### CommandObject

If the filter is triggered, the handler can receive a **CommandObject** (passed
as the `command` parameter):

```python
@dataclass(frozen=True)
class CommandObject:
    prefix: str
    command: str
    args: str | None
    regexp_match: Match[str] | None = None
    magic_result: Any | None = None
```

!!! Note "Fields" 
	 - `prefix` — the prefix character (`/`, `!`, etc.). 
	 - `command` — the command name without the prefix. 
	 - `args` — the argument string (everything after the space). 
	 - `regexp_match` — the result of `re.Match` if the command was specified as a regular expression. 
	 - `magic_result` — optional data returned by `magic` (if applicable).

### Examples

**Basic handler:**

```python
@r.message(Command("ping"))
async def handle_ping(message: Message):
    await bot.send_message(chat_id=message.chat_id, text="pong")
```

**Multiple commands:**

```python
@r.message(Command("info", "about", "whoami"))
async def handle_info(message: Message, command: CommandObject):
    await bot.send_message(chat_id=message.chat_id, text=f"Used /{command.command}")
```

**Command with prefix:**

```python
@r.message(Command(re.compile(r"echo_\d+")))
async def handle_echo_numbered(message: Message, command: CommandObject):
    await bot.send_message(chat_id=message.chat_id, text=f"Echo: {command.command} {command.args or ''}")
```

## MagicFilter

**MagicFilter** is a declarative, chainable filter from the **magic-filter**
package. It allows you to express checks on event fields using chains and
operators. Instead of manually checking update fields within the handler,
conditions can be set directly in the decorator.

The filter works "lazily": when a handler is declared, only the chain of checks
is stored, not the result. The actual evaluation happens only when a new event
arrives, so filters can be easily combined and remain readable. This approach
makes the code shorter and clearer, showing exactly which updates will be
processed by a given handler.

The idea behind **MagicFilter** is simple: describe an attribute chain and a
condition, then apply it to an object. Imagine you have an object with nested
fields. Instead of manually checking something like
`if obj.foo.bar.baz == "spam": ...`, you can construct the filter declaratively:

```python
F.foo.bar.baz == "spam"
```

The resulting filter is not an immediate check, but an object that "remembers"
the condition. When processing an update, this filter is automatically applied
to the object (the router handles the check under the hood). Technically, the
`.resolve(obj)` method is used for this, but you don't need to call it manually
— just define the condition in the decorator, and it will be executed during
routing.

```python
@r.message(F.text == "ping")
async def ping_handler(message):
    await message.answer("pong")
```

Here, the filter `F.text == "ping"` will be automatically checked for each
incoming message. If the condition matches, the handler will be triggered.

### Examples

The **MagicFilter** object supports basic logical operations on object attributes.

**Existence Check:**

```python
F.photo  # lambda message: message.photo
```

**Equality:**

```python
F.text == "hello"        # lambda message: message.text == "hello"
F.from_user.id == 42     # lambda message: message.from_user.id == 42
F.text != "spam"         # lambda message: message.text != "spam"
```

**Set membership:**

```python
# lambda query: query.from_user.id in {42, 1000, 123123}
F.from_user.id.in_({42, 1000, 123123})  

# lambda query: query.data in {"foo", "bar", "baz"}
F.data.in_({"foo", "bar", "baz"})
```

**Contains:**

```python
F.text.contains("foo")  # lambda message: "foo" in message.text
```

**Starts/ends with the string:**

```python
F.text.startswith("foo")  # lambda message: message.text.startswith("foo")
F.text.endswith("bar")    # lambda message: message.text.endswith("bar")
```

**Regular Expressions:**

```python
F.text.regexp(r"Hello, .+")  # lambda message: re.match(r"Hello, .+", message.text)
```

**Custom Function:**

```python
# lambda message: (lambda chat: chat.id == -42)(message.chat)
F.chat.func(lambda chat: chat.id == -42)
```

**Inversion of result:**

```python
~F.text # not message.text        
~F.text.startswith("spam") #not message.text.startswith("spam")
```

**Combining conditions:**

```python
(F.from_user.id == 42) & (F.text == "admin")

F.text.startswith("a") | F.text.endswith("b")

(F.from_user.id.in_({42, 777, 911})) & (F.text.startswith("!") | F.text.startswith("/")) & F.text.contains("ban")
```

**Attribute Modifiers (Strings):**

```python
F.text.lower() == "test"           # message.text.lower() == "test"  
F.text.upper().in_({"FOO", "BAR"}) # message.text.upper() in {"FOO", "BAR"}
F.text.len() == 5                  # len(message.text) == 5
```

## Combining Filters

Combining **Command** and **MagicFilter** is a common and recommended practice:
**Command** parses the command and creates a **CommandObject**, while `magic`
allows you to impose additional conditions on `args` or other parts of the
**CommandObject**.

**Filter the /echo command only if arguments are present:**

```python
@r.message(Command("echo", magic=F.args.is_not(None)))
async def handle_echo(message: Message, command: CommandObject):
    await bot.send_message(chat_id=message.chat_id, text=command.args)
```

**Additional argument length check:**

```python
@r.message(Command("upper", magic=F.args.len() > 3))
async def handle_upper(message: Message, command: CommandObject):
    await bot.send_message(chat_id=message.chat_id, text=(command.args or "").upper())
```

**Check with func — single word:**

```python
@r.message(Command("repeat", magic=F.args.func(lambda x: isinstance(x, str) and len(x.split()) == 1)))
async def handle_repeat(message: Message, command: CommandObject):
    await bot.send_message(chat_id=message.chat_id, text=f"{command.args} {command.args}")
```

**Combining regexp and magic:**

```python
@r.message(Command(re.compile(r"echo_\\d+"), magic=F.args))
async def handle_special_echo(message: Message, command: CommandObject):
    await bot.send_message(chat_id=message.chat_id, text=f"Special: {command.command} -> {command.args}")
```
