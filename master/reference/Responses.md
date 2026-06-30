# Responses⚓︎

```
from trueconf import Bot
```

## `` trueconf.types.responses ⚓︎

### `` AddChatParticipantResponse ⚓︎

```
AddChatParticipantResponse()
```

### `` ApiError ⚓︎

```
ApiError(error_code)
```

#### `` error_code ⚓︎

```
error_code = field(metadata={'alias': 'errorCode'})
```

#### `` message ⚓︎

```
message()
```

#### `` to_exception ⚓︎

```
to_exception(payload=None)
```

### `` AuthResponsePayload ⚓︎

```
AuthResponsePayload(user_id, connection_id)
```

#### `` connection_id ⚓︎

```
connection_id = field(metadata={'alias': 'connectionId'})
```

#### `` user_id ⚓︎

```
user_id = field(metadata={'alias': 'userId'})
```

### `` ChangeParticipantRoleResponse ⚓︎

```
ChangeParticipantRoleResponse()
```

### `` CreateChannelResponse ⚓︎

```
CreateChannelResponse(chat_id)
```

#### `` chat_id ⚓︎

```
chat_id = field(metadata={'alias': 'chatId'})
```

### `` CreateGroupChatResponse ⚓︎

```
CreateGroupChatResponse(chat_id)
```

#### `` chat_id ⚓︎

```
chat_id = field(metadata={'alias': 'chatId'})
```

### `` CreateP2PChatResponse ⚓︎

```
CreateP2PChatResponse(chat_id)
```

#### `` chat_id ⚓︎

```
chat_id = field(metadata={'alias': 'chatId'})
```

### `` EditChatTitleResponse ⚓︎

```
EditChatTitleResponse(chat_id, timestamp)
```

#### `` chat_id ⚓︎

```
chat_id = field(metadata={'alias': 'chatId'})
```

#### `` timestamp ⚓︎

```
timestamp
```

### `` EditMessageResponse ⚓︎

```
EditMessageResponse(message_id, timestamp)
```

#### `` message_id ⚓︎

```
message_id = field(metadata={'alias': 'messageId'})
```

#### `` timestamp ⚓︎

```
timestamp
```

### `` EditSurveyResponse ⚓︎

```
EditSurveyResponse(message_id, timestamp)
```

#### `` message_id ⚓︎

```
message_id = field(metadata={'alias': 'messageId'})
```

#### `` timestamp ⚓︎

```
timestamp
```

### `` ForwardMessageResponse ⚓︎

```
ForwardMessageResponse(chat_id, message_id, timestamp)
```

#### `` chat_id ⚓︎

```
chat_id = field(metadata={'alias': 'chatId'})
```

#### `` message_id ⚓︎

```
message_id = field(metadata={'alias': 'messageId'})
```

#### `` timestamp ⚓︎

```
timestamp
```

### `` GetChatByIdResponse ⚓︎

```
GetChatByIdResponse(title, chat_id, chat_type, unread_messages, avatar_url=None, last_message=None)
```

#### `` avatar_url ⚓︎

```
avatar_url = field(default=None, metadata={'alias': 'avatarUrl'})
```

#### `` chat_id ⚓︎

```
chat_id = field(metadata={'alias': 'chatId'})
```

#### `` chat_type ⚓︎

```
chat_type = field(metadata={'alias': 'chatType'})
```

#### `` last_message ⚓︎

```
last_message = field(default=None, metadata={'alias': 'lastMessage'})
```

#### `` title ⚓︎

```
title
```

#### `` unread_messages ⚓︎

```
unread_messages = field(metadata={'alias': 'unreadMessages'})
```

### `` GetChatHistoryResponse ⚓︎

```
GetChatHistoryResponse(count, chat_id, messages=list())
```

#### `` chat_id ⚓︎

```
chat_id = field(metadata={'alias': 'chatId'})
```

#### `` count ⚓︎

```
count
```

#### `` messages ⚓︎

```
messages = field(default_factory=list, metadata={'alias': 'messages'})
```

### `` GetChatParticipantsResponse ⚓︎

```
GetChatParticipantsResponse(participants=list())
```

#### `` participants ⚓︎

```
participants = field(default_factory=list, metadata={'alias': 'participants'})
```

### `` GetChatsResponse ⚓︎

```
GetChatsResponse(chats=list())
```

#### `` chats ⚓︎

```
chats = field(default_factory=list, metadata={'alias': 'chats'})
```

### `` GetFileInfoResponse ⚓︎

```
GetFileInfoResponse(name, size, mimetype, ready_state, file_id, previews=None, download_url=None)
```

#### `` download_url ⚓︎

