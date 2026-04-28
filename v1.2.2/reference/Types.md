# Types⚓︎

You can import all types at once:

```
from trueconf.types import *
```

## `` trueconf.types.AddedChatParticipant `dataclass` ⚓︎

```
AddedChatParticipant(timestamp, chat_id, user_id, added_by)
```

Event type: a new participant was added to a chat.

This object is received in the handler when a user is added to a personal chat, group chat, channel, or conference chat.

### Notes

This class is used as the event type in handler functions decorated with `@.added_chat_participant()`.

### Source

trueconf.com/docs/chatbot-connector/en/chats/#addedChatParticipant

Attributes:

| Name | Type | Description |
| --- | --- | --- |
| `` timestamp

`instance-attribute`
(`trueconf.types.AddedChatParticipant.timestamp`)' href=#trueconf.types.AddedChatParticipant.timestamp>timestamp | `int` | Unix timestamp (milliseconds) of when the event occurred. |
| `` chat_id

`class-attribute`
`instance-attribute`
(`trueconf.types.AddedChatParticipant.chat_id`)' href=#trueconf.types.AddedChatParticipant.chat_id>chat_id | `str` | Unique identifier of the chat where the participant was added. |
| `` user_id

`class-attribute`
`instance-attribute`
(`trueconf.types.AddedChatParticipant.user_id`)' href=#trueconf.types.AddedChatParticipant.user_id>user_id | `str` | TrueConf ID of the participant who was added. |
| `` added_by

`class-attribute`
`instance-attribute`
(`trueconf.types.AddedChatParticipant.added_by`)' href=#trueconf.types.AddedChatParticipant.added_by>added_by | `EnvelopeAuthor` | Information about the user who added the participant. |

Examples:

```
from trueconf.types import AddedChatParticipant

@.added_chat_participant()
async def on_added(event: AddedChatParticipant):
print(event.user_id)
```

### `` added_by `class-attribute` `instance-attribute` ⚓︎

```
added_by = field(metadata={'alias': 'addedBy'})
```

### `` chat_id `class-attribute` `instance-attribute` ⚓︎

```
chat_id = field(metadata={'alias': 'chatId'})
```

### `` timestamp `instance-attribute` ⚓︎

```
timestamp
```

### `` user_id `class-attribute` `instance-attribute` ⚓︎

```
user_id = field(metadata={'alias': 'userId'})
```

## `` trueconf.types.ChangedParticipantRole `dataclass` ⚓︎

```
ChangedParticipantRole(timestamp, role, chat_id, user_id)
```

Event type: a participant's role was changed in a chat.

This object is received in the handler when a participant's role is changed in a personal chat, group chat, channel, or conference chat.

### Notes

This class is used as the event type in handler functions decorated with `@.changed_chat_participant_role()`.

### Source

trueconf.com/docs/chatbot-connector/en/chats/#changedParticipantRole

Attributes:

| Name | Type | Description |
| --- | --- | --- |
| `` timestamp

`instance-attribute`
(`trueconf.types.ChangedParticipantRole.timestamp`)' href=#trueconf.types.ChangedParticipantRole.timestamp>timestamp | `int` | Unix timestamp (in milliseconds) when the role change occurred. |
| `` role

`instance-attribute`
(`trueconf.types.ChangedParticipantRole.role`)' href=#trueconf.types.ChangedParticipantRole.role>role | `str` | New role assigned to the participant. |
| `` chat_id

`class-attribute`
`instance-attribute`
(`trueconf.types.ChangedParticipantRole.chat_id`)' href=#trueconf.types.ChangedParticipantRole.chat_id>chat_id | `str` | Identifier of the chat where the role change occurred. |
| `` user_id

`class-attribute`
`instance-attribute`
(`trueconf.types.ChangedParticipantRole.user_id`)' href=#trueconf.types.ChangedParticipantRole.user_id>user_id | `str` | TrueConf ID of the participant whose role was changed. |

### Example

```
from trueconf.types import ChangedParticipantRole

@router.changed_chat_participant_role()
async def on_role_changed(event: ChangedParticipantRole):
print(f"User {event.user_id} now has role {event.role} in chat {event.chat_id}")
```

### `` chat_id `class-attribute` `instance-attribute` ⚓︎

```
chat_id = field(metadata={'alias': 'chatId'})
```

### `` role `instance-attribute` ⚓︎

```
role
```

### `` timestamp `instance-attribute` ⚓︎

```
timestamp
```

### `` user_id `class-attribute` `instance-attribute` ⚓︎

```
user_id = field(metadata={'alias': 'userId'})
```

## `` trueconf.types.CreatedChannel `dataclass` ⚓︎

```
CreatedChannel(chat_id, title, chat_type, last_message, unread_messages)
```

Event type: a new channel chat was created.

This object is received in the handler when a channel is created in TrueConf.

### Notes

This class is used as the event type in handler functions decorated with `@.created_channel()`.

### Source

trueconf.com/docs/chatbot-connector/en/chats/#createdChannel

Attributes:

| Name | Type | Description |
| --- | --- | --- |
| `` chat_id

`class-attribute`
`instance-attribute`
(`trueconf.types.CreatedChannel.chat_id`)' href=#trueconf.types.CreatedChannel.chat_id>chat_id | `str` | Unique identifier of the created channel. |
| `` title

`instance-attribute`
(`trueconf.types.CreatedChannel.title`)' href=#trueconf.types.CreatedChannel.title>title | `str` | Title of the channel. |
| `` chat_type

`class-attribute`
`instance-attribute`
(`trueconf.types.CreatedChannel.chat_type`)' href=#trueconf.types.CreatedChannel.chat_type>chat_type | `` ChatType (`trueconf.enums.chat_type.ChatType`)' href=../Enums/#trueconf.enums.ChatType>ChatType | Type of the chat (should be `channel`). |
| `` last_message

`class-attribute`
`instance-attribute`
(`trueconf.types.CreatedChannel.last_message`)' href=#trueconf.types.CreatedChannel.last_message>last_message | `LastMessage | None` | The last message in the channel, if available. |
| `` unread_messages

`class-attribute`
`instance-attribute`
(`trueconf.types.CreatedChannel.unread_messages`)' href=#trueconf.types.CreatedChannel.unread_messages>unread_messages | `int` | Number of unread messages in the channel. |

Examples:

```
from trueconf.types import CreatedChannel

@.created_channel()
async def on_created(event: CreatedChannel):
print(f"Channel {event.title} created with id {event.chat_id}")
```

### `` chat_id `class-attribute` `instance-attribute` ⚓︎

```
chat_id = field(metadata={'alias': 'chatId'})
```

### `` chat_type `class-attribute` `instance-attribute` ⚓︎

```
chat_type = field(metadata={'alias': 'chatType'})
```

### `` last_message `class-attribute` `instance-attribute` ⚓︎

```
last_message = field(metadata={'alias': 'lastMessage'})
```

