# Class `Bot`⚓︎

Here is the reference information for the `Bot` class, including all its parameters, attributes, and methods.
You can import the `Bot` class directly from the `trueconf` package:

```
from trueconf import Bot
```

## `` trueconf.Bot ⚓︎

```
Bot(server, token, *, dispatcher=None, receive_unread_messages=False, receive_system_messages=False, verify_ssl=True, web_port=None, https=True, ws_max_retries=5, ws_max_delay=60, debug=False, on_health_check=None)
```

Initializes a TrueConf chatbot instance with WebSocket connection and configuration options.

### Source

trueconf.com/docs/chatbot-connector/en/connect-and-auth/#auth

Parameters:

| Name | Type | Description | Default |
| --- | --- | --- | --- |
| `server` | `str` | Address of the TrueConf server. | required |
| `token` | `str` | Bot authorization token. | required |
| `*` | | All following arguments must be passed by name (keyword-only). | required |
| `dispatcher` | `` trueconf.Dispatcher (`trueconf.dispatcher.dispatcher.Dispatcher`)' href=../Dispatcher/#trueconf.Dispatcher>Dispatcher | None | Dispatcher instance for registering handlers. | `None` |
| `receive_unread_messages` | `bool` | Whether to receive unread messages on connection. Defaults to False. | `False` |
| `receive_system_messages` | `bool` | Whether to receive system messages, such as user additions to the chat or chat title changes. Defaults to False. | `False` |
| `verify_ssl` | `bool | str | SSLContext` | SSL verification mode. If True, verifies the server certificate using the system trust store when available. If False, disables certificate verification. If a string is provided, it must be a path to a CA bundle file. A custom ssl.SSLContext can also be passed. Defaults to True. | `True` |
| `web_port` | `int` | WebSocket connection port. Defaults to 443. | `None` |
| `https` | `bool` | Whether to use HTTPS protocol. Defaults to True. | `True` |
| `ws_max_retries` | `int` | Max connection attempts on network/IP errors before giving up. Defaults to 5. | `5` |
| `ws_max_delay` | `int` | Maximum delay between reconnection attempts (in seconds). Defaults to 60. | `60` |
| `debug` | `bool` | Enables debug mode. Defaults to False. | `False` |
| `on_health_check` | `HealthCheckCallback | None` | Async callback called when the bot connection health changes. The callback receives a dictionary with the current status, WebSocket state, authorization state, server, port, protocol, timestamp, and optional error details. Defaults to None. | `None` |

### Note

Alternatively, you can authorize using a username and password via the `from_credentials()` class method.

### `` authorized_event `instance-attribute` ⚓︎

```
authorized_event = Event()
```

### `` connected_event `instance-attribute` ⚓︎

```
connected_event = Event()
```

### `` debug `instance-attribute` ⚓︎

```
debug = debug
```

### `` dp `instance-attribute` ⚓︎

```
dp = dispatcher or trueconf.Dispatcher (trueconf.dispatcher.dispatcher.Dispatcher)' href=../Dispatcher/#trueconf.Dispatcher>Dispatcher()
```

### `` file_extension_filter_mode `instance-attribute` ⚓︎

```
file_extension_filter_mode = None
```

### `` file_extensions_list `instance-attribute` ⚓︎

```
file_extensions_list = None
```

### `` https `instance-attribute` ⚓︎

```
https = https
```

### `` max_file_size `instance-attribute` ⚓︎

```
max_file_size = None
```

### `` me_id `property` ⚓︎

```
me_id
```

### `` port `instance-attribute` ⚓︎

```
port = 443 if https else 4309
```

### `` receive_system_messages `instance-attribute` ⚓︎

```
receive_system_messages = receive_system_messages
```

### `` receive_unread_messages `instance-attribute` ⚓︎

```
receive_unread_messages = receive_unread_messages
```

### `` server `instance-attribute` ⚓︎

```
server = server
```

### `` ssl_context `instance-attribute` ⚓︎

```
ssl_context = _build_ssl_context(verify_ssl)
```

### `` stopped_event `instance-attribute` ⚓︎

```
stopped_event = Event()
```

### `` token `property` ⚓︎

```
token
```

Returns the bot's authorization token.

Returns:

| Name | Type | Description |
| --- | --- | --- |
| `str` | `str` | The access token used for authentication. |

### `` add_participant_to_chat `async` ⚓︎

```
add_participant_to_chat(chat_id, user_id, display_history=False)
```

Adds a participant to the specified chat.

Optionally allows showing chat history to the newly added participant. The `display_history` parameter is supported only in TrueConf Server version 5.5.2 and above.

### Source

trueconf.com/docs/chatbot-connector/en/chats/#addChatParticipant

Parameters:

| Name | Type | Description | Default |
| --- | --- | --- | --- |
| `chat_id` | `str` | Identifier of the chat to add the participant to. | required |
| `user_id` | `str` | Identifier of the user to be added. If no domain is specified, the server domain will be used. | required |
| `display_history` | `bool` | Whether to show previous chat history to the participant. Requires TrueConf Server 5.5.2+. Defaults to False. | `False` |

Returns:

| Name | Type | Description |
| --- | --- | --- |
| `AddChatParticipantResponse` | `` AddChatParticipantResponse (`trueconf.types.responses.add_chat_participant_response.AddChatParticipantResponse`)' href=../Responses/#trueconf.types.responses.AddChatParticipantResponse>AddChatParticipantResponse | Object containing the result of the participant addition. |

### Example

```
await bot.add_participant_to_chat(
chat_id="chat123",
user_id="user456",
display_history=True
)
```

### `` change_participant_role `async` ⚓︎

```
change_participant_role(chat_id, user_id, role)
```

Requires TrueConf Server 5.5.2+.

Changes the role of a participant in the specified group chat.

This method requires that the bot has moderator (admin) or owner rights in the chat.

### Supported roles in group chat

- "owner" — group chat owner

- "admin" — appointed moderator of the group chat

- "user" — regular participant of a group chat