```
download_url = field(default=None, metadata={'alias': 'downloadUrl'})
```

#### `` file_id ⚓︎

```
file_id = field(metadata={'alias': 'fileId'})
```

#### `` mimetype ⚓︎

```
mimetype = field(metadata={'alias': 'mimeType'})
```

#### `` name ⚓︎

```
name
```

#### `` previews ⚓︎

```
previews = field(default=None)
```

#### `` ready_state ⚓︎

```
ready_state = field(metadata={'alias': 'readyState'})
```

#### `` size ⚓︎

```
size
```

### `` GetFileUploadLimitsResponse ⚓︎

```
GetFileUploadLimitsResponse(extensions, max_size=None)
```

#### `` extensions ⚓︎

```
extensions
```

#### `` max_size ⚓︎

```
max_size = field(default=None, metadata={'alias': 'maxSize'})
```

### `` GetMessageByIdResponse ⚓︎

```
GetMessageByIdResponse(timestamp, type, author, box, content, message_id, chat_id, is_edited, reply_message_id=None)
```

#### `` author ⚓︎

```
author
```

#### `` box ⚓︎

```
box
```

#### `` chat_id ⚓︎

```
chat_id = field(metadata={'alias': 'chatId'})
```

#### `` content ⚓︎

```
content
```

#### `` is_edited ⚓︎

```
is_edited = field(metadata={'alias': 'isEdited'})
```

#### `` message_id ⚓︎

```
message_id = field(metadata={'alias': 'messageId'})
```

#### `` reply_message_id ⚓︎

```
reply_message_id = field(default=None, metadata={'alias': 'replyMessageId'})
```

#### `` timestamp ⚓︎

```
timestamp
```

#### `` type ⚓︎

```
type
```

### `` GetUserDisplayNameResponse ⚓︎

```
GetUserDisplayNameResponse(display_name)
```

#### `` display_name ⚓︎

```
display_name = field(metadata={'alias': 'displayName'})
```

### `` HasChatParticipantResponse ⚓︎

```
HasChatParticipantResponse(result)
```

#### `` result ⚓︎

```
result
```

### `` Previews ⚓︎

```
Previews(name, size, mimetype, download_url)
```

#### `` download_url ⚓︎

```
download_url = field(metadata={'alias': 'downloadUrl'})
```

#### `` mimetype ⚓︎

```
mimetype = field(metadata={'alias': 'mimeType'})
```

#### `` name ⚓︎

```
name
```

#### `` size ⚓︎

```
size
```

### `` RemoveChatParticipantResponse ⚓︎

```
RemoveChatParticipantResponse()
```

### `` RemoveChatResponse ⚓︎

```
RemoveChatResponse()
```

### `` RemoveMessageResponse ⚓︎

```
RemoveMessageResponse()
```

### `` SendFileResponse ⚓︎

```
SendFileResponse(timestamp, chat_id, message_id, file_id)
```

#### `` chat_id ⚓︎

```
chat_id = field(metadata={'alias': 'chatId'})
```

#### `` file_id ⚓︎

```
file_id = field(metadata={'alias': 'fileId'})
```

#### `` message_id ⚓︎

```
message_id = field(metadata={'alias': 'messageId'})
```

#### `` timestamp ⚓︎

```
timestamp
```

### `` SendMessageResponse ⚓︎

```
SendMessageResponse(chat_id, message_id, timestamp)
```

#### `` chat_id ⚓︎

```
chat_id = field(metadata={'alias': 'chatId'})
```

#### `` message_id ⚓︎

```
message_id = field(metadata={'alias': 'messageId'})
```

#### `` timestamp ⚓︎

```
timestamp
```

### `` SendSurveyResponse ⚓︎

```
SendSurveyResponse(chat_id, message_id, timestamp)
```

#### `` chat_id ⚓︎

```
chat_id = field(metadata={'alias': 'chatId'})
```

#### `` message_id ⚓︎

```
message_id = field(metadata={'alias': 'messageId'})
```

#### `` timestamp ⚓︎

```
timestamp
```

### `` SubscribeFileProgressResponse ⚓︎

```
SubscribeFileProgressResponse(result)
```

#### `` result ⚓︎

```
result
```

### `` UnsubscribeFileProgressResponse ⚓︎

```
UnsubscribeFileProgressResponse(result)
```

#### `` result ⚓︎

```
result
```

### `` UploadFileResponse ⚓︎

```
UploadFileResponse(upload_task_id)
```

#### `` upload_task_id ⚓︎

```
upload_task_id = field(metadata={'alias': 'uploadTaskId'})
```

June 30, 2026

February 27, 2026
