"""Quoting strategy: quote both sides around an EMA fair-value signal."""

from __future__ import annotations

from decimal import Decimal

from conftest import make_bars

from vyapaar_strategies import QuotingStrategy, SimulatedContext

INSTRUMENT = "NSE:NIFTY50-INDEX"


def test_posts_single_quote_pair_around_fair_value() -> None:
    context = SimulatedContext()
    strategy = QuotingStrategy(instrument=INSTRUMENT, fast_ema=5, spread="1.00", quantity=5)
    strategy.run(context, make_bars([Decimal(100)] * 10, instrument=INSTRUMENT))

    # Exactly one bid and one ask ever rest (no duplicate stacking).
    bids = [o for o in context.orders if o.side.value == "buy"]
    asks = [o for o in context.orders if o.side.value == "sell"]
    assert len(bids) == 1 and len(asks) == 1
    assert bids[0].limit_price == Decimal("99.50")
    assert asks[0].limit_price == Decimal("100.50")


def test_bid_fills_on_dip_and_no_duplicate_bid_is_posted() -> None:
    context = SimulatedContext()
    strategy = QuotingStrategy(instrument=INSTRUMENT, fast_ema=5, spread="1.00", quantity=5)
    strategy.run(context, make_bars([Decimal(100)] * 6 + [Decimal("99.5")], instrument=INSTRUMENT))

    # On the dip the resting bid at 99.50 is hit -> long 5; no new bid posted.
    assert context.position(INSTRUMENT) == Decimal(5)
    bids = [o for o in context.orders if o.side.value == "buy"]
    assert len(bids) == 1
