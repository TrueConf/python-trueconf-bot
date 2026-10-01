from __future__ import annotations

import pytest

from trueconf.exceptions import ApiErrorException
from trueconf.types.contact import Contact
from trueconf.types.message import Message
from trueconf.types.responses.get_user_display_name_response import GetUserDisplayNameResponse

pytestmark = pytest.mark.anyio


class FakeBot:
    def __init__(
        self,
        *,
        download_result: bytes | None = b"...",
        display_name: str = "AI Bot",
        display_name_error: bool = False,
    ):
        self.download_result = download_result
        self.display_name = display_name
        self.display_name_error = display_name_error
        self.download_calls = 0

    async def download_file_by_id(self, file_id: str) -> bytes | None:
        self.download_calls += 1
        return self.download_result

    async def get_user_display_name(self, user_id: str) -> GetUserDisplayNameResponse:
        if self.display_name_error:
            raise ApiErrorException(code=1, detail="user not found")
        return GetUserDisplayNameResponse(display_name=self.display_name)


VCARD_3 = """BEGIN:VCARD
VERSION:3.0
PRODID:-//Apple Inc.//iPhone OS 18.7.2//EN
N:Бааджи;Антон;;;
FN:Антон Бааджи
TEL;TYPE=CELL:+7123456789
END:VCARD
"""


def _text_raw(message_id: str, text: str) -> dict:
    return {
        "messageId": message_id,
        "chat": {"chatId": "chat-1", "chatTitle": "Chat 1", "chatType": 1},
        "timestamp": 1_725_000_000,
        "replyMessageId": None,
        "isEdited": False,
        "type": 200,
        "author": {"id": "alice@example.com", "type": 1},
        "box": {"id": 1, "position": "incoming"},
        "content": {"text": text, "parseMode": "html"},
    }


def _attachment_raw(message_id: str, mime_type: str = "text/vcard") -> dict:
    return {
        "messageId": message_id,
        "chat": {"chatId": "chat-1", "chatTitle": "Chat 1", "chatType": 1},
        "timestamp": 1_725_000_000,
        "replyMessageId": None,
        "isEdited": False,
        "type": 202,
        "author": {"id": "alice@example.com", "type": 1},
        "box": {"id": 1, "position": "incoming"},
        "content": {"name": "contact.vcf", "size": 209, "fileId": "file-1", "mimeType": mime_type},
    }


# --- Contact._from_vcard ----------------------------------------------------


def test_from_vcard_structured_name_and_phone():
    contact = Contact._from_vcard(VCARD_3)

    assert contact is not None
    assert contact.first_name == "Антон"
    assert contact.last_name == "Бааджи"
    assert contact.phone_number == "+7123456789"
    assert contact.user_id is None
    assert "BEGIN:VCARD" in contact.vcard


def test_from_vcard_fn_fallback():
    text = "BEGIN:VCARD\nVERSION:3.0\nFN:Anton Baadzhi\nEND:VCARD\n"

    contact = Contact._from_vcard(text)

    assert contact is not None
    assert contact.first_name == "Anton Baadzhi"
    assert contact.last_name is None
    assert contact.phone_number is None


def test_from_vcard_no_begin_returns_none():
    assert Contact._from_vcard("hello world") is None


def test_from_vcard_folded_lines():
    text = "BEGIN:VCARD\nVERSION:3.0\nFN:Anton \n Baadzhi\nTEL:+7123456789\nEND:VCARD\n"

    contact = Contact._from_vcard(text)

    assert contact is not None
    assert contact.first_name == "Anton Baadzhi"


def test_from_vcard_escaped_semicolon_in_name():
    text = "BEGIN:VCARD\nVERSION:3.0\nN:Doe;John\\;Smith;;;\nEND:VCARD\n"

    contact = Contact._from_vcard(text)

    assert contact is not None
    assert contact.last_name == "Doe"
    assert contact.first_name == "John;Smith"


def test_from_vcard_escaped_backslash_and_comma():
    text = "BEGIN:VCARD\nVERSION:3.0\nN:Doe;John\\,Jr\\\\;;;\nEND:VCARD\n"

    contact = Contact._from_vcard(text)

    assert contact is not None
    assert contact.first_name == "John,Jr\\"


def test_from_vcard_quoted_printable():
    text = (
        "BEGIN:VCARD\nVERSION:2.1\n"
        "FN;ENCODING=QUOTED-PRINTABLE;CHARSET=UTF-8:=D0=90=D0=BD=D1=82=D0=BE=D0=BD\n"
        "END:VCARD\n"
    )

    contact = Contact._from_vcard(text)

    assert contact is not None
    assert contact.first_name == "Антон"


