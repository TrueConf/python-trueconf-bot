from __future__ import annotations
from typing import List
from trueconf.filters.base import Event
from trueconf.dispatcher.router import Router


class Dispatcher:
    """
        Central event dispatcher for processing and routing incoming events.

        The `Dispatcher` aggregates one or more `Router` instances and feeds each
        incoming event through them. The routers are traversed recursively via their
        `subrouters` (using `_iter_all()`), and each event is passed to `_feed()` of
        each router in order until it is handled.

        Typical usage includes registering routers with handlers and then calling
        `feed_update()` with incoming events.

        Examples:
            >>> dispatcher = Dispatcher()
            >>> dispatcher.include_router(my_router)

        Attributes:
            routers (List[Router]): List of root routers included in the dispatcher.

        """

    def __init__(self):
        """Initializes an empty dispatcher with no routers."""
        self.routers: List[Router] = []

    def include_router(self, router: Router):
        """
            Includes a router to be used by the dispatcher.

            Args:
                router (Router): A `Router` instance to include.
        """
        self.routers.append(router)

    async def _feed_update(self, event: Event):
        """
            Feeds an event to all routers and subrouters in order,
            stopping at the first one that handles it.

            Args:
                event (Event): The event to be processed.

            Returns:
                None
        """

        async def progress_router(router, count = 0):
            handled = await router._feed(event)
            if count < 0 or count >= len(router._subrouters):
                return
            if (not handled) or (handled and router.allow_child_on_event):
                subrouter = router._subrouters[count]
                return await progress_router(subrouter, count=len(router._subrouters) - 1)
            return

        for router in self.routers:
            await progress_router(router)