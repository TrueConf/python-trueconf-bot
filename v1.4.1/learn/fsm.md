# FSM — Finite State Machine⚓︎

## What it is⚓︎

FSM (Finite State Machine) is a mechanism that allows a bot to “remember” which step of a conversation a user is currently on and respond to messages according to that step.

Imagine a multi-step form:

- The bot asks for a name → the user enters a name

- The bot asks for an age → the user enters an age

- The bot asks for a city → the user enters a city

- The bot displays a summary

Without FSM, the bot does not understand which answer it is expecting at the moment. If the user enters “25”, the bot cannot determine whether it is an age or something else. FSM solves this problem: the bot knows that at the `age` step, any message from the user should be treated as the age.

## Why you need it⚓︎

FSM is useful wherever you need a step-by-step dialog:

- Questionnaires and forms — registration, surveys, data collection

- Setup wizards — step-by-step parameter configuration

- Support workflows — request → issue description → file attachment → confirmation

- Section-based menus — navigation using commands or text

## Core concepts⚓︎

| Concept | What it is | Example |
| --- | --- | --- |
| State | A single specific state (step) | `name`, `age`, `confirm` |
| StatesGroup | A group of related states | `Form` with the `name`, `age`, and `confirm` states |
| FSMContext | An object for reading and writing state and data | `await state.get_state()`, `await state.set_state(...)` |
| StateFilter | A filter that allows a handler to run only in the required state | `@router.message(StateFilter(Form.name))` |
| Storage | State storage (in memory) | `MemoryStorage()` |

## Quick start⚓︎

### Step 1. Imports⚓︎

```
from trueconf import Bot, Dispatcher, Router, F
from trueconf.types import Message
from trueconf.filters import Command
from trueconf.fsm import FSMContext, State, StatesGroup, StateFilter
from trueconf.fsm.storage.memory import MemoryStorage
```

### Step 2. Creating storage and a dispatcher⚓︎

```
storage = MemoryStorage()
dp = Dispatcher(storage=storage)
router = Router()
dp.include_router(router)
```

Info

`MemoryStorage` stores states in RAM. After the bot restarts, all states are reset. This is enough for development and testing. For production, you can implement your own persistent storage.

### Step 3. Declaring states⚓︎

Create a class that inherits from `StatesGroup` and declare states in it as attributes:

```
from trueconf.fsm import State, StatesGroup

class Form(StatesGroup):
name = State() # "Form:name"
age = State() # "Form:age"
city = State() # "Form:city"
```

Each state automatically receives a string identifier in the `GroupName:StateName` format. You do not define it manually — it is generated from the class name and the attribute name.

### Step 4. Handlers⚓︎

```
@router.message(Command("start"))
async def cmd_start(msg: Message, state: FSMContext):
await state.set_state(Form.name)
await msg.answer("What is your name?")

@router.message(Form.name)
async def process_name(msg: Message, state: FSMContext):
await state.update_data(name=msg.text)
await state.set_state(Form.age)
await msg.answer("How old are you?")

@router.message(Form.age)
async def process_age(msg: Message, state: FSMContext):
await state.update_data(age=msg.text)
data = await state.get_data()
await state.clear()
await msg.answer(f"Nice to meet you, {data['name']}!\nYou are {data['age']} years old.")

@router.message(Command("cancel"))
async def cmd_cancel(msg: Message, state: FSMContext):
await state.clear()
await msg.answer("Cancelled.")
```

### Step 5. Running the bot⚓︎

```
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

Tip

Note that `state: FSMContext` is passed to the handler automatically as a parameter. You do not need to create it manually — the library injects the required object for you.

## Declaring states⚓︎

Rules

- The class must inherit from `StatesGroup`.

- Each state is a class attribute created with `State()`.

- State names are generated automatically from the group name and the attribute name.

- Do not use the same `State()` object in different groups — each `State` is bound to one group.

```
from trueconf.fsm import State, StatesGroup

class OrderForm(StatesGroup):
product = State() # "OrderForm:product"
quantity = State() # "OrderForm:quantity"
address = State() # "OrderForm:address"
confirm = State() # "OrderForm:confirm"
```

### Multiple groups⚓︎

You can create multiple state groups for different bot scenarios:

- for questionnaires;

- for support requests;

- for placing an order in a warehouse system or 1C.

This prevents states from different dialogs from being mixed together and keeps the code easier to understand and extend.

```
from trueconf.fsm import State, StatesGroup

class FeedbackForm(StatesGroup):
rating = State()
comment = State()

class SupportTicket(StatesGroup):
topic = State()
description = State()
priority = State()
```

### Nested groups⚓︎

Groups can be nested inside one another. This is useful for complex multi-step forms where one scenario contains separate logical blocks. For example, during registration, you can move the address into a separate nested group so that the `city`, `street`, and `zip_code` states are associated specifically with the address and are not mixed with the main form steps.

```
from trueconf.fsm import State, StatesGroup

class Registration(StatesGroup):
name = State() # "Registration:name"
age = State() # "Registration:age"

class Address(StatesGroup): # nested group
city = State() # "Registration.Address:city"
street = State() # "Registration.Address:street"
zip_code = State() # "Registration.Address:zip_code"

