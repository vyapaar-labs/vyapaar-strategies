"""Shared fixtures: deterministic bar builders."""

from __future__ import annotations

from datetime import UTC, datetime, timedelta
from decimal import Decimal

import pytest

from vyapaar_strategies import Bar


def make_bars(
    closes: list[Decimal | int | str],
    instrument: str = "NSE:NIFTY50-INDEX",
    start: datetime | None = None,
) -> list[Bar]:
    """Build a daily bar sequence from closing prices (OHLC = close)."""
    day = start or datetime(2024, 1, 1, tzinfo=UTC)
    bars: list[Bar] = []
    for i, close in enumerate(closes):
        value = close if isinstance(close, Decimal) else Decimal(str(close))
        bars.append(
            Bar(
                instrument=instrument,
                ts=day + timedelta(days=i),
                open=value,
                high=value,
                low=value,
                close=value,
                volume=100_000,
            )
        )
    return bars


@pytest.fixture
def trending_closes() -> list[Decimal]:
    """A rising then falling series that triggers a turtle breakout and exit."""
    values = [Decimal(100) + Decimal(i) for i in range(30)] + [
        Decimal(130) - Decimal(i) for i in range(15)
    ]
    return values
