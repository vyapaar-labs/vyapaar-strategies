"""StrategyManifest: schema validation, POC sidecars, instantiation."""

from __future__ import annotations

from decimal import Decimal
from pathlib import Path

import pytest
from pydantic import ValidationError

from vyapaar_strategies import StrategyManifest

ROOT = Path(__file__).resolve().parent.parent.parent
MANIFEST_DIR = ROOT / "manifests" / "strategies"

TURTLE = MANIFEST_DIR / "turtle_breakout.toml"
TWAP = MANIFEST_DIR / "twap_slicer.toml"


def base_manifest() -> dict[str, object]:
    """A structurally valid manifest dict used as the base for field tests."""
    return {
        "name": "turtle_breakout",
        "version": "0.1.0",
        "strategy": "vyapaar_strategies.strategies.turtle:TurtleBreakout",
        "parameters": {
            "entry_period": {"default": 20, "min": 5, "max": 60, "step": 1},
        },
        "target_instruments": {"instruments": ["NSE:NIFTY50-INDEX"]},
        "capital_allocation": {"weight": 0.5},
    }


# -- Phase 1 proof of concept: sidecar files ---------------------------------
@pytest.mark.parametrize("path", [TURTLE, TWAP], ids=lambda p: p.name)
def test_poc_sidecar_loads(path: Path) -> None:
    manifest = StrategyManifest.load_toml(path)
    assert manifest.promotion_status.value == "draft"
    assert manifest.version.count(".") == 2
    assert manifest.target_instruments.instruments
    assert manifest.capital_allocation.weight is not None


def test_turtle_sidecar_declares_expected_parameters() -> None:
    manifest = StrategyManifest.load_toml(TURTLE)
    assert set(manifest.parameters) == {"instrument", "entry_period", "exit_period", "quantity"}


def test_twap_sidecar_declares_expected_parameters() -> None:
    manifest = StrategyManifest.load_toml(TWAP)
    assert set(manifest.parameters) == {"instrument", "total_quantity", "slices", "side"}


# -- schema validation -------------------------------------------------------
def test_rejects_invalid_name() -> None:
    with pytest.raises(ValidationError):
        StrategyManifest.model_validate({**base_manifest(), "name": "Turtle Breakout"})


def test_rejects_non_semver_version() -> None:
    with pytest.raises(ValidationError):
        StrategyManifest.model_validate({**base_manifest(), "version": "v1"})


def test_rejects_strategy_reference_outside_vyapaar_strategies() -> None:
    with pytest.raises(ValidationError):
        StrategyManifest.model_validate(
            {**base_manifest(), "strategy": "some_other_pkg.thing:Strategy"}
        )


def test_capital_allocation_requires_exactly_one_of_absolute_or_weight() -> None:
    with pytest.raises(ValidationError):
        StrategyManifest.model_validate({**base_manifest(), "capital_allocation": {}})
    with pytest.raises(ValidationError):
        StrategyManifest.model_validate(
            {**base_manifest(), "capital_allocation": {"absolute": 100000, "weight": 0.5}}
        )


def test_weight_must_be_within_open_unit_interval() -> None:
    with pytest.raises(ValidationError):
        StrategyManifest.model_validate({**base_manifest(), "capital_allocation": {"weight": 0}})
    with pytest.raises(ValidationError):
        StrategyManifest.model_validate({**base_manifest(), "capital_allocation": {"weight": 1.5}})


def test_absolute_capital_allocation_is_exact_decimal() -> None:
    manifest = StrategyManifest.model_validate(
        {**base_manifest(), "capital_allocation": {"absolute": 100000}}
    )
    assert manifest.capital_allocation.absolute == Decimal("100000")


def test_target_instruments_requires_instruments_or_rule() -> None:
    with pytest.raises(ValidationError):
        StrategyManifest.model_validate({**base_manifest(), "target_instruments": {}})


def test_target_instruments_accepts_selection_rule() -> None:
    manifest = StrategyManifest.model_validate(
        {**base_manifest(), "target_instruments": {"rule": "NIFTY50 index members"}}
    )
    assert manifest.target_instruments.rule == "NIFTY50 index members"


def test_unknown_fields_are_rejected() -> None:
    with pytest.raises(ValidationError):
        StrategyManifest.model_validate({**base_manifest(), "bogus": True})


# -- strategy class interop --------------------------------------------------
def test_instantiate_builds_a_working_strategy() -> None:
    manifest = StrategyManifest.load_toml(TURTLE)
    strategy = manifest.instantiate()
    assert type(strategy).__name__ == "TurtleBreakout"
    assert strategy.entry_period == 20


def test_instantiate_supports_parameter_overrides() -> None:
    manifest = StrategyManifest.load_toml(TURTLE)
    strategy = manifest.instantiate(entry_period=30)
    assert strategy.entry_period == 30


@pytest.mark.parametrize("path", [TURTLE, TWAP], ids=lambda p: p.name)
def test_validate_parameters_passes_for_sidecars(path: Path) -> None:
    assert StrategyManifest.load_toml(path).validate_parameters() == []


def test_validate_parameters_reports_unknown_parameter() -> None:
    bad = {**base_manifest(), "parameters": {"nope": {"default": 1}}}
    manifest = StrategyManifest.model_validate(bad)
    errors = manifest.validate_parameters()
    assert any("not a declarative Parameter" in error for error in errors)
