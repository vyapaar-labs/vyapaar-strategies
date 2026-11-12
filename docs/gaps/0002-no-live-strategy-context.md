# Gap 0002 — No Live / Feed-Backed `StrategyContext` in Repo

**Status**: open — cross-repo dependency on `vyapaar-runtime` / `vyapaar-exec`

## What's Missing

`vyapaar_strategies/sdk/context.py` defines the execution seam:

```python
@runtime_checkable
class StrategyContext(Protocol):
    def submit(self, request: OrderRequest) -> OrderEvent: ...
    def current_price(self, instrument: str) -> Decimal: ...
    def position(self, instrument: str) -> Decimal: ...
```

The **only** concrete implementation in this repo is `SimulatedContext`
(offline, deterministic, bar-fed). `Strategy.run(context, bars)` accepts any
`StrategyContext`, but no live/feed-backed implementation exists in-repo — a
repo-wide grep finds `SimulatedContext` as the only concrete class. There is no
feed adapter, no broker/WebSocket-backed `current_price`, no live order
submission.

## Why

The tier contract is strict research–live parity: the exact same strategy class
must run against historical bars offline and live WebSocket feeds. The
`StrategyContext` protocol is the parity seam, but parity is currently one-sided
— strategies can be *authored* once, yet cannot be *executed* live from this
repo. A live context is properly owned by the execution/feed side of the
pipeline (`vyapaar-runtime` strategy runner / `vyapaar-exec` gateway), which is
out of this repo's scope; this gap records that no such adapter is wired here.

## How to Close It

1. Implement a `StrategyContext` (or a `LiveContext` subclass) backed by a
   `MarketDataFeed` and an `ExecutionGateway` — the canonical Vyapaar adapter
   traits defined by `vyapaar-market` / `vyapaar-exec`.
2. In this repo: keep the protocol as the contract and add a compatibility test
   that any injected `StrategyContext` drives `on_start`/`on_bar`/`on_stop`
   through `Strategy.run`'s non-`SimulatedContext` branch (already exercised in
   `sdk/strategy.py`).
3. Confirm parity: identical strategy class + identical timestamped bars
   produce identical order streams under `SimulatedContext` and the live
   context.

## Verification

`grep -rn "class .*Context" vyapaar_strategies/` lists a live context alongside
`SimulatedContext`; `Strategy.run` drives it and `tests/sdk/` covers the
non-simulated branch.
