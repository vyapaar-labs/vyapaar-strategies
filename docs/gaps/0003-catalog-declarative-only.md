# Gap 0003 — Catalog `step.toml` Is Declarative-Only; No In-Repo Step Executor

**Status**: open — cross-repo dependency on `vyapaar-runtime` / `vyapaar-ui`

## What's Stubbed / Missing

`catalog/**/*.toml` (10 files across 8 families) names each strategy as
`strategy = "vyapaar_strategies.<module>:<Class>"` plus tunable `[params.*]`
defaults. In this repo these manifests are **validated but never executed**:

- `tools/validate_catalog.py` checks required keys, JSON-schema conformance
  (`schema/step.schema.json`), and that the `module:Class` reference imports and
  instantiates.
- `tests/catalog/test_catalog.py` does the same conformance + strategy-class
  parity checks.

There is no in-repo code that loads a `catalog/*.toml`, builds the strategy,
feeds it bars, and runs it (no executor / runner / CLI). The step schema's own
description points consumption outward: *"for visual-studio chaining and Rust
`StepManifest` parsing"* — i.e. `vyapaar-ui` (Strategy Studio canvas) and
`vyapaar-runtime` (backtest/live step runner), both out of this repo.

## Why

The catalog is the declarative contract between this repo and downstream
consumers, but without an in-repo (or verified cross-repo) executor, a
`step.toml` cannot be *proven runnable* — only importable. Any drift between a
TOML's parameter defaults and the strategy's `Parameter` bounds is caught by
validation, but behavioral drift (does this step produce orders on this bar
series?) is not.

## How to Close It

1. Either implement a thin in-repo executor (`tools/run_step.py` or a
   `catalog`-consuming test) that loads each `step.toml`, runs the strategy
   through `SimulatedContext`, and asserts it produces no exceptions —
   **or**
2. Wire the cross-repo consumer (`vyapaar-runtime-backtest` step runner /
   `vyapaar-ui` canvas) and add a CI smoke test here that invokes it.
3. Either way, extend `tests/catalog/` from "imports and instantiates" to "runs
   N bars deterministically".

## Verification

A `catalog/**/*.toml` is loaded and run against a deterministic bar series in
`tests/catalog/`, and `python tools/validate_catalog.py` still passes.
