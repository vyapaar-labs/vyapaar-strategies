"""Market making: post a single spread around the last trade."""

from __future__ import annotations

from decimal import Decimal

from vyapaar_strategies.sdk import Bar, Parameter, Strategy
from vyapaar_strategies.sdk.quoting import QuoteState


class MarketMakingStrategy(QuoteState, Strategy):
    """Two-sided market maker with inventory-aware quote management.

    At most one bid and one ask are ever resting. When flat both sides are
    quoted; when long only the ask; when short only the bid (aggressive
    inventory bleed). ``Decimal`` arithmetic throughout.
    """

    instrument = Parameter(default="NSE:RELIANCE-EQ")
    spread = Parameter(default="0.50", min="0.10", max="10.00", step="0.10")
    quote_quantity = Parameter(default=5, min=1, max=1000, step=1)
    max_position = Parameter(default=50, min=1, max=10000, step=1)

    def __init__(self, **overrides: object) -> None:
        QuoteState.__init__(self)
        Strategy.__init__(self, **overrides)

    def on_bar(self, bar: Bar) -> None:
        if bar.instrument != self.instrument:
            return
        position = self.position(self.instrument)
        half_spread = Decimal(str(self.spread)) / Decimal(2)
        bid = bar.close - half_spread
        ask = bar.close + half_spread
        if position == 0:
            if not self.bid_open:
                self.buy(self.instrument, self.quote_quantity, limit_price=bid)
            if not self.ask_open:
                self.sell(self.instrument, self.quote_quantity, limit_price=ask)
        elif position > 0 and position < self.max_position:
            if not self.ask_open:
                self.sell(self.instrument, self.quote_quantity, limit_price=ask)
        elif position < 0 and position > -self.max_position and not self.bid_open:
            self.buy(self.instrument, self.quote_quantity, limit_price=bid)
