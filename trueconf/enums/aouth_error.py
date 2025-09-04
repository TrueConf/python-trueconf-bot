from enum import Enum


class OAuthError(str, Enum):
    """
    Error codes, according to the OAuth 2.0 specification, are presented as ASCII strings from the list specified in the specification.

    Source:
        https://trueconf.com/docs/chatbot-connector/en/objects/#oauth-error
    """

    INVALID_REQUEST = "invalid_request"
    INVALID_CLIENT = "invalid_client"
    INVALID_GRANT = "invalid_grant"
    UNSUPORTED_GRANT_TYPE = "unsupported_grant_type"
