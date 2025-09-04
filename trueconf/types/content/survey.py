from __future__ import annotations
from dataclasses import dataclass, field
from typing import Optional
from mashumaro import DataClassDictMixin
from trueconf.types.content.base import AbstractEnvelopeContent


@dataclass
class SurveyContent(AbstractEnvelopeContent, DataClassDictMixin):
    url: str
    title: str
    path: Optional[str] = None
    description: Optional[str] = None
    button_text: Optional[str] = field(default=None, metadata={"alias": "buttonText"})
    app_version: Optional[int] = field(
        default=None, metadata={"alias": "appVersion"}
    )
    secret: Optional[str] = None
    alt: Optional[str] = None
