"""Options strategy: covered call writing on an owned underlying."""

from __future__ import annotations

from decimal import Decimal

from vyapaar_strategies.sdk import Bar, Parameter, Strategy


class CoveredCallWriter(Strategy):
    """Own the underlying and write OTM calls to harvest premium.

    Buys the underlying when flat and writes the call at market on the next
    call bar. When the call premium has appreciated past ``roll_back_percent``
    of the write price the call is bought back. Deterministic and
    ``Decimal``-exact.
    """

    underlying = Parameter(default="NSE:RELIANCE-EQ")
    call_instrument = Parameter(default="NFO:RELIANCE24DEC2500CE")
    quantity = Parameter(default=10, min=1, max=1000, step=1)
    roll_back_percent = Parameter(default="1.05", min="1.00", max="3.00", step="0.05")

    def __init__(self, **overrides: object) -> None:
        super().__init__(**overrides)
        self._call_entry: Decimal | None = None

    def on_bar(self, bar: Bar) -> None:
        underlying_position = self.position(self.underlying)
        call_position = self.position(self.call_instrument)
        if bar.instrument == self.underlying:
            if underlying_position == 0 and call_position == 0:
                self.buy(self.underlying, self.quantity)
        elif bar.instrument == self.call_instrument:
            if call_position == 0 and underlying_position > 0:
                self.sell(self.call_instrument, self.quantity)
                self._call_entry = bar.close
            elif call_position < 0 and self._call_entry is not None:
                threshold = self._call_entry * Decimal(str(self.roll_back_percent))
                if bar.close >= threshold:
                    self.buy(self.call_instrument, abs(call_position))
