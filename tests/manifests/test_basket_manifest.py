"""BasketManifest: grouping, combined-capital budget, sidecars."""

from __future__ import annotations

from decimal import Decimal
from pathlib import Path

import pytest
from pydantic import ValidationError

from vyapaar_strategies import BasketManifest, MemberStrategyRef

ROOT = Path(__file__).resolve().parent.parent.parent
BASKET_DIR = ROOT / "manifests" / "baskets"

BASKETS = sorted(BASKET_DIR.rglob("*.toml"))


def base_basket() -> dict[str, object]:
    """A structurally valid basket dict used as the base for field tests."""
    return {
        "basket_name": "turtle_twap_basket",
        "version": "0.1.0",
        "combined_capital": 1000000,
        "member_strategies": [
            {"name": "turtle_breakout", "version": "0.1.0", "weight": 0.5},
            {"name": "twap_slicer", "version": "0.1.0", "weight": 0.5},
        ],
    }


# -- Phase 2 proof of concept: sidecar file ----------------------------------
@pytest.mark.parametrize("path", BASKETS, ids=lambda p: p.name)
def test_basket_sidecar_loads(path: Path) -> None:
    basket = BasketManifest.load_toml(path)
    assert len(basket.member_strategies) >= 2
    assert basket.combined_capital > 0


# -- schema validation -------------------------------------------------------
def test_member_requires_exactly_one_of_weight_or_allocation() -> None:
    with pytest.raises(ValidationError):
        BasketManifest.model_validate(
            {**base_basket(), "member_strategies": [{"name": "x", "version": "0.1.0"}]}
        )
    with pytest.raises(ValidationError):
        BasketManifest.model_validate(
            {
                **base_basket(),
                "member_strategies": [
                    {"name": "x", "version": "0.1.0", "weight": 0.5, "allocation": 50000}
                ],
            }
        )


def test_weights_must_sum_to_at_most_one() -> None:
    with pytest.raises(ValidationError):
        BasketManifest.model_validate(
            {
                **base_basket(),
                "member_strategies": [
                    {"name": "a", "version": "0.1.0", "weight": 0.6},
                    {"name": "b", "version": "0.1.0", "weight": 0.6},
                ],
            }
        )


def test_members_cannot_mix_weight_and_allocation_modes() -> None:
    with pytest.raises(ValidationError):
        BasketManifest.model_validate(
            {
                **base_basket(),
                "member_strategies": [
                    {"name": "a", "version": "0.1.0", "weight": 0.5},
                    {"name": "b", "version": "0.1.0", "allocation": 300000},
                ],
            }
        )


def test_absolute_allocations_must_sum_within_combined_capital() -> None:
    ok = BasketManifest.model_validate(
        {
            **base_basket(),
            "combined_capital": 1000000,
            "member_strategies": [
                {"name": "a", "version": "0.1.0", "allocation": 400000},
                {"name": "b", "version": "0.1.0", "allocation": 300000},
            ],
        }
    )
    assert ok.member_strategies[0].allocation == Decimal("400000")

    with pytest.raises(ValidationError):
        BasketManifest.model_validate(
            {
                **base_basket(),
                "combined_capital": 1000000,
                "member_strategies": [
                    {"name": "a", "version": "0.1.0", "allocation": 700000},
                    {"name": "b", "version": "0.1.0", "allocation": 400000},
                ],
            }
        )


def test_combined_capital_must_be_positive() -> None:
    with pytest.raises(ValidationError):
        BasketManifest.model_validate({**base_basket(), "combined_capital": 0})


def test_risk_budget_caps_are_validated() -> None:
    with pytest.raises(ValidationError):
        BasketManifest.model_validate(
            {**base_basket(), "risk_budget": {"max_position_fraction": 0}}
        )
    with pytest.raises(ValidationError):
        BasketManifest.model_validate({**base_basket(), "risk_budget": {"max_loss": -1}})


def test_risk_budget_defaults_to_no_caps() -> None:
    basket = BasketManifest.model_validate(base_basket())
    assert basket.risk_budget.max_position_fraction is None
    assert basket.risk_budget.max_loss is None


def test_member_ref_weight_bounds() -> None:
    with pytest.raises(ValidationError):
        MemberStrategyRef(name="a", version="0.1.0", weight=Decimal("1.2"))


def test_unknown_basket_fields_are_rejected() -> None:
    with pytest.raises(ValidationError):
        BasketManifest.model_validate({**base_basket(), "bogus": True})
