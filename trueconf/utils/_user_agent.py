from __future__ import annotations

import platform
from functools import lru_cache
from importlib import metadata

_PACKAGE_NAME = "python-trueconf-bot"


def _library_version() -> str:
    try:
        return metadata.version(_PACKAGE_NAME)
    except metadata.PackageNotFoundError:
        from trueconf._version import __version__

        return __version__


@lru_cache(maxsize=1)
def get_user_agent() -> str:
    """
    Returns the custom User-Agent used by every library HTTP/WebSocket request.

    Format:
        ``python-trueconf-bot/<version> (Python/<version>; <OS>/<release>)``

    The library version comes from the installed package metadata and falls
    back to the generated ``trueconf._version`` when running from sources.
    The string is built once and cached.
    """
    details = [f"Python/{platform.python_version()}"]
    system = platform.system()
    release = platform.release()
    if system and release:
        details.append(f"{system}/{release}")
    return f"python-trueconf-bot/{_library_version()} ({'; '.join(details)})"
