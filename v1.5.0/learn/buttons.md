# Interactive Buttons⚓︎

Inline buttons appear below a message and let users interact with a bot without typing: they can choose a command, open a link, send prepared text, or copy data.

We will start with one button, then build a menu and handle button clicks.

Requirements

- TrueConf Server 5.5.6 or later;

- TrueConf for Windows, macOS, and Linux 8.6.0 or later;

- TrueConf for Android 3.3.0 or later;

- TrueConf for iOS 4.2.0 or later.

Caution

Buttons can only be attached to plain text messages, and only chatbots can send messages with buttons.

For a complete description of the button format at the WebSocket API level, see the TrueConf Server API documentation.

## Your First Button⚓︎

Create a button with `InlineKeyboardButton` and a keyboard with `InlineKeyboardMarkup`:

```
from trueconf import InlineKeyboardButton, InlineKeyboardMarkup

keyboard = InlineKeyboardMarkup(
buttons=[
[InlineKeyboardButton(text="Help", command="menu:help")],
]
)
```

Here, `text` is the button label and `command` is the command the bot receives when the button is clicked.

The `buttons` parameter contains a list of rows. This means that even a single button requires two nested lists: the outer list defines the keyboard, and the inner list defines its first row.

Pass the keyboard to the `buttons` parameter when sending a message:

```
await bot.send_message(
chat_id="chat_id",
text="Choose an action:",
buttons=keyboard,
)
```

You can also pass a keyboard to `message.answer(...)` and `message.reply(...)`.

Tip

If several handlers use the same keyboard, create it once at module level and pass it to the methods that need it.

## Button Actions⚓︎

The previous example used a `command` button, which sends a command to the bot. The library supports four actions, and each button must specify exactly one of them:

| Parameter | What happens when the button is clicked |
| --- | --- |
| `command` | The bot receives a `CallbackQuery` event; no message is posted to the chat |
| `url` | Opens a link using the `http`, `https`, `mailto`, or `trueconf` scheme |
| `message` | Sends the prepared message on behalf of the user |
| `copy_data` | Copies the specified data to the clipboard |

You can arrange buttons in multiple rows:

```
from trueconf import ButtonStyle, InlineKeyboardButton, InlineKeyboardMarkup

keyboard = InlineKeyboardMarkup(
buttons=[
[
InlineKeyboardButton(
text="Help",
command="menu:help",
style=ButtonStyle.PRIMARY,
),
InlineKeyboardButton(
text="Open website",
url="https://trueconf.com",
),
],
[
InlineKeyboardButton(
text="Prepare a question",
message="Tell me more",
draft=True,
),
InlineKeyboardButton(
text="Copy code",
copy_data="code-42",
),
],
]
)
```

In this example:

- `Help` sends the `menu:help` command to the bot;

- `Open website` opens a link;

- `Prepare a question` places text in the input field because `draft=True`;

- `Copy code` copies the `code-42` string.

If `draft=True` is omitted from a `message` button, the prepared text is sent to the chat immediately on behalf of the user.

Tip

The `text` parameter is required for every action except `url`. If a URL button has no label, the client displays the URL itself.

Caution

Only a `command` button sends an event to the bot. The client application handles `url`, `message`, and `copy_data` buttons, so clicking them does not create a `CallbackQuery`.

## Additional Parameters⚓︎

When the basic action is not enough, use additional parameters to customize the button's behavior and appearance:

| Parameter | Available for | Purpose |
| --- | --- | --- |
| `style` | All buttons | Sets `ButtonStyle.DEFAULT`, `ButtonStyle.PRIMARY`, `ButtonStyle.DANGER`, or `ButtonStyle.SUCCESS` |
| `button_id` | All buttons | Sets the button identifier; for a `command` button, it is included in the click event |
| `draft` | `message` only | Places text in the input field instead of sending it immediately |
| `custom_data` | `command` only | Sends additional data to the bot together with the command |
| `to` | `command` only | Directs the command to another bot |

For example, `custom_data` can carry the identifier of a selected object separately from the command:

