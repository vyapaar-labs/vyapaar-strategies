"""Bollinger mean reversion: fade extended moves back to the mid-band."""

from __future__ import annotations

from vyapaar_strategies.sdk import Bar, Parameter, Strategy
from vyapaar_strategies.sdk.indicators import BollingerBands


class BollingerMeanReversion(Strategy):
    """Buy when the close tags the lower band; exit when it returns to the mid.

    Uses a streaming Bollinger band fed by every close.
    """

    instrument = Parameter(default="NSE:RELIANCE-EQ")
    period = Parameter(default=20, min=5, max=100, step=1)
    deviations = Parameter(default=2, min=1, max=4, step=1)
    quantity = Parameter(default=10, min=1, max=1000, step=1)

    def __init__(self, **overrides: object) -> None:
        super().__init__(**overrides)
        self._bands: BollingerBands | None = None

    def on_start(self) -> None:
        self._bands = self.indicators.bollinger(self.instrument, self.period, self.deviations)

    def on_bar(self, bar: Bar) -> None:
        if bar.instrument != self.instrument:
            return
        if self._bands is None:
            return
        self._bands.update(bar.close)
        if not self._bands.ready:
            return
        position = self.position(self.instrument)
        if (
            position == 0
            and bar.close <= self._bands.lower
            and self._bands.lower < self._bands.middle
        ):
            self.buy(self.instrument, self.quantity)
        elif position > 0 and bar.close >= self._bands.middle:
            self.sell(self.instrument, position)
