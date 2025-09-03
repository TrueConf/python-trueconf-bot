


class TrueConfChatBotError(Exception):
    """
    Base exception for all TrueConf ChatBot Connector errors.
    """

class TokenValidationError(TrueConfChatBotError):
    pass

class InvalidGrantError(TrueConfChatBotError):
    pass


class ApiError(TrueConfChatBotError):
    pass