### `` title `instance-attribute` ⚓︎

```
title
```

### `` unread_messages `class-attribute` `instance-attribute` ⚓︎

```
unread_messages = field(metadata={'alias': 'unreadMessages'})
```

## `` trueconf.types.CreatedGroupChat `dataclass` ⚓︎

```
CreatedGroupChat(chat_id, title, chat_type, last_message, unread_messages)
```

Event type: a new group chat was created.

This object is received in the handler when a group chat is created in TrueConf.

### Notes

This class is used as the event type in handler functions decorated with `@.created_group_chat()`.

### Source

trueconf.com/docs/chatbot-connector/en/chats/#createdGroupChat

Attributes:

| Name | Type | Description |
| --- | --- | --- |
| `` chat_id

`class-attribute`
`instance-attribute`
(`trueconf.types.CreatedGroupChat.chat_id`)' href=#trueconf.types.CreatedGroupChat.chat_id>chat_id | `str` | Unique identifier of the group chat. |
| `` title

`instance-attribute`
(`trueconf.types.CreatedGroupChat.title`)' href=#trueconf.types.CreatedGroupChat.title>title | `str` | Title of the group chat. |
| `` chat_type

`class-attribute`
`instance-attribute`
(`trueconf.types.CreatedGroupChat.chat_type`)' href=#trueconf.types.CreatedGroupChat.chat_type>chat_type | `` ChatType (`trueconf.enums.chat_type.ChatType`)' href=../Enums/#trueconf.enums.ChatType>ChatType | Type of the chat (should be `group`). |
| `` last_message

`class-attribute`
`instance-attribute`
(`trueconf.types.CreatedGroupChat.last_message`)' href=#trueconf.types.CreatedGroupChat.last_message>last_message | `LastMessage | None` | The last message in the chat, if available. |
| `` unread_messages

`class-attribute`
`instance-attribute`
(`trueconf.types.CreatedGroupChat.unread_messages`)' href=#trueconf.types.CreatedGroupChat.unread_messages>unread_messages | `int` | Number of unread messages in the group chat. |

Examples:

```
from trueconf.types import CreatedGroupChat

@.created_group_chat()
async def on_created(event: CreatedGroupChat):
print(f"Group chat {event.title} created with id {event.chat_id}")
```

### `` chat_id `class-attribute` `instance-attribute` ⚓︎

```
chat_id = field(metadata={'alias': 'chatId'})
```

### `` chat_type `class-attribute` `instance-attribute` ⚓︎

```
chat_type = field(metadata={'alias': 'chatType'})
```

### `` last_message `class-attribute` `instance-attribute` ⚓︎

```
last_message = field(metadata={'alias': 'lastMessage'})
```

### `` title `instance-attribute` ⚓︎

```
title
```

### `` unread_messages `class-attribute` `instance-attribute` ⚓︎

```
unread_messages = field(metadata={'alias': 'unreadMessages'})
```

## `` trueconf.types.CreatedPersonalChat `dataclass` ⚓︎

```
CreatedPersonalChat(chat_id, title, chat_type, last_message, unread_messages)
```

Event type: a new personal chat was created.

This object is received in the handler when a personal chat is created in TrueConf.

### Notes

This class is used as the event type in handler functions decorated with `@.created_personal_chat()`.

### Source

trueconf.com/docs/chatbot-connector/en/chats/#createdP2PChat

Attributes:

| Name | Type | Description |
| --- | --- | --- |
| `` chat_id

`class-attribute`
`instance-attribute`
(`trueconf.types.CreatedPersonalChat.chat_id`)' href=#trueconf.types.CreatedPersonalChat.chat_id>chat_id | `str` | Unique identifier of the personal chat. |
| `` title

`instance-attribute`
(`trueconf.types.CreatedPersonalChat.title`)' href=#trueconf.types.CreatedPersonalChat.title>title | `str` | Title of the chat (usually the participant’s name). |
| `` chat_type

`class-attribute`
`instance-attribute`
(`trueconf.types.CreatedPersonalChat.chat_type`)' href=#trueconf.types.CreatedPersonalChat.chat_type>chat_type | `` ChatType (`trueconf.enums.chat_type.ChatType`)' href=../Enums/#trueconf.enums.ChatType>ChatType | Type of the chat (should be `p2p`). |
| `` last_message

`class-attribute`
`instance-attribute`
(`trueconf.types.CreatedPersonalChat.last_message`)' href=#trueconf.types.CreatedPersonalChat.last_message>last_message | `LastMessage | None` | The last message in the chat, if available. |
| `` unread_messages

`class-attribute`
`instance-attribute`
(`trueconf.types.CreatedPersonalChat.unread_messages`)' href=#trueconf.types.CreatedPersonalChat.unread_messages>unread_messages | `int` | Number of unread messages in the personal chat. |

Examples:

```
from trueconf.types import CreatedPersonalChat

@.created_personal_chat()
async def on_created(event: CreatedPersonalChat):
print(f"Personal chat created with id {event.chat_id}")
```

### `` chat_id `class-attribute` `instance-attribute` ⚓︎

```
chat_id = field(metadata={'alias': 'chatId'})
```

### `` chat_type `class-attribute` `instance-attribute` ⚓︎

```
chat_type = field(metadata={'alias': 'chatType'})
```

### `` last_message `class-attribute` `instance-attribute` ⚓︎

```
last_message = field(metadata={'alias': 'lastMessage'})
```

### `` title `instance-attribute` ⚓︎

```
title
```

### `` unread_messages `class-attribute` `instance-attribute` ⚓︎

```
unread_messages = field(metadata={'alias': 'unreadMessages'})
```

## `` trueconf.types.EditedMessage `dataclass` ⚓︎

```
EditedMessage(timestamp, content, chat_id)
```

Event type: a message was edited.

This object is received in the handler when a previously sent message is edited in a chat.

### Notes

This class is used as the event type in handler functions decorated with `@.edited_message()`.

### Source

trueconf.com/docs/chatbot-connector/en/messages/#editMessage

Attributes:

| Name | Type | Description |
| --- | --- | --- |
| `` timestamp

`instance-attribute`
(`trueconf.types.EditedMessage.timestamp`)' href=#trueconf.types.EditedMessage.timestamp>timestamp | `int` | Unix timestamp (milliseconds) of when the edit occurred. |
| `` content

`instance-attribute`
(`trueconf.types.EditedMessage.content`)' href=#trueconf.types.EditedMessage.content>content | `TextContent` | The updated content of the edited message. |
| `` chat_id

`class-attribute`
`instance-attribute`
(`trueconf.types.EditedMessage.chat_id`)' href=#trueconf.types.EditedMessage.chat_id>chat_id | `str` | Unique identifier of the chat where the message was edited. |

Examples:

```
from trueconf.types import EditedMessage

@.edited_message()
async def on_edited(event: EditedMessage):
print(f"Message in chat {event.chat_id} was edited: {event.content.text}")
```

