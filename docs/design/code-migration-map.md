# `vyapaar-strategies` — Historical Migration Map (`honba-strategies` → `vyapaar-strategies`)

> **Tier**: Tier 6C
> **Source**: `honba-workspace/honba-strategies`
> **Target**: `vyapaar-strategies`
> **Status**: Migration complete — see [`implementation-record.md`](implementation-record.md).

## What was migrated

The source `honba-strategies` codebase was unavailable, so the strategy SDK and
catalog were **implemented fresh** from the sub-guide contracts and the
StockSharp/Jesse idea-inheritance catalog. The tier claims in the roadmap
(`honba-strategies → vyapaar-strategies`) are therefore a *conceptual* port:
the package layout, strategy families, and declarative catalog were rebuilt in
`vyapaar-strategies` rather than copied file-for-file.

## Layout mapping

| Former / source concept | `vyapaar-strategies` |
|-------------------------|-----------------------|
| Strategy library (`src/honba_strategies/*`) | `vyapaar_strategies/strategies/*.py` — `TurtleBreakout`, `BollingerMeanReversion`, `MarketMakingStrategy`, `QuotingStrategy`, `CashFuturesArbitrage`, `RiskParity`, `TWAPSlicer`/`VWAPSlicer`, `CoveredCallWriter`, `FixedFractional` |
| Strategy authoring base | `vyapaar_strategies/sdk/strategy.py` — `Strategy` + `IndicatorRegistry` |
| Declarative parameters | `vyapaar_strategies/sdk/parameter.py` — `Parameter` descriptor |
| Bars / orders / indicators | `vyapaar_strategies/sdk/` — `bar.py`, `order.py`, `indicators.py`, `context.py`, `quoting.py` |
| `catalog/` step manifests | `catalog/*.toml` (10 files, 8 families: `arbitrage`, `execution`, `market_making`, `mean_reversion`, `options`, `portfolio`, `size`, `trend`) |
| `schema/` | `schema/step.schema.json`, `schema/strategy-manifest.schema.json`, `schema/basket-manifest.schema.json` |
| `tools/` manifest linters | `tools/validate_catalog.py`, `tools/validate_manifests.py` |
| `tests/` | `tests/{sdk,strategies,manifests,catalog}/` + `tests/test_init.py` |
| Versioned strategy/basket manifests (plan 0001) | `vyapaar_strategies/manifest/` + `manifests/strategies/` + `manifests/baskets/` |

## Migration steps performed

1. **Fix `pyproject.toml`** — the invalid `rust_decimal>=1.0.0` dependency was
   removed; `vyapaar` + `pydantic` are declared instead.
2. **Implement the strategy SDK** — `sdk/` package with `Strategy`, streaming
   `Decimal` indicators, `Parameter`, order domain, and `SimulatedContext`.
3. **Port the strategy families** — nine modules / ten classes in
   `strategies/`, mirroring the StockSharp-inspired catalog.
4. **Author the declarative catalog** — `catalog/*.toml` step manifests + JSON
   schemas + validator tools.
5. **Add the manifest layer (plan 0001)** — `StrategyManifest` /
   `BasketManifest` / promotion workflow + sidecar TOMLs + schema/tooling.
6. **Migrate tests** — all tests in `tests/` parallel to the package; zero
   inline `Parameter`/strategy tests inside `vyapaar_strategies/`.

## File-by-file source map

| `vyapaar_strategies/...` | Role |
|--------------------------|------|
| `_compat.py` | Optional `vyapaar` wheel interop (`VYAAPAAR_AVAILABLE`). |
| `sdk/bar.py` | `Bar` (frozen dataclass, `Decimal` OHLCV). |
| `sdk/context.py` | `StrategyContext` protocol + `SimulatedContext`. |
| `sdk/indicators.py` | `SMA`/`EMA`/`RSI`/`ATR`/`BollingerBands` + `crosses_above/below`. |
| `sdk/order.py` | `OrderRequest`, `OrderEvent`, `OrderSide/Type/Status`, `TimeInForce`. |
| `sdk/parameter.py` | `Parameter` descriptor (bounds + step alignment). |
| `sdk/quoting.py` | `QuoteState` mixin (single resting quote per side). |
| `sdk/strategy.py` | `Strategy` base + `IndicatorRegistry`. |
| `strategies/*.py` | Ten strategy classes (see `code-strategies.md`). |
| `manifest/*.py` | `StrategyManifest`, `BasketManifest`, `ParameterSpec`, `PromotionStatus`/`promote()` (see `code-manifest.md`). |

## Verification

```bash
# From the repository root
pytest -q
ruff check .
ruff format --check .
mypy vyapaar_strategies
python tools/validate_catalog.py
python tools/validate_manifests.py
```

See `implementation-record.md` for the completed-milestone status of each
verification gate.
