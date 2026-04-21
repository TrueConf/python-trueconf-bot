


class TrueConfChatBotError(Exception):
    """
    Base exception for all TrueConf ChatBot Connector errors.
    """

class TokenValidationError(TrueConfChatBotError):
    pass

class InvalidGrantError(TrueConfChatBotError):
    pass

class LimitExceededError(TrueConfChatBotError):
    """Base exception for all limit-related errors (length, size, etc.)."""
    def __init__(self, message: str, actual_value: int, limit: int):
        super().__init__(message)
        self.actual_value = actual_value
        self.limit = limit


class TextMessageTooLongError(LimitExceededError):
    """Raised when the message text exceeds TrueConf's allowed length."""
    def __init__(self, actual_length: int, limit: int = 4096):
        message = (
            f"Bad Request: text message is too long. "
            f"Maximum allowed length is {limit} characters, but got {actual_length}. "
            f"Tip: use 'safe_split_text(text=text)' (from trueconf.utils import safe_split_text) to split your message."
        )
        super().__init__(message, actual_length, limit)

class FileCaptionTooLongError(LimitExceededError):
    """Raised when the caption exceeds TrueConf's allowed length."""
    def __init__(self, actual_length: int, limit: int = 4096):
        message = (
            f"Bad Request: caption is too long. "
            f"Maximum allowed length is {limit} characters, but got {actual_length}. "
            f"Tip: use 'safe_split_text(text=caption)' (from trueconf.utils import safe_split_text) to split your message."
        )
        super().__init__(message, actual_length, limit)

class ChatTitleTooLongError(LimitExceededError):
    """Base error for long chat titles."""
    pass

class GroupTitleTooLongError(ChatTitleTooLongError):
    """Raised when the group title exceeds allowed length."""
    def __init__(self, actual_length: int, limit: int = 256):
        message = (
            f"Bad Request: group title is too long. "
            f"Maximum allowed length is {limit} characters, but got {actual_length}."
        )
        super().__init__(message, actual_length, limit)

class ChannelTitleTooLongError(ChatTitleTooLongError):
    """Raised when the channel title exceeds allowed length."""
    def __init__(self, actual_length: int, limit: int = 256):
        message = (
            f"Bad Request: channel title is too long. "
            f"Maximum allowed length is {limit} characters, but got {actual_length}."
        )
        super().__init__(message, actual_length, limit)

class FileValidationError(TrueConfChatBotError):
    """Общий класс для всех ошибок валидации файлов."""
    pass

class FileSizeTooLargeError(FileValidationError, LimitExceededError):
    def __init__(self, actual_size: int, limit: int):
        actual_mb = round(actual_size / (1024 * 1024), 2)
        limit_mb = round(limit / (1024 * 1024), 2)
        message = (
            f"Bad Request: file is too large. "
            f"Maximum allowed size is {limit_mb}MB, but got {actual_mb}MB."
        )
        super().__init__(message, actual_size, limit)


class InvalidFileExtensionError(FileValidationError):
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
    def __init__(self, code: int, detail: str, payload: dict | None = None):
        super().__init__(f"[{code}] {detail}")
        self.code = code
        self.detail = detail
        self.payload = payload or {}