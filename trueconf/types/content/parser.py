from __future__ import annotations

from typing import Union, cast

from trueconf.enums.message_type import MessageType
from trueconf.types.content.attachment import AttachmentContent
from trueconf.types.content.base import AbstractEnvelopeContent
from trueconf.types.content.chat_created import ParticipantRoleContent
from trueconf.types.content.clear_chat_history import ClearChatHistoryContent
from trueconf.types.content.edit_chat_avatar import EditChatAvatarContent
from trueconf.types.content.edit_chat_title import EditChatTitleContent
from trueconf.types.content.forward_message import ForwardMessage
from trueconf.types.content.location import Location
from trueconf.types.content.remove_participant import RemoveParticipant
from trueconf.types.content.survey import SurveyContent
from trueconf.types.content.text import TextContent
from trueconf.types.content.voice import Voice

UserMessageContent = Union[
    TextContent,
    AttachmentContent,
    SurveyContent,
    ForwardMessage,
    Location,
    Voice,
]

SystemMessageContent = Union[
    ParticipantRoleContent,
    RemoveParticipant,
    EditChatTitleContent,
    EditChatAvatarContent,
    ClearChatHistoryContent,
]

USER_CONTENT_TYPES: dict[MessageType, type[AbstractEnvelopeContent]] = {
    MessageType.PLAIN_MESSAGE: TextContent,
    MessageType.FORWARDED_MESSAGE: ForwardMessage,
    MessageType.ATTACHMENT: AttachmentContent,
    MessageType.LOCATION: Location,
    MessageType.SURVEY: SurveyContent,
    MessageType.VOICE_MESSAGE: Voice,
}

SYSTEM_CONTENT_TYPES: dict[MessageType, type[AbstractEnvelopeContent]] = {
    MessageType.ADD_PARTICIPANT: ParticipantRoleContent,
    MessageType.REMOVE_PARTICIPANT: RemoveParticipant,
    MessageType.EDIT_CHAT_TITLE: EditChatTitleContent,
    MessageType.EDIT_CHAT_AVATAR: EditChatAvatarContent,
    MessageType.CLEAR_CHAT_HISTORY: ClearChatHistoryContent,
    MessageType.PARTICIPANT_ROLE: ParticipantRoleContent,
}

ENVELOPE_CONTENT_TYPES = USER_CONTENT_TYPES | SYSTEM_CONTENT_TYPES


class UnsupportedMessageType(ValueError):
    pass


def _deserialize_content(
    message_type: MessageType,
    raw: dict,
    content_types: dict[MessageType, type[AbstractEnvelopeContent]],
) -> AbstractEnvelopeContent:
    try:
        content_type = content_types[message_type]
    except KeyError:
        raise UnsupportedMessageType(message_type) from None
    return content_type.from_dict(raw)


def deserialize_user_content(message_type: MessageType, raw: dict) -> UserMessageContent:
    return cast(UserMessageContent, _deserialize_content(message_type, raw, USER_CONTENT_TYPES))


def deserialize_system_content(message_type: MessageType, raw: dict) -> SystemMessageContent:
    return cast(SystemMessageContent, _deserialize_content(message_type, raw, SYSTEM_CONTENT_TYPES))


def deserialize_envelope_content(message_type: MessageType, raw: dict) -> AbstractEnvelopeContent:
    return _deserialize_content(message_type, raw, ENVELOPE_CONTENT_TYPES)
