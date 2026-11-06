# Vyapaar Strategies (`vyapaar-strategies`)

**Bounded Context**: Production Strategy SDK & Declarative Step Catalog (Tier 6C)

`vyapaar-strategies` is the canonical quantitative strategy repository for the
Vyapaar Labs ecosystem. It follows a Jesse-style Python strategy authoring
model (`on_start` / `on_bar` / `on_tick` / `on_order_event` / `on_stop`) with
declarative `Parameter(default=..., min=..., max=..., step=...)` hyperparameters
and strict research-live parity — the exact same strategy class runs against
historical bars and live WebSocket feeds.

## Included Strategy Families

| Family | Module | Catalog |
| :--- | :--- | :--- |
| Quoting | `vyapaar_strategies.strategies.quoting` | `catalog/` |
| Cash–Futures Arbitrage | `vyapaar_strategies.strategies.arbitrage` | `catalog/arbitrage/` |
| Market Making | `vyapaar_strategies.strategies.market_making` | `catalog/market_making/` |
| Mean Reversion (Bollinger) | `vyapaar_strategies.strategies.mean_reversion` | `catalog/mean_reversion/` |
| Turtle Breakout | `vyapaar_strategies.strategies.turtle` | `catalog/trend/` |
| Risk Parity | `vyapaar_strategies.strategies.risk_parity` | `catalog/portfolio/` |
| TWAP / VWAP Slicers | `vyapaar_strategies.strategies.execution` | `catalog/execution/` |

## Layout (4-Zone Clean Package)

```
vyapaar-strategies/
├── vyapaar_strategies/   # Zone 1: strategy SDK + strategies
├── catalog/              # Zone 2: declarative step.toml manifests
├── tests/                # Zone 3: unit / parity / catalog schema validation
├── schema/               # Zone 4: step.schema.json
├── tools/                # Zone 4: manifest linters
└── docs/                 # Zone 4: architecture & migration guides
```

## Quick Start

```python
from vyapaar_strategies import TurtleBreakout
from vyapaar_strategies.sdk import SimulatedContext

strategy = TurtleBreakout(entry_period=20, exit_period=10)
context = SimulatedContext("NSE:NIFTY50-INDEX", seed=42)
strategy.run(context)
```

## Development

```bash
make test      # pytest -q
make lint      # ruff check .
make check     # lint + format-check + type-check + tests
```

## Verification Gate

```bash
pytest -q
ruff check .
```
