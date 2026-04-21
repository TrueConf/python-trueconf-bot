from __future__ import annotations
from dataclasses import dataclass
from trueconf.types.content.base import AbstractEnvelopeContent


@dataclass
class EditChatTitleContent(AbstractEnvelopeContent):
    title: str
