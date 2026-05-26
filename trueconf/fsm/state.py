from __future__ import annotations

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
        return f"{self._group.__name__}:{self._name}"

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
    def __new__(
        mcs,
        name: str,
        bases: tuple[type, ...],
        namespace: dict[str, Any],
    ) -> _StatesGroupMeta:
        state_names = [
            key for key, value in namespace.items()
            if isinstance(value, State)
        ]
        cls = super().__new__(mcs, name, bases, namespace)
        states: list[State] = []
        for key in state_names:
            state = getattr(cls, key)
            state.bind(cls, key)
            states.append(state)
        cls.__states__ = tuple(states)  # type: ignore[attr-defined]
        return cls


class StatesGroup(metaclass=_StatesGroupMeta):
    __states__: tuple[State, ...] = ()
