import asyncio

import pytest

from trueconf.client.bot import Bot
from trueconf.enums.command import (
    CommandAnswerType,
    CommandMessageLevel,
    CommandMessageStatus,
    CommandMessageVisibility,
)
from trueconf.methods.answer_command import AnswerCommand
from trueconf.types import CallbackQuery
from trueconf.types.responses.answer_command_response import AnswerCommandResponse


def test_answer_command_is_not_implemented():
    with pytest.raises(NotImplementedError, match="supported by TrueConf Server"):
        AnswerCommand(command_id="command-1", answer_type=CommandAnswerType.COMPLETE, text="Done")


def test_answer_command_raises_not_implemented_regardless_of_input():
    with pytest.raises(NotImplementedError, match="supported by TrueConf Server"):
        AnswerCommand(command_id="", answer_type="complete", text="")


def test_bot_answer_command_is_not_implemented():
    bot = object.__new__(Bot)

    with pytest.raises(NotImplementedError, match="supported by TrueConf Server"):
        asyncio.run(
            bot.answer_command(
                command_id="command-4",
                answer_type=CommandAnswerType.COMPLETE,
                text="Done",
            )
        )


def test_callback_query_answer_with_command_id_is_not_implemented():
    callback = CallbackQuery.from_dict(
        {
            "commandId": "command-5",
            "commandSource": {"type": "inlineKeyboard"},
            "commandPayload": {"type": "userCommand", "command": "confirm"},
        }
    ).bind(object.__new__(Bot))

    with pytest.raises(NotImplementedError, match="supported by TrueConf Server"):
        asyncio.run(callback.answer("Done", answer_type="complete"))


def test_callback_query_answer_uses_bound_bot_and_command_id():
    class CapturingBot:
        async def answer_command(self, **kwargs):
            self.answer_command_kwargs = kwargs
            return AnswerCommandResponse()

    bot = CapturingBot()
    callback = CallbackQuery.from_dict(
        {
            "commandId": "command-5",
            "commandSource": {"type": "inlineKeyboard"},
            "commandPayload": {"type": "userCommand", "command": "confirm"},
        }
    ).bind(bot)

    response = asyncio.run(
        callback.answer(
            text="Accepted",
            answer_type=CommandAnswerType.COMPLETE,
            visibility=CommandMessageVisibility.TOAST,
        )
    )

    assert isinstance(response, AnswerCommandResponse)
    assert bot.answer_command_kwargs == {
        "command_id": "command-5",
        "answer_type": CommandAnswerType.COMPLETE,
        "status": None,
        "visibility": CommandMessageVisibility.TOAST,
        "level": None,
        "text": "Accepted",
    }


def test_callback_query_answer_requires_wait_reply_command_id():
    callback = CallbackQuery.from_dict(
        {
            "commandSource": {"type": "inlineKeyboard"},
            "commandPayload": {"type": "userCommand", "command": "confirm"},
        }
    ).bind(object())

    with pytest.raises(
        ValueError,
        match="server did not send command_id",
    ):
        asyncio.run(callback.answer("Done", answer_type="complete"))


def test_callback_query_parses_command_source_wait_reply():
    callback = CallbackQuery.from_dict(
        {
            "commandId": "command-7",
            "commandSource": {"type": "inlineKeyboard", "waitReply": True},
            "commandPayload": {"type": "userCommand", "command": "confirm"},
        }
    )

    assert callback.command_source.wait_reply is True


def test_callback_query_is_exported_from_top_level_package():
    from trueconf import CallbackQuery as ExportedCallbackQuery

    assert ExportedCallbackQuery is CallbackQuery


def test_answer_command_types_are_exported_from_public_subpackages():
    from trueconf.enums import (
        CommandAnswerType as ExportedCommandAnswerType,
        CommandMessageLevel as ExportedCommandMessageLevel,
        CommandMessageStatus as ExportedCommandMessageStatus,
        CommandMessageVisibility as ExportedCommandMessageVisibility,
    )
    from trueconf.methods import AnswerCommand as ExportedAnswerCommand
    from trueconf.types.responses import AnswerCommandResponse as ExportedAnswerCommandResponse

    assert ExportedCommandAnswerType is CommandAnswerType
    assert ExportedCommandMessageLevel is CommandMessageLevel
    assert ExportedCommandMessageStatus is CommandMessageStatus
    assert ExportedCommandMessageVisibility is CommandMessageVisibility
    assert ExportedAnswerCommand is AnswerCommand
    assert ExportedAnswerCommandResponse is AnswerCommandResponse
