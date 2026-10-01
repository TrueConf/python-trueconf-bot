from __future__ import annotations

import re
from dataclasses import dataclass

# Joins folded lines: a continuation line starts with a space or a tab.
_UNFOLD_RE = re.compile(r"\r?\n[ \t]")

# Property line: NAME;PARAM=VAL;PARAM:VALUE. The exact name is captured so that
# e.g. "N" is never confused with "NICKNAME"; everything after the first colon
# is the value (it may itself contain colons).
_PROP_RE = re.compile(r"^([A-Z0-9-]+)((?:;[^:]*)*):(.*)$", re.MULTILINE | re.IGNORECASE)

# vCard escape sequences: \\ \; \, \n \N
_ESCAPE_RE = re.compile(r"\\([\\;,nN])")

# Quoted-printable: "=XX" is a byte; anything else is kept verbatim.
_QP_RE = re.compile(r"=([0-9A-Fa-f]{2})|(.)", re.DOTALL)


def _unescape(value: str) -> str:
    """Unescape vCard sequences (``\\\\``, ``\\;``, ``\\,``, ``\\n``, ``\\N``)."""
    return _ESCAPE_RE.sub(lambda m: "\n" if m.group(1) in "nN" else m.group(1), value)


def _decode_quoted_printable(value: str, charset: str | None = None) -> str:
    """Best-effort quoted-printable decoding for vCard 2.1 values."""
    raw = _QP_RE.sub(
        lambda m: bytes.fromhex(m.group(1)).decode("latin1") if m.group(1) else m.group(2),
        value,
    )
    try:
        return raw.encode("latin1").decode(charset or "utf-8", errors="replace")
    except (UnicodeEncodeError, LookupError):
        return raw


def _split_unescaped(value: str, sep: str = ";") -> list[str]:
    """Split on ``sep``, ignoring escaped occurrences (e.g. ``\\;`` in a component)."""
    parts: list[str] = []
    current: list[str] = []
    i = 0
    while i < len(value):
        if value[i] == "\\" and i + 1 < len(value):
            current.append(value[i : i + 2])
            i += 2
        elif value[i] == sep:
            parts.append("".join(current))
            current = []
            i += 1
        else:
            current.append(value[i])
            i += 1
    parts.append("".join(current))
    return parts


def _parse_params(params: str) -> dict[str, str]:
    """Parse the ``;PARAM=VAL;PARAM`` segment of a property line."""
    result: dict[str, str] = {}
    for item in params.split(";"):
        item = item.strip()
        if not item:
            continue
        if "=" in item:
            key, _, value = item.partition("=")
            result[key.upper()] = value
        else:
            result[item.upper()] = ""
    return result


def _is_quoted_printable(params: dict[str, str]) -> bool:
    """True when the property is quoted-printable encoded (vCard 2.1)."""
    return "QUOTED-PRINTABLE" in params or params.get("ENCODING", "").upper() == "QUOTED-PRINTABLE"


def _decode_value(params: dict[str, str], value: str) -> str:
    """Unescape a value and apply quoted-printable decoding when requested."""
    value = _unescape(value)
    if _is_quoted_printable(params):
        value = _decode_quoted_printable(value, params.get("CHARSET"))
    return value


@dataclass
class Contact:
    """
    Represents a contact parsed from a vCard file or a TrueConf contact link.

    Mirrors the Telegram/aiogram ``Contact`` shape. A vCard attachment provides
    a structured name (``N``), a phone number (``TEL``) and the raw vCard text;
    a TrueConf contact link (``<a href="trueconf:login&do=profile">``) provides
    a user id and a display name.

    Attributes:
        phone_number (str | None): Phone number parsed from the vCard ``TEL``
            field. Always ``None`` for TrueConf contacts (no phone in the API).
        first_name (str): Given name for vCards (from ``N``/``FN``). For
            TrueConf contacts it holds the whole display name: the server-side
            name convention (ФИ/ИФ/ФИО) varies, so it is never split.
        last_name (str | None): Family name parsed from the structured vCard
            ``N`` field. Always ``None`` for TrueConf contacts and for vCards
            that lack ``N``.
        user_id (str | None): TrueConf user id (e.g. ``ai-bot@domain``) for
            TrueConf contacts; ``None`` for vCards.
        vcard (str | None): Raw vCard text for vCard files; ``None`` otherwise.
    """

    phone_number: str | None = None
    first_name: str = ""
    last_name: str | None = None
    user_id: str | None = None
    vcard: str | None = None

    @classmethod
    def _from_vcard(cls, text: str) -> Contact | None:
        """
        Parse a vCard (``.vcf``) text into a :class:`Contact`.

        A minimal, best-effort parser covering the fields used by ``Contact``:
        ``N`` (structured name), ``FN`` (formatted name) and ``TEL`` (phone).
        vCard 2.1 (quoted-printable + charset), 3.0 and 4.0 are supported.

        The structured ``N`` field is the only reliable source of first/last
        name parts. Without it the whole ``FN`` goes into ``first_name`` and no
        guessing is performed. A malformed or non-vCard input returns ``None``
        instead of raising. The raw input text is kept verbatim in
        :attr:`vcard` (before line unfolding).

        Args:
            text (str): Raw vCard content decoded to text.

        Returns:
            Contact | None: The parsed contact, or ``None`` if the text is not a vCard.
        """
        if "BEGIN:VCARD" not in text.upper():
            return None
        original = text
        text = _UNFOLD_RE.sub("", text)

        props: dict[str, tuple[dict[str, str], str]] = {}
        for match in _PROP_RE.finditer(text):
            props.setdefault(match.group(1).upper(), (_parse_params(match.group(2)), match.group(3)))

        first_name = ""
        last_name: str | None = None
        phone_number: str | None = None

        if "N" in props:
            params, n_value = props["N"]
            parts = [_decode_value(params, p) for p in _split_unescaped(n_value)]
            last_name = parts[0] or None
            first_name = parts[1] if len(parts) > 1 else ""
        elif "FN" in props:
            params, fn_value = props["FN"]
            first_name = _decode_value(params, fn_value)

        if "TEL" in props:
            params, tel_value = props["TEL"]
            tel_value = _decode_value(params, tel_value).strip()
            if tel_value.lower().startswith("tel:"):
                tel_value = tel_value[4:]
            phone_number = tel_value or None

        return cls(
            phone_number=phone_number,
            first_name=first_name,
            last_name=last_name,
            vcard=original,
        )

    @classmethod
    def _from_trueconf(cls, user_id: str, display_name: str) -> Contact:
        """
        Build a :class:`Contact` from a TrueConf user id and display name.

        TrueConf contacts have no phone number in the API, and the display name
        is never split: the server-side name convention (ФИ/ИФ/ФИО) varies per
        installation, so the whole name goes into :attr:`first_name`.

        Args:
            user_id (str): TrueConf user id, e.g. ``ai-bot@domain``.
            display_name (str): Display name of the user.

        Returns:
            Contact: A contact with ``user_id`` and ``first_name`` set.
        """
        return cls(user_id=user_id, first_name=display_name)
