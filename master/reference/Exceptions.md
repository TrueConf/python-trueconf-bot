# Exceptions

## `` trueconf.exceptions ⚓︎

### `` ApiErrorException ⚓︎

```
ApiErrorException(code, detail, payload=None)
```

Raised when TrueConf Server returns an API error response.

This exception stores the server error code, human-readable detail, and optional response payload for additional context.

Attributes:

| Name | Type | Description |
| --- | --- | --- |
| `` code

`instance-attribute`
(`trueconf.exceptions.ApiErrorException.code`)' href=#trueconf.exceptions.ApiErrorException.code>code | | Error code returned by the server. |
| `` detail

`instance-attribute`
(`trueconf.exceptions.ApiErrorException.detail`)' href=#trueconf.exceptions.ApiErrorException.detail>detail | | Human-readable error description. |
| `` payload

`instance-attribute`
(`trueconf.exceptions.ApiErrorException.payload`)' href=#trueconf.exceptions.ApiErrorException.payload>payload | | Raw error payload returned by the server, or an empty dict. |

#### `` code `instance-attribute` ⚓︎

```
code = code
```

#### `` detail `instance-attribute` ⚓︎

```
detail = detail
```

#### `` payload `instance-attribute` ⚓︎

```
payload = payload or {}
```

### `` ChannelTitleTooLongError ⚓︎

```
ChannelTitleTooLongError(actual_length, limit=256)
```

Raised when a channel title exceeds the maximum allowed length.

Attributes:

| Name | Type | Description |
| --- | --- | --- |
| `` actual_value

`instance-attribute`
(`trueconf.exceptions.ChannelTitleTooLongError.actual_value`)' href=#trueconf.exceptions.ChannelTitleTooLongError.actual_value>actual_value | | Actual length of the channel title. |
| `` limit

`instance-attribute`
(`trueconf.exceptions.ChannelTitleTooLongError.limit`)' href=#trueconf.exceptions.ChannelTitleTooLongError.limit>limit | | Maximum allowed channel title length. |

#### `` actual_value `instance-attribute` ⚓︎

```
actual_value = actual_value
```

#### `` limit `instance-attribute` ⚓︎

```
limit = limit
```

### `` ChatTitleTooLongError ⚓︎

```
ChatTitleTooLongError(message, actual_value, limit)
```

Base exception for chat title length errors.

This class is inherited by more specific exceptions for group and channel title length validation.

#### `` actual_value `instance-attribute` ⚓︎

```
actual_value = actual_value
```

#### `` limit `instance-attribute` ⚓︎

```
limit = limit
```

### `` FileCaptionTooLongError ⚓︎

```
FileCaptionTooLongError(actual_length, limit=4096)
```

Raised when a file caption exceeds the maximum allowed length.

The default caption limit is 4096 visible characters. For long captions, use `safe_split_text` from `trueconf.utils` and send the returned chunks separately when appropriate.

Attributes:

| Name | Type | Description |
| --- | --- | --- |
| `` actual_value

`instance-attribute`
(`trueconf.exceptions.FileCaptionTooLongError.actual_value`)' href=#trueconf.exceptions.FileCaptionTooLongError.actual_value>actual_value | | Actual visible length of the caption. |
| `` limit

`instance-attribute`
(`trueconf.exceptions.FileCaptionTooLongError.limit`)' href=#trueconf.exceptions.FileCaptionTooLongError.limit>limit | | Maximum allowed caption length. |

#### `` actual_value `instance-attribute` ⚓︎

```
actual_value = actual_value
```

#### `` limit `instance-attribute` ⚓︎

```
limit = limit
```

### `` FileSizeTooLargeError ⚓︎

```
FileSizeTooLargeError(actual_size, limit)
```

Raised when a file exceeds the maximum size allowed by the server.

File size limits are configured by the TrueConf Server administrator and are checked by the bot before sending a file.

Attributes:

| Name | Type | Description |
| --- | --- | --- |
| `` actual_value

`instance-attribute`
(`trueconf.exceptions.FileSizeTooLargeError.actual_value`)' href=#trueconf.exceptions.FileSizeTooLargeError.actual_value>actual_value | | Actual file size in bytes. |
| `` limit

`instance-attribute`
(`trueconf.exceptions.FileSizeTooLargeError.limit`)' href=#trueconf.exceptions.FileSizeTooLargeError.limit>limit | | Maximum allowed file size in bytes. |

#### `` actual_value `instance-attribute` ⚓︎

```
actual_value = actual_value
```

#### `` limit `instance-attribute` ⚓︎

```
limit = limit
```

### `` FileValidationError ⚓︎

Base exception for file validation errors.

This class is used for errors related to file size limits, extension filters, and other file validation rules received from TrueConf Server.

