#!/usr/bin/env python3
"""Validate every ``manifests/strategies/*.toml`` and ``manifests/baskets/*.toml``.

Strategy manifests are checked against ``strategy-manifest.schema.json``, the
``StrategyManifest`` pydantic model, and their strategy class (every declared
parameter must exist and its default must pass bounds). Basket manifests are
checked against ``basket-manifest.schema.json``, the ``BasketManifest`` model,
and that every member reference resolves to a ``manifests/strategies`` file.

Run:  python tools/validate_manifests.py
"""

from __future__ import annotations

import importlib
import json
import sys
import tomllib
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
# Make the strategy package importable when the tool runs from a source tree.
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

MANIFEST_DIR = ROOT / "manifests" / "strategies"
BASKET_DIR = ROOT / "manifests" / "baskets"
STRATEGY_SCHEMA_PATH = ROOT / "schema" / "strategy-manifest.schema.json"
BASKET_SCHEMA_PATH = ROOT / "schema" / "basket-manifest.schema.json"


def load_strategy_manifests() -> dict[str, set[str]]:
    """Map manifest name -> {versions} from the strategy manifest directory."""
    registry: dict[str, set[str]] = {}
    for path in sorted(MANIFEST_DIR.rglob("*.toml")):
        data = tomllib.loads(path.read_text())
        registry.setdefault(str(data["name"]), set()).add(str(data["version"]))
    return registry


def load_validator(schema_path: Path):
    try:
        import jsonschema  # type: ignore[import-not-found]

        return jsonschema.Draft7Validator(json.loads(schema_path.read_text()))
    except ImportError:
        return None


def schema_errors(data: dict[str, object], validator: object) -> list[str]:
    if validator is None:
        return []
    return sorted(str(error.message) for error in validator.iter_errors(data))


def validate_strategy_manifest(path: Path, validator: object) -> list[str]:
    data = tomllib.loads(path.read_text())
    errors = schema_errors(data, validator)
    strategies = importlib.import_module("vyapaar_strategies")
    try:
        manifest = strategies.StrategyManifest.model_validate(data)
    except Exception as exc:
        return [*errors, f"StrategyManifest rejected {path.name}: {exc}"]
    errors.extend(f"parameter {error}" for error in manifest.validate_parameters())
    try:
        manifest.instantiate()
    except Exception as exc:
        errors.append(f"instantiate() failed: {exc}")
    return errors


def validate_basket_manifest(
    path: Path, validator: object, registry: dict[str, set[str]]
) -> list[str]:
    data = tomllib.loads(path.read_text())
    errors = schema_errors(data, validator)
    strategies = importlib.import_module("vyapaar_strategies")
    try:
        basket = strategies.BasketManifest.model_validate(data)
    except Exception as exc:
        return [*errors, f"BasketManifest rejected {path.name}: {exc}"]
    for member in basket.member_strategies:
        if member.version not in registry.get(member.name, set()):
            errors.append(
                f"member {member.name}@{member.version} has no strategy manifest in {MANIFEST_DIR}"
            )
    return errors


def main() -> int:
    strategy_validator = load_validator(STRATEGY_SCHEMA_PATH)
    basket_validator = load_validator(BASKET_SCHEMA_PATH)
    registry = load_strategy_manifests()
    failures = 0
    for path in sorted(MANIFEST_DIR.rglob("*.toml")):
        errors = validate_strategy_manifest(path, strategy_validator)
        print(f"{'FAIL' if errors else 'ok'}   {path.relative_to(ROOT)}")
        for error in errors:
            print(f"  - {error}")
        failures += bool(errors)
    for path in sorted(BASKET_DIR.rglob("*.toml")):
        errors = validate_basket_manifest(path, basket_validator, registry)
        print(f"{'FAIL' if errors else 'ok'}   {path.relative_to(ROOT)}")
        for error in errors:
            print(f"  - {error}")
        failures += bool(errors)
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