### It is recommended to use the enumeration class for safer role assignment

```
from trueconf.enums import ChatParticipantRole
```

For a full list of roles in conference, channel, or Favorites chats, see the documentation:

### Role descriptions

trueconf.com/docs/chatbot-connector/en/roles-and-users-rules/#which-roles-has-apis

### Role permissions matrix

trueconf.com/docs/chatbot-connector/en/roles-and-users-rules/#roles-rules-group-chats

### Source

trueconf.com/docs/chatbot-connector/en/chats/#changeParticipantRole

Parameters:

| Name | Type | Description | Default |
| --- | --- | --- | --- |
| `chat_id` | `str` | Identifier of the chat where the role should be changed. | required |
| `user_id` | `str` | Identifier of the participant whose role is being updated. | required |
| `role` | `str |` ChatParticipantRole (`trueconf.enums.chat_participant_role.ChatParticipantRole`)' href=../Enums/#trueconf.enums.ChatParticipantRole>ChatParticipantRole | New role to assign. Must be one of the supported roles listed above. | required |

Returns:

| Name | Type | Description |
| --- | --- | --- |
| `ChangeParticipantRoleResponse` | `` ChangeParticipantRoleResponse (`trueconf.types.responses.change_participant_role_response.ChangeParticipantRoleResponse`)' href=../Responses/#trueconf.types.responses.ChangeParticipantRoleResponse>ChangeParticipantRoleResponse | Object containing the result of the role change operation. |

### Example

```
from trueconf.enums import ChatParticipantRole as role

await bot.change_participant_role(
chat_id="chat123",
user_id="user456",
role=role.ADMIN
)
```

### `` check_version `async` ⚓︎

```
check_version()
```

### `` clear_chat_history `async` ⚓︎

```
clear_chat_history(chat_id, for_all=False)
```

```
**Requires TrueConf Server 5.5.3+**
```

Parameters:

| Name | Type | Description | Default |
| --- | --- | --- | --- |
| `chat_id` | `str` | Identifier of the chat to clear the history for. | required |
| `for_all` | `bool` | If True, the history will be cleared for all participants. If False, it will only be cleared for the current user. Defaults to False. | `False` |

Returns:

| Name | Type | Description |
| --- | --- | --- |
| `ClearChatHistoryResponse` | `ClearChatHistoryResponse` | Object containing the result of the history clearing. |

### `` create_channel `async` ⚓︎

```
create_channel(title)
```

Creates a new channel with the specified title.

### Source

trueconf.com/docs/chatbot-connector/en/chats/#createChannel

Parameters:

| Name | Type | Description | Default |
| --- | --- | --- | --- |
| `title` | `str` | Title of the new channel. | required |

Returns:

| Name | Type | Description |
| --- | --- | --- |
| `CreateChannelResponse` | `` CreateChannelResponse (`trueconf.types.responses.create_channel_response.CreateChannelResponse`)' href=../Responses/#trueconf.types.responses.CreateChannelResponse>CreateChannelResponse | Object containing the result of the channel creation. |

### `` create_favorites_chat `async` ⚓︎

```
create_favorites_chat()
```

Requires TrueConf Server 5.5.2+

Creates a "Favorites" chat for the current user.

This type of chat is a personal space accessible only to its owner. It can be used to store notes, upload files, or test bot features in a private context.

### Source

trueconf.com/docs/chatbot-connector/en/chats/#createFavoritesChat

Returns:

| Name | Type | Description |
| --- | --- | --- |
| `CreateFavoritesChatResponse` | `CreateFavoritesChatResponse` | An object containing information about the newly created chat. |

### `` create_group_chat `async` ⚓︎

```
create_group_chat(title)
```

Creates a new group chat with the specified title.

### Source

trueconf.com/docs/chatbot-connector/en/chats/#createGroupChat

Parameters:

| Name | Type | Description | Default |
| --- | --- | --- | --- |
| `title` | `str` | Title of the new group chat. | required |

Returns:

| Name | Type | Description |
| --- | --- | --- |
| `CreateGroupChatResponse` | `` CreateGroupChatResponse (`trueconf.types.responses.create_group_chat_response.CreateGroupChatResponse`)' href=../Responses/#trueconf.types.responses.CreateGroupChatResponse>CreateGroupChatResponse | Object containing the result of the group chat creation. |

### `` create_personal_chat `async` ⚓︎

```
create_personal_chat(user_id)
```

Creates a personal (P2P) chat with a user by their identifier.

### Source

trueconf.com/docs/chatbot-connector/en/chats/#createP2PChat

Parameters:

| Name | Type | Description | Default |
| --- | --- | --- | --- |
| `user_id` | `str` | Identifier of the user. Can be with or without a domain. | required |

Returns:

| Name | Type | Description |
| --- | --- | --- |
| `CreateP2PChatResponse` | `` CreateP2PChatResponse (`trueconf.types.responses.create_p2p_chat_response.CreateP2PChatResponse`)' href=../Responses/#trueconf.types.responses.CreateP2PChatResponse>CreateP2PChatResponse | Object containing the result of the personal chat creation. |

### Note

Creating a personal chat (peer-to-peer) with a server user. If the bot has never messaged this user before, a new chat will be created. If the bot has previously sent messages to this user, the existing chat will be returned.

### `` delete_chat `async` ⚓︎

```
delete_chat(chat_id)
```

Deletes a chat by its identifier.

### Source

trueconf.com/docs/chatbot-connector/en/chats/#removeChat

Parameters:

| Name | Type | Description | Default |
| --- | --- | --- | --- |
| `chat_id` | `str` | Identifier of the chat to be deleted. | required |

Returns:

| Name | Type | Description |
| --- | --- | --- |
| `RemoveChatResponse` | `` RemoveChatResponse (`trueconf.types.responses.remove_chat_response.RemoveChatResponse`)' href=../Responses/#trueconf.types.responses.RemoveChatResponse>RemoveChatResponse | Object containing the result of the chat deletion. |

