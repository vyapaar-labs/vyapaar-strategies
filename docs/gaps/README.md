# Gap Index — `vyapaar-strategies`

Per workspace rule `.agents/rules/gap-tracking.md`:
- **Gaps** (`docs/gaps/XXXX-*.md`): individual missing features, stubs, or
  cross-repo dependencies.
- **Plans** (`docs/plans/XXXX-*.md`): collections of gaps.
- Numbering is per-repo, sequential, never reused.

Dismantled from the former `docs/roadmap/` directory: every completed milestone
now lives in [`docs/design/`](../design/architecture.md) +
[`docs/design/implementation-record.md`](../design/implementation-record.md);
the remaining future work is enumerated below.

## Open Gaps

| # | Title | Severity | Status | Plan |
|---|-------|----------|--------|------|
| [0001](0001-on-tick-not-dispatched.md) | `Strategy.on_tick` declared but never dispatched | Medium | Open | — |
| [0002](0002-no-live-strategy-context.md) | No live/feed-backed `StrategyContext` in-repo (only `SimulatedContext`) | High | Open | — |
| [0003](0003-catalog-declarative-only.md) | Catalog `step.toml` is declarative-only; no in-repo step executor | Medium | Open | — |
| [0004](0004-no-basket-run-loop.md) | No `BasketManifest`-driven run loop in-repo | Medium | Open | — |
| [0005](0005-risk-budget-simple-cap.md) | Basket `RiskBudget` is a Phase-1 simple cap; no allocation optimizer | Low | Open | — |

The gaps are small and independent, so they are intentionally **not grouped
into a plan**; the plan column is `—`.

## Closed Gaps

| # | Title | Closed In |
|---|-------|-----------|
| — | — | (none yet) |
