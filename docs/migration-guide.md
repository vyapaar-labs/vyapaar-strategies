# `vyapaar-strategies` — Subagent Migration & DDD Refactoring Guide

> **Tier**: Tier 6C
> **Source**: `/home/pmallapp/Devel/Finance/honba-workspace/honba-strategies`
> **Target**: `/home/pmallapp/Devel/Finance/vyapaar-labs/vyapaar-strategies`

---

## 1. Migration & DDD Refactoring Steps
1. **Fix `pyproject.toml`**:
   - Remove invalid `"rust_decimal>=1.0.0"` from `vyapaar-strategies/pyproject.toml`.
2. **Port Strategy Library & Catalog**:
   - Copy `honba-workspace/honba-strategies/src/honba_strategies/*` (or package modules) into `vyapaar-labs/vyapaar-strategies/vyapaar_strategies/`.
   - Copy `catalog/`, `schema/`, `tools/`, and `tests/` into `vyapaar-labs/vyapaar-strategies/`.
   - Replace `honba_strategies` → `vyapaar_strategies` and `honba` → `vyapaar` across all Python files, `step.toml` manifests, and `registry.json`.

## 2. Verification Commands
```bash
cd /home/pmallapp/Devel/Finance/vyapaar-labs/vyapaar-strategies
pytest -q
ruff check .
```