def test_from_vcard_bare_quoted_printable_param():
    text = "BEGIN:VCARD\nVERSION:2.1\nFN;QUOTED-PRINTABLE;CHARSET=UTF-8:=D0=90=D0=BD=D1=82=D0=BE=D0=BD\nEND:VCARD\n"

    contact = Contact._from_vcard(text)

    assert contact is not None
    assert contact.first_name == "Антон"


def test_from_vcard_vcard_field_preserves_raw_folded_text():
    text = "BEGIN:VCARD\nVERSION:3.0\nFN:Anton \n Baadzhi\nTEL:+7123456789\nEND:VCARD\n"

    contact = Contact._from_vcard(text)

    assert contact is not None
    assert contact.first_name == "Anton Baadzhi"
    # The raw vCard text is kept verbatim, including the folded line.
    assert contact.vcard == text
    assert "Anton \n Baadzhi" in contact.vcard


def test_from_vcard_tel_prefix():
    text = "BEGIN:VCARD\nVERSION:3.0\nN:Doe;John;;;\nTEL:tel:+7123456789\nEND:VCARD\n"

    contact = Contact._from_vcard(text)

    assert contact is not None
    assert contact.phone_number == "+7123456789"


def test_from_vcard_empty_fields():
    text = "BEGIN:VCARD\nVERSION:3.0\nEND:VCARD\n"

    contact = Contact._from_vcard(text)

    assert contact is not None
    assert contact.first_name == ""
    assert contact.last_name is None
    assert contact.phone_number is None


def test_from_vcard_nickname_not_confused_with_n():
    text = "BEGIN:VCARD\nVERSION:3.0\nNICKNAME:Bob\nN:Doe;John;;;\nEND:VCARD\n"

    contact = Contact._from_vcard(text)

    assert contact is not None
    assert contact.last_name == "Doe"
    assert contact.first_name == "John"


# --- Contact._from_trueconf -------------------------------------------------


def test_from_trueconf_keeps_whole_display_name():
    contact = Contact._from_trueconf(user_id="anton@example.net", display_name="Антон Бааджи")

    assert contact.user_id == "anton@example.net"
    assert contact.first_name == "Антон Бааджи"
    assert contact.last_name is None
    assert contact.phone_number is None
    assert contact.vcard is None


# --- Message.contact property -----------------------------------------------


async def test_contact_property_vcard_attachment():
    bot = FakeBot(download_result=VCARD_3.encode("utf-8"))
    message = Message.from_dict(_attachment_raw("m1")).bind(bot)

    contact = await message.contact

    assert isinstance(contact, Contact)
    assert contact.first_name == "Антон"
    assert contact.last_name == "Бааджи"
    assert contact.phone_number == "+7123456789"
    assert "BEGIN:VCARD" in contact.vcard


async def test_contact_property_download_none_returns_none():
    bot = FakeBot(download_result=None)
    message = Message.from_dict(_attachment_raw("m1")).bind(bot)

    assert await message.contact is None


async def test_contact_property_non_vcard_attachment_is_none():
    bot = FakeBot()
    message = Message.from_dict(_attachment_raw("m1", mime_type="application/pdf")).bind(bot)

    assert await message.contact is None


async def test_contact_property_trueconf_link_uses_display_name():
    bot = FakeBot(display_name="Антон Бааджи")
    message = Message.from_dict(
        _text_raw("m1", '<a href="trueconf:anton@example.net&do=profile">Антон Бааджи</a>')
    ).bind(bot)

    contact = await message.contact

    assert isinstance(contact, Contact)
    assert contact.user_id == "anton@example.net"
    assert contact.first_name == "Антон Бааджи"
    assert contact.last_name is None
    assert contact.phone_number is None
    assert contact.vcard is None


async def test_contact_property_trueconf_link_falls_back_on_api_error():
    bot = FakeBot(display_name_error=True)
    message = Message.from_dict(
        _text_raw("m1", '<a href="trueconf:anton@example.net&do=profile">Anton Baadzhi</a>')
    ).bind(bot)

    contact = await message.contact

    assert isinstance(contact, Contact)
    assert contact.user_id == "anton@example.net"
    assert contact.first_name == "Anton Baadzhi"


async def test_contact_property_mention_in_sentence_is_none():
    bot = FakeBot()
    message = Message.from_dict(
        _text_raw("m1", 'Привет, <a href="trueconf:anton@example.net&do=profile">Антон</a>!')
    ).bind(bot)

    assert await message.contact is None


async def test_contact_property_plain_text_is_none():
    bot = FakeBot()
    message = Message.from_dict(_text_raw("m1", "hello")).bind(bot)

    assert await message.contact is None


async def test_contact_property_caches_result():
    bot = FakeBot(download_result=VCARD_3.encode("utf-8"))
    message = Message.from_dict(_attachment_raw("m1")).bind(bot)

    first = await message.contact
    second = await message.contact

    assert first is second
    assert bot.download_calls == 1
