"""Manifest copy of one ``Parameter(...)`` declaration.

A :class:`StrategyManifest` stores the parameter defaults (and optional
bounds/step) a version was validated against, mirroring the ``Parameter``
descriptor declared on the strategy class.
"""

from __future__ import annotations

from decimal import Decimal

from pydantic import BaseModel, ConfigDict


class ParameterSpec(BaseModel):
    """The manifest-side snapshot of a strategy's declarative parameter."""

    model_config = ConfigDict(extra="forbid")

    default: str | int | Decimal
    min: Decimal | None = None
    max: Decimal | None = None
    step: Decimal | None = None
