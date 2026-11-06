# `vyapaar-strategies` — Inter-Agent Handoff

## Phase / Slice Status
* **Layer 3 (COMPLETE, 2026-11-06)**: plan 0001 — Versioned Strategy Manifests &
  Baskets (all 3 phases). New `vyapaar_strategies/manifest/` package:
  `StrategyManifest` (name/semver/module:Class/parameters/target_instruments/
  capital_allocation), `BasketManifest` (member weight-XOR-allocation refs,
  combined-capital budget, Phase-1 `RiskBudget` caps), `PromotionStatus`
  workflow (`promote()` = exactly one stage forward + status-prefixed evidence
  ref `backtest:`/`paper:`/`live:`, audited into `promotion_evidence`).
  POC sidecars: `manifests/strategies/{turtle_breakout,twap_slicer}.toml`,
  `manifests/baskets/turtle_twap_basket.toml`. Zone 4: `schema/strategy-manifest
  .schema.json`, `schema/basket-manifest.schema.json`,
  `tools/validate_manifests.py`. 42 new tests in `tests/manifests/`.
  Gate: `pytest` 119/119, `ruff check`/`format --check`, `mypy` all PASS.
  No runtime (`vyapaar-runtime-backtest`) changes — consumption is cross-ref only.
* **Tier 6C (COMPLETE)**: Implemented the Production Strategy SDK & Declarative
  Step Catalog from the sub-guide contracts (source `honba-strategies`
  unavailable; implemented fresh).
* Package `vyapaar_strategies/`:
  * `sdk/`: `Parameter` (declarative, validated bounds + step alignment),
    `Bar`, order domain (`OrderRequest`/`OrderEvent`/enums), streaming
    `Decimal` indicators (SMA/EMA/RSI/ATR/Bollinger + cross helpers),
    `SimulatedContext` (resting limit orders, deterministic fills),
    `Strategy` base (Jesse-style hooks + `indicators` registry), `QuoteState`
    mixin (single resting quote per side).
  * `strategies/`: `turtle`, `mean_reversion`, `market_making`, `quoting`,
    `arbitrage`, `risk_parity`, `execution` (TWAP/VWAP slicers), `options`
    (covered call), `sizing` (fixed-fractional).
* Zone 2 `catalog/`: 10 `step.toml` manifests across all 8 families.
  Zone 4: `schema/step.schema.json` + `tools/validate_catalog.py` (validates
  schema + strategy importability).

## Decisions & Discoveries
* pyproject: removed `rust_decimal`; declared `vyapaar` + `pydantic`.
* **Zero-float guard (ruff RUF032)**: `Decimal(<float literal>)` is rejected in
  source and tests; all literals are strings.
* `SimulatedContext` holds resting limit orders re-checked per bar — posting a
  fresh quote each bar without cancellation would stack duplicates; quoting /
  market-making strategies therefore track open quotes via `QuoteState` and
  `on_order_event` (OPEN/COMPLETE).
* Bollinger bands in zero-volatility regimes (stddev == 0) collapse to a
  single line; mean reversion guards with `lower < middle` to avoid
  buy/sell oscillation.
* Donchian channels exclude the current bar (`highs[-N-1:-1]`).

## Immediate Next Step
* Layer 4A (`vyapaar-agent/0003` remaining Fincept analytics engines, benefits
  from Layer 0) and Layer 4B (`vyapaar-agent/0004` free-tier LLM backend, fully
  independent) are the next layers in the bottoms-up build order. In this repo,
  next logical slice is a `BasketManifest`-driven multi-strategy run loop when
  `vyapaar-runtime-backtest` gains basket consumption (out of this repo's scope).

## Operating Invariants
* Zero floats in financial math; `Parameter` bounds/step validated at
  assignment; tests live in `tests/` only.