### `` chat_id `class-attribute` `instance-attribute` ⚓︎

```
chat_id = field(metadata={'alias': 'chatId'})
```

### `` content `instance-attribute` ⚓︎

```
content
```

### `` timestamp `instance-attribute` ⚓︎

```
timestamp
```

## `` trueconf.types.InputFile ⚓︎

```
InputFile(file_name=None, file_size=None, mime_type=None)
```

Base abstract class representing uploadable files.

This class defines a common interface for all file types that can be uploaded to the TrueConf Server. It should not be used directly. Instead, use one of its subclasses:

- `BufferedInputFile` — for in-memory byte data

- `FSInputFile` — for files from the local filesystem

- `URLInputFile` — for downloading files from a URL

Each subclass implements the `read()` and `clone()` methods required for asynchronous uploads and reusability of the same file object.

### Source

trueconf.com/docs/chatbot-connector/en/files/#upload-file-to-server-storage

Parameters:

| Name | Type | Description | Default |
| --- | --- | --- | --- |
| `file_name` | `str` | Name of the file to display when sending. | `None` |
| `file_size` | `int | None` | File size in bytes (optional). | `None` |
| `mime_type` | `str | None` | MIME type of the file. Can be detected automatically. | `None` |

### Abstract Methods

read(): Asynchronously reads the file content. clone(): Creates a new copy of the file object. Useful for reuse (e.g., preview uploads).

### Example

```
file = FSInputFile("example.pdf")
await bot.send_document(chat_id="...", file=file)
```

### `` extension `instance-attribute` ⚓︎

```
extension = lower()[1:]
```

### `` file_name `instance-attribute` ⚓︎

```
file_name = file_name
```

### `` file_size `instance-attribute` ⚓︎

```
file_size = file_size
```

### `` mime_type `instance-attribute` ⚓︎

```
mime_type = mime_type
```

### `` clone `abstractmethod` ⚓︎

```
clone()
```

### `` read `abstractmethod` `async` ⚓︎

```
read()
```

## `` trueconf.types.BufferedInputFile ⚓︎

```
BufferedInputFile(file, file_name=None, file_size=None, mime_type=None, **kwargs)
```

Represents a file uploaded from a bytes buffer.

This class is useful when the file is already available as a `bytes` object, for example, if it was retrieved from a database, memory, or downloaded from an external source. Automatically detects MIME type and file size if not provided.

### Example

```
file = BufferedInputFile(file=data_bytes, file_name="example.txt")
await bot.send_document(chat_id="...", file=file)
```

### Note

Use `BufferedInputFile.from_file(...)` for convenient file loading from disk.

Initializes a file from a bytes buffer.

Parameters:

| Name | Type | Description | Default |
| --- | --- | --- | --- |
| `file` | `bytes` | Raw file content in bytes. | required |
| `file_name` | `str` | The name of the file. | `None` |
| `file_size` | `int` | Size of the file in bytes. Auto-detected if not specified. | `None` |
| `mime_type` | `str` | MIME type of the file. Auto-detected if not specified. | `None` |

### `` data `instance-attribute` ⚓︎

```
data = file
```

### `` extension `instance-attribute` ⚓︎

```
extension = lower()[1:]
```

### `` file_name `instance-attribute` ⚓︎

```
file_name = file_name
```

### `` file_size `instance-attribute` ⚓︎

```
file_size = file_size
```

### `` mime_type `instance-attribute` ⚓︎

```
mime_type = mime_type
```

### `` clone ⚓︎

```
clone()
```

Creates a clone of the current file object.

This method is useful when the same file needs to be reused (e.g., as a preview), while keeping the original instance intact.

Returns:

| Name | Type | Description |
| --- | --- | --- |
| `BufferedInputFile` | `` trueconf.types.BufferedInputFile (`trueconf.types.input_file.BufferedInputFile`)' href=#trueconf.types.BufferedInputFile>BufferedInputFile | A new instance with identical content. |

### `` from_file `classmethod` ⚓︎

```
from_file(path, file_name=None, file_size=None, mime_type=None, **kwargs)
```

Creates a `BufferedInputFile` from a file on disk.

This is a convenient way to load a file into memory if it needs to be reused or processed before sending.

Parameters:

| Name | Type | Description | Default |
| --- | --- | --- | --- |
| `path` | `str | Path` | Path to the local file. | required |
| `file_name` | `str` | File name to propagate. Defaults to the name extracted from path. | `None` |
| `file_size` | `int` | File size in bytes. Auto-detected if not specified. | `None` |
| `mime_type` | `str` | MIME type of the file. Auto-detected if not specified. | `None` |

Returns:

| Name | Type | Description |
| --- | --- | --- |
| `BufferedInputFile` | `` trueconf.types.BufferedInputFile (`trueconf.types.input_file.BufferedInputFile`)' href=#trueconf.types.BufferedInputFile>BufferedInputFile | A new instance ready for upload. |

### `` read `async` ⚓︎

```
read()
```

Asynchronously returns the file content as a `BytesIO` stream.

Returns:

| Name | Type | Description |
| --- | --- | --- |
| `BytesIO` | | A stream containing the file content. |

## `` trueconf.types.FSInputFile ⚓︎

```
FSInputFile(path, file_name=None, file_size=None, mime_type=None, **kwargs)
```

Represents a file uploaded from the local filesystem.

Used for uploading documents, images, or any other files directly from disk. Automatically detects the file name, size, and MIME type when not explicitly provided.

### Example

```
file = FSInputFile("path/to/file.zip")
await bot.send_document(chat_id="...", file=file)
```

Initializes an `FSInputFile` instance from a local file.

If not provided, `file_name`, `file_size`, and `mime_type` are automatically detected:

- `file_name` is extracted from the file path.

- `file_size` is determined via `os.path.getsize()`.

- `mime_type` is detected from the first 2048 bytes of the file content (using `python-magic` if available).

Parameters:

| Name | Type | Description | Default |
| --- | --- | --- | --- |
| `path` | `str | Path` | Path to the local file. | required |
| `file_name` | `str` | File name to be propagated in the upload. | `None` |
| `file_size` | `int` | File size in bytes. | `None` |
| `mime_type` | `str` | File MIME type. | `None` |

### `` extension `instance-attribute` ⚓︎

```
extension = lower()[1:]
```

### `` file_name `instance-attribute` ⚓︎

```
file_name = file_name
```

### `` file_size `instance-attribute` ⚓︎

```
file_size = file_size
```

### `` mime_type `instance-attribute` ⚓︎

```
mime_type = mime_type
```

### `` path `instance-attribute` ⚓︎

```
path = path
```

### `` clone ⚓︎

```
clone()
```

Creates a clone of the current `FSInputFile` instance.

Useful when the same file needs to be reused, for example, when sending preview images. The cloned object retains the same path, name, size, and MIME type but is a separate instance in memory.