### `` download_file_by_id `async` ⚓︎

```
download_file_by_id(file_id, dest_path=None)
```

Downloads a file by its ID, waiting for the upload to complete if necessary.

If `dest_path` is provided, the file is saved to disk and the Path is returned. If `dest_path` is None, the file content is returned as bytes.

Parameters:

| Name | Type | Description | Default |
| --- | --- | --- | --- |
| `file_id` | `str` | Unique identifier of the file on the server. | required |
| `dest_path` | `str | Path` | Path where the file should be saved. | `None` |

Returns:

| Type | Description |
| --- | --- |
| `bytes | Path | None` | bytes | Path | None: File content (bytes), path to file (Path), or None if failed. |

### `` edit_chat_avatar `async` ⚓︎

```
edit_chat_avatar(chat_id, file)
```

Updates the avatar of the specified chat. Use this method to set a new chat avatar for a group chat and channel.

### Notes

Requires TrueConf Server 5.5.3 or later. The bot must have sufficient permissions in the chat (e.g., owner or admin/moderator). The file must be provided as an instance of one of the `InputFile` subclasses: `FSInputFile`, `BufferedInputFile`, or `URLInputFile`.

### Source

trueconf.com/docs/chatbot-connector/en/chats/#editChatAvatar

Parameters:

| Name | Type | Description | Default |
| --- | --- | --- | --- |
| `chat_id` | `str` | Identifier of the chat whose avatar should be updated. | required |
| `file` | `` trueconf.types.InputFile (`trueconf.types.input_file.InputFile`)' href=../Types/#trueconf.types.InputFile>InputFile | Image file to be uploaded as the new chat avatar. | required |

Returns:

| Name | Type | Description |
| --- | --- | --- |
| `EditChatAvatarResponse` | `EditChatAvatarResponse` | Object containing the result of the avatar update. |

### Example

```
await bot.edit_chat_avatar(
chat_id="a1s2d3f4f5g6",
file=FSInputFile("avatar.png")
)
```

### `` edit_chat_title `async` ⚓︎

```
edit_chat_title(chat_id, title)
```

Updates the display title of the specified chat.

Use this method to set a new visible name for a chat (e.g., a group chat or channel).

### Notes

Requires TrueConf Server 5.5.3 or later. The bot must have sufficient permissions in the chat (e.g., owner or admin/moderator).

### Source

trueconf.com/docs/chatbot-connector/en/chats/#editChatTitle

Parameters:

| Name | Type | Description | Default |
| --- | --- | --- | --- |
| `chat_id` | `str` | Identifier of the chat whose title should be updated. | required |
| `title` | `str` | New title for the chat. | required |

Returns:

| Name | Type | Description |
| --- | --- | --- |
| `EditChatTitleResponse` | `` EditChatTitleResponse (`trueconf.types.responses.edit_chat_title_response.EditChatTitleResponse`)' href=../Responses/#trueconf.types.responses.EditChatTitleResponse>EditChatTitleResponse | Object containing the result of the title update. |

### Example

```
await bot.edit_chat_title(chat_id="a1s2d3f4f5g6", title="Project Alpha – Team")
```

### `` edit_message `async` ⚓︎

```
edit_message(message_id, text, parse_mode= TEXT

class-attribute
instance-attribute
(trueconf.enums.parse_mode.ParseMode.TEXT)' href=../Enums/#trueconf.enums.ParseMode.TEXT>TEXT)
```

Edits a previously sent message.

### Source

trueconf.com/docs/chatbot-connector/en/messages/#editMessage

Parameters:

| Name | Type | Description | Default |
| --- | --- | --- | --- |
| `message_id` | `str` | Identifier of the message to be edited. | required |
| `text` | `str` | New text content for the message. | required |
| `parse_mode` | `` ParseMode (`trueconf.enums.parse_mode.ParseMode`)' href=../Enums/#trueconf.enums.ParseMode>ParseMode | str | Text formatting mode. Defaults to plain text. | `` TEXT

`class-attribute`
`instance-attribute`
(`trueconf.enums.parse_mode.ParseMode.TEXT`)' href=../Enums/#trueconf.enums.ParseMode.TEXT>TEXT |

Returns:

| Name | Type | Description |
| --- | --- | --- |
| `EditMessageResponse` | `` EditMessageResponse (`trueconf.types.responses.edit_message_response.EditMessageResponse`)' href=../Responses/#trueconf.types.responses.EditMessageResponse>EditMessageResponse | Object containing the result of the message update. |

### `` edit_survey `async` ⚓︎

```
edit_survey(message_id, title, survey_campaign_id, survey_type= NON_ANONYMOUS

class-attribute
instance-attribute
(trueconf.enums.survey_type.SurveyType.NON_ANONYMOUS)' href=../Enums/#trueconf.enums.SurveyType.NON_ANONYMOUS>NON_ANONYMOUS)
```

Edits a previously sent survey.

### Source

trueconf.com/docs/chatbot-connector/en/surveys/#editSurvey

Parameters:

| Name | Type | Description | Default |
| --- | --- | --- | --- |
| `message_id` | `str` | Identifier of the message containing the survey to edit. | required |
| `title` | `str` | New title of the survey. | required |
| `survey_campaign_id` | `str` | Identifier of the survey campaign. | required |
| `survey_type` | `` SurveyType (`trueconf.enums.survey_type.SurveyType`)' href=../Enums/#trueconf.enums.SurveyType>SurveyType | Type of the survey (anonymous or non-anonymous). Defaults to non-anonymous. | `` NON_ANONYMOUS

`class-attribute`
`instance-attribute`
(`trueconf.enums.survey_type.SurveyType.NON_ANONYMOUS`)' href=../Enums/#trueconf.enums.SurveyType.NON_ANONYMOUS>NON_ANONYMOUS |

Returns:

| Name | Type | Description |
| --- | --- | --- |
| `EditSurveyResponse` | `` EditSurveyResponse (`trueconf.types.responses.edit_survey_response.EditSurveyResponse`)' href=../Responses/#trueconf.types.responses.EditSurveyResponse>EditSurveyResponse | Object containing the result of the survey update. |

