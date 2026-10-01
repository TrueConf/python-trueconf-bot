import asyncio

import pytest

from trueconf.client.bot import Bot
from trueconf.enums import ParseMode
from trueconf.exceptions import TextMessageTooLongError
from trueconf.methods.send_message import SendMessage
from trueconf.types.message import Message
from trueconf.types.responses.send_message_response import SendMessageResponse
from trueconf.utils.formatting.text import _quote_reply_html, _quote_reply_markdown, _quote_reply_plain


def test_quote_reply_html_composes_body():
    assert _quote_reply_html("Встреча в 15:00", "Можно перенести?") == (
        '<quote class="reply">Встреча в 15:00</quote><br><br>Можно перенести?'
    )


def test_quote_reply_html_escapes_quote_specials():
    assert _quote_reply_html("a<b>&c", "ok") == ('<quote class="reply">a&lt;b&gt;&amp;c</quote><br><br>ok')


def test_quote_reply_html_keeps_quotes_unescaped():
    assert _quote_reply_html('say "hi"', "ok") == ('<quote class="reply">say "hi"</quote><br><br>ok')


def test_quote_reply_plain_escapes_text_into_html():
    assert _quote_reply_plain("a<b>", "x&y") == ('<quote class="reply">a&lt;b&gt;</quote><br><br>x&amp;y')


def test_quote_reply_markdown_composes_blockquote():
    assert _quote_reply_markdown("Встреча в 15:00", "Можно перенести?") == ">Встреча в 15:00\n\nМожно перенести?"


class CapturingBot(Bot):
    async def __call__(self, method):
        self.captured_method = method
        return SendMessageResponse(chat_id="chat-1", message_id="message-2", timestamp=1)


def test_bot_send_message_with_quote_builds_reply_body():
    bot = object.__new__(CapturingBot)

    asyncio.run(
        bot.send_message(
            chat_id="chat-1",
            text="Можно перенести?",
            reply_message_id="message-1",
            quote="Встреча в 15:00",
        )
    )

    assert isinstance(bot.captured_method, SendMessage)
    payload = bot.captured_method.payload()
    assert payload["replyMessageId"] == "message-1"
    assert payload["content"]["text"] == ('<quote class="reply">Встреча в 15:00</quote><br><br>Можно перенести?')
    assert payload["content"]["parseMode"] == "html"


def test_bot_send_message_quote_without_reply_message_id_raises():
    bot = object.__new__(CapturingBot)

    with pytest.raises(ValueError, match="quote requires reply_message_id"):
        asyncio.run(bot.send_message(chat_id="chat-1", text="текст", quote="цитата"))


def test_bot_send_message_quote_with_plain_text_escapes_it_into_html():
    bot = object.__new__(CapturingBot)

    asyncio.run(
        bot.send_message(
            chat_id="chat-1",
            text="a < b & c",
            reply_message_id="message-1",
            quote="цитата",
        )
    )

    payload = bot.captured_method.payload()
    assert payload["content"]["text"] == '<quote class="reply">цитата</quote><br><br>a &lt; b &amp; c'
    assert payload["content"]["parseMode"] == "html"


def test_bot_send_message_quote_with_markdown_builds_blockquote():
    bot = object.__new__(CapturingBot)

    asyncio.run(
        bot.send_message(
            chat_id="chat-1",
            text="**Можно** перенести?",
            reply_message_id="message-1",
            quote="Встреча в 15:00",
            parse_mode=ParseMode.MARKDOWN,
        )
    )

    payload = bot.captured_method.payload()
    assert payload["content"]["text"] == ">Встреча в 15:00\n\n**Можно** перенести?"
    assert payload["content"]["parseMode"] == "markdown"


def test_bot_send_message_quote_with_html_keeps_text_as_is():
    bot = object.__new__(CapturingBot)

    asyncio.run(
        bot.send_message(
            chat_id="chat-1",
            text="<b>Можно</b> перенести?",
            reply_message_id="message-1",
            quote="Встреча в 15:00",
            parse_mode=ParseMode.HTML,
        )
    )

    payload = bot.captured_method.payload()
    assert payload["content"]["text"] == ('<quote class="reply">Встреча в 15:00</quote><br><br><b>Можно</b> перенести?')
    assert payload["content"]["parseMode"] == "html"


@pytest.mark.parametrize("quote", ["", "   ", "\n\t"])
def test_bot_send_message_empty_quote_raises(quote: str):
    bot = object.__new__(CapturingBot)

    with pytest.raises(ValueError, match="quote must be a non-empty string"):
        asyncio.run(
            bot.send_message(
                chat_id="chat-1",
                text="текст",
                reply_message_id="message-1",
                quote=quote,
            )
        )


