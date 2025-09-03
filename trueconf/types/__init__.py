__all__ = [
    "Update",
    "Message",
    "CreatedGroupChat",
    "RemovedChat",
    "EditedMessage",
    "RemovedMessage",
    "UploadingProgress",
    "CreatedChannel",
    "AddedChatParticipant",
    "RemovedChatParticipant",
    "CreatedPersonalChat",
]

_MAP = {
    "Update": ".update",
    "Message": ".message",
    "CreatedGroupChat": ".requests.created_group_chat",
    "RemovedChat": ".requests.removed_chat",
    "EditedMessage": ".requests.edited_message",
    "RemovedMessage": ".requests.removed_message",
    "UploadingProgress": ".requests.uploading_progress",
    "CreatedChannel": ".requests.created_channel",
    "AddedChatParticipant": ".requests.added_chat_participant",
    "RemovedChatParticipant": ".requests.removed_chat_participant",
    "CreatedPersonalChat": ".requests.created_personal_chat",
}

def __getattr__(name: str):
    modname = _MAP.get(name)
    if not modname:
        raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
    from importlib import import_module
    mod = import_module(f"{__name__}{modname}")
    return getattr(mod, name)

def __dir__():
    return sorted(list(globals().keys()) + __all__)