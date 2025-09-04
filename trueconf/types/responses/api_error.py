from __future__ import annotations
from dataclasses import dataclass, field
from mashumaro import DataClassDictMixin


@dataclass
class ApiError(DataClassDictMixin):
    error_code: int = field(metadata={"alias": "errorCode"})

    _error_messages = {
        # Network Errors
        100: "Connection error",
        101: "Connection timeout",
        102: "TLS/SSL error",
        103: "Unsupported protocol",
        104: "Route not found",

        # Authorization Errors
        200: "Not authorized",
        201: "Invalid credentials",
        202: "User disabled",
        203: "Credentials expired",

        # Chat Errors
        300: "Internal server error",
        301: "Operation timeout",
        302: "Access denied",
        303: "Not enough rights",
        304: "Chat not found",
        305: "User is not a chat participant",
        306: "Message not found",
        307: "Unknown message",
        308: "File not found",
        309: "User already in chat",
    }

    def __str__(self):
        return f"[{self.error_code}] {self._error_messages.get(self.error_code, 'Unknown error')}"
