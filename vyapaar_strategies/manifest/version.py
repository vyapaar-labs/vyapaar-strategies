"""Promotion workflow for versioned strategy manifests (Phase 3).

A manifest version advances strictly forward through
``draft -> backtested -> paper -> live``. Every promotion past ``draft``
requires an evidence reference describing which backtest run / paper-trading
window / live deployment justified the move.
"""

from __future__ import annotations

from datetime import UTC, datetime
from enum import StrEnum

from pydantic import BaseModel, ConfigDict, Field


class PromotionStatus(StrEnum):
    """Lifecycle stage of one ``StrategyManifest`` version."""

    DRAFT = "draft"
    BACKTESTED = "backtested"
    PAPER = "paper"
    LIVE = "live"


PROMOTION_ORDER: tuple[PromotionStatus, ...] = (
    PromotionStatus.DRAFT,
    PromotionStatus.BACKTESTED,
    PromotionStatus.PAPER,
    PromotionStatus.LIVE,
)

#: Evidence reference prefix required to promote into each status.
_PROMOTION_EVIDENCE_PREFIX: dict[PromotionStatus, str] = {
    PromotionStatus.BACKTESTED: "backtest:",
    PromotionStatus.PAPER: "paper:",
    PromotionStatus.LIVE: "live:",
}


def evidence_prefix(status: PromotionStatus) -> str:
    """Return the evidence-ref prefix required to promote to ``status``."""
    prefix = _PROMOTION_EVIDENCE_PREFIX.get(status)
    if prefix is None:
        raise ValueError(f"no evidence reference applies to promotion to {status.value!r}")
    return prefix


class PromotionRecord(BaseModel):
    """One audited promotion step with its justifying evidence."""

    model_config = ConfigDict(extra="forbid")

    status: PromotionStatus
    evidence_ref: str = Field(min_length=1)
    recorded_at: datetime
    note: str = ""


def utc_now() -> datetime:
    """Timezone-aware UTC clock; overridable by tests via ``promote(at=...)``."""
    return datetime.now(UTC)
