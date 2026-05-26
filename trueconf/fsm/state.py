from __future__ import annotations

import inspect
from typing import Any


class State:
    def __init__(self, state: str | None = None) -> None:
        self._custom_state = state
        self._name: str | None = None
        self._group: type[StatesGroup] | None = None

    def bind(self, group: type[StatesGroup], name: str) -> None:
        if self._group is not None or self._name is not None:
            raise RuntimeError(
                f"State '{self._name}' is already bound to {self._group}. "
                f"Cannot rebind to {group.__name__}:{name}."
            )
        self._group = group
        self._name = name

    def __str__(self) -> str:
        if self._custom_state is not None:
            return self._custom_state
        if self._group is None or self._name is None:
            raise RuntimeError(
                "State is not bound to a StatesGroup. "
                "Use State inside a StatesGroup class definition, "
                "or pass a custom string: State('my:state')."
            )
        return f"{self._group.__full_group_name__}:{self._name}"

    def __repr__(self) -> str:
        return f"State({str(self)!r})"

    def __eq__(self, other: object) -> bool:
        if isinstance(other, State):
            return str(self) == str(other)
        if isinstance(other, str):
            return str(self) == other
        return NotImplemented

    def __hash__(self) -> int:
        return hash(str(self))


class _StatesGroupMeta(type):
    __parent__: type[StatesGroup] | None
    __childs__: tuple[type[StatesGroup], ...]
    __states__: tuple[State, ...]
    __all_states__: tuple[State, ...]
    __all_childs__: tuple[type[StatesGroup], ...]

    def __new__(
        mcs,
        name: str,
        bases: tuple[type, ...],
        namespace: dict[str, Any],
    ) -> _StatesGroupMeta:
        cls = super().__new__(mcs, name, bases, namespace)

        states: list[State] = []
        childs: list[type[StatesGroup]] = []

        for key, value in namespace.items():
            if isinstance(value, State):
                value.bind(cls, key)
                states.append(value)
            elif (
                inspect.isclass(value)
                and issubclass(value, StatesGroup)
                and value is not StatesGroup
            ):
                child = cls._prepare_child(value)
                childs.append(child)

        cls.__parent__ = None  # type: ignore[attr-defined]
        cls.__childs__ = tuple(childs)  # type: ignore[attr-defined]
        cls.__states__ = tuple(states)  # type: ignore[attr-defined]
        cls.__all_childs__ = cls._get_all_childs()  # type: ignore[attr-defined]
        cls.__all_states__ = cls._get_all_states()  # type: ignore[attr-defined]

        return cls

    @property
    def __full_group_name__(cls) -> str:  # type: ignore[override]
        if cls.__parent__ is not None:
            return f"{cls.__parent__.__full_group_name__}.{cls.__name__}"
        return cls.__name__

    def _prepare_child(cls, child: type[StatesGroup]) -> type[StatesGroup]:
        child.__parent__ = cls  # type: ignore[assignment]
        return child

    def _get_all_childs(cls) -> tuple[type[StatesGroup], ...]:
        result: list[type[StatesGroup]] = list(cls.__childs__)
        for child in cls.__childs__:
            result.extend(child.__childs__)
        return tuple(result)

    def _get_all_states(cls) -> tuple[State, ...]:
        result: list[State] = list(cls.__states__)
        for child in cls.__childs__:
            result.extend(child.__all_states__)
        return tuple(result)

    def __contains__(cls, item: Any) -> bool:
        if isinstance(item, str):
            return item in tuple(str(s) for s in cls.__all_states__)
        if isinstance(item, State):
            return item in cls.__all_states__
        if isinstance(item, _StatesGroupMeta):
            return item in cls.__all_childs__
        return False

    def __iter__(cls) -> Any:
        return iter(cls.__all_states__)


class StatesGroup(metaclass=_StatesGroupMeta):
    __parent__: type[StatesGroup] | None = None
    __childs__: tuple[type[StatesGroup], ...] = ()
    __states__: tuple[State, ...] = ()
    __all_states__: tuple[State, ...] = ()
    __all_childs__: tuple[type[StatesGroup], ...] = ()

    @classmethod
    def get_root(cls) -> type[StatesGroup]:
        if cls.__parent__ is None:
            return cls
        return cls.__parent__.get_root()
