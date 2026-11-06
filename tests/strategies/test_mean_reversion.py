"""Bollinger mean reversion: fade extended moves back to the mid-band."""

from __future__ import annotations

from decimal import Decimal

from conftest import make_bars

from vyapaar_strategies import BollingerMeanReversion, SimulatedContext

INSTRUMENT = "NSE:RELIANCE-EQ"


def test_buys_when_close_tags_lower_band() -> None:
    context = SimulatedContext()
    closes = [Decimal(100)] * 30 + [Decimal(80)]
    strategy = BollingerMeanReversion(period=10, deviations=2, quantity=10)
    strategy.run(context, make_bars(closes, instrument=INSTRUMENT))

    assert context.position(INSTRUMENT) == Decimal(10)
    fills = [e for e in context.events if e.status.value == "complete"]
    assert len(fills) == 1
    assert fills[0].price == Decimal(80)


def test_exits_when_close_returns_to_mid_band() -> None:
    context = SimulatedContext()
    closes = [Decimal(100)] * 30 + [Decimal(80), Decimal(81), Decimal(120)]
    strategy = BollingerMeanReversion(period=10, deviations=2, quantity=10)
    strategy.run(context, make_bars(closes, instrument=INSTRUMENT))

    assert context.position(INSTRUMENT) == 0
    fills = [e for e in context.events if e.status.value == "complete"]
    assert len(fills) == 2  # buy then exit


def test_does_not_trade_when_band_not_ready() -> None:
    context = SimulatedContext()
    strategy = BollingerMeanReversion(period=50, deviations=2, quantity=10)
    strategy.run(context, make_bars([Decimal(100)] * 20, instrument=INSTRUMENT))
    assert len(context.orders) == 0
