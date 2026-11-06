"""Streaming indicators: decimal-exact math and cross detection."""

from __future__ import annotations

from decimal import Decimal

from vyapaar_strategies.sdk import Bar
from vyapaar_strategies.sdk.indicators import (
    ATR,
    EMA,
    RSI,
    SMA,
    BollingerBands,
    crosses_above,
    crosses_below,
)

D = Decimal


def test_sma_matches_manual_mean() -> None:
    sma = SMA(3)
    for value in (D(1), D(2), D(3), D(4)):
        sma.update(value)
    assert sma.ready
    assert sma.value == D(3)  # mean of 2,3,4


def test_sma_previous_value_enables_crosses() -> None:
    fast = SMA(2)
    slow = SMA(3)
    # Declining series keeps fast below slow; the final jump crosses above.
    for value in (D(5), D(4), D(3), D(2), D(1), D(5)):
        fast.update(value)
        slow.update(value)
    assert crosses_above(fast, slow) is True
    assert crosses_below(fast, slow) is False


def test_ema_is_exponential() -> None:
    ema = EMA(3)
    for value in (D(1), D(2), D(3)):
        ema.update(value)
    # EMA(3) alpha = 2/(3+1) = 0.5: 1 -> 1.5 -> 2.25
    assert ema.value.quantize(D("0.0001")) == D("2.2500")


def test_rsi_is_bounded_when_ready() -> None:
    rsi = RSI(5)
    for i in range(20):
        rsi.update(D(i))
    assert rsi.ready
    assert D(0) <= rsi.value <= D(100)


def test_rsi_is_100_on_streak_of_gains() -> None:
    rsi = RSI(3)
    for i in range(1, 10):
        rsi.update(D(i))
    assert rsi.value == D(100)


def test_atr_tracks_true_range() -> None:
    atr = ATR(3)
    for i in range(5):
        atr.update(_bar(i))
    assert atr.ready
    assert atr.value > 0


def _bar(i: int) -> Bar:
    from datetime import UTC, datetime

    close = D(i + 10)
    return Bar(
        instrument="X",
        ts=datetime(2024, 1, 1, tzinfo=UTC),
        open=close,
        high=close + D("2"),
        low=close - D("2"),
        close=close,
    )


def test_bollinger_bands_symmetry() -> None:
    bands = BollingerBands(period=4, deviations=2)
    for value in (D(10), D(11), D(12), D(13)):
        bands.update(value)
    assert bands.ready
    assert bands.middle == D("11.5")
    upper_leg = bands.upper - bands.middle
    lower_leg = bands.middle - bands.lower
    # Exact Decimal sqrt rounds at context precision; compare to a tolerance.
    assert abs(upper_leg - lower_leg) < D("1e-15")
    assert bands.upper > bands.middle > bands.lower
