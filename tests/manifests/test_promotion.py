"""Promotion workflow: draft -> backtested -> paper -> live (Phase 3)."""

from __future__ import annotations

from datetime import UTC, datetime

import pytest
from test_strategy_manifest import base_manifest

from vyapaar_strategies import PromotionStatus, StrategyManifest


def make_manifest() -> StrategyManifest:
    return StrategyManifest.model_validate(base_manifest())


def test_initial_status_is_draft() -> None:
    assert make_manifest().promotion_status is PromotionStatus.DRAFT


def test_promote_to_backtested_records_evidence() -> None:
    manifest = make_manifest()
    at = datetime(2026, 1, 5, tzinfo=UTC)
    manifest.promote(PromotionStatus.BACKTESTED, "backtest:run/2026-01-05/bt-123", at=at)
    assert manifest.promotion_status is PromotionStatus.BACKTESTED
    assert len(manifest.promotion_evidence) == 1
    record = manifest.promotion_evidence[0]
    assert record.status is PromotionStatus.BACKTESTED
    assert record.evidence_ref == "backtest:run/2026-01-05/bt-123"
    assert record.recorded_at == at


def test_promote_requires_status_appropriate_evidence() -> None:
    manifest = make_manifest()
    with pytest.raises(ValueError):
        manifest.promote(PromotionStatus.BACKTESTED, "paper:window/1")


def test_promote_requires_an_evidence_reference() -> None:
    manifest = make_manifest()
    with pytest.raises(ValueError):
        manifest.promote(PromotionStatus.BACKTESTED, "")


def test_promotion_cannot_skip_a_stage() -> None:
    manifest = make_manifest()
    with pytest.raises(ValueError):
        manifest.promote(PromotionStatus.LIVE, "live:dep/nse-1")


def test_cannot_demote() -> None:
    manifest = make_manifest()
    manifest.promote(PromotionStatus.BACKTESTED, "backtest:run/1")
    with pytest.raises(ValueError):
        manifest.promote(PromotionStatus.DRAFT, "backtest:run/2")


def test_full_promotion_chain_records_all_steps() -> None:
    manifest = make_manifest()
    manifest.promote(PromotionStatus.BACKTESTED, "backtest:run/2026-01/1")
    manifest.promote(PromotionStatus.PAPER, "paper:window/2026-02")
    manifest.promote(PromotionStatus.LIVE, "live:dep/nse-1")
    assert manifest.promotion_status is PromotionStatus.LIVE
    assert [record.status for record in manifest.promotion_evidence] == [
        PromotionStatus.BACKTESTED,
        PromotionStatus.PAPER,
        PromotionStatus.LIVE,
    ]


def test_promotion_note_is_recorded() -> None:
    manifest = make_manifest()
    manifest.promote(
        PromotionStatus.BACKTESTED,
        "backtest:run/1",
        note="turtle params validated against 2026-01 data",
    )
    assert manifest.promotion_evidence[0].note.startswith("turtle")
