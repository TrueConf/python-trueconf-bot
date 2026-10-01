from __future__ import annotations

from dataclasses import dataclass, field

from mashumaro import DataClassDictMixin

from trueconf.types.content.base import AbstractEnvelopeContent


@dataclass
class SurveyContent(AbstractEnvelopeContent, DataClassDictMixin):
    url: str
    title: str
    path: str | None = None
    description: str | None = None
    button_text: str | None = field(default=None, metadata={"alias": "buttonText"})
    app_version: int | None = field(default=None, metadata={"alias": "appVersion"})
    secret: str | None = None
    alt: str | None = None
