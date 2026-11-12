# `vyapaar-strategies` — Manifest Reference

Documents `vyapaar_strategies/manifest/`: the versioned, promotable strategy and
basket manifests (plan 0001, Layer 3). All models are Pydantic v2
`BaseModel`s with `extra="forbid"` and validate their own invariants on
construction.

## `PromotionStatus` & promotion workflow (`manifest/version.py`)

```python
class PromotionStatus(StrEnum):
    DRAFT = "draft"
    BACKTESTED = "backtested"
    PAPER = "paper"
    LIVE = "live"

PROMOTION_ORDER: tuple[PromotionStatus, ...]  # draft -> backtested -> paper -> live
```

`StrategyManifest.promote(status, evidence_ref, *, note="", at=None)` advances a
manifest **exactly one stage forward** and raises `ValueError` for skips,
demotions, or promotions without the target-status evidence prefix:

| Target status | Required `evidence_ref` prefix |
|---------------|-------------------------------|
| `BACKTESTED` | `backtest:` |
| `PAPER` | `paper:` |
| `LIVE` | `live:` |

Each promotion appends a `PromotionRecord` (`status`, `evidence_ref`
(min_length 1), `recorded_at` (UTC, override via `at=`), `note`) to
`promotion_evidence` and updates `promotion_status`. `utc_now()` is the
timezone-aware clock used when `at` is omitted.

## `ParameterSpec` (`manifest/params.py`)

The manifest-side snapshot of one `Parameter(...)` declaration:

```python
class ParameterSpec(BaseModel):
    default: str | int | Decimal
    min: Decimal | None = None
    max: Decimal | None = None
    step: Decimal | None = None
```

## `StrategyManifest` (`manifest/strategy.py`)

```python
class StrategyManifest(BaseModel):
    name: str                                   # ^[a-z0-9_]+$
    version: str                                # ^[0-9]+\.[0-9]+\.[0-9]+$  (semver pattern)
    strategy: str                               # ^vyapaar_strategies\...:Class$
    parameters: dict[str, ParameterSpec]        # min_length 1
    target_instruments: InstrumentSelector
    capital_allocation: CapitalAllocation
    promotion_status: PromotionStatus = PromotionStatus.DRAFT
    promotion_evidence: list[PromotionRecord] = []
```

| Member | Semantics |
|--------|-----------|
| `strategy_class` (property) | `importlib`-resolves `module:Class` to the class. |
| `instantiate(**overrides)` | Builds an instance with this version's parameter defaults (`spec.default` per declared parameter) plus `overrides`. |
| `validate_parameters()` | Cross-checks every declared parameter: it must be a `Parameter` descriptor on the class and its default must pass the descriptor bounds; returns a list of error strings (empty when valid). |
| `promote(...)` | See promotion workflow above. |
| `from_toml(text)` / `load_toml(path)` | Parse from TOML (stdlib `tomllib`). |

### `InstrumentSelector`

`target_instruments` sets **exactly one** of an explicit `instruments` list
(e.g. `["NSE:RELIANCE-EQ"]`) or a `rule` string; both empty raises
`ValueError`.

### `CapitalAllocation`

`capital_allocation` sets **exactly one** of `absolute` (Money amount, INR,
`>= 0`) or `weight` (portfolio fraction in the open unit interval `(0, 1]`).

## `BasketManifest` (`manifest/basket.py`)

```python
class BasketManifest(BaseModel):
    basket_name: str                            # ^[a-z0-9_]+$
    version: str                                # semver pattern
    combined_capital: Decimal                   # > 0
    member_strategies: list[MemberStrategyRef]  # min_length 1
    risk_budget: RiskBudget = RiskBudget()
```

Validates on construction:
- members must all use the same allocation mode (weight **xor** absolute);
- weights sum `<= 1.0`; absolute allocations sum `<= combined_capital`.
- `from_toml` / `load_toml` loaders (stdlib `tomllib`).

### `MemberStrategyRef`

A reference to one `StrategyManifest` version: `name`, `version` (semver
pattern), and **exactly one** of `weight` (in `(0, 1]`) or `allocation`
(`>= 0`). Members are validated by name/version against the
`manifests/strategies/` directory by `tools/validate_manifests.py`.

### `RiskBudget`

Phase-1 basket-level risk budget — deliberately a **simple cap** (per the
module docstring; an allocation-objective optimizer such as
`vyapaar-ledger-allocation` is a later, out-of-scope integration — see
[gap 0005](../gaps/0005-risk-budget-simple-cap.md)):

```python
class RiskBudget(BaseModel):
    max_position_fraction: Decimal | None = None  # in (0, 1]
    max_loss: Decimal | None = None               # >= 0
```

## On-disk manifests

| File | Model | Notes |
|------|-------|-------|
| `manifests/strategies/turtle_breakout.toml` | `StrategyManifest` | `TurtleBreakout` v0.1.0, `promotion_status = "draft"`, `weight = 0.5`. |
| `manifests/strategies/twap_slicer.toml` | `StrategyManifest` | `TWAPSlicer` v0.1.0, draft, `weight = 0.5`. |
| `manifests/baskets/turtle_twap_basket.toml` | `BasketManifest` | Two members (0.5 + 0.5), `combined_capital = 1000000`, `risk_budget` caps. |

## Validation tooling & schemas

| Tool | Checks |
|------|--------|
| `tools/validate_manifests.py` | Strategy manifests: JSON schema + pydantic model + `validate_parameters()` + `instantiate()`. Basket manifests: JSON schema + pydantic model + member name/version resolves to a strategy manifest. |
| `tools/validate_catalog.py` | `catalog/**/*.toml` against `schema/step.schema.json` + strategy import/instantiate. |

Schemas: `schema/strategy-manifest.schema.json`,
`schema/basket-manifest.schema.json`, `schema/step.schema.json` (JSON Schema
draft-07 mirrors; exact-capital/step constraints are enforced by the pydantic
models).

## Zero-Floats / Decimal Policy

`combined_capital`, weights, and allocations are `decimal.Decimal`; weight and
allocation ranges are validated in exact `Decimal` arithmetic.

## Related

- `docs/design/code-migration-map.md` — Tier 6C port origin
- `docs/plans/README.md` — plan 0001 (implemented) and gap index
- `docs/gaps/0004-no-basket-run-loop.md`, `docs/gaps/0005-risk-budget-simple-cap.md`
