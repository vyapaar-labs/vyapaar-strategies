# `vyapaar-strategies` — TDD & Engineering Roadmap

## Milestone 1: Core Strategy Library & Sizing Components (P0) — [COMPLETED]
- [x] Fix `pyproject.toml` (remove invalid `rust_decimal` dependency).
- [x] Port `src/honba_strategies/*` into `vyapaar_strategies/`.

## Milestone 2: Declarative `catalog/` & Step Schema Conformance (P0) — [COMPLETED]
- [x] Port `catalog/` (`arbitrage`, `execution`, `market_making`, `mean_reversion`, `options`, `portfolio`, `size`, `trend`) and `schema/`.
- [x] Port all tests in `tests/` and verify 100% pass rate under `pytest`.

## Migration Verification — [COMPLETED]
- [x] `pytest -q` — passing
- [x] `ruff check .` — clean
- [x] `ruff format --check .` — clean
- [x] Zero floats — all prices, stop levels, quantities use `decimal.Decimal`
- [x] Parallel test directory rule — tests in `tests/`, not inline

See `docs/roadmap/migration-verification.md` for full migration milestone status.
