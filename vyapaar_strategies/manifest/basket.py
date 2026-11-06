"""BasketManifest: several strategy versions under one capital/risk budget.

Phase 2 of plan 0001. A basket references one or more ``StrategyManifest``
versions and validates that the combined allocation fits ``combined_capital``.
The basket-level risk budget is deliberately a simple cap in Phase 1 (an
allocation-objective optimizer such as ``vyapaar-ledger-allocation`` is a later
integration, out of scope).
"""

from __future__ import annotations

import tomllib
from decimal import Decimal
from pathlib import Path
from typing import Self

from pydantic import BaseModel, ConfigDict, Field, model_validator


class MemberStrategyRef(BaseModel):
    """A reference to one ``StrategyManifest`` version plus its allocation."""

    model_config = ConfigDict(extra="forbid")

    name: str = Field(pattern=r"^[a-z0-9_]+$")
    version: str = Field(pattern=r"^[0-9]+\.[0-9]+\.[0-9]+$")
    weight: Decimal | None = Field(default=None, description="Fraction of combined capital.")
    allocation: Decimal | None = Field(default=None, description="Absolute Money amount (INR).")

    @model_validator(mode="after")
    def _exactly_one_allocation(self) -> Self:
        has_weight = self.weight is not None
        has_allocation = self.allocation is not None
        if has_weight == has_allocation:
            raise ValueError("member strategy must set exactly one of weight or allocation")
        if self.weight is not None and not Decimal("0") < self.weight <= Decimal("1"):
            raise ValueError("member weight must be in the open unit interval (0, 1]")
        if self.allocation is not None and self.allocation < 0:
            raise ValueError("member allocation must be non-negative")
        return self


class RiskBudget(BaseModel):
    """Phase-1 simple-cap risk budget at the basket level."""

    model_config = ConfigDict(extra="forbid")

    max_position_fraction: Decimal | None = Field(
        default=None, description="Simple cap on total position fraction in (0, 1]."
    )
    max_loss: Decimal | None = Field(default=None, description="Absolute loss cap (INR).")

    @model_validator(mode="after")
    def _validate_caps(self) -> Self:
        if self.max_position_fraction is not None and not (
            Decimal("0") < self.max_position_fraction <= Decimal("1")
        ):
            raise ValueError(
                "risk_budget.max_position_fraction must be in the open unit interval (0, 1]"
            )
        if self.max_loss is not None and self.max_loss < 0:
            raise ValueError("risk_budget.max_loss must be non-negative")
        return self


class BasketManifest(BaseModel):
    """A group of strategy versions run as one logical unit."""

    model_config = ConfigDict(extra="forbid")

    basket_name: str = Field(pattern=r"^[a-z0-9_]+$")
    version: str = Field(pattern=r"^[0-9]+\.[0-9]+\.[0-9]+$")
    combined_capital: Decimal = Field(gt=Decimal(0))
    member_strategies: list[MemberStrategyRef] = Field(min_length=1)
    risk_budget: RiskBudget = Field(default_factory=RiskBudget)

    @model_validator(mode="after")
    def _allocations_within_combined_capital(self) -> Self:
        weights = [member.weight for member in self.member_strategies if member.weight is not None]
        allocations = [
            member.allocation for member in self.member_strategies if member.allocation is not None
        ]
        if weights and allocations:
            raise ValueError(
                "basket members must all use the same mode: either weight or absolute allocation"
            )
        if weights:
            total = sum(weights, Decimal(0))
            if total > Decimal(1):
                raise ValueError(
                    f"member weights sum to {total} which exceeds the basket budget of 1.0"
                )
        else:
            total = sum(allocations, Decimal(0))
            if total > self.combined_capital:
                raise ValueError(
                    f"member allocations sum to {total} which exceeds "
                    f"combined_capital {self.combined_capital}"
                )
        return self

    # -- loading -------------------------------------------------------------
    @classmethod
    def from_toml(cls, text: str) -> Self:
        return cls.model_validate(tomllib.loads(text))

    @classmethod
    def load_toml(cls, path: str | Path) -> Self:
        return cls.from_toml(Path(path).read_text(encoding="utf-8"))
