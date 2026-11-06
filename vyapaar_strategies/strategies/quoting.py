"""Quoting strategy: post a single spread around a fair-value signal."""

from __future__ import annotations

from decimal import Decimal

from vyapaar_strategies.sdk import Bar, Parameter, Strategy
from vyapaar_strategies.sdk.indicators import EMA
from vyapaar_strategies.sdk.quoting import QuoteState


class QuotingStrategy(QuoteState, Strategy):
    """Quote both sides around an EMA fair-value signal.

    At most one bid and one ask are ever resting: a side is quoted only when no
    order of that side is already open, so stale quotes never stack. While
    holding a position only the reducing side is quoted.
    """

    instrument = Parameter(default="NSE:NIFTY50-INDEX")
    fast_ema = Parameter(default=20, min=5, max=100, step=1)
    spread = Parameter(default="1.00", min="0.10", max="20.00", step="0.10")
    quantity = Parameter(default=5, min=1, max=1000, step=1)

    def __init__(self, **overrides: object) -> None:
        QuoteState.__init__(self)
        Strategy.__init__(self, **overrides)
        self._ema: EMA | None = None

    def on_start(self) -> None:
        self._ema = self.indicators.ema(self.instrument, self.fast_ema)

    def on_bar(self, bar: Bar) -> None:
        if bar.instrument != self.instrument:
            return
        if self._ema is None:
            return
        self._ema.update(bar.close)
        if not self._ema.ready:
            return
        fair = self._ema.value
        half_spread = Decimal(str(self.spread)) / Decimal(2)
        position = self.position(self.instrument)
        if position == 0:
            if not self.bid_open:
                self.buy(self.instrument, self.quantity, limit_price=fair - half_spread)
            if not self.ask_open:
                self.sell(self.instrument, self.quantity, limit_price=fair + half_spread)
        elif position > 0:
            if not self.ask_open:
                self.sell(self.instrument, self.quantity, limit_price=fair + half_spread)
        else:
            if not self.bid_open:
                self.buy(self.instrument, self.quantity, limit_price=fair - half_spread)
