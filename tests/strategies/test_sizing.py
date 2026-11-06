"""Fixed-fractional position sizing."""

from __future__ import annotations

from decimal import Decimal

from conftest import make_bars

from vyapaar_strategies import FixedFractional, SimulatedContext

INSTRUMENT = "NSE:RELIANCE-EQ"


def test_sizes_quantity_from_notional_risk_fraction() -> None:
    context = SimulatedContext()
    strategy = FixedFractional(
        instrument=INSTRUMENT,
        notional=100000,
        risk_percent="1",
        stop_distance="5",
        fast_period=2,
        slow_period=5,
    )
    # Rising closes drive the fast SMA above the slow SMA after bar 5.
    strategy.run(
        context, make_bars([Decimal(100) + Decimal(i) for i in range(20)], instrument=INSTRUMENT)
    )

    # risked = 100000 * 1% = 1000; qty = 1000 / 5 = 200.
    assert context.position(INSTRUMENT) == Decimal(200)


def test_exits_on_fast_crossing_below_slow() -> None:
    context = SimulatedContext()
    strategy = FixedFractional(
        instrument=INSTRUMENT,
        notional=100000,
        risk_percent="1",
        stop_distance="5",
        fast_period=2,
        slow_period=5,
    )
    closes = [Decimal(100) + Decimal(i) for i in range(10)] + [
        Decimal(110) - Decimal(2 * i) for i in range(10)
    ]
    strategy.run(context, make_bars(closes, instrument=INSTRUMENT))
    assert context.position(INSTRUMENT) == 0


def test_does_not_trade_before_fast_ready() -> None:
    context = SimulatedContext()
    strategy = FixedFractional(instrument=INSTRUMENT, fast_period=50, slow_period=60)
    strategy.run(context, make_bars([Decimal(100)] * 30, instrument=INSTRUMENT))
    assert len(context.orders) == 0
