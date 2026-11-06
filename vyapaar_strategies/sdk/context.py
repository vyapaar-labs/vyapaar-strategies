"""Execution contexts: protocol + deterministic simulated harness."""

from __future__ import annotations

import logging
from decimal import Decimal
from typing import Protocol, runtime_checkable

from vyapaar_strategies.sdk.bar import Bar
from vyapaar_strategies.sdk.order import (
    OrderEvent,
    OrderRequest,
    OrderSide,
    OrderStatus,
)


@runtime_checkable
class StrategyContext(Protocol):
    """The execution environment a strategy runs against (sim or live)."""

    def submit(self, request: OrderRequest) -> OrderEvent: ...
    def current_price(self, instrument: str) -> Decimal: ...
    def position(self, instrument: str) -> Decimal: ...


class SimulatedContext:
    """Deterministic offline execution context.

    Market orders fill immediately at the current bar's close. Limit orders
    fill when the close has already crossed the limit, otherwise they rest and
    are re-checked on every subsequent bar (realistic resting-order semantics).
    Positions are exact ``Decimal`` arithmetic.
    """

    def __init__(self, logger: logging.Logger | None = None) -> None:
        self._bars: dict[str, Bar] = {}
        self._positions: dict[str, Decimal] = {}
        self._resting: list[tuple[str, OrderRequest]] = []
        self._outbox: list[OrderEvent] = []
        self._counter = 0
        self.events: list[OrderEvent] = []
        self.orders: list[OrderRequest] = []
        self.logger = logger or logging.getLogger("vyapaar.strategy")

    def feed(self, bar: Bar) -> None:
        """Deliver a new bar; resting limit orders are evaluated at its close."""
        self._bars[bar.instrument] = bar
        self._process_resting(bar.close)

    def current_price(self, instrument: str) -> Decimal:
        bar = self._bars.get(instrument)
        if bar is None:
            raise KeyError(f"no bar fed for {instrument}")
        return bar.close

    def position(self, instrument: str) -> Decimal:
        return self._positions.get(instrument, Decimal(0))

    def submit(self, request: OrderRequest) -> OrderEvent:
        self._counter += 1
        order_id = f"SIM-{self._counter:05d}"
        self.orders.append(request)
        price = self.current_price(request.instrument)

        if request.order_type.value == "market":
            return self._fill(order_id, request, price)
        if request.limit_price is not None:
            crossed = (request.side is OrderSide.BUY and price <= request.limit_price) or (
                request.side is OrderSide.SELL and price >= request.limit_price
            )
            if crossed:
                return self._fill(order_id, request, request.limit_price)
            self._resting.append((order_id, request))
        event = OrderEvent(
            order_id=order_id,
            instrument=request.instrument,
            side=request.side,
            status=OrderStatus.OPEN,
            quantity=request.quantity,
            filled_quantity=Decimal(0),
            price=None,
        )
        self.events.append(event)
        return event

    def run(self, strategy: object, bars: list[Bar]) -> None:
        """Drive a strategy through a bar sequence deterministically."""
        strategy._context = self  # type: ignore[attr-defined]
        strategy.on_start()  # type: ignore[attr-defined]
        for bar in bars:
            self.feed(bar)
            for event in self._drain_outbox():
                strategy.on_order_event(event)  # type: ignore[attr-defined]
            strategy.on_bar(bar)  # type: ignore[attr-defined]
        strategy.on_stop()  # type: ignore[attr-defined]

    # -- internals ----------------------------------------------------------
    def _process_resting(self, price: Decimal) -> None:
        remaining: list[tuple[str, OrderRequest]] = []
        for order_id, request in self._resting:
            if request.limit_price is None:
                self._outbox.append(self._fill(order_id, request, price))
                continue
            crossed = (request.side is OrderSide.BUY and price <= request.limit_price) or (
                request.side is OrderSide.SELL and price >= request.limit_price
            )
            if crossed:
                self._outbox.append(self._fill(order_id, request, request.limit_price))
            else:
                remaining.append((order_id, request))
        self._resting = remaining

    def _fill(self, order_id: str, request: OrderRequest, price: Decimal) -> OrderEvent:
        signed = request.quantity if request.side is OrderSide.BUY else -request.quantity
        self._positions[request.instrument] = (
            self._positions.get(request.instrument, Decimal(0)) + signed
        )
        event = OrderEvent(
            order_id=order_id,
            instrument=request.instrument,
            side=request.side,
            status=OrderStatus.COMPLETE,
            quantity=request.quantity,
            filled_quantity=request.quantity,
            price=price,
        )
        self.events.append(event)
        return event

    def _drain_outbox(self) -> list[OrderEvent]:
        events, self._outbox = self._outbox, []
        return events
