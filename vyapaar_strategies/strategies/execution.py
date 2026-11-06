"""Execution algorithms: TWAP and VWAP order slicers.

Slicers decompose a parent order into deterministic child slices. Total
submitted quantity is conserved exactly (``Decimal`` arithmetic).
"""

from __future__ import annotations

from decimal import Decimal

from vyapaar_strategies.sdk import Bar, Parameter, Strategy


class TWAPSlicer(Strategy):
    """Time-weighted average price slicer.

    Splits ``total_quantity`` across ``slices`` equal child orders, submitting
    one slice per bar. The final slice absorbs any rounding remainder so the
    parent quantity is always conserved.
    """

    instrument = Parameter(default="NSE:RELIANCE-EQ")
    total_quantity = Parameter(default=100, min=1, max=1000000, step=1)
    slices = Parameter(default=10, min=1, max=500, step=1)
    side = Parameter(default="buy")

    def __init__(self, **overrides: object) -> None:
        super().__init__(**overrides)
        self._submitted = 0
        self._slice_size = Decimal(0)

    def on_start(self) -> None:
        total = Decimal(self.total_quantity)
        self._slice_size = total / Decimal(self.slices)
        self._submitted = 0

    def on_bar(self, bar: Bar) -> None:
        if bar.instrument != self.instrument:
            return
        if self._submitted >= self.slices:
            return
        self._submitted += 1
        remaining = Decimal(self.total_quantity) - (self._slice_size * Decimal(self._submitted - 1))
        slice_qty = min(self._slice_size, remaining)
        if self.side == "buy":
            self.buy(self.instrument, slice_qty)
        else:
            self.sell(self.instrument, slice_qty)


class VWAPSlicer(Strategy):
    """Volume-weighted average price slicer.

    Child quantities follow a normalized intra-day volume profile. The profile
    is cyclic so it is fully deterministic offline; the last slice absorbs
    rounding remainder to conserve the parent quantity.
    """

    instrument = Parameter(default="NSE:RELIANCE-EQ")
    total_quantity = Parameter(default=100, min=1, max=1000000, step=1)
    slices = Parameter(default=10, min=1, max=500, step=1)
    side = Parameter(default="buy")
    profile = Parameter(default="15,13,12,11,10,9,8,7,8,7")

    def __init__(self, **overrides: object) -> None:
        super().__init__(**overrides)
        self._submitted = 0
        self._weights: list[Decimal] = []

    def on_start(self) -> None:
        raw = [Decimal(part) for part in str(self.profile).split(",")]
        total = sum(raw, Decimal(0))
        self._weights = [value / total for value in raw]
        self._submitted = 0

    def on_bar(self, bar: Bar) -> None:
        if bar.instrument != self.instrument:
            return
        if self._submitted >= self.slices:
            return
        self._submitted += 1
        target = (Decimal(self.total_quantity) * self._weights[self._submitted - 1]).quantize(
            Decimal("0.01")
        )
        submitted_so_far = sum(
            (Decimal(self.total_quantity) * self._weights[i]).quantize(Decimal("0.01"))
            for i in range(self._submitted - 1)
        )
        remaining = Decimal(self.total_quantity) - submitted_so_far
        slice_qty = min(target, remaining)
        if slice_qty <= 0:
            return
        if self.side == "buy":
            self.buy(self.instrument, slice_qty)
        else:
            self.sell(self.instrument, slice_qty)
