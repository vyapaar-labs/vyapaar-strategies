"""Risk parity: inverse-volatility allocation favors calm legs."""

from __future__ import annotations

from decimal import Decimal

from conftest import make_bars

from vyapaar_strategies import RiskParity, SimulatedContext

NIFTY = "NSE:NIFTY50-INDEX"
BANK = "NSE:BANKNIFTY-INDEX"


def test_allocates_more_notional_to_the_calmer_leg() -> None:
    context = SimulatedContext()
    strategy = RiskParity(
        instruments=f"{NIFTY},{BANK}",
        lookback=5,
        rebalance_period=2,
        notional=100000,
    )
    nifty_closes = [Decimal(100), Decimal(101), Decimal(99), Decimal(102), Decimal(98)] * 10
    bank_closes = [Decimal(100), Decimal(120), Decimal(80), Decimal(130), Decimal(70)] * 10
    nifty_bars = make_bars(nifty_closes, instrument=NIFTY)
    bank_bars = make_bars(bank_closes, instrument=BANK)
    bars = [item for pair in zip(nifty_bars, bank_bars, strict=True) for item in pair]
    strategy.run(context, bars)

    nifty_qty = context.position(NIFTY)
    bank_qty = context.position(BANK)
    assert nifty_qty > 0
    assert bank_qty > 0
    assert nifty_qty > bank_qty  # calmer leg receives the larger allocation


def test_weights_sum_to_one() -> None:
    strategy = RiskParity(instruments=f"{NIFTY},{BANK}", lookback=5, rebalance_period=2)
    context = SimulatedContext()
    nifty_bars = make_bars(
        [Decimal(100), Decimal(101), Decimal(99), Decimal(102), Decimal(98)] * 10, instrument=NIFTY
    )
    bank_bars = make_bars(
        [Decimal(100), Decimal(120), Decimal(80), Decimal(130), Decimal(70)] * 10, instrument=BANK
    )
    bars = [item for pair in zip(nifty_bars, bank_bars, strict=True) for item in pair]
    strategy.run(context, bars)
    weights = strategy._weights([NIFTY, BANK])
    assert abs(sum(weights, Decimal(0)) - 1) < Decimal("1e-15")
    assert weights[0] > weights[1]