Returns:

| Name | Type | Description |
| --- | --- | --- |
| `FSInputFile` | `` trueconf.types.FSInputFile (`trueconf.types.input_file.FSInputFile`)' href=#trueconf.types.FSInputFile>FSInputFile | A new instance of `FSInputFile` with identical properties. |

### `` read `async` ⚓︎

```
read()
```

Asynchronously reads the file content from the local filesystem.

Returns:

| Name | Type | Description |
| --- | --- | --- |
| `bytes` | | The file content as raw bytes. |

## `` trueconf.types.URLInputFile ⚓︎

```
URLInputFile(url, headers=None, file_name=None, file_size=None, mime_type=None, timeout=30, verify_ssl=True, **kwargs)
```

Represents a file to be downloaded and uploaded from a remote URL.

Used for uploading files from external sources (e.g., public file links, APIs). Automatically handles MIME type detection and file size parsing from HTTP headers.

### Example

```
file = URLInputFile("https://example.com/file.pdf")
await bot.send_document(chat_id="...", file=file)
```

Initializes a `URLInputFile` instance from a remote URL.

Parameters:

| Name | Type | Description | Default |
| --- | --- | --- | --- |
| `url` | `str` | URL of the file to download. | required |
| `headers` | `Optional[Dict[str, Any]]` | Optional HTTP headers for the request. | `None` |
| `file_name` | `str` | Optional file name to propagate in the upload. | `None` |
| `file_size` | `int` | Optional file size in bytes. | `None` |
| `mime_type` | `str` | Optional MIME type of the file. | `None` |
| `timeout` | `int` | Timeout (in seconds) for the HTTP request. | `30` |

### `` extension `instance-attribute` ⚓︎

```
extension = lower()[1:]
```

### `` file_name `instance-attribute` ⚓︎

```
file_name = file_name
```

### `` file_size `instance-attribute` ⚓︎

```
file_size = file_size
```

### `` headers `instance-attribute` ⚓︎

```
headers = headers
```

### `` mime_type `instance-attribute` ⚓︎

```
mime_type = mime_type
```

### `` timeout `instance-attribute` ⚓︎

```
timeout = timeout
```

### `` url `instance-attribute` ⚓︎

```
url = url
```

### `` verify_ssl `instance-attribute` ⚓︎

```
verify_ssl = verify_ssl
```

### `` clone ⚓︎

```
clone()
```

Creates a clone of the current `URLInputFile` instance.

Useful when the same file needs to be reused (e.g., sending a preview). The cloned object retains the same URL, headers, and metadata.

Returns:

| Name | Type | Description |
| --- | --- | --- |
| `URLInputFile` | `` trueconf.types.URLInputFile (`trueconf.types.input_file.URLInputFile`)' href=#trueconf.types.URLInputFile>URLInputFile | A new instance with identical parameters. |

### `` prepare `async` ⚓︎

```
prepare()
```

Prepares file metadata by sending a HEAD request to the specified URL.

This method attempts to detect:

- MIME type from the `Content-Type` header.

- File size from the `Content-Length` header.

- File name from the `Content-Disposition` header or URL path.

Raises:

| Type | Description |
| --- | --- |
| `ValueError` | If the server does not provide a valid `Content-Length`. |

### `` read `async` ⚓︎

```
read()
```

Downloads the file content from the remote URL.

Performs a full GET request and returns the content as raw bytes.

Returns:

| Name | Type | Description |
| --- | --- | --- |
| `bytes` | | File content. |

## `` trueconf.types.Message `dataclass` ⚓︎

```
Message(timestamp, type, author, box, content, message_id, chat_id, is_edited, reply_message_id=None)
```

Represents a single chat message within TrueConf Chatbot Connector.

The `Message` object is automatically created for each incoming update and contains metadata (author, chat, timestamp, type) along with the actual message content. It also provides helper properties and shortcut methods to interact with the message (e.g., replying, forwarding, deleting, sending media files).

### Source

trueconf.com/docs/chatbot-connector/en/messages/#sendMessage

Attributes:

| Name | Type | Description |
| --- | --- | --- |
| `` timestamp

`instance-attribute`
(`trueconf.types.Message.timestamp`)' href=#trueconf.types.Message.timestamp>timestamp | `int` | Unix timestamp of the message. |
| `` type

`instance-attribute`
(`trueconf.types.Message.type`)' href=#trueconf.types.Message.type>type | `` MessageType (`trueconf.enums.message_type.MessageType`)' href=../Enums/#trueconf.enums.MessageType>MessageType | Type of the message (e.g., TEXT, ATTACHMENT). |
| `` author

`instance-attribute`
(`trueconf.types.Message.author`)' href=#trueconf.types.Message.author>author | `EnvelopeAuthor` | Information about the user who sent the message. |
| `` box

`instance-attribute`
(`trueconf.types.Message.box`)' href=#trueconf.types.Message.box>box | `EnvelopeBox` | Information about the chat (box) where the message was sent. |
| `` message_id

`class-attribute`
`instance-attribute`
(`trueconf.types.Message.message_id`)' href=#trueconf.types.Message.message_id>message_id | `str` | Unique identifier of the message. |
| `` chat_id

`class-attribute`
`instance-attribute`
(`trueconf.types.Message.chat_id`)' href=#trueconf.types.Message.chat_id>chat_id | `str` | Unique identifier of the chat where the message was sent. |
| `` is_edited

`class-attribute`
`instance-attribute`
(`trueconf.types.Message.is_edited`)' href=#trueconf.types.Message.is_edited>is_edited | `bool` | Indicates whether the message was edited. |
| `` reply_message_id

`class-attribute`
`instance-attribute`
(`trueconf.types.Message.reply_message_id`)' href=#trueconf.types.Message.reply_message_id>reply_message_id | `Optional[str]` | Identifier of the message this one replies to. |
| `` from_user

`property`
(`trueconf.types.Message.from_user`)' href=#trueconf.types.Message.from_user>from_user | `EnvelopeAuthor` | Shortcut for accessing the message author. |
| `` content_type

`property`
(`trueconf.types.Message.content_type`)' href=#trueconf.types.Message.content_type>content_type | `` MessageType (`trueconf.enums.message_type.MessageType`)' href=../Enums/#trueconf.enums.MessageType>MessageType | Returns the type of the message. |
| `` text

`property`
(`trueconf.types.Message.text`)' href=#trueconf.types.Message.text>text | `Optional[str]` | Returns the message text if it contains text, else None. |
| `` document

`property`
(`trueconf.types.Message.document`)' href=#trueconf.types.Message.document>document | `Optional[Document]` | Returns a document attachment if the message contains a non-media file (not photo, video, sticker). |
| `` photo

`property`
(`trueconf.types.Message.photo`)' href=#trueconf.types.Message.photo>photo | `Optional[Photo]` | Returns a photo attachment if available. |
| `` video

