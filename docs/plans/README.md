# Plans Index — `vyapaar-strategies`

Per workspace rule `.agents/rules/gap-tracking.md`:
- Gaps are individual features (`docs/gaps/XXXX-*.md`).
- Plans are collections of gaps (`docs/plans/XXXX-*.md`).
- When implemented, plan documents are cleaned up from `docs/plans/` and
  recorded in this index.

Dismantled from the former `docs/roadmap/` directory: completed migration
milestones live in [`docs/design/implementation-record.md`](../design/implementation-record.md)
and open gaps in [`docs/gaps/README.md`](../gaps/README.md).

## Active Plans

The current open gaps (see [`docs/gaps/README.md`](../gaps/README.md)) are small
and independent, so they are intentionally **not grouped into a plan document**;
the plan column below is `—` until a plan is written.

| # | Title | Target Scope | Status |
|---|-------|--------------|--------|
| — | (no active plan documents) | — | — |

## Open Gaps (un-grouped)

| Gap | Title | Plan |
|-----|-------|------|
| [0001](../gaps/0001-on-tick-not-dispatched.md) | `Strategy.on_tick` declared but never dispatched | — |
| [0002](../gaps/0002-no-live-strategy-context.md) | No live/feed-backed `StrategyContext` in-repo | — |
| [0003](../gaps/0003-catalog-declarative-only.md) | Catalog `step.toml` is declarative-only; no in-repo step executor | — |
| [0004](../gaps/0004-no-basket-run-loop.md) | No `BasketManifest`-driven run loop in-repo | — |
| [0005](../gaps/0005-risk-budget-simple-cap.md) | Basket `RiskBudget` is a Phase-1 simple cap | — |

## Implemented Plans

| # | Title | Target Scope | Implemented In |
|---|-------|--------------|----------------|
| 0001 | Versioned Strategy Manifests & Basket Strategies | `vyapaar-strategies` | Implemented in commit `207a70c` (`StrategyManifest`, `BasketManifest`, promotion workflow) |
