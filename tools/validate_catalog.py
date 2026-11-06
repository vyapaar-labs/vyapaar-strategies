#!/usr/bin/env python3
"""Validate every ``catalog/**/step.toml`` manifest against ``step.schema.json``.

Also verifies that each ``strategy = module:Class`` reference imports and
instantiates, so the catalog never points at a missing strategy.

Run:  python tools/validate_catalog.py
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

CATALOG_DIR = ROOT / "catalog"
SCHEMA_PATH = ROOT / "schema" / "step.schema.json"

MANIFEST_SCHEMA = {
    "name": str,
    "title": str,
    "family": str,
    "version": str,
    "strategy": str,
    "params": dict,
}


def load_schema() -> dict[str, object]:
    try:
        import jsonschema  # type: ignore[import-not-found]

        return {"validator": jsonschema.Draft7Validator(json.loads(SCHEMA_PATH.read_text()))}
    except ImportError:
        return {"validator": None}


def validate_manifest(manifest: dict[str, object], path: Path) -> list[str]:
    errors: list[str] = []
    for required, expected in MANIFEST_SCHEMA.items():
        value = manifest.get(required)
        if value is None:
            errors.append(f"missing required key {required!r}")
        elif not isinstance(value, expected):
            errors.append(f"{required!r} must be {expected.__name__}, got {type(value).__name__}")
    if isinstance(manifest.get("params"), dict):
        for param_name, spec in manifest["params"].items():  # type: ignore[union-attr]
            if not isinstance(spec, dict) or "default" not in spec:
                errors.append(f"param {param_name!r} requires a default")
    strategy = manifest.get("strategy")
    if isinstance(strategy, str):
        module_name, _, class_name = strategy.partition(":")
        if not module_name or not class_name:
            errors.append(f"strategy {strategy!r} must be module:Class")
        else:
            try:
                strategy_class = getattr(importlib.import_module(module_name), class_name)
                strategy_class()
            except Exception as exc:
                errors.append(f"strategy {strategy!r} failed to import/instantiate: {exc}")
    else:
        errors.append("strategy must be a string")
    return errors


def main() -> int:
    validator = load_schema()
    failures = 0
    for path in sorted(CATALOG_DIR.rglob("*.toml")):
        manifest = tomllib.loads(path.read_text())
        errors = validate_manifest(manifest, path)
        if validator["validator"] is not None:
            schema_errors = sorted(validator["validator"].iter_errors(manifest))  # type: ignore[union-attr]
            errors.extend(str(error.message) for error in schema_errors)
        if errors:
            failures += 1
            print(f"FAIL {path.relative_to(ROOT)}")
            for error in errors:
                print(f"  - {error}")
        else:
            print(f"ok   {path.relative_to(ROOT)}")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