`property`
(`trueconf.types.Message.video`)' href=#trueconf.types.Message.video>video | `Optional[Video]` | Returns a video attachment if available. |
| `` sticker

`property`
(`trueconf.types.Message.sticker`)' href=#trueconf.types.Message.sticker>sticker | `Optional[Sticker]` | Returns a sticker attachment if available. |

Methods:

| Name | Description |
| --- | --- |
| `` answer

`async`
(`trueconf.types.Message.answer`)' href=#trueconf.types.Message.answer>answer | Sends a text message in the same chat. |
| `` reply

`async`
(`trueconf.types.Message.reply`)' href=#trueconf.types.Message.reply>reply | Sends a reply message referencing the current one. |
| `` forward

`async`
(`trueconf.types.Message.forward`)' href=#trueconf.types.Message.forward>forward | Forwards the current message to another chat. |
| `` copy_to

`async`
(`trueconf.types.Message.copy_to`)' href=#trueconf.types.Message.copy_to>copy_to | Sends a copy of the current message (text-only). |
| `` answer_photo

`async`
(`trueconf.types.Message.answer_photo`)' href=#trueconf.types.Message.answer_photo>answer_photo | Sends a photo to the current chat. |
| `` answer_document

`async`
(`trueconf.types.Message.answer_document`)' href=#trueconf.types.Message.answer_document>answer_document | Sends a document to the current chat. |
| `` answer_sticker

`async`
(`trueconf.types.Message.answer_sticker`)' href=#trueconf.types.Message.answer_sticker>answer_sticker | Sends a sticker to the current chat. |
| `` delete

`async`
(`trueconf.types.Message.delete`)' href=#trueconf.types.Message.delete>delete | Deletes the current message from the chat. |

### `` author `instance-attribute` ⚓︎

```
author
```

### `` box `instance-attribute` ⚓︎

```
box
```

### `` chat_id `class-attribute` `instance-attribute` ⚓︎

```
chat_id = field(metadata={'alias': 'chatId'})
```

### `` content `instance-attribute` ⚓︎

```
content
```

### `` content_type `property` ⚓︎

```
content_type
```

Returns the type of the current message content.

Returns:

| Name | Type | Description |
| --- | --- | --- |
| `MessageType` | `` MessageType (`trueconf.enums.message_type.MessageType`)' href=../Enums/#trueconf.enums.MessageType>MessageType | Message content type (e.g., TEXT, ATTACHMENT). |

### `` document `property` ⚓︎

```
document
```

Returns the attached document if the message contains a non-media file.

Use this property only for documents that are not photos, videos, or stickers. For media attachments, use the corresponding properties: `photo`, `video`, or `sticker`. If you need to handle any attached file (including media), use `message.content` directly.

Returns:

| Type | Description |
| --- | --- |
| `Optional['Document']` | Optional[Document]: Document attachment bound to the bot, or None if not applicable. |

### `` from_user `property` ⚓︎

```
from_user
```

Returns the author of the current message.

Returns:

| Name | Type | Description |
| --- | --- | --- |
| `EnvelopeAuthor` | `EnvelopeAuthor` | Shortcut for accessing the message author. |

### `` is_edited `class-attribute` `instance-attribute` ⚓︎

```
is_edited = field(metadata={'alias': 'isEdited'})
```

### `` message_id `class-attribute` `instance-attribute` ⚓︎

```
message_id = field(metadata={'alias': 'messageId'})
```

### `` photo `property` ⚓︎

```
photo
```

Returns the attached photo object if the current message contains an image.

This is a shortcut for accessing photo metadata from image attachments.

Returns:

| Type | Description |
| --- | --- |
| `Optional['Photo']` | Optional[Photo]: A `Photo` object bound to the bot, or None if the message does not contain an image. |

### `` reply_message_id `class-attribute` `instance-attribute` ⚓︎

```
reply_message_id = field(default=None, metadata={'alias': 'replyMessageId'})
```

### `` sticker `property` ⚓︎

```
sticker
```

Returns the attached sticker object if the current message contains a sticker.

Returns:

| Type | Description |
| --- | --- |
| `Optional['Sticker']` | Optional[Sticker]: A `Sticker` object bound to the bot, or None if the message does not contain a sticker. |

### `` text `property` ⚓︎

```
text
```

Returns the text of the current message if present.

Returns:

| Type | Description |
| --- | --- |
| `str | None` | Optional[str]: Message text, or None if the message has no text content. |

### `` timestamp `instance-attribute` ⚓︎

```
timestamp
```

### `` type `instance-attribute` ⚓︎

```
type
```

### `` video `property` ⚓︎

```
video
```

Returns the attached video object if the current message contains a video.

This is a shortcut for accessing video metadata from video attachments.

Returns:

| Type | Description |
| --- | --- |
| `Optional['Video']` | Optional[Video]: A `Video` object bound to the bot, or None if the message does not contain a video. |

### `` answer `async` ⚓︎

```
answer(text, parse_mode= HTML

class-attribute
instance-attribute
(trueconf.enums.parse_mode.ParseMode.HTML)' href=../Enums/#trueconf.enums.ParseMode.HTML>HTML)
```

Shortcut for the `async` ' href=../Bot/#trueconf.Bot.send_message>`send_message` method of the bot instance. Use this method to send a text message to the current chat.

### Automatically fills the following attributes

- `chat_id`

### Source

trueconf.com/docs/chatbot-connector/en/messages/#sendMessage

Parameters:

| Name | Type | Description | Default |
| --- | --- | --- | --- |
| `text` | `str` | Text of the message to be sent. | required |
| `parse_mode` | `` ParseMode (`trueconf.enums.parse_mode.ParseMode`)' href=../Enums/#trueconf.enums.ParseMode>ParseMode | str | Text formatting mode. Defaults to HTML. | `` HTML

`class-attribute`
`instance-attribute`
(`trueconf.enums.parse_mode.ParseMode.HTML`)' href=../Enums/#trueconf.enums.ParseMode.HTML>HTML |

Returns:

| Name | Type | Description |
| --- | --- | --- |
| `SendMessageResponse` | `object` | Object containing the result of the message delivery. |

Examples:

```
>>> @.message()
>>> async def on_message(message:Message):
>>> await message.answer("Hi, there!")
```

```
>>> @.message()
>>> async def on_message(message:Message):
>>> await message.answer("Hi, **there!**", parse_mode=ParseMode.MARKDOWN)
```

### `` answer_document `async` ⚓︎

```
answer_document(file, caption=None, parse_mode= TEXT

class-attribute
instance-attribute
(trueconf.enums.parse_mode.ParseMode.TEXT)' href=../Enums/#trueconf.enums.ParseMode.TEXT>TEXT)
```

Shortcut for the `async` ' href=../Bot/#trueconf.Bot.send_document>`send_document` method of the bot instance. Use this method to send a document in response to the current message.

