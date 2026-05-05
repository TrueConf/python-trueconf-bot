class TrueConfChatBotError(Exception):
    """
    Base exception for all TrueConf ChatBot Connector errors.

    All custom exceptions raised by the library inherit from this class.
    You can catch this exception to handle any library-specific error in a
    single place.
    """

class TokenValidationError(TrueConfChatBotError):
    """
    Raised when the bot token fails local validation.

    This error indicates that the token value has an invalid format or
    cannot be used by the connector before the authorization request is sent.
    """
    pass

class InvalidGrantError(TrueConfChatBotError):
    """
    Raised when the server rejects the provided authorization grant.

    This usually means that the token or credentials are invalid, expired,
    revoked, or cannot be used to authorize the bot.
    """
    pass

class LimitExceededError(TrueConfChatBotError):
    """
    Base exception for all limit-related errors.

    This class is used for errors related to text length, title length,
    file size, and other numeric limits.

    Attributes:
        actual_value: Actual value that exceeded the limit.
        limit: Maximum allowed value.
    """
    def __init__(self, message: str, actual_value: int, limit: int):
        super().__init__(message)
        self.actual_value = actual_value
        self.limit = limit


class TextMessageTooLongError(LimitExceededError):
    """
    Raised when a text message exceeds the maximum allowed length.

    The default text message limit is 4096 visible characters. For long texts,
    such as LLM-generated responses, use `safe_split_text` from `trueconf.utils`
    and send the returned chunks one by one.

    Attributes:
        actual_value: Actual visible length of the message text.
        limit: Maximum allowed message length.
    """
    def __init__(self, actual_length: int, limit: int = 4096):
        message = (
            f"Bad Request: text message is too long. "
            f"Maximum allowed length is {limit} characters, but got {actual_length}. "
            f"Tip: use 'safe_split_text(text=text)' (from trueconf.utils import safe_split_text) to split your message."
        )
        super().__init__(message, actual_length, limit)

class FileCaptionTooLongError(LimitExceededError):
    """
    Raised when a file caption exceeds the maximum allowed length.

    The default caption limit is 4096 visible characters. For long captions,
    use `safe_split_text` from `trueconf.utils` and send the returned chunks
    separately when appropriate.

    Attributes:
        actual_value: Actual visible length of the caption.
        limit: Maximum allowed caption length.
    """
    def __init__(self, actual_length: int, limit: int = 4096):
        message = (
            f"Bad Request: caption is too long. "
            f"Maximum allowed length is {limit} characters, but got {actual_length}. "
            f"Tip: use 'safe_split_text(text=caption)' (from trueconf.utils import safe_split_text) to split your message."
        )
        super().__init__(message, actual_length, limit)

class ChatTitleTooLongError(LimitExceededError):
    """
    Base exception for chat title length errors.

    This class is inherited by more specific exceptions for group and channel
    title length validation.
    """
    pass

class GroupTitleTooLongError(ChatTitleTooLongError):
    """
    Raised when a group title exceeds the maximum allowed length.

    Attributes:
        actual_value: Actual length of the group title.
        limit: Maximum allowed group title length.
    """
    def __init__(self, actual_length: int, limit: int = 256):
        message = (
            f"Bad Request: group title is too long. "
            f"Maximum allowed length is {limit} characters, but got {actual_length}."
        )
        super().__init__(message, actual_length, limit)

class ChannelTitleTooLongError(ChatTitleTooLongError):
    """
    Raised when a channel title exceeds the maximum allowed length.

    Attributes:
        actual_value: Actual length of the channel title.
        limit: Maximum allowed channel title length.
    """
    def __init__(self, actual_length: int, limit: int = 256):
        message = (
            f"Bad Request: channel title is too long. "
            f"Maximum allowed length is {limit} characters, but got {actual_length}."
        )
        super().__init__(message, actual_length, limit)

class FileValidationError(TrueConfChatBotError):
    """
    Base exception for file validation errors.

    This class is used for errors related to file size limits, extension filters,
    and other file validation rules received from TrueConf Server.
    """
    pass

class FileSizeTooLargeError(FileValidationError, LimitExceededError):
    """
    Raised when a file exceeds the maximum size allowed by the server.

    File size limits are configured by the TrueConf Server administrator and
    are checked by the bot before sending a file.

    Attributes:
        actual_value: Actual file size in bytes.
        limit: Maximum allowed file size in bytes.
    """
    def __init__(self, actual_size: int, limit: int):
        actual_mb = round(actual_size / (1024 * 1024), 2)
        limit_mb = round(limit / (1024 * 1024), 2)
        message = (
            f"Bad Request: file is too large. "
            f"Maximum allowed size is {limit_mb}MB, but got {actual_mb}MB."
        )
        super().__init__(message, actual_size, limit)


class InvalidFileExtensionError(FileValidationError):
    """
    Raised when a file extension does not satisfy the server extension filter.

    File extension rules are configured by the TrueConf Server administrator.
    Depending on the filter mode, the extension list can work either as an
    allow list or as a block list.

    Attributes:
        extension: File extension that failed validation.
        extensions: Set of extensions used for validation.
        mode: Extension filter mode.
    """
    def __init__(self, extension: str, extensions: set[str] | None = None, mode: str = "allow"):
        self.extension = extension
        self.extensions = extensions or set()
        self.mode = mode

        formatted_exts = ", ".join(sorted(self.extensions))

        if mode == "allow":
            if self.extensions:
                message = (
                    f"Bad Request: extension '.{extension}' is not allowed. "
                    f"Allowed extensions: {formatted_exts}"
                )
            else:
                message = f"Bad Request: extension '.{extension}' is not in the allowed list."

        else:  # mode == "block"
            if self.extensions:
                message = (
                    f"Bad Request: extension '.{extension}' is blacklisted. "
                    f"Blocked extensions: {formatted_exts}"
                )
            else:
                message = f"Bad Request: extension '.{extension}' is blocked."

        super().__init__(message)

class ApiErrorException(TrueConfChatBotError):
    """
    Raised when TrueConf Server returns an API error response.

    This exception stores the server error code, human-readable detail, and
    optional response payload for additional context.

    Attributes:
        code: Error code returned by the server.
        detail: Human-readable error description.
        payload: Raw error payload returned by the server, or an empty dict.
    """
    def __init__(self, code: int, detail: str, payload: dict | None = None):
        super().__init__(f"[{code}] {detail}")
        self.code = code
        self.detail = detail
        self.payload = payload or {}