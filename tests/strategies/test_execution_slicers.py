"""TWAP and VWAP slicers: parent quantity conserved exactly."""

from __future__ import annotations

from decimal import Decimal

from conftest import make_bars

from vyapaar_strategies import SimulatedContext, TWAPSlicer, VWAPSlicer

INSTRUMENT = "NSE:RELIANCE-EQ"


def _submitted_total(context: SimulatedContext) -> Decimal:
    return sum((o.quantity for o in context.orders), Decimal(0))


def test_twap_conserves_total_quantity() -> None:
    context = SimulatedContext()
    strategy = TWAPSlicer(instrument=INSTRUMENT, total_quantity=100, slices=10)
    strategy.run(context, make_bars([Decimal(100)] * 12, instrument=INSTRUMENT))

    assert len(context.orders) == 10
    assert _submitted_total(context) == Decimal(100)
    assert context.position(INSTRUMENT) == Decimal(100)


def test_twap_uses_equal_slices() -> None:
    context = SimulatedContext()
    strategy = TWAPSlicer(instrument=INSTRUMENT, total_quantity=100, slices=5)
    strategy.run(context, make_bars([Decimal(100)] * 5, instrument=INSTRUMENT))
    quantities = [order.quantity for order in context.orders]
    assert quantities == [Decimal(20)] * 5


def test_twap_with_remainder_absorbs_into_final_slice() -> None:
    context = SimulatedContext()
    strategy = TWAPSlicer(instrument=INSTRUMENT, total_quantity=103, slices=10)
    strategy.run(context, make_bars([Decimal(100)] * 10, instrument=INSTRUMENT))
    assert _submitted_total(context) == Decimal(103)


def test_vwap_conserves_total_quantity() -> None:
    context = SimulatedContext()
    strategy = VWAPSlicer(instrument=INSTRUMENT, total_quantity=100, slices=10)
    strategy.run(context, make_bars([Decimal(100)] * 10, instrument=INSTRUMENT))
    assert _submitted_total(context) == Decimal(100)
    assert context.position(INSTRUMENT) == Decimal(100)


def test_vwap_profile_weights_sum_to_total() -> None:
    context = SimulatedContext()
    strategy = VWAPSlicer(
        instrument=INSTRUMENT, total_quantity=200, slices=4, profile="40,30,20,10"
    )
    strategy.run(context, make_bars([Decimal(100)] * 4, instrument=INSTRUMENT))
    quantities = [order.quantity for order in context.orders]
    assert quantities == [Decimal("80.00"), Decimal("60.00"), Decimal("40.00"), Decimal("20.00")]
