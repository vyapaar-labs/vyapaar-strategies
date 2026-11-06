"""Position sizing: fixed-fractional-of-notional sizing strategy."""

from __future__ import annotations

from decimal import Decimal

from vyapaar_strategies.sdk import Bar, Parameter, Strategy
from vyapaar_strategies.sdk.indicators import SMA


class FixedFractional(Strategy):
    """Size orders as a fixed fraction of notional risked per trade.

    ``quantity = (notional * risk_percent / 100) / stop_distance`` (rounded down
    to whole shares). Enters on a fast SMA crossing above a slow SMA, sizes the
    trade with the fixed-fractional rule, and exits on the cross back below.
    """

    instrument = Parameter(default="NSE:RELIANCE-EQ")
    notional = Parameter(default=100000, min=1000, max=100000000, step=1000)
    risk_percent = Parameter(default="1", min="0.1", max="10", step="0.1")
    stop_distance = Parameter(default="5", min="0.1", max="100", step="0.1")
    fast_period = Parameter(default=10, min=2, max=50, step=1)
    slow_period = Parameter(default=30, min=5, max=100, step=5)

    def __init__(self, **overrides: object) -> None:
        super().__init__(**overrides)
        self._fast: SMA | None = None
        self._slow: SMA | None = None

    def on_start(self) -> None:
        self._fast = self.indicators.sma(self.instrument, self.fast_period)
        self._slow = self.indicators.sma(self.instrument, self.slow_period)

    def on_bar(self, bar: Bar) -> None:
        if bar.instrument != self.instrument:
            return
        if self._fast is None or self._slow is None:
            return
        self._fast.update(bar.close)
        self._slow.update(bar.close)
        if not (self._fast.ready and self._slow.ready):
            return
        position = self.position(self.instrument)
        if position == 0 and self._fast.value > self._slow.value:
            quantity = self._size()
            if quantity > 0:
                self.buy(self.instrument, quantity)
        elif position > 0 and self._fast.value < self._slow.value:
            self.sell(self.instrument, position)

    def _size(self) -> Decimal:
        risked = (Decimal(str(self.notional)) * Decimal(str(self.risk_percent))) / Decimal(100)
        quantity = risked / Decimal(str(self.stop_distance))
        return quantity.to_integral_value(rounding="ROUND_DOWN")
