from enum import Enum


class CommandAnswerType(str, Enum):
    COMPLETE = "complete"
    TIMEOUT = "timeout"
    CANCEL = "cancel"
    MESSAGE = "message"


class CommandMessageStatus(str, Enum):
    UNKNOWN = "unknown"
    PENDING = "pending"
    RUNNING = "running"
    OK = "ok"
    FAILED = "failed"
    CANCELED = "canceled"
    TIMEOUT = "timeout"


class CommandMessageVisibility(str, Enum):
    DEFAULT = "default"
    TOAST = "toast"
    STICKY = "sticky"
    ALERT = "alert"


class CommandMessageLevel(str, Enum):
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"
