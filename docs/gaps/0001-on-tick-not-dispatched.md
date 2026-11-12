# Gap 0001 — `Strategy.on_tick` Declared but Never Dispatched

**Status**: open

## What's Stubbed / Missing

`vyapaar_strategies/sdk/strategy.py`:

```python
# -- lifecycle hooks (overridable) -------------------------------------
def on_start(self) -> None: ...
def on_bar(self, bar: Bar) -> None: ...
def on_tick(self, tick: object) -> None: ...
def on_order_event(self, event: OrderEvent) -> None: ...
def on_stop(self) -> None: ...
```

`on_tick` is a no-op stub. Neither driver path ever calls it:
- `Strategy.run(context, bars)` iterates `bars` and calls `on_bar` only
  (`sdk/strategy.py:138-147`).
- `SimulatedContext.run(strategy, bars)` calls `feed` / `on_order_event` /
  `on_bar` per bar — never `on_tick` (`sdk/context.py:87-96`).

A repo-wide grep confirms `on_tick` appears only in the docstring and the stub
definition; nothing in `vyapaar_strategies/` or `tests/` dispatches a tick.

## Why

The SDK advertises a Jesse-style lifecycle including `on_tick`, and the tier
contract names tick-level strategies (`strategies/quoting.py` etc. are
bar-driven, but tick-driven variants are part of the intended API surface).
Until a tick dispatch path exists, a strategy overriding `on_tick` silently
never executes its logic, and live tick feeds (the primary data source for
market-making/quoting) cannot be consumed by this SDK.

## How to Close It

1. Define a canonical `Tick` model (currently `tick: object`).
2. Add a tick-driven entry point — e.g. `Strategy.run(context, ticks)` or a
   `context.feed_tick(tick)` / `on_tick` dispatch in `SimulatedContext`, keeping
   bars and ticks on the same deterministic clock.
3. Wire a per-tick outbox event drain (mirroring the per-bar one) so
   `on_order_event` fires for tick-triggered fills.
4. Add lifecycle tests in `tests/sdk/` covering tick ordering and fills.

## Verification

`grep -rn "on_tick" vyapaar_strategies/` shows a dispatch site (not just the
stub); a tick-fed strategy in `tests/sdk/test_strategy_lifecycle.py` records
ticks in order.