### `` forward_message `async` ⚓︎

```
forward_message(chat_id, message_id)
```

Forwards a message to the specified chat.

### Source

trueconf.com/docs/chatbot-connector/en/messages/#forwardMessage

Parameters:

| Name | Type | Description | Default |
| --- | --- | --- | --- |
| `chat_id` | `str` | Identifier of the chat to forward the message to. | required |
| `message_id` | `str` | Identifier of the message to be forwarded. | required |

Returns:

| Name | Type | Description |
| --- | --- | --- |
| `ForwardMessageResponse` | `` ForwardMessageResponse (`trueconf.types.responses.forward_message_response.ForwardMessageResponse`)' href=../Responses/#trueconf.types.responses.ForwardMessageResponse>ForwardMessageResponse | Object containing the result of the message forwarding. |

### `` from_credentials `classmethod` ⚓︎

```
from_credentials(server, username, password, *, dispatcher=None, receive_unread_messages=False, receive_system_messages=False, verify_ssl=True, web_port=None, https=True, ws_max_retries=5, ws_max_delay=60, debug=False, on_health_check=None)
```

Creates a bot instance using username and password authentication.

### Source

trueconf.com/docs/chatbot-connector/en/connect-and-auth/#connect-and-auth

Parameters:

| Name | Type | Description | Default |
| --- | --- | --- | --- |
| `server` | `str` | Address of the TrueConf server. | required |
| `username` | `str` | Username for authentication. | required |
| `password` | `str` | Password for authentication. | required |
| `*` | | All following arguments must be passed by name (keyword-only). | required |
| `dispatcher` | `` trueconf.Dispatcher (`trueconf.dispatcher.dispatcher.Dispatcher`)' href=../Dispatcher/#trueconf.Dispatcher>Dispatcher | None | Dispatcher instance for registering handlers. | `None` |
| `receive_unread_messages` | `bool` | Whether to receive unread messages on connection. Defaults to False. | `False` |
| `receive_system_messages` | `bool` | Whether to receive system messages, such as user additions to the chat or chat title changes. Defaults to False. | `False` |
| `verify_ssl` | `bool | str | SSLContext` | SSL verification mode. If True, verifies the server certificate using the system trust store when available. If False, disables certificate verification. If a string is provided, it must be a path to a CA bundle file. A custom ssl.SSLContext can also be passed. Defaults to True. | `True` |
| `web_port` | `int` | WebSocket connection port. Defaults to 443. | `None` |
| `https` | `bool` | Whether to use HTTPS protocol. Defaults to True. | `True` |
| `ws_max_retries` | `int` | Max connection attempts on network/IP errors before giving up. Defaults to 5. | `5` |
| `ws_max_delay` | `int` | Maximum delay between reconnection attempts (in seconds). Defaults to 60. | `60` |
| `debug` | `bool` | Enables debug mode. Defaults to False. | `False` |
| `on_health_check` | `HealthCheckCallback | None` | Async callback called when the bot connection health changes. The callback receives a dictionary with the current status, WebSocket state, authorization state, server, port, protocol, timestamp, and optional error details. Defaults to None. | `None` |

Returns:

| Name | Type | Description |
| --- | --- | --- |
| `Bot` | `Self` | An authorized bot instance. |

Raises:

| Type | Description |
| --- | --- |
| `RuntimeError` | If the token could not be obtained. |

### `` get_chat_by_id `async` ⚓︎

```
get_chat_by_id(chat_id)
```

Retrieves information about a chat by its identifier.

### Source

trueconf.com/docs/chatbot-connector/en/chats/#getChatById

Parameters:

| Name | Type | Description | Default |
| --- | --- | --- | --- |
| `chat_id` | `str` | Identifier of the chat. | required |

Returns:

| Name | Type | Description |
| --- | --- | --- |
| `GetChatByIDResponse` | `` GetChatByIdResponse (`trueconf.types.responses.get_chat_by_id_response.GetChatByIdResponse`)' href=../Responses/#trueconf.types.responses.GetChatByIdResponse>GetChatByIdResponse | Object containing information about the chat. |

### `` get_chat_history `async` ⚓︎

```
get_chat_history(chat_id, count, from_message_id=None)
```

Retrieves the message history of the specified chat.

### Source

trueconf.com/docs/chatbot-connector/en/messages/#getChatHistory

Parameters:

| Name | Type | Description | Default |
| --- | --- | --- | --- |
| `chat_id` | `str` | Identifier of the chat. | required |
| `count` | `int` | Number of messages to retrieve. | required |
| `from_message_id` | `str | None` | Identifier of the message to start retrieving history from. If not specified, the history will be loaded from the most recent message. | `None` |

Returns:

| Name | Type | Description |
| --- | --- | --- |
| `GetChatHistoryResponse` | `` GetChatHistoryResponse (`trueconf.types.responses.get_chat_history_response.GetChatHistoryResponse`)' href=../Responses/#trueconf.types.responses.GetChatHistoryResponse>GetChatHistoryResponse | Object containing the result of the chat history request. |

Raises:

| Type | Description |
| --- | --- |
| `ValueError` | If the count number is less than 1. |

### `` get_chat_participant `async` ⚓︎

```
get_chat_participant(chat_id, user_id)
```

Retrieves information about a chat participant.

### Source

trueconf.com/docs/chatbot-connector/en/chats/#getChatParticipant

Parameters:

| Name | Type | Description | Default |
| --- | --- | --- | --- |
| `chat_id` | `str` | Identifier of the chat. | required |
| `user_id` | `str` | Identifier of the user. Can be with or without a domain. | required |

Returns:

| Type | Description |
| --- | --- |
| `GetChatParticipantResponse |` ApiError (`trueconf.types.responses.ApiError`)' href=../Responses/#trueconf.types.responses.ApiError>ApiError | GetChatParticipantResponse | ApiError: Object containing information about the requested |
| `GetChatParticipantResponse |` ApiError (`trueconf.types.responses.ApiError`)' href=../Responses/#trueconf.types.responses.ApiError>ApiError | participant, or an API error if the user is not a participant of the chat. |