def test_bot_send_message_quote_length_checked_on_composed_text():
    bot = object.__new__(CapturingBot)
    quote = "q" * 4096

    with pytest.raises(TextMessageTooLongError):
        asyncio.run(
            bot.send_message(
                chat_id="chat-1",
                text="x",
                reply_message_id="message-1",
                quote=quote,
            )
        )


def _bound_text_message(bot, text: str = "Исходное сообщение") -> Message:
    message = Message.from_dict(
        {
            "messageId": "message-1",
            "chat": {"chatId": "chat-1", "chatTitle": "Chat 1", "chatType": 1},
            "timestamp": 1_725_000_000,
            "replyMessageId": None,
            "isEdited": False,
            "type": 200,
            "author": {"id": "alice@example.com", "type": 1},
            "box": {"id": 1, "position": "incoming"},
            "content": {"text": text, "parseMode": "html"},
        }
    )
    return message.bind(bot)


def test_message_reply_with_quote_sends_reply_with_composed_body():
    class CapturingBot:
        async def send_message(self, **kwargs):
            self.send_message_kwargs = kwargs
            return SendMessageResponse(chat_id="chat-1", message_id="message-2", timestamp=1)

    bot = CapturingBot()
    message = _bound_text_message(bot)

    asyncio.run(message.reply("Можно перенести?", quote="Исходное"))

    assert bot.send_message_kwargs["reply_message_id"] == "message-1"
    assert bot.send_message_kwargs["quote"] == "Исходное"


def test_message_reply_with_non_substring_quote_raises():
    class CapturingBot:
        async def send_message(self, **kwargs):
            raise AssertionError("send_message must not be called")

    message = _bound_text_message(CapturingBot())

    with pytest.raises(ValueError, match="quote must be a substring of the replied message"):
        asyncio.run(message.reply("текст", quote="Нет такого текста"))


def test_message_answer_without_quote_keeps_plain_send():
    class CapturingBot:
        async def send_message(self, **kwargs):
            self.send_message_kwargs = kwargs
            return SendMessageResponse(chat_id="chat-1", message_id="message-2", timestamp=1)

    bot = CapturingBot()
    message = _bound_text_message(bot)

    asyncio.run(message.answer("Обычный ответ"))

    assert bot.send_message_kwargs.get("reply_message_id") is None
    assert bot.send_message_kwargs.get("quote") is None


def test_message_quote_property_extracts_quote_block():
    bot = object.__new__(CapturingBot)
    message = _bound_text_message(
        bot,
        text='<quote class="reply">Встреча в 15:00</quote><br><br>Можно перенести?',
    )

    assert message.quote == "Встреча в 15:00"


def test_message_quote_property_unescapes_entities():
    bot = object.__new__(CapturingBot)
    message = _bound_text_message(
        bot,
        text='<quote class="reply">a&lt;b&gt;&amp;c</quote><br><br>ok',
    )

    assert message.quote == "a<b>&c"


def test_message_quote_property_returns_none_without_quote_block():
    bot = object.__new__(CapturingBot)
    message = _bound_text_message(bot, text="Обычное сообщение")

    assert message.quote is None


def test_message_quote_property_returns_first_quote_block():
    bot = object.__new__(CapturingBot)
    message = _bound_text_message(
        bot,
        text='<quote class="reply">первая</quote><br><br><quote class="reply">вторая</quote>',
    )

    assert message.quote == "первая"


def test_message_quote_property_returns_none_for_non_text_content():
    message = Message.from_dict(
        {
            "messageId": "message-1",
            "chat": {"chatId": "chat-1", "chatTitle": "Chat 1", "chatType": 1},
            "timestamp": 1_725_000_000,
            "replyMessageId": None,
            "isEdited": False,
            "type": 205,
            "author": {"id": "alice@example.com", "type": 1},
            "box": {"id": 1, "position": "incoming"},
            "content": {"fileId": "voice-1", "size": 12_345, "mimeType": "audio/ogg", "duration": 7},
        }
    )

    assert message.quote is None


def test_message_text_strips_leading_quote_block():
    bot = object.__new__(CapturingBot)
    message = _bound_text_message(
        bot,
        text='<quote class="reply">Пункт B…</quote><br><br>Сделай это сегодня',
    )

    assert message.text == "Сделай это сегодня"
    assert message.quote == "Пункт B…"


def test_message_text_without_quote_is_unchanged():
    bot = object.__new__(CapturingBot)
    message = _bound_text_message(bot, text="Обычное сообщение")

    assert message.text == "Обычное сообщение"
    assert message.quote is None
