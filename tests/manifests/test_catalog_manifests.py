"""Catalog manifests & baskets: JSON-schema conformance and cross-references."""

from __future__ import annotations

import json
import tomllib
from pathlib import Path

import pytest

from vyapaar_strategies import BasketManifest, StrategyManifest

ROOT = Path(__file__).resolve().parent.parent.parent
MANIFEST_DIR = ROOT / "manifests" / "strategies"
BASKET_DIR = ROOT / "manifests" / "baskets"
STRATEGY_SCHEMA = json.loads((ROOT / "schema" / "strategy-manifest.schema.json").read_text())
BASKET_SCHEMA = json.loads((ROOT / "schema" / "basket-manifest.schema.json").read_text())

MANIFESTS = sorted(MANIFEST_DIR.rglob("*.toml"))
BASKETS = sorted(BASKET_DIR.rglob("*.toml"))


def draft7_validator(schema: dict[str, object]) -> object:
    jsonschema = pytest.importorskip("jsonschema")
    return jsonschema.Draft7Validator(schema)


@pytest.mark.parametrize("path", MANIFESTS, ids=lambda p: p.relative_to(ROOT))
def test_strategy_manifest_conforms_to_schema(path: Path) -> None:
    validator = draft7_validator(STRATEGY_SCHEMA)
    data = tomllib.loads(path.read_text())
    errors = sorted(str(error.message) for error in validator.iter_errors(data))
    assert errors == []


@pytest.mark.parametrize("path", MANIFESTS, ids=lambda p: p.relative_to(ROOT))
def test_strategy_manifest_validates_and_cross_checks(path: Path) -> None:
    manifest = StrategyManifest.load_toml(path)
    assert manifest.validate_parameters() == []
    assert manifest.instantiate() is not None


@pytest.mark.parametrize("path", BASKETS, ids=lambda p: p.relative_to(ROOT))
def test_basket_manifest_conforms_to_schema(path: Path) -> None:
    validator = draft7_validator(BASKET_SCHEMA)
    data = tomllib.loads(path.read_text())
    errors = sorted(str(error.message) for error in validator.iter_errors(data))
    assert errors == []


@pytest.mark.parametrize("path", BASKETS, ids=lambda p: p.relative_to(ROOT))
def test_basket_members_resolve_to_catalog_manifests(path: Path) -> None:
    basket = BasketManifest.load_toml(path)
    versions: dict[str, set[str]] = {}
    for manifest_path in MANIFESTS:
        manifest = tomllib.loads(manifest_path.read_text())
        versions.setdefault(str(manifest["name"]), set()).add(str(manifest["version"]))
    for member in basket.member_strategies:
        assert member.version in versions.get(member.name, set()), (
            f"basket {path.name} references {member.name}@{member.version} which has no manifest"
        )
