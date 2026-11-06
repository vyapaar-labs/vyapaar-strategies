# `vyapaar-strategies` — DDD Architecture & Strategy Catalog Bounded Context

## 1. Bounded Context & Responsibility
`vyapaar-strategies` (Tier 6C, ported from `honba-strategies`) is the **Production Quantitative Strategy SDK & Declarative Step Catalog** housing institutional algorithms (Arbitrage, Execution Slicers, Market Making, Mean Reversion, Options, Portfolio Construction, Position Sizing, Trend Following).

## 2. 4-Zone Clean Architecture
* **Zone 1 (`vyapaar_strategies/`)**: Pure Python 3.11+ strategy classes using `decimal.Decimal` and `vyapaar` domain primitives; `manifest/` subpackage holds the versioned `StrategyManifest`/`BasketManifest` models and promotion workflow (plan 0001, Layer 3).
* **Zone 2 (`catalog/` & `manifests/`)**: Declarative `step.toml` manifests (`arbitrage/`, `execution/`, `market_making/`, `mean_reversion/`, `options/`, `portfolio/`, `size/`, `trend/`) for visual studio chaining and Rust `StepManifest` parsing; `manifests/strategies/` + `manifests/baskets/` hold the versioned strategy and basket sidecars.
* **Zone 3 (`tests/`)**: Unit, parity, and catalog manifest schema validation tests (`tests/unit/`, `tests/catalog/`, `tests/manifests/`).
* **Zone 4 (`schema/` & `tools/`)**: `step.schema.json`, `strategy-manifest.schema.json`, `basket-manifest.schema.json`, and manifest linters (`validate_catalog.py`, `validate_manifests.py`).
