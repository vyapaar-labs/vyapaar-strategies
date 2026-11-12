# `vyapaar-strategies` — Migration Verification Milestone

Verification commands for the `honba-strategies → vyapaar-strategies` migration:

```bash
# Run from the repository root
pytest -q
ruff check .
```

## Migration Milestone Status

| Milestone | Status |
|-----------|--------|
| `pyproject.toml` fixed | Complete |
| `vyapaar_strategies/` package ported | Complete |
| `catalog/` declarative `step.toml` manifests | Complete |
| `manifests/` versioned strategy + basket sidecars | Complete |
| `schema/` JSON schemas | Complete |
| `tools/` manifest linters | Complete |
| `tests/` (unit, catalog, manifests, sdk, strategies) | Complete |
| `pytest -q` | Passing |
| `ruff check .` | Clean |