### `` get_chat_participants `async` ⚓︎

```
get_chat_participants(chat_id, page_size, page_number)
```

Retrieves a paginated list of chat participants.

### Source

trueconf.com/docs/chatbot-connector/en/chats/#getChatParticipants

Parameters:

| Name | Type | Description | Default |
| --- | --- | --- | --- |
| `chat_id` | `str` | Identifier of the chat. | required |
| `page_size` | `int` | Number of participants per page. | required |
| `page_number` | `int` | Page number. | required |

Returns:

| Name | Type | Description |
| --- | --- | --- |
| `GetChatParticipantsResponse` | `` GetChatParticipantsResponse (`trueconf.types.responses.get_chat_participants_response.GetChatParticipantsResponse`)' href=../Responses/#trueconf.types.responses.GetChatParticipantsResponse>GetChatParticipantsResponse | Object containing the result of the participant list request. |

### `` get_chats `async` ⚓︎

```
get_chats(count=10, page=1)
```

Retrieves a paginated list of chats available to the bot.

### Source

trueconf.com/docs/chatbot-connector/en/chats/#getChats

Parameters:

| Name | Type | Description | Default |
| --- | --- | --- | --- |
| `count` | `int` | Number of chats per page. Defaults to 10. | `10` |
| `page` | `int` | Page number. Must be greater than 0. Defaults to 1. | `1` |

Returns:

| Name | Type | Description |
| --- | --- | --- |
| `GetChatsResponse` | `` GetChatsResponse (`trueconf.types.responses.get_chats_response.GetChatsResponse`)' href=../Responses/#trueconf.types.responses.GetChatsResponse>GetChatsResponse | Object containing the result of the chat list request. |

Raises:

| Type | Description |
| --- | --- |
| `ValueError` | If the page number is less than 1. |

### `` get_file_info `async` ⚓︎

```
get_file_info(file_id)
```

Retrieves information about a file by its identifier.

### Source

trueconf.com/docs/chatbot-connector/en/files/#getFileInfo

Parameters:

| Name | Type | Description | Default |
| --- | --- | --- | --- |
| `file_id` | `str` | Identifier of the file. | required |

Returns:

| Name | Type | Description |
| --- | --- | --- |
| `GetFileInfoResponse` | `` GetFileInfoResponse (`trueconf.types.responses.get_file_info_response.GetFileInfoResponse`)' href=../Responses/#trueconf.types.responses.GetFileInfoResponse>GetFileInfoResponse | Object containing information about the file. |

### `` get_file_info_upload_limits `async` ⚓︎

```
get_file_info_upload_limits()
```

Returns the current file upload limits configured on the TrueConf Server.

Useful for validating outgoing files in advance (e.g., checking maximum file size and allowed types/extensions).

### Notes

Requires TrueConf Server 5.5.3 or later.

### Source

trueconf.com/docs/chatbot-connector/en/files/#getFileUploadLimits

Returns:

| Name | Type | Description |
| --- | --- | --- |
| `GetFileUploadLimitsResponse` | `` GetFileUploadLimitsResponse (`trueconf.types.responses.GetFileUploadLimitsResponse`)' href=../Responses/#trueconf.types.responses.GetFileUploadLimitsResponse>GetFileUploadLimitsResponse | Object describing upload constraints |
| | `` GetFileUploadLimitsResponse (`trueconf.types.responses.GetFileUploadLimitsResponse`)' href=../Responses/#trueconf.types.responses.GetFileUploadLimitsResponse>GetFileUploadLimitsResponse | (e.g., maximum file size, allowed types/extensions). |

### Example

```
limits = await bot.get_file_info_upload_limits()
# Use `limits` fields to validate a file before uploading
```

### `` get_message_by_id `async` ⚓︎

```
get_message_by_id(message_id)
```

Retrieves a message by its identifier.

### Source

trueconf.com/docs/chatbot-connector/en/messages/#getMessageById

Parameters:

| Name | Type | Description | Default |
| --- | --- | --- | --- |
| `message_id` | `str` | Identifier of the message to retrieve. | required |

Returns:

| Name | Type | Description |
| --- | --- | --- |
| `GetMessageByIdResponse` | `` GetMessageByIdResponse (`trueconf.types.responses.get_message_by_id_response.GetMessageByIdResponse`)' href=../Responses/#trueconf.types.responses.GetMessageByIdResponse>GetMessageByIdResponse | Object containing the retrieved message data. |

### `` get_user_display_name `async` ⚓︎

```
get_user_display_name(user_id)
```

Retrieves the display name of a user by their TrueConf ID.

### Source

trueconf.com/docs/chatbot-connector/en/contacts/#getUserDisplayName

Parameters:

| Name | Type | Description | Default |
| --- | --- | --- | --- |
| `user_id` | `str` | User's TrueConf ID. Can be specified with or without a domain. | required |

Returns:

| Name | Type | Description |
| --- | --- | --- |
| `GetUserDisplayNameResponse` | `` GetUserDisplayNameResponse (`trueconf.types.responses.get_user_display_name_response.GetUserDisplayNameResponse`)' href=../Responses/#trueconf.types.responses.GetUserDisplayNameResponse>GetUserDisplayNameResponse | Object containing the user's display name. |

### `` has_chat_participant `async` ⚓︎

```
has_chat_participant(chat_id, user_id)
```

Checks whether the specified user is a participant in the chat.

### Source

trueconf.com/docs/chatbot-connector/en/chats/#hasChatParticipant

Parameters:

| Name | Type | Description | Default |
| --- | --- | --- | --- |
| `chat_id` | `str` | Identifier of the chat. | required |
| `user_id` | `str` | Identifier of the user. Can be with or without a domain. | required |

Returns:

