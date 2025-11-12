


class TrueConfChatBotError(Exception):
    """
    Base exception for all TrueConf ChatBot Connector errors.
    """

class TokenValidationError(TrueConfChatBotError):
    pass

class InvalidGrantError(TrueConfChatBotError):
    pass


class ApiErrorException(TrueConfChatBotError):
    def __init__(self, code: int, detail: str, payload: dict | None = None):
        super().__init__(f"[{code}] {detail}")
        self.code = code
        self.detail = detail
        self.payload = payload or {}