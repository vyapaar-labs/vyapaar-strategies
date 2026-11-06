# 0001 — Versioned Strategy Manifests & Basket Strategies

> **Status**: Proposed — not yet implemented.
> **Target Crates**: vyapaar-strategies (Python strategy definitions); cross-references vyapaar-runtime-strategy / vyapaar-runtime-backtest (Rust, not modified here)
> **Depends on reading**:
> - (none external)

---

## 0. Executive Summary & Objective

Fincept's `algo` toolset (algorithm library, versions, baskets, paper deployments) has no clean equivalent in Vyapaar today. `vyapaar-strategies` already has production strategies — Quoting, Arbitrage, TWAP/VWAP slicers, Turtle breakout, Risk Parity — but no versioning scheme for any of them, and no "basket" concept for running several strategies together as one logical unit with combined risk and capital allocation. This doc proposes a `StrategyManifest` / `BasketManifest` schema to close both gaps.

---

## 1. Context

`vyapaar-strategies`'s own `AGENTS.md` describes it as "Production Strategies — Ported StockSharp strategies (Quoting, Arbitrage, TWAP/VWAP slicers, Turtle breakout, Risk Parity)." There is no versioned-strategy-manifest or basket-of-strategies concept in this repo, nor in `vyapaar-runtime`'s `vyapaar-runtime-strategy` or `vyapaar-runtime-backtest` crates (the latter has `catalog.rs` and `engine.rs`). Today, running more than one strategy together, or tracking which parameter version of a strategy produced a given backtest or live result, has no structured representation — it's implicit in whatever script or config a user wires up by hand.

This doc's scope is the manifest schema and the Python-side authoring convention in `vyapaar-strategies`. It is consumed by, but does not modify, `vyapaar-runtime-backtest`'s existing `catalog.rs` (strategy registration/lookup) and `engine.rs` (execution loop) — those two files are cross-referenced here as the eventual consumers of the manifest, not as files this doc changes.

---

## 2. Component Specifications

- `StrategyManifest` — a schema (e.g. a `strategy.yaml`/`strategy.toml` sidecar file or an in-module Python declaration) stored alongside each strategy's existing Python module, covering: `name`, `version` (semantic version string), `parameters` (the `Parameter(...)` declarations a strategy already exposes per the workspace's Python-first SDK architecture — `fast_period = Parameter(default=10, min=5, max=50, step=5)`-style), `target_instruments` (a list of `InstrumentId`s or instrument-selection rule), and `capital_allocation` (either an absolute `Money` amount or a weight, to be reconciled against whatever the consuming runtime's capital model expects).
- `BasketManifest` — a schema that groups several `StrategyManifest` references under one combined capital/risk budget: `basket_name`, `member_strategies: list[StrategyManifestRef]`, `combined_capital: Money`, and a basket-level risk budget (deliberately left as a simple cap in Phase 1 rather than a full allocation-objective — if `vyapaar-ledger-allocation` exists by the time this is built, it would be the natural optimizer for basket-level weight decisions, but that integration is out of scope for this doc).
- Consumption path (not modified here, only cross-referenced): `vyapaar-runtime-backtest/src/catalog.rs` would register manifests for discovery, and `vyapaar-runtime-backtest/src/engine.rs` would read a `BasketManifest` to drive a multi-strategy backtest run as one logical unit instead of one strategy at a time.

---

## 3. Implementation Phases

### Phase 1: Manifest schema + proof of concept
Define the `StrategyManifest` schema and retrofit it onto 1-2 existing strategies (e.g. a TWAP/VWAP slicer and the Turtle breakout strategy) as a proof of concept, with no runtime consumption yet — just the schema and the sidecar files/declarations living next to the existing strategy modules.

### Phase 2: Basket grouping + combined capital allocation
Define `BasketManifest`, group the Phase 1 proof-of-concept strategies into a basket, and specify how combined capital/risk budget is represented and validated (e.g. member allocations summing to at most the basket's `combined_capital`).

### Phase 3: Versioning / promotion workflow
Define the draft → backtested → paper → live promotion workflow for a `StrategyManifest` version: what evidence (which backtest run, which paper-trading window) is required to advance a version's status, and how that status is recorded (likely as a field on the manifest itself, e.g. `promotion_status` plus a reference to the backtest/paper run that justified the promotion).
