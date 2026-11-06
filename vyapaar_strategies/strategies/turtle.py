"""Turtle breakout trend-following (entry/exit channel breakout)."""

from __future__ import annotations

from decimal import Decimal

from vyapaar_strategies.sdk import Bar, Parameter, Strategy


class TurtleBreakout(Strategy):
    """Classic Turtle: enter on a 20-bar high breakout, exit on a 10-bar low.

    Entry and exit channels use the Donchian high/low of the most recent
    ``entry_period`` / ``exit_period`` bars.
    """

    instrument = Parameter(default="NSE:NIFTY50-INDEX")
    entry_period = Parameter(default=20, min=5, max=60, step=1)
    exit_period = Parameter(default=10, min=5, max=60, step=1)
    quantity = Parameter(default=10, min=1, max=1000, step=1)

    def __init__(self, **overrides: object) -> None:
        super().__init__(**overrides)
        self._highs: list[Decimal] = []
        self._lows: list[Decimal] = []

    def on_bar(self, bar: Bar) -> None:
        if bar.instrument != self.instrument:
            return
        self._highs.append(bar.high)
        self._lows.append(bar.low)
        if len(self._highs) <= self.entry_period:
            return
        # Donchian channels exclude the current bar: breakout must beat the
        # highest high / lowest low of the *previous* N bars.
        channel_high = max(self._highs[-self.entry_period - 1 : -1])
        channel_low = min(self._lows[-self.exit_period - 1 : -1])
        position = self.position(self.instrument)
        if position == 0 and bar.close > channel_high:
            self.buy(self.instrument, self.quantity)
        elif position > 0 and bar.close < channel_low:
            self.sell(self.instrument, position)
