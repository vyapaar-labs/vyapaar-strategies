# Gap 0004 — No `BasketManifest`-Driven Run Loop in Repo

**Status**: open — cross-repo dependency on `vyapaar-runtime-backtest`

## What's Missing

`vyapaar_strategies/manifest/basket.py` models and validates a basket of
strategy versions under one combined capital and risk budget
(`BasketManifest`, `MemberStrategyRef`, `RiskBudget`). In this repo the basket
is **metadata-only**:

- `tools/validate_manifests.py` and `tests/manifests/` prove the TOML sidecar
  conforms to `basket-manifest.schema.json`, the pydantic model validates, and
  every `member_strategies` reference resolves to a `manifests/strategies/`
  file.
- Nothing in-repo instantiates the member strategies, sizes them by
  weight/allocation, enforces the risk budget, or runs them together.

The runtime consumption path is cross-referenced by the module docstring
(`vyapaar-runtime-backtest`), not implemented here.

## Why

A basket is only useful when something *executes* it as a logical unit:
allocate `combined_capital` across members (by `weight`/`allocation`), run each
`StrategyManifest.instantiate()` through an execution context, and apply the
`risk_budget` caps. Until then, a `BasketManifest` describes a portfolio that
this repo cannot run, and the Phase-1 budget caps are unchecked at runtime
(they are validated as numbers, never enforced on positions).

## How to Close It

1. Implement a basket run loop: for each `MemberStrategyRef`, resolve the
   `StrategyManifest` sidecar, `instantiate()` it, and run it with a capital
   slice derived from `weight * combined_capital` (or `allocation`).
2. Enforce `risk_budget` (e.g. abort/re-scale when total position fraction
   exceeds `max_position_fraction` or loss exceeds `max_loss`).
3. Keep the run loop deterministic under `SimulatedContext` and add
   `tests/manifests/` coverage (or land it in `vyapaar-runtime-backtest` and
   smoke-test from here).

## Verification

Running the `turtle_twap_basket` sidecar through the loop consumes exactly
`combined_capital` (weights sum to 1.0) and produces deterministic order streams
for both members; `python tools/validate_manifests.py` still passes.
