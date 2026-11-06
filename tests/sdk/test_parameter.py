"""Declarative Parameter descriptor: defaults, bounds, step alignment."""

from __future__ import annotations

from decimal import Decimal

import pytest

from vyapaar_strategies import Parameter, Strategy


class Demo(Strategy):
    fast = Parameter(default=10, min=5, max=50, step=5)
    risk = Parameter(default="1", min="0.1", max="10", step="0.1")
    label = Parameter(default="default")


def test_parameter_default_is_used() -> None:
    strategy = Demo()
    assert strategy.fast == 10


def test_parameter_override_is_validated() -> None:
    strategy = Demo(fast=20)
    assert strategy.fast == 20


def test_parameter_rejects_below_minimum() -> None:
    with pytest.raises(ValueError):
        Demo(fast=3)  # type: ignore[arg-type]


def test_parameter_rejects_above_maximum() -> None:
    with pytest.raises(ValueError):
        Demo(fast=60)  # type: ignore[arg-type]


def test_parameter_rejects_misaligned_step() -> None:
    with pytest.raises(ValueError):
        Demo(fast=12)  # type: ignore[arg-type]


def test_parameter_step_alignment_uses_decimal() -> None:
    strategy = Demo(risk="0.5")
    assert strategy.risk == "0.5"
    with pytest.raises(ValueError):
        Demo(risk="0.35")  # type: ignore[arg-type]


def test_parameter_string_values_stay_exact() -> None:
    strategy = Demo(label="production")
    assert strategy.label == "production"
    assert Decimal(str(strategy.risk)) == Decimal("1")