| Name | Type | Description |
| --- | --- | --- |
| `HasChatParticipantResponse` | `` HasChatParticipantResponse (`trueconf.types.responses.has_chat_participant_response.HasChatParticipantResponse`)' href=../Responses/#trueconf.types.responses.HasChatParticipantResponse>HasChatParticipantResponse | Object containing the result of the check. |

### `` health_check ⚓︎

```
health_check()
```

Returns the current bot health status.

This method can be used by external monitoring systems, HTTP health endpoints, or application code that needs to check the current WebSocket and authorization state without waiting for a callback event.

Returns:

| Type | Description |
| --- | --- |
| `Dict[str, Any]` | Dict[str, Any]: Dictionary containing the current status, WebSocket state, authorization state, server, port, protocol, and UTC timestamp. |

### `` me `async` ⚓︎

```
me()
```

Returns the identifier of the bot's personal (Favorites) chat.

If the chat does not exist yet, it will be created automatically. The result is cached to prevent redundant API calls.

Returns:

| Name | Type | Description |
| --- | --- | --- |
| `str` | `str` | Chat ID of the bot's personal Favorites chat. |

### `` me_chat `async` ⚓︎

```
me_chat()
```

Returns the identifier of the bot's personal (Favorites) chat.

If the chat does not exist yet, it will be created automatically. The result is cached to prevent redundant API calls.

Returns:

| Name | Type | Description |
| --- | --- | --- |
| `str` | `str` | Chat ID of the bot's personal Favorites chat. |

### `` remove_message `async` ⚓︎

```
remove_message(message_id, for_all=False)
```

Removes a message by its identifier.

### Source

trueconf.com/docs/chatbot-connector/en/messages/#removeMessage

Parameters:

| Name | Type | Description | Default |
| --- | --- | --- | --- |
| `message_id` | `str` | Identifier of the message to be removed. | required |
| `for_all` | `bool` | If True, the message will be removed for all participants. Default to False (the message is removed only for the bot). | `False` |

Returns:

| Name | Type | Description |
| --- | --- | --- |
| `RemoveMessageResponse` | `` RemoveMessageResponse (`trueconf.types.responses.remove_message_response.RemoveMessageResponse`)' href=../Responses/#trueconf.types.responses.RemoveMessageResponse>RemoveMessageResponse | Object containing the result of the message deletion. |

### `` remove_participant_from_chat `async` ⚓︎

```
remove_participant_from_chat(chat_id, user_id, clear_history=False)
```

Removes a participant from the specified chat.

### Source

trueconf.com/docs/chatbot-connector/en/chats/#removeChatParticipant

Parameters:

| Name | Type | Description | Default |
| --- | --- | --- | --- |
| `chat_id` | `str` | Identifier of the chat to remove the participant from. | required |
| `user_id` | `str` | Identifier of the user to be removed. | required |
| `clear_history` | `bool` | If True, the chat history will be cleared for the removed participant. Defaults to False. | `False` |

Returns:

| Name | Type | Description |
| --- | --- | --- |
| `RemoveChatParticipantResponse` | `` RemoveChatParticipantResponse (`trueconf.types.responses.remove_chat_participant_response.RemoveChatParticipantResponse`)' href=../Responses/#trueconf.types.responses.RemoveChatParticipantResponse>RemoveChatParticipantResponse | Object containing the result of the participant removal. |

### `` reply_message `async` ⚓︎

```
reply_message(chat_id, message_id, text, parse_mode= TEXT

class-attribute
instance-attribute
(trueconf.enums.parse_mode.ParseMode.TEXT)' href=../Enums/#trueconf.enums.ParseMode.TEXT>TEXT)
```

Sends a reply to an existing message in the chat.

### Source

trueconf.com/docs/chatbot-connector/en/messages/#replyMessage

Parameters:

| Name | Type | Description | Default |
| --- | --- | --- | --- |
| `chat_id` | `str` | Identifier of the chat where the reply will be sent. | required |
| `message_id` | `str` | Identifier of the message to reply to. | required |
| `text` | `str` | Text content of the reply. | required |
| `parse_mode` | `` ParseMode (`trueconf.enums.parse_mode.ParseMode`)' href=../Enums/#trueconf.enums.ParseMode>ParseMode | str | Text formatting mode. Defaults to plain text. | `` TEXT

`class-attribute`
`instance-attribute`
(`trueconf.enums.parse_mode.ParseMode.TEXT`)' href=../Enums/#trueconf.enums.ParseMode.TEXT>TEXT |

Returns:

| Name | Type | Description |
| --- | --- | --- |
| `SendMessageResponse` | `` SendMessageResponse (`trueconf.types.responses.send_message_response.SendMessageResponse`)' href=../Responses/#trueconf.types.responses.SendMessageResponse>SendMessageResponse | Object containing the result of the message delivery. |

### `` run `async` ⚓︎

```
run(handle_signals=True)
```

Runs the bot and waits until it stops. Supports handling termination signals (SIGINT, SIGTERM).

Parameters:

| Name | Type | Description | Default |
| --- | --- | --- | --- |
| `handle_signals` | `bool` | Whether to handle termination signals. Defaults to True. | `True` |

Returns:

| Type | Description |
| --- | --- |
| `None` | None |

### `` send_document `async` ⚓︎

```
send_document(chat_id, file, caption=None, parse_mode= TEXT

class-attribute
instance-attribute
(trueconf.enums.parse_mode.ParseMode.TEXT)' href=../Enums/#trueconf.enums.ParseMode.TEXT>TEXT, reply_message_id=None)
```

Sends a document or any arbitrary file to the specified chat.

This method supports all file types, including images. However, images sent via this method will be transferred in original, uncompressed form. If you want to send a compressed image with preview support, use `send_photo()` instead.

The file must be provided as an instance of one of the `InputFile` subclasses: `FSInputFile`, `BufferedInputFile`, or `URLInputFile`.

Parameters:

