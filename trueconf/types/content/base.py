from __future__ import annotations
from abc import ABC
from mashumaro import DataClassDictMixin


class AbstractEnvelopeContent(DataClassDictMixin, ABC):
    """Маркерный базовый класс."""
    pass
