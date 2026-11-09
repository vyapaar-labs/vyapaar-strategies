# `vyapaar-strategies` — Manifest Reference

Documents `vyapaar_strategies/manifest/`: versioned strategy manifests and basket
strategies for declarative step catalog and visual studio chaining.

## `StrategyManifest`

Versioned manifest for a single strategy. Defines:

- Strategy name and version
- Driving timeframe (aggregation + interval)
- Parameters with `ParameterSpec` (default, min, max, step)
- Indicator declarations
- Warmup bars

## `BasketManifest`

Manifest for a basket of strategies running together. Defines:

- Member strategy references (`MemberStrategyRef`)
- Capital allocation per member (`CapitalAllocation`)
- Promotion status and records (`PromotionRecord`, `PromotionStatus`)
- Instrument selector (`InstrumentSelector`)

## Manifest Promotion Workflow

Strategies progress through promotion statuses:
- `Draft` → `Backtested` → `Paper` → `Live` → `Retired`

Each promotion records a `PromotionRecord` with timestamp, approver, and
performance metrics.

## Schemas

| Schema File | Purpose |
|-------------|---------|
| `step.schema.json` | Step.toml manifest schema |
| `strategy-manifest.schema.json` | Strategy manifest validation |
| `basket-manifest.schema.json` | Basket manifest validation |

## Tools

| Tool | Purpose |
|------|---------|
| `validate_catalog.py` | Lint catalog step.toml manifests |
| `validate_manifests.py` | Validate strategy/basket manifests |

## Related

- `catalog/` — Declarative `step.toml` manifests (`arbitrage/`, `execution/`, `market_making/`, `mean_reversion/`, `options/`, `portfolio/`, `size/`, `trend/`)
- `manifests/strategies/` + `manifests/baskets/` — Versioned strategy and basket sidecars
- `vyapaar-runtime-strategy` — Rust `StrategyManifest` parsing (research-live parity)
