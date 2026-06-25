# Class `Dispatcher`⚓︎

Here is the reference information for the `Dispatcher` class, including all its parameters, attributes, and methods.
You can import the `Dispatcher` class directly from the `trueconf` package:

```
from trueconf import Dispatcher
```

## `` trueconf.Dispatcher ⚓︎

```
Dispatcher(*, storage=None, fsm_manager=None, key_builder=None, strategy=None)
```

Central dispatcher for routing incoming events.

The dispatcher is the root router of an application. It receives incoming events, applies its own outer middleware chain, and then passes each event to the included root routers in order. Processing stops when a router handles the event, unless that router allows propagation to its child routers.

`Dispatcher` inherits from `Router`, so it supports the same handler, middleware, and subrouter registration APIs.

### Example

```
dispatcher = Dispatcher()
dispatcher.include_router(router)
```

### FSM example

```
from trueconf.fsm.storage.memory import MemoryStorage

storage = MemoryStorage()
dp = Dispatcher(storage=storage)
```

Parameters:

| Name | Type | Description | Default |
| --- | --- | --- | --- |
| `storage` | `BaseStorage | None` | Storage backend used to create an FSM manager. Cannot be used together with `fsm_manager`. | `None` |
| `fsm_manager` | `FSMManager | None` | Existing FSM manager instance. Cannot be used together with `storage`. | `None` |
| `key_builder` | `KeyBuilder | None` | Key builder used when creating an FSM manager from `storage`. Ignored when `fsm_manager` is passed. | `None` |
| `strategy` | `FSMStrategy | None` | FSM strategy used when creating an FSM manager from `storage`. Ignored when `fsm_manager` is passed. | `None` |

Attributes:

| Name | Type | Description |
| --- | --- | --- |
| `routers` | `List[` trueconf.Router (`trueconf.dispatcher.router.Router`)' href=../Router/#trueconf.Router>Router] | Root routers included in the dispatcher. |
| `fsm` | `FSMManager | None` | FSM manager configured for the dispatcher, or `None` if FSM support has not been enabled. |

### `` include_router ⚓︎

```
include_router(router)
```

Include a root router in the dispatcher.

The dispatcher's own middleware is applied in `_feed_update` before the event reaches child routers. Therefore we do NOT set `_parent` — child routers should not inherit the dispatcher's middleware through the ancestor chain.
