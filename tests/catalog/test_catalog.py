"""Catalog manifests: schema conformance and strategy-class parity."""

from __future__ import annotations

import importlib
import json
import tomllib
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent.parent
CATALOG_DIR = ROOT / "catalog"
SCHEMA_PATH = ROOT / "schema" / "step.schema.json"

FAMILIES = (
    "arbitrage",
    "execution",
    "market_making",
    "mean_reversion",
    "options",
    "portfolio",
    "size",
    "trend",
)

MANIFESTS = sorted(CATALOG_DIR.rglob("*.toml"))


def load_manifest(path: Path) -> dict[str, object]:
    return tomllib.loads(path.read_text())


@pytest.mark.parametrize("path", MANIFESTS, ids=lambda p: p.relative_to(ROOT))
def test_manifest_has_required_structure(path: Path) -> None:
    manifest = load_manifest(path)
    for key in ("name", "title", "family", "version", "strategy", "params"):
        assert key in manifest, f"{path.name} missing {key!r}"
    assert manifest["family"] in FAMILIES
    assert ":" in str(manifest["strategy"])


@pytest.mark.parametrize("path", MANIFESTS, ids=lambda p: p.relative_to(ROOT))
def test_every_param_declares_a_default(path: Path) -> None:
    manifest = load_manifest(path)
    params = manifest["params"]
    assert isinstance(params, dict) and params
    for name, spec in params.items():
        assert isinstance(spec, dict) and "default" in spec, f"param {name!r} needs a default"


@pytest.mark.parametrize("path", MANIFESTS, ids=lambda p: p.relative_to(ROOT))
def test_strategy_reference_imports_and_instantiates(path: Path) -> None:
    manifest = load_manifest(path)
    module_name, _, class_name = str(manifest["strategy"]).partition(":")
    strategy_class = getattr(importlib.import_module(module_name), class_name)
    strategy = strategy_class()
    # Every declared parameter is a real declarative parameter on the class.
    for param_name in manifest["params"]:  # type: ignore[union-attr]
        assert param_name in vars(type(strategy)), f"{path.name}: missing Parameter {param_name!r}"


def test_every_catalog_family_has_a_manifest() -> None:
    families = {str(load_manifest(p)["family"]) for p in MANIFESTS}
    assert families == set(FAMILIES)


def test_manifests_conform_to_step_schema() -> None:
    jsonschema = pytest.importorskip("jsonschema")
    schema = json.loads(SCHEMA_PATH.read_text())
    validator = jsonschema.Draft7Validator(schema)
    errors: list[str] = []
    for path in MANIFESTS:
        for error in validator.iter_errors(load_manifest(path)):
            errors.append(f"{path.name}: {error.message}")
    assert errors == []
