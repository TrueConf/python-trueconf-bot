from urllib.parse import urlsplit, urlunsplit


def _sanitize_url_for_log(url: str | None) -> str:
    """Strip query string and fragment from a URL before it is written to logs."""
    if not url:
        return ""
    return urlunsplit(urlsplit(url)._replace(query="", fragment=""))
