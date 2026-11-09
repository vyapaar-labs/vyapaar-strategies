# `vyapaar-strategies` — Strategy SDK Reference

Documents `vyapaar_strategies/sdk/`: the Python-first strategy SDK with Jesse-style
lifecycle hooks and declarative parameters.

## `Strategy` Base Class

The base class all strategies inherit from. Provides lifecycle hooks:

| Hook | Purpose |
|------|---------|
| `on_start()` | Called once before the first bar — initialize indicators, state |
| `on_bar(bar)` | Called on each new bar — main strategy logic |
| `on_tick(tick)` | Called on each new tick — for tick-level strategies |
| `on_order_event(event)` | Called on order status changes |
| `on_stop()` | Called when strategy stops — cleanup |

## Order Helpers

| Method | Purpose |
|--------|---------|
| `self.buy(instrument, quantity, ...)` | Place a buy order |
| `self.sell(instrument, quantity, ...)` | Place a sell order |
| `self.stop_loss(...)` | Attach a stop-loss to a position |

## Indicators

| Indicator | Purpose |
|-----------|---------|
| `SMA(period)` | Simple Moving Average |
| `EMA(period)` | Exponential Moving Average |
| `RSI(period)` | Relative Strength Index |
| `ATR(period)` | Average True Range |
| `BollingerBands(period, deviations)` | Bollinger Bands |

## `IndicatorRegistry`

Per-(instrument, kind, params) indicator store. Strategies request indicators once
in `on_start`; the same streaming instance is fed by every bar.

```python
self.sma = self.indicators.sma("NSE:NIFTY50-INDEX", 20)
self.rsi = self.indicators.rsi("NSE:NIFTY50-INDEX", 14)
```

## `Parameter`

Declarative parameter descriptors for tunable inputs:

```python
fast_period = Parameter(default=10, min=5, max=50, step=5)
```

## Zero-Floats Policy

All prices, stop levels, and quantities use `decimal.Decimal` — no `float` in
financial calculations.

## Related

- `vyapaar_strategies/strategies/` — Ported StockSharp strategies
- `vyapaar_strategies/manifest/` — Versioned `StrategyManifest` / `BasketManifest`
- `vyapaar-runtime-strategy` — Rust `Strategy` trait (research-live parity)
