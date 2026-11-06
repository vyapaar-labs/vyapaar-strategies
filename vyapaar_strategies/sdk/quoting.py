"""Shared quote-state tracking for quoting-style strategies.

A quoting strategy must never stack duplicate resting quotes. ``QuoteState``
tracks whether a bid/ask is currently open so strategies post at most one of
each side and start quoting again only after a fill.
"""

from __future__ import annotations

from vyapaar_strategies.sdk.order import OrderEvent, OrderSide, OrderStatus


class QuoteState:
    """Tracks resting bid/ask state from the order-event stream."""

    def __init__(self) -> None:
        self._bid_open = False
        self._ask_open = False

    def on_order_event(self, event: OrderEvent) -> None:
        if event.status is OrderStatus.OPEN:
            if event.side is OrderSide.BUY:
                self._bid_open = True
            else:
                self._ask_open = True
        elif event.status is OrderStatus.COMPLETE:
            if event.side is OrderSide.BUY:
                self._bid_open = False
            else:
                self._ask_open = False

    @property
    def bid_open(self) -> bool:
        return self._bid_open

    @property
    def ask_open(self) -> bool:
        return self._ask_open
