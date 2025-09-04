from __future__ import annotations
from typing import TypeVar
from trueconf.enums.incoming_update_method import IncomingUpdateMethod as IUM
from trueconf.enums.message_type import MessageType
from trueconf.enums.update_type import UpdateType
from trueconf.types.author_box import EnvelopeAuthor, EnvelopeBox
from trueconf.types.content.attachment import AttachmentContent
from trueconf.types.content.survey import SurveyContent
from trueconf.types.content.text import TextContent
from trueconf.types.message import Message
from trueconf.types.requests.added_chat_participant import AddedChatParticipant
from trueconf.types.requests.created_channel import CreatedChannel
from trueconf.types.requests.created_group_chat import CreatedGroupChat
from trueconf.types.requests.created_personal_chat import CreatedPersonalChat
from trueconf.types.requests.edited_message import EditedMessage
from trueconf.types.requests.removed_chat import RemovedChat
from trueconf.types.requests.removed_chat_participant import RemovedChatParticipant
from trueconf.types.requests.removed_message import RemovedMessage
from trueconf.types.requests.uploading_progress import UploadingProgress
from trueconf.types.update import Update

T = TypeVar("T")


def _content_factory(env_type: MessageType, raw: dict):
    if env_type == MessageType.PLAIN_MESSAGE:
        return TextContent.from_dict(raw)
    if env_type == MessageType.ATTACHMENT:
        return AttachmentContent.from_dict(raw)
    if env_type == MessageType.SURVEY:
        return SurveyContent.from_dict(raw)
    return None


def parse_update(raw: dict):
    if raw.get("type") == UpdateType.RESPONSE:
        return None

    p = raw.get("payload")
    if not isinstance(p, dict):
        return None

    match raw["method"]:
        case IUM.UPLOADING_PROGRESS:
            return UploadingProgress.from_dict(raw["payload"])

        case IUM.REMOVED_CHAT_PARTICIPANT:
            return RemovedChatParticipant.from_dict(raw["payload"])

        case IUM.REMOVED_MESSAGE:
            return RemovedMessage.from_dict(raw["payload"])

        case IUM.REMOVED_CHAT:
            return RemovedChat.from_dict(raw["payload"])

        case IUM.EDITED_MESSAGE:
            return EditedMessage.from_dict(raw["payload"])

        case IUM.ADDED_CHAT_PARTICIPANT:
            return AddedChatParticipant.from_dict(raw["payload"])

        case IUM.CREATED_PERSONAL_CHAT:
            return CreatedPersonalChat.from_dict(raw["payload"])

        case IUM.CREATED_GROUP_CHAT:
            return CreatedGroupChat.from_dict(raw["payload"])

        case IUM.CREATED_CHANNEL:
            return CreatedChannel.from_dict(raw["payload"])

        case IUM.MESSAGE:
            env_type = MessageType(p.get("type", 0))
            content = _content_factory(env_type, p.get("content", {}))
            if content is None:
                return None
            p["content"] = content
            return Message(
                message_id=p["messageId"],
                chat_id=p["chatId"],
                timestamp=p["timestamp"],
                reply_message_id=p.get("replyMessageId"),
                is_edited=p["isEdited"],
                type=env_type,
                author=EnvelopeAuthor.from_dict(p["author"]),
                box=EnvelopeBox.from_dict(p["box"]),
                content=content,
            )

        case _:
            return Update(raw["method"], raw["type"], raw["id"], raw["payload"])
