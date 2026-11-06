"""Covered call writer: owns the underlying and sells an OTM call."""

from __future__ import annotations

from decimal import Decimal

from conftest import make_bars

from vyapaar_strategies import Bar, CoveredCallWriter, SimulatedContext

UNDERLYING = "NSE:RELIANCE-EQ"
CALL = "NFO:RELIANCE24DEC2500CE"


def test_buys_underlying_and_writes_call_on_first_underlying_bar() -> None:
    context = SimulatedContext()
    strategy = CoveredCallWriter(quantity=10)
    underlying = make_bars([Decimal(200)] * 3, instrument=UNDERLYING)
    call = make_bars([Decimal(10)] * 3, instrument=CALL)
    bars = [item for pair in zip(underlying, call, strict=True) for item in pair]
    strategy.run(context, bars)

    assert context.position(UNDERLYING) == Decimal(10)
    assert context.position(CALL) == Decimal(-10)


def test_rolls_call_back_after_premium_rally() -> None:
    context = SimulatedContext()
    strategy = CoveredCallWriter(quantity=10, roll_back_percent="1.05")
    underlying = make_bars([Decimal(200)] * 3 + [Decimal(300)], instrument=UNDERLYING)
    call = make_bars([Decimal(10), Decimal(10), Decimal(10), Decimal(11)], instrument=CALL)
    bars: list[Bar] = []
    for i in range(4):
        bars.append(underlying[i])
        bars.append(call[i])
    strategy.run(context, bars)

    # After the rally the call is bought back: position returns to zero.
    assert context.position(CALL) == 0
    assert context.position(UNDERLYING) == Decimal(10)


def test_no_trade_without_underlying_bar() -> None:
    context = SimulatedContext()
    strategy = CoveredCallWriter(quantity=10)
    strategy.run(context, make_bars([Decimal(10)] * 2, instrument=CALL))
    assert len(context.orders) == 0
