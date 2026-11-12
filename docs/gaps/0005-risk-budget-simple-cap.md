# Gap 0005 — Basket `RiskBudget` Is a Phase-1 Simple Cap; No Allocation Optimizer

**Status**: open — cross-repo dependency on `vyapaar-ledger-allocation`

## What's Stubbed / Hardcoded

`vyapaar_strategies/manifest/basket.py` — the module docstring states it
directly:

> The basket-level risk budget is deliberately a simple cap in Phase 1 (an
> allocation-objective optimizer such as `vyapaar-ledger-allocation` is a later
> integration, out of scope).

`RiskBudget` exposes only two numeric caps:

```python
class RiskBudget(BaseModel):
    max_position_fraction: Decimal | None = None  # in (0, 1]
    max_loss: Decimal | None = None               # >= 0
```

Both are validated as *numbers* on construction (open unit interval / `>= 0`)
but nothing in-repo **enforces** them — there is no run loop (see gap 0004), no
risk-check step, and no allocation objective. Basket capital is split by member
`weight`/`allocation` only; no optimizer targets an objective subject to the
budget.

## Why

The manifest layer's job is to describe *deployable* baskets. A risk budget
that is never consulted is declarative sugar: `max_position_fraction` and
`max_loss` cannot currently bound a live or simulated basket's behavior. The
proper fix belongs to the allocation/optimization side of the ecosystem
(`vyapaar-ledger-allocation`), which is out of this repo's scope — this gap
records the dependency so the Phase-1 simplification is visible.

## How to Close It

1. Integrate an allocation-objective optimizer (e.g.
   `vyapaar-ledger-allocation`) that sizes member capital subject to
   `risk_budget.max_position_fraction` and `max_loss`.
2. In-repo: keep `RiskBudget` as the declarative contract and document that
   enforcement happens in the basket run loop / `vyapaar-runtime-backtest`.
3. Add a test that a `RiskBudget` cap changes a basket's allocation when the
   naive weights would exceed it.

## Verification

A `BasketManifest` with `max_position_fraction = 0.25` produces member
allocations whose total position fraction never exceeds 0.25 when run;
`tests/manifests/` covers the cap math.
