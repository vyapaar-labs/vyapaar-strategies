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
├── vyapaar_strategies/   # Zone 1: strategy SDK + strategies + manifest models
├── catalog/              # Zone 2: declarative step.toml manifests
├── manifests/            # Zone 2: versioned strategy & basket manifests (plan 0001)
│   ├── strategies/       #   StrategyManifest sidecars (turtle_breakout, twap_slicer, ...)
│   └── baskets/          #   BasketManifest groupings
├── tests/                # Zone 3: unit / parity / catalog schema validation
├── schema/               # Zone 4: step + strategy/basket manifest JSON schemas
├── tools/                # Zone 4: manifest linters
└── docs/                 # Zone 4: architecture & migration guides
```

## Versioned Strategy Manifests & Baskets

Every strategy can carry a versioned, promotable manifest (plan 0001, Layer 3):
`name`, semver `version`, `module:Class` reference, parameter defaults, target
instruments, and a capital allocation (absolute `Money` amount or weight). A
`BasketManifest` groups several strategy versions under one combined capital and
risk budget. Promotion follows `draft → backtested → paper → live`, each step
requiring a justifying evidence reference.

```python
from vyapaar_strategies import BasketManifest, PromotionStatus, StrategyManifest

turtle = StrategyManifest.load_toml("manifests/strategies/turtle_breakout.toml")
turtle.promote(PromotionStatus.BACKTESTED, "backtest:run/2026-01-05/bt-123")

basket = BasketManifest.load_toml("manifests/baskets/turtle_twap_basket.toml")
for member in basket.member_strategies:  # weights are exact Decimal fractions
    print(member.name, member.weight)
```

Validate every manifest sidecar with:

```bash
python tools/validate_manifests.py   # schema + model + strategy class + basket refs
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