confirm = State() # "Registration:confirm"
```

Tip

Nested state identifiers are generated using a dot: `Registration.Address:city`.

## Working with states⚓︎

When working with a form, it is important to check which state the user is currently in. The examples below show how to work with the state machine:

Set stateGet stateClear state

```
await state.set_state(Form.name)
```

All subsequent messages from this user will be handled by handlers bound to `Form.name`.

```
current = await state.get_state()
```

`"Form:name"` or `None` if there is no active state.

```
await state.clear()
```

Clears the current state and all saved data. After calling `clear()`, the user is considered to have “no state” — handlers with `StateFilter` will no longer match them.

Difference between clear and set_state(None)

- `await state.clear()` clears the state and deletes all data

- `await state.set_state(None)` clears the state, but keeps the data

Use `clear()` when the dialog is fully completed and the data is no longer needed.

## Storing and reading data⚓︎

In addition to the state — that is, the step the user is currently on — FSM allows you to store arbitrary data. For example, a name, age, selected menu item, or any other values the user entered during the dialog.

Save dataGet all dataGet one valueUpdate all data

```
await state.update_data(name="Ivan", age=25)
```

`update_data()` adds new data to the data that has already been saved. If a key already exists, its value will be updated.

You can also pass data as a dictionary:

```
await state.update_data({"name": "Ivan", "age": 25})
```

Or combine both approaches:

```
await state.update_data({"name": "Ivan"}, age=25)
```

Note

`update_data()` merges new data with the existing data. To replace all data completely, use `set_data()`.

```
data = await state.get_data()
```

The method returns a dictionary with all saved data:

```
{"name": "Ivan","age": 25}
```

```
name = await state.get_value("name")
# "Ivan"
```

You can specify a default value that will be returned if the key does not exist:

```
name = await state.get_value("name", "Not specified")
```

We also recommend retrieving a value this way when you only need one field and do not want to load the entire dictionary.

```
await state.set_data({"name": "Peter"})
```

Completely replaces all saved data with a new dictionary. Previous data will be deleted.

## Filtering by state⚓︎

To make a handler run only at a specific step of the dialog, use `StateFilter`. It compares the user's current state with the specified state and lets the event pass only if they match.

```
from trueconf.fsm import StateFilter

@router.message(StateFilter(Form.name))
async def process_name(msg: Message, state: FSMContext):
...
```

For convenience, we made it possible to pass a `State` object directly to the decorator. The library automatically treats it as a `StateFilter`, so the following options are equivalent:

```
@router.message(StateFilter(Form.name))
async def process_name(msg: Message, state: FSMContext): ...

@router.message(Form.name)
async def process_name(msg: Message, state: FSMContext): ...
```

If the same handler should work in several states at once, pass them separated by commas. The handler will be called if the current state matches at least one of them:

```
@router.message(Form.name, Form.age)
async def process_name_or_age(msg: Message, state: FSMContext):
...
```

For users without an active dialog, use `StateFilter(None)`. This handler will run only if the state has not been set yet or has already been cleared:

```
from trueconf.fsm import StateFilter

@router.message(StateFilter(None))
async def no_active_state(msg: Message, state: FSMContext):
await msg.answer("You do not have an active dialog. Enter /start.")
```

If you need to handle a message regardless of the current state, use `any_state`:

```
from trueconf.fsm import any_state

@router.message(any_state)
async def catch_all(msg: Message, state: FSMContext):
await msg.answer("I do not understand. Enter /cancel to cancel.")
```

### Commands inside states⚓︎

You can combine `StateFilter` with `Command` — the handler will run only if the user is in the required state AND has sent the specified command:

```
# /skip works ONLY in the Form.name state
@router.message(Form.name, Command("skip"))
async def skip_name(msg: Message, state: FSMContext):
await state.update_data(name="Anonymous")
await state.set_state(Form.age)
await msg.answer("Name skipped. How old are you?")
```

You can also use multiple commands in the same state:

```
@router.message(Form.confirm, Command("yes"))
async def confirm_yes(msg: Message, state: FSMContext):
data = await state.get_data()
await state.clear()
await msg.answer(f"Done, {data['name']}!")

@router.message(Form.confirm, Command("no"))
async def confirm_no(msg: Message, state: FSMContext):
await state.clear()
await msg.answer("Cancelled.")
```

Handler order matters!

Router checks handlers in registration order and stops at the first match.

If you have a handler with `Command("cancel")` and a handler with `Form.name`, register commands first, otherwise `/cancel` will be handled by the state handler and will not work as cancellation:

```
# Correct:
@router.message(Command("cancel"))
async def cmd_cancel(msg: Message, state: FSMContext):
await state.clear()
await msg.answer("Cancelled.")

@router.message(Form.name)
async def process_name(msg: Message, state: FSMContext):
...
```

## Input validation⚓︎

If the user enters invalid data, do not call `set_state()`. The user will remain in the current state and will be able to try again:

```
@router.message(Form.age)
async def process_age(msg: Message, state: FSMContext):
if not msg.text.isdigit():
await msg.answer("Please enter a number. How old are you?")
return # ← stay in Form.age

await state.update_data(age=int(msg.text))
await state.set_state(Form.city)
await msg.answer("Which city do you live in?")
```

## FSM strategies⚓︎

By default, the state is stored separately for each user in each chat. This works for most bots. However, in some cases, you may need different behavior.

### FSMStrategy⚓︎

```
from trueconf.fsm import FSMStrategy

dp = Dispatcher(storage=MemoryStorage(), strategy=FSMStrategy.CHAT)
```

| Strategy | Behavior | When to use |
| --- | --- | --- |
| `USER_IN_CHAT` | Each user in each chat has a separate state | Default. Private messages, questionnaires |
| `CHAT` | The entire chat has one state shared by all users | Polls, collaborative games |
| `GLOBAL_USER` | A user has one state across all chats | Global user settings |

## Creating custom storage⚓︎

`MemoryStorage` is suitable for development, but data is lost after a restart. For production, you can implement your own storage.

Tip

If you need to store data in a storage backend so it survives bot restarts, implement the abstract `BaseStorage` class:

```
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

Connect it just as easily:

```
dp = Dispatcher(storage=MyCustomStorage())
```

All user code (`state.set_state()`, `state.get_data()`, and so on) works without changes — only the storage implementation changes.