```
button = InlineKeyboardButton(
text="Add to cart",
command="cart:add",
custom_data="product-42",
button_id="add-product",
)
```

Warning

The `wait_reply=True` parameter and the `CallbackQuery.answer()` method cannot be used yet because TrueConf client applications do not currently support this scenario. The library therefore raises `NotImplementedError` when they are used.

## Handling a Command⚓︎

After the user clicks a `command` button, the bot receives a `CallbackQuery` object. Register a `@router.callback_query()` handler and add a filter for the command value:

```
from trueconf import CallbackQuery, F, Router

router = Router()

@router.callback_query(F.command == "menu:help")
async def show_help(callback: CallbackQuery):
await callback.edit_message(text="Help", buttons=help_keyboard)
```

The `F.command == "menu:help"` filter ensures that the handler responds only to the intended button. For a group of related commands, use a common prefix and an `F.command.startswith(...)` filter:

```
@router.callback_query(F.command.startswith("menu:"))
async def handle_menu(callback: CallbackQuery):
...
```

The click data is available through the properties of the `CallbackQuery` object:

- `callback.command` — the command of the clicked button;

- `callback.custom_data` — the data from `custom_data`;

- `callback.message` — the message containing the button;

- `callback.chat` — the chat in which the button was clicked;

- `callback.command_source.button_id` — the `button_id` value, if specified.

## Updating a Menu After a Click⚓︎

Buttons are often used for navigation: the user opens a section, and the bot changes the message text and displays a new set of actions. From a callback handler, use `callback.edit_message(...)`:

```
@router.callback_query(F.command == "menu:catalog")
async def show_catalog(callback: CallbackQuery):
await callback.edit_message(
text="Choose a category:",
buttons=catalog_keyboard,
)
```

You can update the text and keyboard independently:

```
# Update only the text and keep the current buttons
await callback.edit_message(text="New text")

# Update only the buttons and keep the current text
await callback.edit_message(buttons=new_keyboard)

# Update the text and buttons together
await callback.edit_message(
text="New text",
buttons=new_keyboard,
)

# Remove the buttons and keep the current text
await callback.edit_message(buttons=None)
```

If the `buttons` parameter is omitted, the current buttons are preserved. To remove them, explicitly pass `buttons=None`.

To edit a message outside a `CallbackQuery` handler, use `bot.edit_message(...)`. In this case, you must provide the message text:

```
await bot.edit_message(
message_id="message_id",
text="Updated text",
buttons=new_keyboard,
)
```

## Getting a Message Keyboard⚓︎

The keyboard of a received text message is available through `TextContent.buttons`:

```
message = await bot.get_message_by_id(message_id)

if message.content.buttons is not None:
keyboard = message.content.buttons
```

## Restrictions⚓︎

Observe the following restrictions when creating a keyboard:

- no more than 8 rows and 8 buttons per row;

- no more than 64 buttons in a keyboard;

- `text` must contain 1 to 32 characters when a label is provided;

- `command` must contain 1 to 255 ASCII characters;

- `custom_data` must contain 1 to 4096 ASCII characters;

- `copy_data` must contain 1 to 4095 Unicode characters;

- `url` must contain 8 to 8095 ASCII characters;

- HTML and Markdown in button labels are not processed, and line breaks are replaced with spaces.

## Complete Example⚓︎

Ready-to-use bots

More ready-to-use button scenarios are available in the examples on GitHub.

This bot sends a menu in response to the `/menu` command and then handles the `Say hello` button:

```
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
InlineKeyboardButton(text="Say hello", command="menu:hello"),
InlineKeyboardButton(text="Open website", url="https://trueconf.com"),
],
[InlineKeyboardButton(text="Copy", copy_data="trueconf")],
]
)

@router.message(Command("menu"))
async def show_menu(message: Message):
await message.answer("Choose an action:", buttons=MAIN_MENU)

@router.callback_query(F.command == "menu:hello")
async def say_hello(callback: CallbackQuery):
await callback.edit_message(text="Hello!", buttons=MAIN_MENU)

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

October 1, 2026

October 1, 2026
