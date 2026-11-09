# `vyapaar-strategies` — Historical Migration Map (honba-strategies → vyapaar-strategies)

> **Tier**: Tier 6C
> **Source**: `/home/pmallapp/Devel/Finance/honba-workspace/honba-strategies`
> **Target**: `/home/pmallapp/Devel/Finance/vyapaar-labs/vyapaar-strategies`
> **Status**: Migration complete.

## Migration & DDD Refactoring Steps

### 1. Fix `pyproject.toml`

- Remove invalid `"rust_decimal>=1.0.0"` from `vyapaar-strategies/pyproject.toml`.

### 2. Port Strategy Library & Catalog

- Copy `honba-workspace/honba-strategies/src/honba_strategies/*` (or package modules) into `vyapaar-labs/vyapaar-strategies/vyapaar_strategies/`.
- Copy `catalog/`, `schema/`, `tools/`, and `tests/` into `vyapaar-labs/vyapaar-strategies/`.
- Replace `honba_strategies` → `vyapaar_strategies` and `honba` → `vyapaar` across all Python files, `step.toml` manifests, and `registry.json`.

## Verification Commands

```bash
cd /home/pmallapp/Devel/Finance/vyapaar-labs/vyapaar-strategies
pytest -q
ruff check .
```

## Migration Milestone Status

| Milestone | Status |
|-----------|--------|
| `pyproject.toml` fixed (invalid `rust_decimal` removed) | Complete |
| Strategy library ported (`vyapaar_strategies/`) | Complete |
| `catalog/` (`arbitrage`, `execution`, `market_making`, `mean_reversion`, `options`, `portfolio`, `size`, `trend`) | Complete |
| `manifests/` (strategy + basket sidecars) | Complete |
| `schema/` (`step.schema.json`, manifest schemas) | Complete |
| `tools/` (manifest linters) | Complete |
| `tests/` (unit, catalog, manifests, sdk, strategies) | Complete |
| `pytest -q` | Passing |
| `ruff check .` | Clean |
