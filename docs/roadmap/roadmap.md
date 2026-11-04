# `vyapaar-strategies` — TDD & Engineering Roadmap

## Milestone 1: Core Strategy Library & Sizing Components (P0)
- [ ] Fix `pyproject.toml` (remove invalid `rust_decimal` dependency).
- [ ] Port `src/honba_strategies/*` into `vyapaar_strategies/`.

## Milestone 2: Declarative `catalog/` & Step Schema Conformance (P0)
- [ ] Port `catalog/` (`arbitrage`, `execution`, `market_making`, `mean_reversion`, `options`, `portfolio`, `size`, `trend`) and `schema/`.
- [ ] Port all tests in `tests/` and verify 100% pass rate under `pytest`.