| Name | Type | Description | Default |
| --- | --- | --- | --- |
| `chat_id` | `str` | The identifier of the chat to which the document will be sent. | required |
| `file` | `` trueconf.types.InputFile (`trueconf.types.input_file.InputFile`)' href=../Types/#trueconf.types.InputFile>InputFile | The file to be uploaded. Must be a subclass of `InputFile`. | required |
| `caption` | `str | None` | Optional caption text to be sent with the file. | `None` |
| `parse_mode` | `` ParseMode (`trueconf.enums.parse_mode.ParseMode`)' href=../Enums/#trueconf.enums.ParseMode>ParseMode | str | Text formatting mode (e.g., Markdown, HTML, or plain text). | `` TEXT

`class-attribute`
`instance-attribute`
(`trueconf.enums.parse_mode.ParseMode.TEXT`)' href=../Enums/#trueconf.enums.ParseMode.TEXT>TEXT |
| `reply_message_id` | `str` | Optional identifier of the message to which this message is a reply. | `None` |

Returns:

| Name | Type | Description |
| --- | --- | --- |
| `SendFileResponse` | `` SendFileResponse (`trueconf.types.responses.send_file_response.SendFileResponse`)' href=../Responses/#trueconf.types.responses.SendFileResponse>SendFileResponse | An object containing the result of the file upload. |

### Example

```
await bot.send_document(
chat_id="a1s2d3f4f5g6",
file=FSInputFile("report.pdf"),
caption="📄 Annual report **for 2025**",
parse_mode=ParseMode.MARKDOWN
)
```

### `` send_message `async` ⚓︎

```
send_message(chat_id, text, parse_mode= TEXT

class-attribute
instance-attribute
(trueconf.enums.parse_mode.ParseMode.TEXT)' href=../Enums/#trueconf.enums.ParseMode.TEXT>TEXT, reply_message_id=None)
```

Sends a message to the specified chat.

### Source

trueconf.com/docs/chatbot-connector/en/messages/#sendMessage

Parameters:

| Name | Type | Description | Default |
| --- | --- | --- | --- |
| `chat_id` | `str` | Identifier of the chat to send the message to. | required |
| `text` | `str` | Text content of the message. | required |
| `parse_mode` | `` ParseMode (`trueconf.enums.parse_mode.ParseMode`)' href=../Enums/#trueconf.enums.ParseMode>ParseMode | str | Text formatting mode. Defaults to plain text. | `` TEXT

`class-attribute`
`instance-attribute`
(`trueconf.enums.parse_mode.ParseMode.TEXT`)' href=../Enums/#trueconf.enums.ParseMode.TEXT>TEXT |
| `reply_message_id` | `str` | Optional identifier of the message to which this message is a reply. | `None` |

Returns:

| Name | Type | Description |
| --- | --- | --- |
| `SendMessageResponse` | `` SendMessageResponse (`trueconf.types.responses.send_message_response.SendMessageResponse`)' href=../Responses/#trueconf.types.responses.SendMessageResponse>SendMessageResponse | Object containing the result of the message delivery. |

### `` send_photo `async` ⚓︎

```
send_photo(chat_id, file, preview, caption=None, parse_mode= TEXT

class-attribute
instance-attribute
(trueconf.enums.parse_mode.ParseMode.TEXT)' href=../Enums/#trueconf.enums.ParseMode.TEXT>TEXT, reply_message_id=None)
```

Sends a photo to the specified chat, with optional caption and preview support.

This method is recommended when sending compressed images with preview support. If you want to send uncompressed images or arbitrary files, use `send_document()` instead.

The file must be provided as an instance of one of the `InputFile` subclasses: `FSInputFile`, `BufferedInputFile`, or `URLInputFile`.

Supported image formats include: `.jpg`, `.jpeg`, `.png`, `.webp`, `.bmp`, `.gif`, `.tiff`

### Source

trueconf.com/docs/chatbot-connector/en/files/#file-transfer

Parameters:

| Name | Type | Description | Default |
| --- | --- | --- | --- |
| `chat_id` | `str` | Identifier of the chat to which the photo will be sent. | required |
| `file` | `` trueconf.types.InputFile (`trueconf.types.input_file.InputFile`)' href=../Types/#trueconf.types.InputFile>InputFile | The photo file to upload. Must be a subclass of `InputFile`. | required |
| `preview` | `` trueconf.types.InputFile (`trueconf.types.input_file.InputFile`)' href=../Types/#trueconf.types.InputFile>InputFile | None | Optional preview image. Must also be an `InputFile` if provided. | required |
| `caption` | `str | None` | Optional caption to be sent along with the image. | `None` |
| `parse_mode` | `` ParseMode (`trueconf.enums.parse_mode.ParseMode`)' href=../Enums/#trueconf.enums.ParseMode>ParseMode | str | Formatting mode for the caption (e.g., Markdown, HTML, plain text). | `` TEXT

`class-attribute`
`instance-attribute`
(`trueconf.enums.parse_mode.ParseMode.TEXT`)' href=../Enums/#trueconf.enums.ParseMode.TEXT>TEXT |
| `reply_message_id` | `str` | Optional identifier of the message to which this message is a reply. | `None` |

Returns:

| Name | Type | Description |
| --- | --- | --- |
| `SendFileResponse` | `` SendFileResponse (`trueconf.types.responses.send_file_response.SendFileResponse`)' href=../Responses/#trueconf.types.responses.SendFileResponse>SendFileResponse | An object containing the result of the file upload. |

### Example

```
await bot.send_photo(
chat_id="a1s2d3f4f5g6",
file=FSInputFile("image.jpg"),
preview=FSInputFile("image_preview.webp"),
caption="Here's our **team** photo 📸",
parse_mode=ParseMode.MARKDOWN
)
```

### `` send_sticker `async` ⚓︎

```
send_sticker(chat_id, file, reply_message_id=None)
```

Sends a sticker in WebP format to the specified chat.

The file must have a MIME type of `'image/webp'`, otherwise a `TypeError` will be raised. The file must be an instance of one of the `InputFile` subclasses: `FSInputFile`, `BufferedInputFile`, or `URLInputFile`.

