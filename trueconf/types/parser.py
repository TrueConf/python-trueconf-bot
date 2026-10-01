from __future__ import annotations

from typing import TypeVar

from trueconf.enums.incoming_update_method import IncomingUpdateMethod as IUM
from trueconf.enums.update_type import UpdateType
from trueconf.types.callback_query import CallbackQuery
from trueconf.types.content.parser import UnsupportedMessageType
from trueconf.types.envelope_parser import deserialize_envelope
from trueconf.types.requests.added_chat_participant import AddedChatParticipant
from trueconf.types.requests.changed_file_upload_limits import ChangedFileUploadLimits
from trueconf.types.requests.changed_participant_role import ChangedParticipantRole
from trueconf.types.requests.cleared_chat_history import ClearedChatHistory
from trueconf.types.requests.created_channel import CreatedChannel
from trueconf.types.requests.created_favorites_chat import CreatedFavoritesChat
from trueconf.types.requests.created_group_chat import CreatedGroupChat
from trueconf.types.requests.created_personal_chat import CreatedPersonalChat
from trueconf.types.requests.edited_chat_avatar import EditedChatAvatar
from trueconf.types.requests.edited_chat_title import EditedChatTitle
from trueconf.types.requests.edited_message import EditedMessage
from trueconf.types.requests.removed_chat import RemovedChat
from trueconf.types.requests.removed_chat_participant import RemovedChatParticipant
from trueconf.types.requests.removed_message import RemovedMessage
from trueconf.types.requests.uploading_progress import UploadingProgress
from trueconf.types.update import Update

T = TypeVar("T")

_INBOX_EVENT_MAP = {
    IUM.COMMAND: CallbackQuery,
    IUM.UPLOADING_PROGRESS: UploadingProgress,
    IUM.REMOVED_CHAT_PARTICIPANT: RemovedChatParticipant,
    IUM.REMOVED_MESSAGE: RemovedMessage,
    IUM.REMOVED_CHAT: RemovedChat,
    IUM.EDITED_CHAT_AVATAR: EditedChatAvatar,
    IUM.EDITED_CHAT_TITLE: EditedChatTitle,
    IUM.EDITED_MESSAGE: EditedMessage,
    IUM.ADDED_CHAT_PARTICIPANT: AddedChatParticipant,
    IUM.CREATED_PERSONAL_CHAT: CreatedPersonalChat,
    IUM.CREATED_GROUP_CHAT: CreatedGroupChat,
    IUM.CREATED_CHANNEL: CreatedChannel,
    IUM.CREATED_FAVORITES_CHAT: CreatedFavoritesChat,
    IUM.CHANGED_PARTICIPANT_ROLE: ChangedParticipantRole,
    IUM.CHANGED_FILE_UPLOAD_LIMITS: ChangedFileUploadLimits,
    IUM.CLEARED_CHAT_HISTORY: ClearedChatHistory,
}


def parse_update(raw: dict):
    if raw.get("type") == UpdateType.RESPONSE:
        return None

    p = raw.get("payload")
    if not isinstance(p, dict):
        return None

    parser = _INBOX_EVENT_MAP.get(raw["method"])
    if parser is not None:
        return parser.from_dict(p)

    if raw["method"] == IUM.MESSAGE:
        try:
            return deserialize_envelope(p)
        except UnsupportedMessageType:
            return None

    return Update(raw["method"], raw["type"], raw["id"], raw["payload"])
