from __future__ import annotations

from trueconf.filters.base import Event
from trueconf.types.update import Update


class RawUpdateFilter:
    """Filter for ``@r.event``: matches the raw envelope and substitutes the event with ``Update``.

    The raw envelope is taken from the ``update`` context entry (provided by ``Bot``).
    If the context is absent (a direct ``router._feed`` call in tests), the filter
    matches against the event itself when it is already an ``Update``.
    """

    def __init__(self, method: str | None = None):
        self.method = method

    async def __call__(self, event: Event, update: Update | None = None):
        raw = update if update is not None else (event if isinstance(event, Update) else None)
        if raw is None:
            return False
        if self.method is not None and raw.method != self.method:
            return False
        return {"event": raw}
