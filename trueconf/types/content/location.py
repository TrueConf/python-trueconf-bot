from __future__ import annotations

from dataclasses import dataclass

from trueconf.types.content.base import AbstractEnvelopeContent


@dataclass
class Location(AbstractEnvelopeContent):
    latitude: float
    longitude: float
    title: str
