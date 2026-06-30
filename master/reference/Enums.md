# Enums

You can import all enums at once:

```
from trueconf.enums import *
```

## `` trueconf.enums ⚓︎

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