A preview is automatically generated from the source file, as required for sticker uploads in TrueConf.

### Source

trueconf.com/docs/chatbot-connector/en/files/#file-transfer

Parameters:

| Name | Type | Description | Default |
| --- | --- | --- | --- |
| `chat_id` | `str` | Identifier of the chat to which the sticker will be sent. | required |
| `file` | `` trueconf.types.InputFile (`trueconf.types.input_file.InputFile`)' href=../Types/#trueconf.types.InputFile>InputFile | The sticker file in WebP format. Must be a subclass of `InputFile`. | required |
| `reply_message_id` | `str` | Optional identifier of the message to which this message is a reply. | `None` |

Returns:

| Name | Type | Description |
| --- | --- | --- |
| `SendFileResponse` | `` SendFileResponse (`trueconf.types.responses.send_file_response.SendFileResponse`)' href=../Responses/#trueconf.types.responses.SendFileResponse>SendFileResponse | An object containing the result of the file upload. |

Raises:

| Type | Description |
| --- | --- |
| `TypeError` | If the file's MIME type is not `'image/webp'`. |

### Example

```
await bot.send_sticker(chat_id="user123", file=FSInputFile("sticker.webp"))
```

### `` send_survey `async` ⚓︎

```
send_survey(chat_id, title, survey_campaign_id, reply_message_id=None, survey_type= NON_ANONYMOUS

class-attribute
instance-attribute
(trueconf.enums.survey_type.SurveyType.NON_ANONYMOUS)' href=../Enums/#trueconf.enums.SurveyType.NON_ANONYMOUS>NON_ANONYMOUS)
```

Sends a survey to the specified chat.

### Source

trueconf.com/docs/chatbot-connector/en/surveys/#sendSurvey

Parameters:

| Name | Type | Description | Default |
| --- | --- | --- | --- |
| `chat_id` | `str` | Identifier of the chat to send the survey to. | required |
| `title` | `str` | Title of the survey displayed in the chat. | required |
| `survey_campaign_id` | `str` | Identifier of the survey campaign. | required |
| `reply_message_id` | `str` | Optional identifier of the message to which this message is a reply. | `None` |
| `survey_type` | `` SurveyType (`trueconf.enums.survey_type.SurveyType`)' href=../Enums/#trueconf.enums.SurveyType>SurveyType | Type of the survey (anonymous or non-anonymous). Defaults to non-anonymous. | `` NON_ANONYMOUS

`class-attribute`
`instance-attribute`
(`trueconf.enums.survey_type.SurveyType.NON_ANONYMOUS`)' href=../Enums/#trueconf.enums.SurveyType.NON_ANONYMOUS>NON_ANONYMOUS |

Returns:

| Name | Type | Description |
| --- | --- | --- |
| `SendSurveyResponse` | `` SendSurveyResponse (`trueconf.types.responses.send_survey_response.SendSurveyResponse`)' href=../Responses/#trueconf.types.responses.SendSurveyResponse>SendSurveyResponse | Object containing the result of the survey submission. |

### `` server_name `async` ⚓︎

```
server_name()
```

Returns the domain name of the TrueConf server.

Returns:

| Name | Type | Description |
| --- | --- | --- |
| `str` | `str` | Domain name of the connected server. |

### `` server_version `async` ⚓︎

```
server_version()
```

Returns the domain name of the TrueConf server.

Returns:

| Name | Type | Description |
| --- | --- | --- |
| `str` | `str` | Domain name of the connected server. |

### `` shutdown `async` ⚓︎

```
shutdown()
```

Gracefully shuts down the bot, cancels the connection task, and closes active sessions.

This method:

- Cancels the connection task if it is still active;

- Closes the WebSocket session or `self.session` if they are open;

- Clears the connection and authorization events;

- Sets the `stopped_event` flag.

Returns:

| Type | Description |
| --- | --- |
| `None` | None |

### `` start `async` ⚓︎

```
start()
```

Starts the bot by connecting to the server and listening for incoming events.

### Note

This method is safe to call multiple times — subsequent calls are ignored if the connection is already active.

Returns:

| Type | Description |
| --- | --- |
| `None` | None |

### `` subscribe_file_progress `async` ⚓︎

```
subscribe_file_progress(file_id)
```

Subscribes to file transfer progress updates.

### Source

trueconf.com/docs/chatbot-connector/en/files/#subscribeFileProgress

Parameters:

| Name | Type | Description | Default |
| --- | --- | --- | --- |
| `file_id` | `str` | Identifier of the file. | required |

Returns:

| Name | Type | Description |
| --- | --- | --- |
| `SubscribeFileProgressResponse` | `` SubscribeFileProgressResponse (`trueconf.types.responses.subscribe_file_progress_response.SubscribeFileProgressResponse`)' href=../Responses/#trueconf.types.responses.SubscribeFileProgressResponse>SubscribeFileProgressResponse | Object containing the result of the subscription. |

### Note

If the file is in the UPLOADING status, you can subscribe to the upload process to be notified when the file becomes available.

### `` unsubscribe_file_progress `async` ⚓︎

```
unsubscribe_file_progress(file_id)
```

Unsubscribes from receiving file upload progress events.

### Source

trueconf.com/docs/chatbot-connector/en/files/#unsubscribeFileProgress

Parameters:

| Name | Type | Description | Default |
| --- | --- | --- | --- |
| `file_id` | `str` | Identifier of the file. | required |

Returns:

| Name | Type | Description |
| --- | --- | --- |
| `UnsubscribeFileProgressResponse` | `` UnsubscribeFileProgressResponse (`trueconf.types.responses.unsubscribe_file_progress_response.UnsubscribeFileProgressResponse`)' href=../Responses/#trueconf.types.responses.UnsubscribeFileProgressResponse>UnsubscribeFileProgressResponse | Object containing the result of the unsubscription. |

### Note

If necessary, you can unsubscribe from file upload events that were previously subscribed to using the `subscribe_file_progress()` method.
