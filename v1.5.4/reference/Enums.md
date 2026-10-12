# Enums

You can import all enums at once:

```
from trueconf.enums import *
```

## `` trueconf.enums ⚓︎

### `` ALLOWED_BUTTON_URL_SCHEMES `module-attribute` ⚓︎

```
ALLOWED_BUTTON_URL_SCHEMES = (
"http",
"https",
"mailto",
"trueconf",
)
```

### `` ButtonStyle ⚓︎

#### `` DANGER `class-attribute` `instance-attribute` ⚓︎

```
DANGER = 'danger'
```

#### `` DEFAULT `class-attribute` `instance-attribute` ⚓︎

```
DEFAULT = 'default'
```

#### `` PRIMARY `class-attribute` `instance-attribute` ⚓︎

```
PRIMARY = 'primary'
```

#### `` SUCCESS `class-attribute` `instance-attribute` ⚓︎

```
SUCCESS = 'success'
```

### `` ButtonType ⚓︎

#### `` COMMAND `class-attribute` `instance-attribute` ⚓︎

```
COMMAND = 'command'
```

#### `` COPY `class-attribute` `instance-attribute` ⚓︎

```
COPY = 'copy'
```

#### `` MESSAGE `class-attribute` `instance-attribute` ⚓︎

```
MESSAGE = 'message'
```

#### `` SHARE `class-attribute` `instance-attribute` ⚓︎

```
SHARE = 'share'
```

#### `` URL `class-attribute` `instance-attribute` ⚓︎

```
URL = 'url'
```

### `` ChatActivity ⚓︎

This object represents a type of activity that the bot can show in a chat.

### Source

trueconf.com/docs/chatbot-connector/en/messages/#sendChatActivity

#### `` CHOOSING_STICKER `class-attribute` `instance-attribute` ⚓︎

```
CHOOSING_STICKER = 'choosing_sticker'
```

#### `` TYPING `class-attribute` `instance-attribute` ⚓︎

```
TYPING = 'typing'
```

#### `` UPLOADING_FILE `class-attribute` `instance-attribute` ⚓︎

```
UPLOADING_FILE = 'uploading_file'
```

### `` ChatParticipantRole ⚓︎

This object represents a possible participant role in a chat.

### Source

trueconf.com/docs/chatbot-connector/en/objects/#chatparticipantroleenum

#### `` ADMIN `class-attribute` `instance-attribute` ⚓︎

```
ADMIN = 'admin'
```

#### `` CONF_MODERATOR `class-attribute` `instance-attribute` ⚓︎

```
CONF_MODERATOR = 'conf_moderator'
```

#### `` CONF_OWNER `class-attribute` `instance-attribute` ⚓︎

```
CONF_OWNER = 'conf_owner'
```

#### `` FAVORITES_OWNER `class-attribute` `instance-attribute` ⚓︎

```
FAVORITES_OWNER = 'favorites_owner'
```

#### `` OWNER `class-attribute` `instance-attribute` ⚓︎

```
OWNER = 'owner'
```

#### `` USER `class-attribute` `instance-attribute` ⚓︎

```
USER = 'user'
```

#### `` WRITER `class-attribute` `instance-attribute` ⚓︎

```
WRITER = 'writer'
```

### `` ChatType ⚓︎

The enumeration contains possible chat types.

### Source

trueconf.com/docs/chatbot-connector/en/objects/#chattypeenum

#### `` CHANNEL `class-attribute` `instance-attribute` ⚓︎

```
CHANNEL = 6
```

#### `` FAVORITES `class-attribute` `instance-attribute` ⚓︎

```
FAVORITES = 5
```

#### `` GROUP `class-attribute` `instance-attribute` ⚓︎

```
GROUP = 2
```

#### `` P2P `class-attribute` `instance-attribute` ⚓︎

```
P2P = 1
```

#### `` SYSTEM `class-attribute` `instance-attribute` ⚓︎

```
SYSTEM = 3
```

#### `` UNDEF `class-attribute` `instance-attribute` ⚓︎

```
UNDEF = 0
```

### `` CommandAnswerType ⚓︎

#### `` CANCEL `class-attribute` `instance-attribute` ⚓︎

```
CANCEL = 'cancel'
```

#### `` COMPLETE `class-attribute` `instance-attribute` ⚓︎

```
COMPLETE = 'complete'
```

#### `` MESSAGE `class-attribute` `instance-attribute` ⚓︎

```
MESSAGE = 'message'
```

#### `` TIMEOUT `class-attribute` `instance-attribute` ⚓︎

```
TIMEOUT = 'timeout'
```

### `` CommandMessageLevel ⚓︎

#### `` CRITICAL `class-attribute` `instance-attribute` ⚓︎

```
CRITICAL = 'critical'
```

#### `` ERROR `class-attribute` `instance-attribute` ⚓︎

```
ERROR = 'error'
```

