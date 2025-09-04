# Features

## Asyncio-based Asynchronous Architecture

The entire system is built using async/await, ensuring high performance and non-blocking operations.

## Familiar aiogram-like Design

Leverages familiar concepts: Router, decorators, shortcuts like message.answer, message.reply, filters, and even magic-filter (F.text, F.document, F.photo).

## Convenient Handling of Incoming Events

All incoming JSON payloads are automatically transformed into Python classes (Message, AttachmentContent, UploadingProgress, etc.), making data handling simple and type-safe.

## Decorators for Routing

The router enables elegant and structured handling of events:

```python
from trueconf import Router, Message
from trueconf.enums import MessageType
from trueconf.filters import F

router = Router()

@router.message(F.text.startswith("/start"))
async def on_start(msg: Message):
  await msg.answer("Hello! I'm TrueConf bot 👋")

@router.message(F.document.mime_type == "application/pdf")
async def on_pdf(msg: Message):
  await msg.reply("Thanks for the PDF!")
```

## Two Connection Options

1. Using a pre-obtained JWT token:

   ```python
   bot = Bot(server="video.example.com", token="...")
   ```

2. Or via login and password authentication:

   ```python
   bot = Bot.from_credentials(server, username, password)
   ```

## Aliases and Shortcuts in aiogram Style

Common methods are available for messages:

```python
await msg.answer("Text to chat")
await msg.reply("Reply to a message")
await msg.copy_to(chat_id="other_chat")
```

## Multi-Bot Support

You can run multiple bots simultaneously and route events separately for each one.

## Asynchronous Transport — WebSocket

All communication with the server is handled via WebSocket, which is faster and more efficient than traditional REST requests.

## Magic-filter, Just Like in aiogram

Exactly the same as in aiogram:

```python
@router.message(F.photo)
async def on_photo(msg: Message): ...

@router.message(F.document.mime_type.in_(["application/pdf", "application/msword"]))
async def on_doc(msg: Message): ...
```

## Files and Uploads

Asynchronous file upload and download are supported. Files can be downloaded to a temporary directory or a specified path.

```python
path = await bot.download_file_by_id(file_id)
await msg.answer(f"File downloaded to {path}")
```

## Full Set of Public API Methods

The library implements all core TrueConf API methods: sending messages, uploading/downloading files, polls, conferences, participant management, and more.
