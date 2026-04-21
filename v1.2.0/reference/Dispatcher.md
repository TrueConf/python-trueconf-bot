# Class `Dispatcher`⚓︎

Here is the reference information for the `Dispatcher` class, including all its parameters, attributes, and methods.
You can import the `Dispatcher` class directly from the `trueconf` package:

```
from trueconf import Dispatcher
```

## `` trueconf.Dispatcher ⚓︎

```
Dispatcher()
```

Central event dispatcher for processing and routing incoming events.

The `Dispatcher` aggregates one or more `Router` instances and feeds each incoming event through them. The routers are traversed recursively via their `subrouters` (using `_iter_all()`), and each event is passed to `_feed()` of each router in order until it is handled.

Typical usage includes registering routers with handlers and then calling `feed_update()` with incoming events.

Examples:

```
>>> dispatcher = Dispatcher()
>>> dispatcher.include_router(my_router)
```

Attributes:

| Name | Type | Description |
| --- | --- | --- |
| `` routers

`instance-attribute`
(`trueconf.Dispatcher.routers`)' href=#trueconf.Dispatcher.routers>routers | `List[` trueconf.Router (`trueconf.dispatcher.router.Router`)' href=../Router/#trueconf.Router>Router] | List of root routers included in the dispatcher. |

Initializes an empty dispatcher with no routers.

### `` routers `instance-attribute` ⚓︎

```
routers = []
```

### `` include_router ⚓︎

```
include_router(router)
```

Includes a router to be used by the dispatcher.

Parameters:

| Name | Type | Description | Default |
| --- | --- | --- | --- |
| `router` | `` trueconf.Router (`trueconf.dispatcher.router.Router`)' href=../Router/#trueconf.Router>Router | A `Router` instance to include. | required |
