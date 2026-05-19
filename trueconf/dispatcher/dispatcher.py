from __future__ import annotations
from typing import TYPE_CHECKING, Any, Awaitable, Callable, Dict, List
from trueconf.filters.base import Event
from trueconf.dispatcher.router import Router

MiddlewareHandler = Callable[[Event, Dict[str, Any]], Awaitable[None]]

if TYPE_CHECKING:
    pass


class Dispatcher(Router):
    """
        Central event dispatcher for processing and routing incoming events.

        The `Dispatcher` extends `Router` and aggregates one or more child `Router`
        instances. Each incoming event is passed through the dispatcher's own
        middleware chain first, then fed to each child router in order until handled.

        Because ``Dispatcher`` inherits from ``Router``, it supports registering
        middleware directly:

        >>> dp.outer_middleware(MyMiddleware())

        Typical usage:

        >>> dispatcher = Dispatcher()
        >>> dispatcher.include_router(my_router)
        >>> await dispatcher._feed_update(event, {"bot": bot})

        Attributes:
            routers (List[Router]): List of root routers included in the dispatcher.
    """

    def __init__(self):
        super().__init__(name="dispatcher")
        self.routers: List[Router] = []

    def include_router(self, router: "Router") -> None:
        """Include a root router in the dispatcher.

        The dispatcher's own middleware is applied in ``_feed_update`` before
        the event reaches child routers. Therefore we do NOT set ``_parent`` —
        child routers should not inherit the dispatcher's middleware through
        the ancestor chain.
        """
        self.routers.append(router)

    async def _feed_update(self, event: Event, data: Dict[str, Any]) -> None:
        """
            Feeds an event to all child routers in order,
            stopping at the first one that handles it.

            The event first passes through the dispatcher's own middleware chain
            (outer middlewares from dispatcher ancestors → dispatcher), then is
            fed to each child router.

        Args:
            event (Event): The event to be processed.
            data (Dict[str, Any]): Context data passed through the middleware pipeline.
        """

        async def _feed_children(evt: Event, ctx: Dict[str, Any]) -> None:
            async def progress_router(router: Router, count: int = 0) -> None:
                handled = await router._feed(evt, ctx)
                if count < 0 or count >= len(router._subrouters):
                    return
                if (not handled) or (handled and router.allow_child_on_event):
                    subrouter = router._subrouters[count]
                    await progress_router(subrouter, count=len(router._subrouters) - 1)

            for router in self.routers:
                await progress_router(router)

        # Build outer middleware chain: dispatcher outer_mw → feed_children
        chain: MiddlewareHandler = _feed_children
        for mw in reversed(self._collect_middlewares("_outer_middlewares")):
            nxt = chain
            chain = Router._wrap_middleware(mw, nxt)

        await chain(event, data)