#### `` INFO `class-attribute` `instance-attribute` ⚓︎

```
INFO = 'info'
```

#### `` WARNING `class-attribute` `instance-attribute` ⚓︎

```
WARNING = 'warning'
```

### `` CommandMessageStatus ⚓︎

#### `` CANCELED `class-attribute` `instance-attribute` ⚓︎

```
CANCELED = 'canceled'
```

#### `` FAILED `class-attribute` `instance-attribute` ⚓︎

```
FAILED = 'failed'
```

#### `` OK `class-attribute` `instance-attribute` ⚓︎

```
OK = 'ok'
```

#### `` PENDING `class-attribute` `instance-attribute` ⚓︎

```
PENDING = 'pending'
```

#### `` RUNNING `class-attribute` `instance-attribute` ⚓︎

```
RUNNING = 'running'
```

#### `` TIMEOUT `class-attribute` `instance-attribute` ⚓︎

```
TIMEOUT = 'timeout'
```

#### `` UNKNOWN `class-attribute` `instance-attribute` ⚓︎

```
UNKNOWN = 'unknown'
```

### `` CommandMessageVisibility ⚓︎

#### `` ALERT `class-attribute` `instance-attribute` ⚓︎

```
ALERT = 'alert'
```

#### `` DEFAULT `class-attribute` `instance-attribute` ⚓︎

```
DEFAULT = 'default'
```

#### `` STICKY `class-attribute` `instance-attribute` ⚓︎

```
STICKY = 'sticky'
```

#### `` TOAST `class-attribute` `instance-attribute` ⚓︎

```
TOAST = 'toast'
```

### `` EnvelopeAuthorType ⚓︎

The enumeration contains possible author types.

### Source

trueconf.com/docs/chatbot-connector/en/objects/#envelopeauthortypeenum

#### `` SYSTEM `class-attribute` `instance-attribute` ⚓︎

```
SYSTEM = 0
```

#### `` USER `class-attribute` `instance-attribute` ⚓︎

```
USER = 1
```

### `` FileReadyState ⚓︎

This enumeration is used to indicate the status of a file on the server.

### Source

trueconf.com/docs/chatbot-connector/en/objects/#filereadystateenum

#### `` NOT_AVAILABLE `class-attribute` `instance-attribute` ⚓︎

```
NOT_AVAILABLE = 0
```

#### `` READY `class-attribute` `instance-attribute` ⚓︎

```
READY = 2
```

#### `` UPLOADING `class-attribute` `instance-attribute` ⚓︎

```
UPLOADING = 1
```

### `` IncomingUpdateMethod ⚓︎

#### `` ADDED_CHAT_PARTICIPANT `class-attribute` `instance-attribute` ⚓︎

```
ADDED_CHAT_PARTICIPANT = 'addChatParticipant'
```

#### `` CHANGED_FILE_UPLOAD_LIMITS `class-attribute` `instance-attribute` ⚓︎

```
CHANGED_FILE_UPLOAD_LIMITS = 'getFileUploadLimits'
```

#### `` CHANGED_PARTICIPANT_ROLE `class-attribute` `instance-attribute` ⚓︎

```
CHANGED_PARTICIPANT_ROLE = 'changeParticipantRole'
```

#### `` CLEARED_CHAT_HISTORY `class-attribute` `instance-attribute` ⚓︎

```
CLEARED_CHAT_HISTORY = 'clearHistory'
```

#### `` COMMAND `class-attribute` `instance-attribute` ⚓︎

```
COMMAND = 'command'
```

#### `` CREATED_CHANNEL `class-attribute` `instance-attribute` ⚓︎

```
CREATED_CHANNEL = 'createChannel'
```

#### `` CREATED_FAVORITES_CHAT `class-attribute` `instance-attribute` ⚓︎

```
CREATED_FAVORITES_CHAT = 'createFavoritesChat'
```

#### `` CREATED_GROUP_CHAT `class-attribute` `instance-attribute` ⚓︎

```
CREATED_GROUP_CHAT = 'createGroupChat'
```

#### `` CREATED_PERSONAL_CHAT `class-attribute` `instance-attribute` ⚓︎

```
CREATED_PERSONAL_CHAT = 'createP2PChat'
```

#### `` EDITED_CHAT_AVATAR `class-attribute` `instance-attribute` ⚓︎

```
EDITED_CHAT_AVATAR = 'editChatAvatar'
```

#### `` EDITED_CHAT_TITLE `class-attribute` `instance-attribute` ⚓︎

```
EDITED_CHAT_TITLE = 'editChatTitle'
```

#### `` EDITED_MESSAGE `class-attribute` `instance-attribute` ⚓︎

```
EDITED_MESSAGE = 'editMessage'
```

#### `` MESSAGE `class-attribute` `instance-attribute` ⚓︎

```
MESSAGE = 'sendMessage'
```

