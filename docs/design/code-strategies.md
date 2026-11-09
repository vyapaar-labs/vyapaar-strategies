# `vyapaar-strategies` — Ported StockSharp Strategies Reference

Documents `vyapaar_strategies/strategies/`: production quantitative strategies
ported from StockSharp, with Jesse-style lifecycle hooks.

## Strategies

| Strategy | File | Type | Description |
|----------|------|------|-------------|
| `QuotingStrategy` | `quoting.py` | Market Making | Two-sided quoting with spread capture |
| `CashFuturesArbitrage` | `arbitrage.py` | Arbitrage | Cash-futures basis arbitrage |
| `MarketMakingStrategy` | `market_making.py` | Market Making | Continuous bid/ask quoting |
| `BollingerMeanReversion` | `mean_reversion.py` | Mean Reversion | Bollinger Band mean reversion |
| `CoveredCallWriter` | `options.py` | Options | Covered call income strategy |
| `TWAPSlicer` / `VWAPSlicer` | `execution.py` | Execution | TWAP/VWAP order slicers |
| `RiskParity` | `risk_parity.py` | Portfolio | Risk parity position sizing |
| `TurtleBreakout` | `turtle.py` | Trend Following | Turtle breakout system |
| `FixedFractional` | `sizing.py` | Position Sizing | Fixed fractional position sizing |

## Common Pattern

```python
class MyStrategy(Strategy):
    param1 = Parameter(default=..., min=..., max=..., step=...)
    
    def on_start(self):
        self.indicator = self.indicators.sma("NSE:RELIANCE-EQ", 20)
    
    def on_bar(self, bar: Bar):
        if signal:
            self.buy("NSE:RELIANCE-EQ", quantity=Decimal("100"))
    
    def on_order_event(self, event: OrderEvent):
        self.logger.info(f"Order {event.order_id}: {event.status}")
```

## Research-Live Parity

The exact same strategy class executes against:
- Historical Parquet bars (backtest via `vyapaar-runtime-backtest`)
- Live WebSocket feeds (production via `vyapaar-exec`)

## Zero-Floats Policy

All prices, stop levels, and quantities use `decimal.Decimal`.

## Related

- `vyapaar_strategies/sdk/` — Strategy base class, indicators, parameters
- `vyapaar_strategies/manifest/` — Versioned `StrategyManifest`
- `catalog/` — Declarative `step.toml` manifests per strategy type
- `tests/strategies/` — Unit tests for each strategy
