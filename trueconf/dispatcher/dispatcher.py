from __future__ import annotations

from typing import TYPE_CHECKING, Any, Awaitable, Callable, Dict, List

from trueconf.dispatcher.router import Router
from trueconf.filters.base import Event

MiddlewareHandler = Callable[[Event, Dict[str, Any]], Awaitable[None]]

if TYPE_CHECKING:
    from trueconf.fsm.key_builder import KeyBuilder
    from trueconf.fsm.manager import FSMManager
    from trueconf.fsm.storage.base import BaseStorage
    from trueconf.fsm.strategy import FSMStrategy


class Dispatcher(Router):
    """Central dispatcher for routing incoming events.

    The dispatcher receives incoming events, applies its outer middleware chain,
    and then passes each event to every included root router in registration order.
    Root routers are independent; handling an event in one root does not prevent
    another root from receiving it.

    Each root owns an ordered tree of child routers. Within one tree, traversal
    stops at the first router that handles the event. A router created with
    ``allow_child_on_event=True`` also propagates handled events to its children.

    `Dispatcher` inherits from `Router`, so it supports the same handler,
    middleware, and subrouter registration APIs.

    Example:
        ```python
        dispatcher = Dispatcher()
        dispatcher.include_router(router)
        ```

    FSM example:
        ```python
        from trueconf.fsm.storage.memory import MemoryStorage

        storage = MemoryStorage()
        dp = Dispatcher(storage=storage)
        ```

    Args:
        storage: Storage backend used to create an FSM manager. Cannot be used
            together with `fsm_manager`.
        fsm_manager: Existing FSM manager instance. Cannot be used together
            with `storage`.
        key_builder: Key builder used when creating an FSM manager from
            `storage`. Ignored when `fsm_manager` is passed.
        strategy: FSM strategy used when creating an FSM manager from `storage`.
            Ignored when `fsm_manager` is passed.

    Attributes:
        routers: Root routers included in the dispatcher.
        fsm: FSM manager configured for the dispatcher, or `None` if FSM support
            has not been enabled.
    """

    def __init__(
        self,
        *,
        storage: BaseStorage | None = None,
        fsm_manager: FSMManager | None = None,
        key_builder: KeyBuilder | None = None,
        strategy: FSMStrategy | None = None,
    ):
        super().__init__(name="dispatcher")
        self.routers: List[Router] = []
        self.fsm: FSMManager | None = None

        if fsm_manager is not None and storage is not None:
            raise ValueError("Pass either fsm_manager or storage, not both")

        if fsm_manager is not None:
            self.setup_fsm(fsm_manager=fsm_manager)
        elif storage is not None:
            self.setup_fsm(storage=storage, key_builder=key_builder, strategy=strategy)

    def setup_fsm(
        self,
        *,
        fsm_manager: FSMManager | None = None,
        storage: BaseStorage | None = None,
        key_builder: KeyBuilder | None = None,
        strategy: FSMStrategy | None = None,
    ) -> FSMManager:
        from trueconf.fsm.key_builder import DefaultKeyBuilder
        from trueconf.fsm.manager import FSMManager
        from trueconf.fsm.middleware import FSMMiddleware
        from trueconf.fsm.storage.memory import MemoryStorage
        from trueconf.fsm.strategy import FSMStrategy

        if self.fsm is not None:
            raise RuntimeError(
                "FSM is already configured for this Dispatcher. Call setup_fsm() only once, or create a new Dispatcher."
            )

        if fsm_manager is None:
            fsm_manager = FSMManager(
                storage=storage or MemoryStorage(),
                key_builder=key_builder or DefaultKeyBuilder(),
                strategy=strategy or FSMStrategy.USER_IN_CHAT,
            )

        self.fsm = fsm_manager
        self._outer_middlewares.insert(0, FSMMiddleware(fsm_manager))
        return fsm_manager

    def include_router(self, router: "Router") -> None:
        """Include a root router in the dispatcher.

        The dispatcher's own middleware is applied in ``_feed_update`` before
        the event reaches child routers. Therefore we do NOT set ``_parent`` —
        child routers should not inherit the dispatcher's middleware through
        the ancestor chain.
        """
        self.routers.append(router)

    async def _feed_update(self, event: Event, data: Dict[str, Any]) -> None:
        """Feed an event to every independent root router in order.

        The event first passes through the dispatcher's outer middleware chain.
        Each root then traverses its child tree in registration order until one
        branch handles the event, subject to ``allow_child_on_event``.

        Args:
            event (Event): The event to be processed.
            data (Dict[str, Any]): Context data passed through the middleware pipeline.
        """

        async def _feed_children(evt: Event, ctx: Dict[str, Any]) -> None:
            async def progress_router(router: Router) -> bool:
                handled = await router._feed(evt, ctx)
                if handled and not router.allow_child_on_event:
                    return True

                for subrouter in router._subrouters:
                    if await progress_router(subrouter):
                        return True

                return handled

            for router in self.routers:
                await progress_router(router)

        # Build outer middleware chain: dispatcher outer_mw → feed_children
        chain: MiddlewareHandler = _feed_children
        for mw in reversed(self._collect_middlewares("_outer_middlewares")):
            nxt = chain
            chain = Router._wrap_middleware(mw, nxt)

        await chain(event, data)