### `` GroupTitleTooLongError ⚓︎

```
GroupTitleTooLongError(actual_length, limit=256)
```

Raised when a group title exceeds the maximum allowed length.

Attributes:

| Name | Type | Description |
| --- | --- | --- |
| `` actual_value

`instance-attribute`
(`trueconf.exceptions.GroupTitleTooLongError.actual_value`)' href=#trueconf.exceptions.GroupTitleTooLongError.actual_value>actual_value | | Actual length of the group title. |
| `` limit

`instance-attribute`
(`trueconf.exceptions.GroupTitleTooLongError.limit`)' href=#trueconf.exceptions.GroupTitleTooLongError.limit>limit | | Maximum allowed group title length. |

#### `` actual_value `instance-attribute` ⚓︎

```
actual_value = actual_value
```

#### `` limit `instance-attribute` ⚓︎

```
limit = limit
```

### `` InvalidFileExtensionError ⚓︎

```
InvalidFileExtensionError(extension, extensions=None, mode='allow')
```

Raised when a file extension does not satisfy the server extension filter.

File extension rules are configured by the TrueConf Server administrator. Depending on the filter mode, the extension list can work either as an allow list or as a block list.

Attributes:

| Name | Type | Description |
| --- | --- | --- |
| `` extension

`instance-attribute`
(`trueconf.exceptions.InvalidFileExtensionError.extension`)' href=#trueconf.exceptions.InvalidFileExtensionError.extension>extension | | File extension that failed validation. |
| `` extensions

`instance-attribute`
(`trueconf.exceptions.InvalidFileExtensionError.extensions`)' href=#trueconf.exceptions.InvalidFileExtensionError.extensions>extensions | | Set of extensions used for validation. |
| `` mode

`instance-attribute`
(`trueconf.exceptions.InvalidFileExtensionError.mode`)' href=#trueconf.exceptions.InvalidFileExtensionError.mode>mode | | Extension filter mode. |

#### `` extension `instance-attribute` ⚓︎

```
extension = extension
```

#### `` extensions `instance-attribute` ⚓︎

```
extensions = extensions or set()
```

#### `` mode `instance-attribute` ⚓︎

```
mode = mode
```

### `` InvalidGrantError ⚓︎

Raised when the server rejects the provided authorization grant.

This usually means that the token or credentials are invalid, expired, revoked, or cannot be used to authorize the bot.

### `` LimitExceededError ⚓︎

```
LimitExceededError(message, actual_value, limit)
```

Base exception for all limit-related errors.

This class is used for errors related to text length, title length, file size, and other numeric limits.

Attributes:

| Name | Type | Description |
| --- | --- | --- |
| `` actual_value

`instance-attribute`
(`trueconf.exceptions.LimitExceededError.actual_value`)' href=#trueconf.exceptions.LimitExceededError.actual_value>actual_value | | Actual value that exceeded the limit. |
| `` limit

`instance-attribute`
(`trueconf.exceptions.LimitExceededError.limit`)' href=#trueconf.exceptions.LimitExceededError.limit>limit | | Maximum allowed value. |

#### `` actual_value `instance-attribute` ⚓︎

```
actual_value = actual_value
```

#### `` limit `instance-attribute` ⚓︎

```
limit = limit
```

### `` TextMessageTooLongError ⚓︎

```
TextMessageTooLongError(actual_length, limit=4096)
```

Raised when a text message exceeds the maximum allowed length.

The default text message limit is 4096 visible characters. For long texts, such as LLM-generated responses, use `safe_split_text` from `trueconf.utils` and send the returned chunks one by one.

Attributes:

| Name | Type | Description |
| --- | --- | --- |
| `` actual_value

`instance-attribute`
(`trueconf.exceptions.TextMessageTooLongError.actual_value`)' href=#trueconf.exceptions.TextMessageTooLongError.actual_value>actual_value | | Actual visible length of the message text. |
| `` limit

`instance-attribute`
(`trueconf.exceptions.TextMessageTooLongError.limit`)' href=#trueconf.exceptions.TextMessageTooLongError.limit>limit | | Maximum allowed message length. |

#### `` actual_value `instance-attribute` ⚓︎

```
actual_value = actual_value
```

#### `` limit `instance-attribute` ⚓︎

```
limit = limit
```

### `` TokenValidationError ⚓︎

Raised when the bot token fails local validation.

This error indicates that the token value has an invalid format or cannot be used by the connector before the authorization request is sent.

### `` TrueConfChatBotError ⚓︎

Base exception for all TrueConf ChatBot Connector errors.

All custom exceptions raised by the library inherit from this class. You can catch this exception to handle any library-specific error in a single place.

June 30, 2026

May 5, 2026