### Automatically fills the following attributes

- `chat_id`

### Source

trueconf.com/docs/chatbot-connector/en/files/#working-with-files

Parameters:

| Name | Type | Description | Default |
| --- | --- | --- | --- |
| `file` | `` trueconf.types.InputFile (`trueconf.types.input_file.InputFile`)' href=#trueconf.types.InputFile>InputFile | The file to be uploaded. Must be a subclass of `InputFile`. | required |
| `caption` | `str | None` | Optional caption text to be sent with the file. | `None` |
| `parse_mode` | `` ParseMode (`trueconf.enums.parse_mode.ParseMode`)' href=../Enums/#trueconf.enums.ParseMode>ParseMode | str | Text formatting mode (e.g., Markdown, HTML, or plain text). | `` TEXT

`class-attribute`
`instance-attribute`
(`trueconf.enums.parse_mode.ParseMode.TEXT`)' href=../Enums/#trueconf.enums.ParseMode.TEXT>TEXT |

Returns:

| Name | Type | Description |
| --- | --- | --- |
| `SendFileResponse` | `object` | Object containing the result of the document upload. |

Examples:

```
>>> @.message()
>>> async def on_message(message:Message):
>>> await message.answer_document(file=FSInputFile("sticker.webp"))
```

### `` answer_photo `async` ⚓︎

```
answer_photo(file, preview, caption=None, parse_mode= TEXT

class-attribute
instance-attribute
(trueconf.enums.parse_mode.ParseMode.TEXT)' href=../Enums/#trueconf.enums.ParseMode.TEXT>TEXT)
```

Shortcut for the `async` ' href=../Bot/#trueconf.Bot.send_photo>`send_photo` method of the bot instance. Use this method to send a photo in response to the current message.

### Automatically fills the following attributes

- `chat_id`

### Source

trueconf.com/docs/chatbot-connector/en/files/#sending-an-image

Parameters:

| Name | Type | Description | Default |
| --- | --- | --- | --- |
| `file` | `` trueconf.types.InputFile (`trueconf.types.input_file.InputFile`)' href=#trueconf.types.InputFile>InputFile | The photo file to upload. Must be a subclass of `InputFile`. | required |
| `preview` | `` trueconf.types.InputFile (`trueconf.types.input_file.InputFile`)' href=#trueconf.types.InputFile>InputFile | None | Optional preview image. Must also be an `InputFile` if provided. | required |
| `caption` | `str | None` | Optional caption to be sent along with the image. | `None` |
| `parse_mode` | `` ParseMode (`trueconf.enums.parse_mode.ParseMode`)' href=../Enums/#trueconf.enums.ParseMode>ParseMode | str | Formatting mode for the caption (e.g., Markdown, HTML, plain text). | `` TEXT

`class-attribute`
`instance-attribute`
(`trueconf.enums.parse_mode.ParseMode.TEXT`)' href=../Enums/#trueconf.enums.ParseMode.TEXT>TEXT |

Returns:

| Name | Type | Description |
| --- | --- | --- |
| `SendFileResponse` | `object` | Object containing the result of the photo upload. |

Examples:

```
>>> @.message()
>>> async def on_message(message:Message):
>>> await message.answer_photo(file=FSInputFile("sticker.webp"), preview=FSInputFile("sticker.webp"))
```

### `` answer_sticker `async` ⚓︎

```
answer_sticker(file)
```

Shortcut for the `async` ' href=../Bot/#trueconf.Bot.send_sticker>`send_sticker` method of the bot instance. Use this method to send a sticker in response to the current message.

### Automatically fills the following attributes

- `chat_id`

### Source

trueconf.com/docs/chatbot-connector/en/files/#upload-file-to-server-storage

Parameters:

| Name | Type | Description | Default |
| --- | --- | --- | --- |
| `file` | `` trueconf.types.InputFile (`trueconf.types.input_file.InputFile`)' href=#trueconf.types.InputFile>InputFile | The sticker file in WebP format. Must be a subclass of `InputFile`. | required |

Returns:

| Name | Type | Description |
| --- | --- | --- |
| `SendFileResponse` | `object` | Object containing the result of the sticker delivery. |

Examples:

```
>>> @.message()
>>> async def on_message(message:Message):
>>> await message.answer_sticker(file=FSInputFile("sticker.webp"))
```

### `` copy_to `async` ⚓︎

```
copy_to(chat_id)
```

Shortcut for the `async` ' href=../Bot/#trueconf.Bot.send_message>`send_message` method of the bot instance. Use this method to send a copy of the current message (without metadata or reply context) to another chat.

### Automatically fills the following attributes

- `text`

- `parse_mode`

### Source

trueconf.com/docs/chatbot-connector/en/messages/#sendMessage

Parameters:

| Name | Type | Description | Default |
| --- | --- | --- | --- |
| `chat_id` | `str` | Identifier of the target chat to send the copied message to. | required |

Returns:

| Name | Type | Description |
| --- | --- | --- |
| `SendMessageResponse` | `object` | Object containing the result of the message delivery. |

### `` delete `async` ⚓︎

```
delete(for_all=False)
```

Shortcut for the `async` ' href=../Bot/#trueconf.Bot.remove_message>`remove_message` method of the bot instance. Use this method to delete the current message from the chat.

### Automatically fills the following attributes

- `message_id`

### Source

trueconf.com/docs/chatbot-connector/en/messages/#removeMessage

Parameters:

| Name | Type | Description | Default |
| --- | --- | --- | --- |
| `for_all` | `bool` | If True, delete the message for all participants. Defaults to False (deletes only for the bot). | `False` |

Returns:

| Name | Type | Description |
| --- | --- | --- |
| `RemoveMessageResponse` | `object` | Object containing the result of the message deletion. |

### `` forward `async` ⚓︎

```
forward(chat_id)
```

Shortcut for the `async` ' href=../Bot/#trueconf.Bot.forward_message>`forward_message` method of the bot instance. Use this method to forward the current message to another chat.

### Automatically fills the following attributes

- `message_id`

### Source

trueconf.com/docs/chatbot-connector/en/messages/#forwardMessage

Parameters:

| Name | Type | Description | Default |
| --- | --- | --- | --- |
| `chat_id` | `str` | Identifier of the target chat to forward the message to. | required |

Returns:

| Name | Type | Description |
| --- | --- | --- |
| `ForwardMessageResponse` | `object` | Object containing the result of the message forwarding. |

### `` reply `async` ⚓︎

```
reply(text, parse_mode= HTML

class-attribute
instance-attribute
(trueconf.enums.parse_mode.ParseMode.HTML)' href=../Enums/#trueconf.enums.ParseMode.HTML>HTML)
```

Shortcut for the `async` ' href=../Bot/#trueconf.Bot.send_message>`send_message` method. Sends a reply to this message in the current chat.

### Automatically fills the following attributes