#### `` REMOVED_CHAT `class-attribute` `instance-attribute` ⚓︎

```
REMOVED_CHAT = 'removeChat'
```

#### `` REMOVED_CHAT_PARTICIPANT `class-attribute` `instance-attribute` ⚓︎

```
REMOVED_CHAT_PARTICIPANT = 'removeChatParticipant'
```

#### `` REMOVED_MESSAGE `class-attribute` `instance-attribute` ⚓︎

```
REMOVED_MESSAGE = 'removeMessage'
```

#### `` UPLOADING_PROGRESS `class-attribute` `instance-attribute` ⚓︎

```
UPLOADING_PROGRESS = 'uploadFileProgress'
```

### `` MessageType ⚓︎

The enumeration contains the message type.

### Source

trueconf.com/docs/chatbot-connector/en/objects/#envelopetypeenum

#### `` ADD_PARTICIPANT `class-attribute` `instance-attribute` ⚓︎

```
ADD_PARTICIPANT = 1
```

#### `` ATTACHMENT `class-attribute` `instance-attribute` ⚓︎

```
ATTACHMENT = 202
```

#### `` CLEAR_CHAT_HISTORY `class-attribute` `instance-attribute` ⚓︎

```
CLEAR_CHAT_HISTORY = 23
```

#### `` EDIT_CHAT_AVATAR `class-attribute` `instance-attribute` ⚓︎

```
EDIT_CHAT_AVATAR = 22
```

#### `` EDIT_CHAT_TITLE `class-attribute` `instance-attribute` ⚓︎

```
EDIT_CHAT_TITLE = 21
```

#### `` FORWARDED_MESSAGE `class-attribute` `instance-attribute` ⚓︎

```
FORWARDED_MESSAGE = 201
```

#### `` LOCATION `class-attribute` `instance-attribute` ⚓︎

```
LOCATION = 203
```

#### `` PARTICIPANT_ROLE `class-attribute` `instance-attribute` ⚓︎

```
PARTICIPANT_ROLE = 110
```

#### `` PLAIN_MESSAGE `class-attribute` `instance-attribute` ⚓︎

```
PLAIN_MESSAGE = 200
```

#### `` REMOVE_PARTICIPANT `class-attribute` `instance-attribute` ⚓︎

```
REMOVE_PARTICIPANT = 2
```

#### `` SURVEY `class-attribute` `instance-attribute` ⚓︎

```
SURVEY = 204
```

#### `` VOICE_MESSAGE `class-attribute` `instance-attribute` ⚓︎

```
VOICE_MESSAGE = 205
```

### `` OAuthError ⚓︎

Error codes, according to the OAuth 2.0 specification, are presented as ASCII strings from the list specified in the specification.

### Source

trueconf.com/docs/chatbot-connector/en/objects/#oauth-error

#### `` INVALID_CLIENT `class-attribute` `instance-attribute` ⚓︎

```
INVALID_CLIENT = 'invalid_client'
```

#### `` INVALID_GRANT `class-attribute` `instance-attribute` ⚓︎

```
INVALID_GRANT = 'invalid_grant'
```

#### `` INVALID_REQUEST `class-attribute` `instance-attribute` ⚓︎

```
INVALID_REQUEST = 'invalid_request'
```

#### `` UNSUPORTED_GRANT_TYPE `class-attribute` `instance-attribute` ⚓︎

```
UNSUPORTED_GRANT_TYPE = 'unsupported_grant_type'
```

### `` ParseMode ⚓︎

Formatting options

### Source

trueconf.com/docs/chatbot-connector/en/messages/#message-formatting

#### `` HTML `class-attribute` `instance-attribute` ⚓︎

```
HTML = 'html'
```

#### `` MARKDOWN `class-attribute` `instance-attribute` ⚓︎

```
MARKDOWN = 'markdown'
```

#### `` TEXT `class-attribute` `instance-attribute` ⚓︎

```
TEXT = 'text'
```

### `` SurveyType ⚓︎

#### `` ANONYMOUS `class-attribute` `instance-attribute` ⚓︎

```
ANONYMOUS = '{{Anonymous survey}}'
```

#### `` NON_ANONYMOUS `class-attribute` `instance-attribute` ⚓︎

```
NON_ANONYMOUS = '{{Survey}}'
```

### `` UpdateType ⚓︎

There are three types of messages. Only REQUEST and RESPONSE are applicable.

### Source

trueconf.com/docs/chatbot-connector/en/objects/#message-type

#### `` REQUEST `class-attribute` `instance-attribute` ⚓︎

```
REQUEST = 1
```

#### `` RESERVED `class-attribute` `instance-attribute` ⚓︎

```
RESERVED = 0
```

#### `` RESPONSE `class-attribute` `instance-attribute` ⚓︎

```
RESPONSE = 2
```

June 30, 2026

September 3, 2025
