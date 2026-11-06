# `vyapaar-strategies` — Inter-Agent Handoff

## Phase / Slice Status
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
* Tier 6D: `vyapaar-examples` (numbered learning path with `Pitfalls::`
  docstrings, `ScriptedFakeLlm`, per-example regression tests).

## Operating Invariants
* Zero floats in financial math; `Parameter` bounds/step validated at
  assignment; tests live in `tests/` only.
