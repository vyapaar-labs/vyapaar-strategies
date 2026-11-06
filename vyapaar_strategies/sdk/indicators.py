"""Streaming technical indicators with exact ``Decimal`` arithmetic.

Indicators are fed one value (or one ``Bar`` for range-based indicators) at a
time, exactly as a live or backtest event loop delivers data. Every calculation
stays in ``Decimal`` (``Decimal.sqrt`` is used for standard deviation).
"""

from __future__ import annotations

from collections import deque
from decimal import Decimal

from vyapaar_strategies.sdk.bar import Bar


class Indicator:
    """Base class for streaming indicators."""

    def __init__(self, period: int) -> None:
        if period <= 0:
            raise ValueError("period must be positive")
        self.period = period

    @property
    def ready(self) -> bool:
        raise NotImplementedError

    @property
    def value(self) -> Decimal:
        raise NotImplementedError


class SMA(Indicator):
    """Simple moving average over the trailing ``period`` values."""

    def __init__(self, period: int) -> None:
        super().__init__(period)
        self._history: list[Decimal] = []

    def update(self, value: Decimal) -> None:
        self._history.append(value)

    @property
    def ready(self) -> bool:
        return len(self._history) >= self.period

    @property
    def value(self) -> Decimal:
        return self._mean(self._history[-self.period :])

    @property
    def previous_value(self) -> Decimal | None:
        """SMA over the window one step ago (used for cross detection)."""
        if len(self._history) < self.period + 1:
            return None
        return self._mean(self._history[-self.period - 1 : -1])

    @staticmethod
    def _mean(values: list[Decimal]) -> Decimal:
        return sum(values, Decimal(0)) / Decimal(len(values))


class EMA(Indicator):
    """Exponential moving average."""

    def __init__(self, period: int) -> None:
        super().__init__(period)
        self._multiplier = Decimal(2) / Decimal(period + 1)
        self._ema: Decimal | None = None

    def update(self, value: Decimal) -> None:
        previous = self._ema
        if previous is None:
            self._ema = value
        else:
            self._ema = value * self._multiplier + previous * (Decimal(1) - self._multiplier)

    @property
    def ready(self) -> bool:
        return self._ema is not None

    @property
    def value(self) -> Decimal:
        if self._ema is None:
            raise ValueError("EMA is not ready")
        return self._ema


class RSI(Indicator):
    """Wilder's Relative Strength Index."""

    def __init__(self, period: int = 14) -> None:
        super().__init__(period)
        self._gains: list[Decimal] = []
        self._losses: list[Decimal] = []
        self._avg_gain: Decimal | None = None
        self._avg_loss: Decimal | None = None
        self._previous: Decimal | None = None

    def update(self, value: Decimal) -> None:
        previous = self._previous
        if previous is not None:
            change = value - previous
            gain = max(change, Decimal(0))
            loss = max(-change, Decimal(0))
            self._gains.append(gain)
            self._losses.append(loss)
            avg_gain = self._avg_gain
            avg_loss = self._avg_loss
            if avg_gain is None and len(self._gains) >= self.period:
                window = self._gains[-self.period :]
                self._avg_gain = sum(window, Decimal(0)) / Decimal(self.period)
                self._avg_loss = sum(self._losses[-self.period :], Decimal(0)) / Decimal(
                    self.period
                )
            elif avg_gain is not None and avg_loss is not None:
                self._avg_gain = (avg_gain * Decimal(self.period - 1) + gain) / Decimal(self.period)
                self._avg_loss = (avg_loss * Decimal(self.period - 1) + loss) / Decimal(self.period)
        self._previous = value

    @property
    def ready(self) -> bool:
        return self._avg_gain is not None

    @property
    def value(self) -> Decimal:
        if self._avg_gain is None or self._avg_loss is None:
            raise ValueError("RSI is not ready")
        if self._avg_loss == 0:
            return Decimal(100)
        relative_strength = self._avg_gain / self._avg_loss
        return Decimal(100) - Decimal(100) / (Decimal(1) + relative_strength)


class ATR(Indicator):
    """Wilder's Average True Range, fed one ``Bar`` at a time."""

    def __init__(self, period: int = 14) -> None:
        super().__init__(period)
        self._true_ranges: list[Decimal] = []
        self._previous_close: Decimal | None = None
        self._atr: Decimal | None = None

    def update(self, bar: Bar) -> None:
        true_range = bar.high - bar.low
        if self._previous_close is not None:
            true_range = max(
                true_range,
                abs(bar.high - self._previous_close),
                abs(bar.low - self._previous_close),
            )
        self._true_ranges.append(true_range)
        self._previous_close = bar.close
        if self._atr is None and len(self._true_ranges) >= self.period:
            window = self._true_ranges[-self.period :]
            self._atr = sum(window, Decimal(0)) / Decimal(self.period)
        elif self._atr is not None:
            self._atr = (self._atr * Decimal(self.period - 1) + true_range) / Decimal(self.period)

    @property
    def ready(self) -> bool:
        return self._atr is not None

    @property
    def value(self) -> Decimal:
        if self._atr is None:
            raise ValueError("ATR is not ready")
        return self._atr


class BollingerBands:
    """Bollinger Bands around a simple moving average."""

    def __init__(self, period: int = 20, deviations: Decimal | int = 2) -> None:
        if period <= 0:
            raise ValueError("period must be positive")
        self.period = period
        self.deviations = (
            deviations if isinstance(deviations, Decimal) else Decimal(str(deviations))
        )
        self._history: deque[Decimal] = deque(maxlen=period)

    def update(self, value: Decimal) -> None:
        self._history.append(value)

    @property
    def ready(self) -> bool:
        return len(self._history) == self.period

    @property
    def middle(self) -> Decimal:
        window = list(self._history)
        return sum(window, Decimal(0)) / Decimal(len(window))

    @property
    def upper(self) -> Decimal:
        return self.middle + self.deviations * self._stddev()

    @property
    def lower(self) -> Decimal:
        return self.middle - self.deviations * self._stddev()

    def _stddev(self) -> Decimal:
        window = list(self._history)
        mean = sum(window, Decimal(0)) / Decimal(len(window))
        variance = sum((value - mean) ** 2 for value in window) / Decimal(len(window))
        return variance.sqrt()


def crosses_above(fast: Indicator, slow: Indicator) -> bool:
    """True when ``fast`` crossed above ``slow`` on the latest update."""
    return _cross(fast, slow, above=True)


def crosses_below(fast: Indicator, slow: Indicator) -> bool:
    """True when ``fast`` crossed below ``slow`` on the latest update."""
    return _cross(fast, slow, above=False)


def _cross(fast: Indicator, slow: Indicator, *, above: bool) -> bool:
    if not (fast.ready and slow.ready):
        return False
    fast_prev = getattr(fast, "previous_value", None)
    slow_prev = getattr(slow, "previous_value", None)
    if fast_prev is None or slow_prev is None:
        return False
    if above:
        return fast_prev <= slow_prev and fast.value > slow.value
    return fast_prev >= slow_prev and fast.value < slow.value
