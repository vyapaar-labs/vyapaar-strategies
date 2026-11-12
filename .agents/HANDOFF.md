# `vyapaar-strategies` — Inter-Agent Handoff

## Phase / Slice Status
* **Tier 6C (COMPLETE, `af20843`)**: Strategy SDK (`sdk/`) + 10 ported strategy
  classes (`strategies/`) + declarative `catalog/` (10 step.toml, 8 families) +
  `schema/` + `tools/validate_catalog.py`. Source `honba-strategies` was
  unavailable; implemented fresh from contracts.
* **Plan 0001 Layer 3 (COMPLETE, `207a70c`)**: `manifest/` package —
  `StrategyManifest`, `BasketManifest`, `PromotionStatus`/`promote()`
  (exactly-one-stage + `backtest:`/`paper:`/`live:` evidence prefixes). POC
  sidecars `manifests/strategies/{turtle_breakout,twap_slicer}.toml`,
  `manifests/baskets/turtle_twap_basket.toml`; `schema/*-manifest.schema.json`;
  `tools/validate_manifests.py`; 42 tests in `tests/manifests/`.
* **Gate (2026-11-06)**: `pytest` 119/119, `ruff check`/`format --check`,
  `mypy` all PASS. No runtime (`vyapaar-runtime-backtest`) changes — consumption
  is cross-ref only.
* **Docs (this change)**: `docs/roadmap/` dismantled → `docs/design/`
  (rewritten `architecture.md`, `code-{sdk,strategies,manifest,migration-map}.md`,
  new `implementation-record.md`), new `docs/gaps/` (0001–0005), `docs/plans/`
  index updated.

## Decisions & Discoveries
* pyproject: removed `rust_decimal`; declared `vyapaar` + `pydantic`.
* **Zero-float guard (ruff RUF032)**: `Decimal(<float literal>)` is rejected in
  source and tests; all literals are strings.
* `SimulatedContext` holds resting limit orders re-checked per bar — quoting /
  market-making strategies track open quotes via `QuoteState` +
  `on_order_event` (OPEN/COMPLETE) so quotes never stack.
* Bollinger bands in zero-volatility regimes collapse; mean reversion guards
  with `lower < middle` to avoid buy/sell oscillation.
* Donchian channels exclude the current bar (`highs[-N-1:-1]`).
* `on_tick` is a declared stub: neither `Strategy.run` nor
  `SimulatedContext.run` dispatches ticks (bars only) — gap 0001.

## Immediate Next Step
* Open gaps (see `docs/gaps/README.md`): 0001 tick dispatch, 0002 live
  `StrategyContext` (High), 0003 catalog step executor, 0004 `BasketManifest`
  run loop, 0005 Phase-2 risk budget. All cross-repo consumers are out of this
  repo's scope. In-repo slice with the most leverage: a deterministic
  catalog-driven smoke test / step runner (gap 0003) using `SimulatedContext`,
  or a basket run-loop unit test once `vyapaar-runtime-backtest` lands basket
  consumption.

## Operating Invariants
* Zero floats in financial math; `Parameter` bounds/step validated at
  assignment; tests live in `tests/` only.
* `docs/roadmap/` is gone — completed milestones live in
  `docs/design/implementation-record.md`; new work goes to `docs/gaps/`
  (numbered 0006+ if added).