- `chat_id`: Current chat identifier.

- `reply_message_id`: ID of the current message.

Source: trueconf.com/docs/chatbot-connector/en/messages/#replyMessage

Parameters:

| Name | Type | Description | Default |
| --- | --- | --- | --- |
| `text` | `str` | Text of the reply message. | required |
| `parse_mode` | `` ParseMode (`trueconf.enums.parse_mode.ParseMode`)' href=../Enums/#trueconf.enums.ParseMode>ParseMode | str | Text formatting mode. Defaults to HTML. | `` HTML

`class-attribute`
`instance-attribute`
(`trueconf.enums.parse_mode.ParseMode.HTML`)' href=../Enums/#trueconf.enums.ParseMode.HTML>HTML |

Returns:

| Name | Type | Description |
| --- | --- | --- |
| `SendMessageResponse` | `object` | Object containing the result of the message delivery. |

### `` reply_document `async` ⚓︎

```
reply_document(file, caption=None, parse_mode= TEXT

class-attribute
instance-attribute
(trueconf.enums.parse_mode.ParseMode.TEXT)' href=../Enums/#trueconf.enums.ParseMode.TEXT>TEXT)
```

Shortcut for the `async` ' href=../Bot/#trueconf.Bot.send_document>`send_document` method of the bot instance. Sends a document as a reply to the current message in this chat.

### Automatically fills the following attributes

- `chat_id`: Current chat identifier.

- `reply_message_id`: ID of the current message.

### Source

trueconf.com/docs/chatbot-connector/en/files/#working-with-files

Parameters:

| Name | Type | Description | Default |
| --- | --- | --- | --- |
| `file` | `` trueconf.types.InputFile (`trueconf.types.input_file.InputFile`)' href=#trueconf.types.InputFile>InputFile | The file to be uploaded. Must be a subclass of `InputFile`. | required |
| `caption` | `str | None` | Optional caption text to be sent with the file. | `None` |
| `parse_mode` | `` ParseMode (`trueconf.enums.parse_mode.ParseMode`)' href=../Enums/#trueconf.enums.ParseMode>ParseMode | str | Text formatting mode (e.g., Markdown, HTML, or plain text). | `` TEXT

`class-attribute`
`instance-attribute`
(`trueconf.enums.parse_mode.ParseMode.TEXT`)' href=../Enums/#trueconf.enums.ParseMode.TEXT>TEXT |

Returns:

| Name | Type | Description |
| --- | --- | --- |
| `SendFileResponse` | `object` | Object containing the result of the document upload. |

Examples:

```
>>> @.message()
>>> async def on_message(message:Message):
>>> await message.answer_document(file=FSInputFile("sticker.webp"))
```

### `` reply_photo `async` ⚓︎

```
reply_photo(file, preview, caption=None, parse_mode= TEXT

class-attribute
instance-attribute
(trueconf.enums.parse_mode.ParseMode.TEXT)' href=../Enums/#trueconf.enums.ParseMode.TEXT>TEXT)
```

Shortcut for the `async` ' href=../Bot/#trueconf.Bot.send_photo>`send_photo` method of the bot instance. Sends a photo as a reply to the current message in this chat.

### Automatically fills the following attributes

- `chat_id`: Current chat identifier.

- `reply_message_id`: ID of the current message.

### Source

trueconf.com/docs/chatbot-connector/en/files/#sending-an-image

Parameters:

| Name | Type | Description | Default |
| --- | --- | --- | --- |
| `file` | `` trueconf.types.InputFile (`trueconf.types.input_file.InputFile`)' href=#trueconf.types.InputFile>InputFile | The photo file to upload. Must be a subclass of `InputFile`. | required |
| `preview` | `` trueconf.types.InputFile (`trueconf.types.input_file.InputFile`)' href=#trueconf.types.InputFile>InputFile | None | Optional preview image. Must also be an `InputFile` if provided. | required |
| `caption` | `str | None` | Optional caption to be sent along with the image. | `None` |
| `parse_mode` | `` ParseMode (`trueconf.enums.parse_mode.ParseMode`)' href=../Enums/#trueconf.enums.ParseMode>ParseMode | str | Formatting mode for the caption (e.g., Markdown, HTML, plain text). | `` TEXT

`class-attribute`
`instance-attribute`
(`trueconf.enums.parse_mode.ParseMode.TEXT`)' href=../Enums/#trueconf.enums.ParseMode.TEXT>TEXT |
| `reply_message_id` | `str | None` | Optional identifier of the message to which this message is a reply. | required |

Returns:

| Name | Type | Description |
| --- | --- | --- |
| `SendFileResponse` | `object` | Object containing the result of the photo upload. |

Examples:

```
>>> @.message()
>>> async def on_message(message:Message):
>>> await message.answer_photo(file=FSInputFile("sticker.webp"), preview=FSInputFile("sticker.webp"))
```

### `` reply_sticker `async` ⚓︎

```
reply_sticker(file)
```

Shortcut for the `async` ' href=../Bot/#trueconf.Bot.send_sticker>`send_sticker` method of the bot instance. Sends a sticker as a reply to the current message in this chat.

### Automatically fills the following attributes

- `chat_id`: Current chat identifier.

- `reply_message_id`: ID of the current message.

### Source

trueconf.com/docs/chatbot-connector/en/files/#upload-file-to-server-storage

Parameters:

| Name | Type | Description | Default |
| --- | --- | --- | --- |
| `file` | `` trueconf.types.InputFile (`trueconf.types.input_file.InputFile`)' href=#trueconf.types.InputFile>InputFile | The sticker file in WebP format. Must be a subclass of `InputFile`. | required |

Returns:

| Name | Type | Description |
| --- | --- | --- |
| `SendFileResponse` | `object` | Object containing the result of the sticker delivery. |

Examples:

```
>>> @.message()
>>> async def on_message(message:Message):
>>> await message.answer_sticker(file=FSInputFile("sticker.webp"))
```

### `` save_to_favorites `async` ⚓︎

```
save_to_favorites(copy=False)
```

Saves the current message to the bot's "Favorites" chat.

By default, the message is forwarded to the bot's personal Favorites chat. If `copy=True`, the message will be copied instead — only for text messages.

Use this method to store important messages, logs, or media content in the bot’s private space.

### Notes

- The Favorites chat is created automatically on first use.

- `copy=True` only works for text messages and does not preserve metadata (like replies or sender info).

- Non-text messages with `copy=True` will be ignored with a warning.

Parameters:

| Name | Type | Description | Default |
| --- | --- | --- | --- |
| `copy` | `bool` | If True, copies the message instead of forwarding it. Defaults to False. | `False` |

Returns:

| Type | Description |
| --- | --- |
| `object` | SendMessageResponse | ForwardMessageResponse | None: |
| `object` | Result of sending or forwarding the message. Returns `None` if copying is not supported for the message type. |

### Example

