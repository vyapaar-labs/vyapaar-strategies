# `vyapaar-strategies` — Implementation Record

Dismantled from the former `docs/roadmap/` (`roadmap.md` +
`migration-verification.md`). Completed milestones are recorded here; remaining
future work moved to [`docs/gaps/`](../gaps/README.md) and
[`docs/plans/`](../plans/README.md).

## Migration: `honba-strategies` → `vyapaar-strategies` (Tier 6C)

| Milestone | Status | Commit |
|-----------|--------|--------|
| `pyproject.toml` fixed (invalid `rust_decimal` removed) | Complete | `af20843` |
| Strategy SDK implemented (`sdk/`) | Complete | `af20843` |
| Strategy families ported (`strategies/`) | Complete | `af20843` |
| Declarative `catalog/` step manifests + schema | Complete | `af20843` |
| Manifest tooling (`tools/validate_catalog.py`) | Complete | `af20843` |
| Tests in `tests/` (parallel to package, no inline tests) | Complete | `af20843` |

The source `honba-strategies` tree was unavailable, so the tier was implemented
fresh from the sub-guide contracts — see
[`code-migration-map.md`](code-migration-map.md) for the layout mapping.

## Subsequent landings

| Landing | Commit |
|---------|--------|
| Plan 0001 Layer 3: `StrategyManifest` / `BasketManifest` / promotion workflow (`manifest/`), POC sidecars (`manifests/strategies/`, `manifests/baskets/`), `schema/strategy-manifest.schema.json`, `schema/basket-manifest.schema.json`, `tools/validate_manifests.py`, 42 tests in `tests/manifests/` | `207a70c` |
| Docs: code reference docs (`code-sdk.md`, `code-strategies.md`, `code-manifest.md`, `code-migration-map.md`) | `a5076c2` |
| Docs: plans index cleanup (plan 0001 → Implemented) | `a838b16` |
| Docs: `docs/roadmap/` dismantled into `docs/design/` + `docs/gaps/` + `docs/plans/` | this change |

## Verification (recorded green gate, 2026-11-06, plan 0001)

```bash
pytest -q              # 119 tests, all passing
ruff check .           # clean
ruff format --check .  # clean
mypy vyapaar_strategies  # clean
python tools/validate_catalog.py    # 10/10 catalog manifests ok
python tools/validate_manifests.py  # 2 strategy + 1 basket manifest ok
```

- Test distribution (computed from `tests/` incl. parametrization): SDK 18,
  strategies 26, manifests 42, catalog 32, `test_init` 1 — total **119**
  (matches the Layer 3 handoff gate).
- Zero inline tests in `vyapaar_strategies/` (tests live in `tests/` only).
- Zero-floats gate: all prices/quantities/weights use `decimal.Decimal`
  (string literals; `Decimal(<float>)` is rejected by ruff RUF032).

## Migration status

Migration is **complete**. No outstanding migration work remains; the open items
below are future features, not unfinished port work.

## Open future work

All open items now live in [`docs/gaps/`](../gaps/README.md) and
[`docs/plans/`](../plans/README.md): tick-level dispatch (`0001`), a
live/feed-backed `StrategyContext` (`0002`), an in-repo catalog step executor
(`0003`), a `BasketManifest`-driven run loop (`0004`), and a Phase-2 basket risk
budget / allocation optimizer (`0005`).
