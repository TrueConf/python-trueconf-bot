import ssl
from pathlib import Path
from typing import TypeAlias
import truststore

SSLVerify: TypeAlias = bool | str | ssl.SSLContext

def _build_ssl_context(verify_ssl: SSLVerify) -> ssl.SSLContext:
    if isinstance(verify_ssl, ssl.SSLContext):
        return verify_ssl

    if verify_ssl is False:
        ctx = ssl.create_default_context()
        ctx.check_hostname = False
        ctx.verify_mode = ssl.CERT_NONE
        return ctx

    if verify_ssl is True:
        return truststore.SSLContext(ssl.PROTOCOL_TLS_CLIENT)

    if isinstance(verify_ssl, str):
        cafile = Path(verify_ssl).expanduser()
        if not cafile.is_file():
            raise FileNotFoundError(
                f"SSL CA bundle file not found: {cafile}. "
                "Pass verify_ssl=True to use the system trust store, "
                "verify_ssl=False to disable verification, or provide a valid path to a CA bundle."
            )
        return ssl.create_default_context(cafile=str(cafile))

    raise TypeError(
        "verify_ssl must be bool, str path to CA bundle, or ssl.SSLContext"
    )

def _describe_ssl_context(ctx: ssl.SSLContext) -> str:
    if ctx.verify_mode == ssl.CERT_NONE:
        return "disabled"

    return (
        f"enabled "
        f"(context={type(ctx).__module__}.{type(ctx).__name__}, "
        f"verify_mode={ctx.verify_mode.name}, "
        f"check_hostname={ctx.check_hostname})"
    )