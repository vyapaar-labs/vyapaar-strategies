"""StrategyManifest: a versioned sidecar describing one production strategy.

Phase 1 of plan 0001. Each ``manifests/strategies/*.toml`` file names the
strategy class, the parameter defaults/bounds it was validated against, its
target instruments, and its capital allocation (an absolute ``Money`` amount or
a portfolio weight). The runtime consumption path (``vyapaar-runtime-backtest``
``catalog.rs`` / ``engine.rs``) is cross-referenced but not modified here.
"""

from __future__ import annotations

import importlib
import tomllib
from datetime import datetime
from decimal import Decimal
from pathlib import Path
from typing import Self

from pydantic import BaseModel, ConfigDict, Field, model_validator

from vyapaar_strategies.manifest.params import ParameterSpec
from vyapaar_strategies.manifest.version import (
    PROMOTION_ORDER,
    PromotionRecord,
    PromotionStatus,
    evidence_prefix,
    utc_now,
)
from vyapaar_strategies.sdk.parameter import Parameter
from vyapaar_strategies.sdk.strategy import Strategy


class InstrumentSelector(BaseModel):
    """``target_instruments``: an explicit ``InstrumentId`` list or a rule."""

    model_config = ConfigDict(extra="forbid")

    instruments: list[str] = Field(
        default_factory=list,
        description='Explicit InstrumentId list, e.g. ["NSE:RELIANCE-EQ"].',
    )
    rule: str | None = Field(default=None, description="Instrument-selection rule.")

    @model_validator(mode="after")
    def _requires_a_target(self) -> Self:
        if not self.instruments and not self.rule:
            raise ValueError("target_instruments must set instruments or rule")
        return self


class CapitalAllocation(BaseModel):
    """``capital_allocation``: an absolute Money amount or a weight, not both."""

    model_config = ConfigDict(extra="forbid")

    absolute: Decimal | None = Field(default=None, description="Absolute Money amount (INR).")
    weight: Decimal | None = Field(default=None, description="Portfolio fraction in (0, 1].")

    @model_validator(mode="after")
    def _exactly_one(self) -> Self:
        has_absolute = self.absolute is not None
        has_weight = self.weight is not None
        if has_absolute == has_weight:
            raise ValueError("capital_allocation must set exactly one of absolute or weight")
        if self.weight is not None and not Decimal("0") < self.weight <= Decimal("1"):
            raise ValueError("capital_allocation.weight must be in the open unit interval (0, 1]")
        if self.absolute is not None and self.absolute < 0:
            raise ValueError("capital_allocation.absolute must be non-negative")
        return self


class StrategyManifest(BaseModel):
    """A versioned, promotable strategy definition."""

    model_config = ConfigDict(extra="forbid")

    name: str = Field(pattern=r"^[a-z0-9_]+$")
    version: str = Field(pattern=r"^[0-9]+\.[0-9]+\.[0-9]+$")
    strategy: str = Field(pattern=r"^vyapaar_strategies\.[A-Za-z0-9_.]+:[A-Za-z_][A-Za-z0-9_]*$")
    parameters: dict[str, ParameterSpec] = Field(min_length=1)
    target_instruments: InstrumentSelector
    capital_allocation: CapitalAllocation
    promotion_status: PromotionStatus = PromotionStatus.DRAFT
    promotion_evidence: list[PromotionRecord] = Field(default_factory=list)

    # -- strategy class interop ---------------------------------------------
    @property
    def strategy_class(self) -> type[Strategy]:
        module_name, _, class_name = self.strategy.partition(":")
        return getattr(importlib.import_module(module_name), class_name)

    def instantiate(self, **overrides: object) -> Strategy:
        """Build a strategy instance with this version's parameter defaults."""
        parameters: dict[str, object] = {
            name: spec.default for name, spec in self.parameters.items()
        }
        parameters.update(overrides)
        return self.strategy_class(**parameters)

    def validate_parameters(self) -> list[str]:
        """Cross-check declared parameters against the strategy class.

        Every declared parameter must exist as a ``Parameter`` descriptor on
        the strategy class, and its default must satisfy the descriptor bounds.
        """
        errors: list[str] = []
        strategy_class = self.strategy_class
        for name, spec in self.parameters.items():
            descriptor = vars(strategy_class).get(name)
            if not isinstance(descriptor, Parameter):
                errors.append(
                    f"parameter {name!r} is not a declarative Parameter on {self.strategy!r}"
                )
                continue
            try:
                descriptor.validate(spec.default)
            except ValueError as exc:
                errors.append(f"parameter {name!r}: {exc}")
        return errors

    # -- promotion workflow (Phase 3) ---------------------------------------
    def promote(
        self,
        status: PromotionStatus,
        evidence_ref: str,
        *,
        note: str = "",
        at: datetime | None = None,
    ) -> None:
        """Advance ``promotion_status`` one stage along draft->backtested->paper->live.

        Promotions must move exactly one stage forward and, past ``draft``, must
        carry an evidence reference prefixed for the target status
        (``backtest:``, ``paper:``, or ``live:``).
        """
        current = PROMOTION_ORDER.index(self.promotion_status)
        target = PROMOTION_ORDER.index(status)
        if target != current + 1:
            raise ValueError(
                f"cannot promote {self.promotion_status.value} -> {status.value}: "
                "promotions must advance exactly one stage forward"
            )
        prefix = evidence_prefix(status)
        if not evidence_ref.startswith(prefix):
            raise ValueError(
                f"promotion to {status.value} requires evidence_ref starting with {prefix!r}"
            )
        self.promotion_evidence.append(
            PromotionRecord(
                status=status,
                evidence_ref=evidence_ref,
                recorded_at=at if at is not None else utc_now(),
                note=note,
            )
        )
        self.promotion_status = status

    # -- loading -------------------------------------------------------------
    @classmethod
    def from_toml(cls, text: str) -> Self:
        return cls.model_validate(tomllib.loads(text))

    @classmethod
    def load_toml(cls, path: str | Path) -> Self:
        return cls.from_toml(Path(path).read_text(encoding="utf-8"))
