"""Market making: both-side quoting and inventory management."""

from __future__ import annotations

from decimal import Decimal

from conftest import make_bars

from vyapaar_strategies import MarketMakingStrategy, SimulatedContext

INSTRUMENT = "NSE:RELIANCE-EQ"


def test_posts_single_quote_pair_when_flat() -> None:
    context = SimulatedContext()
    mm = MarketMakingStrategy(spread="1.00", quote_quantity=5)
    mm.run(context, make_bars([Decimal(100)] * 3, instrument=INSTRUMENT))

    # Exactly one bid and one ask are quoted (no stacking across bars).
    bids = [o for o in context.orders if o.side.value == "buy"]
    asks = [o for o in context.orders if o.side.value == "sell"]
    assert len(bids) == 1 and len(asks) == 1
    assert bids[0].limit_price == Decimal("99.50")
    assert asks[0].limit_price == Decimal("100.50")


def test_bid_fills_on_dip_and_stops_bidding_when_long() -> None:
    context = SimulatedContext()
    strategy = MarketMakingStrategy(spread="1.00", quote_quantity=5)
    strategy.run(context, make_bars([Decimal(100), Decimal(98)], instrument=INSTRUMENT))

    # The drop hits the resting bid at 99.50 -> long 5; no new bid is posted.
    assert context.position(INSTRUMENT) == Decimal(5)
    bids = [o for o in context.orders if o.side.value == "buy"]
    assert len(bids) == 1