```
@router.message()
async def on_message(msg: Message):
await msg.save_to_favorites() # forwards message
await msg.save_to_favorites(copy=True) # copies if possible
```

## `` trueconf.types.RemovedChat `dataclass` ⚓︎

```
RemovedChat(chat_id)
```

Event type: a chat was removed.

This object is received in the handler when a private, group, channel, or conference chat is deleted.

### Notes

This class is used as the event type in handler functions decorated with `@.removed_chat()`.

### Source

trueconf.com/docs/chatbot-connector/en/chats/#removedChat

Attributes:

| Name | Type | Description |
| --- | --- | --- |
| `` chat_id

`class-attribute`
`instance-attribute`
(`trueconf.types.RemovedChat.chat_id`)' href=#trueconf.types.RemovedChat.chat_id>chat_id | `str` | Unique identifier of the chat that was removed. |

Examples:

```
from trueconf.types import RemovedChat

@.removed_chat()
async def on_removed(event: RemovedChat):
print(f"Chat removed: {event.chat_id}")
```

### `` chat_id `class-attribute` `instance-attribute` ⚓︎

```
chat_id = field(metadata={'alias': 'chatId'})
```

## `` trueconf.types.RemovedChatParticipant `dataclass` ⚓︎

```
RemovedChatParticipant(timestamp, chat_id, user_id, removed_by)
```

Event type: a participant was removed from a chat.

This object is received in the handler when a user is removed from a group, channel, or conference chat.

### Notes

This class is used as the event type in handler functions decorated with `@.removed_chat_participant()`.

### Source

trueconf.com/docs/chatbot-connector/en/chats/#removedChatParticipant

Attributes:

| Name | Type | Description |
| --- | --- | --- |
| `` timestamp

`instance-attribute`
(`trueconf.types.RemovedChatParticipant.timestamp`)' href=#trueconf.types.RemovedChatParticipant.timestamp>timestamp | `int` | Unix timestamp (milliseconds) of when the event occurred. |
| `` chat_id

`class-attribute`
`instance-attribute`
(`trueconf.types.RemovedChatParticipant.chat_id`)' href=#trueconf.types.RemovedChatParticipant.chat_id>chat_id | `str` | Unique identifier of the chat where the participant was removed. |
| `` user_id

`class-attribute`
`instance-attribute`
(`trueconf.types.RemovedChatParticipant.user_id`)' href=#trueconf.types.RemovedChatParticipant.user_id>user_id | `str` | TrueConf ID of the participant who was removed. |
| `` removed_by

`class-attribute`
`instance-attribute`
(`trueconf.types.RemovedChatParticipant.removed_by`)' href=#trueconf.types.RemovedChatParticipant.removed_by>removed_by | `EnvelopeAuthor` | Information about the user who removed the participant. |

Examples:

```
from trueconf.types import RemovedChatParticipant

@.removed_chat_participant()
async def on_removed(event: RemovedChatParticipant):
print(event.user_id)
```

### `` chat_id `class-attribute` `instance-attribute` ⚓︎

```
chat_id = field(metadata={'alias': 'chatId'})
```

### `` removed_by `class-attribute` `instance-attribute` ⚓︎

```
removed_by = field(metadata={'alias': 'removedBy'})
```

### `` timestamp `instance-attribute` ⚓︎

```
timestamp
```

### `` user_id `class-attribute` `instance-attribute` ⚓︎

```
user_id = field(metadata={'alias': 'userId'})
```

## `` trueconf.types.RemovedMessage `dataclass` ⚓︎

```
RemovedMessage(chat_id, message_id, removed_by)
```

Event type: a message was removed.

This object is received in the handler when a message is deleted from a chat.

### Notes

This class is used as the event type in handler functions decorated with `@.removed_message()`.

### Source

trueconf.com/docs/chatbot-connector/en/messages/#removedMessage

Attributes:

| Name | Type | Description |
| --- | --- | --- |
| `` chat_id

`class-attribute`
`instance-attribute`
(`trueconf.types.RemovedMessage.chat_id`)' href=#trueconf.types.RemovedMessage.chat_id>chat_id | `str` | Unique identifier of the chat from which the message was removed. |
| `` message_id

`class-attribute`
`instance-attribute`
(`trueconf.types.RemovedMessage.message_id`)' href=#trueconf.types.RemovedMessage.message_id>message_id | `str` | Unique identifier of the removed message. |
| `` removed_by

`class-attribute`
`instance-attribute`
(`trueconf.types.RemovedMessage.removed_by`)' href=#trueconf.types.RemovedMessage.removed_by>removed_by | `EnvelopeAuthor` | Information about the user who removed the message. |

Examples:

```
from trueconf.types import RemovedMessage

@.removed_message()
async def on_removed(event: RemovedMessage):
print(f"Message {event.message_id} removed from chat {event.chat_id}")
```

### `` chat_id `class-attribute` `instance-attribute` ⚓︎

```
chat_id = field(metadata={'alias': 'chatId'})
```

### `` message_id `class-attribute` `instance-attribute` ⚓︎

```
message_id = field(metadata={'alias': 'messageId'})
```

### `` removed_by `class-attribute` `instance-attribute` ⚓︎

```
removed_by = field(metadata={'alias': 'removedBy'})
```

## `` trueconf.types.Update `dataclass` ⚓︎

```
Update(method, type, id, payload)
```

### `` id `instance-attribute` ⚓︎

```
id
```

### `` method `instance-attribute` ⚓︎

```
method
```

### `` payload `instance-attribute` ⚓︎

```
payload
```

### `` type `instance-attribute` ⚓︎

```
type
```

## `` trueconf.types.UploadingProgress `dataclass` ⚓︎

```
UploadingProgress(file_id, progress)
```

Event type: file upload progress.

This object is received in the handler when a file is being uploaded and the upload progress is updated.

### Notes

This class is used as the event type in handler functions decorated with `@.uploading_progress()`.

### Source

trueconf.com/docs/chatbot-connector/en/files/#uploadingProgress

Attributes:

| Name | Type | Description |
| --- | --- | --- |
| `` file_id

`class-attribute`
`instance-attribute`
(`trueconf.types.UploadingProgress.file_id`)' href=#trueconf.types.UploadingProgress.file_id>file_id | `str` | Unique identifier of the file being uploaded. |
| `` progress

`instance-attribute`
(`trueconf.types.UploadingProgress.progress`)' href=#trueconf.types.UploadingProgress.progress>progress | `int` | Number of bytes uploaded to the server. |

Examples:

```
from trueconf.types import UploadingProgress

@.uploading_progress()
async def on_progress(event: UploadingProgress):
print(f"File {event.file_id}: uploaded {event.progress} bytes")
```

### `` file_id `class-attribute` `instance-attribute` ⚓︎

```
file_id = field(metadata={'alias': 'fileId'})
```

### `` progress `instance-attribute` ⚓︎

```
progress
```
