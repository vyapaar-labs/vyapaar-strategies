"""Declarative hyperparameter descriptor.

Jesse-style declarative parameters::

    class MyStrategy(Strategy):
        fast = Parameter(default=10, min=5, max=50, step=5)

Values are validated on assignment: they must fall inside ``[min, max]`` and
align to ``step`` from ``min``.
"""

from __future__ import annotations

from decimal import Decimal
from typing import Any


def _as_decimal(value: Any) -> Decimal:
    return value if isinstance(value, Decimal) else Decimal(str(value))


class Parameter:
    """A validated, declarative strategy hyperparameter."""

    def __init__(
        self,
        default: Any,
        min: Any | None = None,
        max: Any | None = None,
        step: Any | None = None,
    ) -> None:
        self.default = default
        self.min = min
        self.max = max
        self.step = step
        self._name = ""

    def __set_name__(self, owner: type, name: str) -> None:
        del owner
        self._name = name

    def __get__(self, instance: object | None, owner: type | None = None) -> Any:
        if instance is None:
            return self
        return instance.__dict__.get(self._name, self.default)

    def __set__(self, instance: object, value: Any) -> None:
        self.validate(value)
        instance.__dict__[self._name] = value

    def validate(self, value: Any) -> None:
        if self.min is not None:
            minimum = _as_decimal(self.min)
            if _as_decimal(value) < minimum:
                raise ValueError(f"{self._name}: {value} below minimum {self.min}")
        if self.max is not None:
            maximum = _as_decimal(self.max)
            if _as_decimal(value) > maximum:
                raise ValueError(f"{self._name}: {value} above maximum {self.max}")
        if self.step is not None and self.min is not None:
            offset = _as_decimal(value) - _as_decimal(self.min)
            step = _as_decimal(self.step)
            if offset % step != 0:
                raise ValueError(
                    f"{self._name}: {value} is not aligned to step {self.step} from min {self.min}"
                )
