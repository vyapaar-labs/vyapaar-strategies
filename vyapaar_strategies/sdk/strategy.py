"""Strategy base class: lifecycle hooks, order helpers, indicator registry."""

from __future__ import annotations

import logging
from decimal import Decimal

from vyapaar_strategies.sdk.bar import Bar
from vyapaar_strategies.sdk.context import SimulatedContext, StrategyContext
from vyapaar_strategies.sdk.indicators import (
    ATR,
    EMA,
    RSI,
    SMA,
    BollingerBands,
    Indicator,
)
from vyapaar_strategies.sdk.order import (
    OrderEvent,
    OrderRequest,
    OrderSide,
    OrderType,
)


class IndicatorRegistry:
    """Per-(instrument, kind, params) indicator store.

    A strategy requests ``self.indicators.sma("NSE:NIFTY50-INDEX", 20)`` once
    in ``on_start``; the same streaming instance is then fed by every bar.
    """

    def __init__(self) -> None:
        self._store: dict[tuple[object, ...], Indicator | BollingerBands] = {}

    def sma(self, instrument: str, period: int) -> SMA:
        return self._get(("sma", instrument, period), SMA(period))  # type: ignore[return-value]

    def ema(self, instrument: str, period: int) -> EMA:
        return self._get(("ema", instrument, period), EMA(period))  # type: ignore[return-value]

    def rsi(self, instrument: str, period: int = 14) -> RSI:
        return self._get(("rsi", instrument, period), RSI(period))  # type: ignore[return-value]

    def atr(self, instrument: str, period: int = 14) -> ATR:
        return self._get(("atr", instrument, period), ATR(period))  # type: ignore[return-value]

    def bollinger(
        self, instrument: str, period: int = 20, deviations: Decimal | int = 2
    ) -> BollingerBands:
        key = ("bollinger", instrument, period, str(deviations))
        if key not in self._store:
            self._store[key] = BollingerBands(period, deviations)
        return self._store[key]  # type: ignore[return-value]

    def _get(
        self, key: tuple[object, ...], indicator: Indicator | BollingerBands
    ) -> Indicator | BollingerBands:
        if key not in self._store:
            self._store[key] = indicator
        return self._store[key]


class Strategy:
    """Base class for Vyapaar strategies.

    Lifecycle hooks (Jesse-style): ``on_start``, ``on_bar``, ``on_tick``,
    ``on_order_event``, ``on_stop``. Orders are authored through ``self.buy`` /
    ``self.sell`` or ``self.submit``; indicators are declared in ``on_start``
    via ``self.indicators``.
    """

    def __init__(self, **overrides: object) -> None:
        self._context: StrategyContext | None = None
        self._indicators = IndicatorRegistry()
        self._logger = logging.getLogger(f"{type(self).__module__}.{type(self).__name__}")
        for name, value in overrides.items():
            setattr(self, name, value)

    # -- lifecycle hooks (overridable) -------------------------------------
    def on_start(self) -> None: ...
    def on_bar(self, bar: Bar) -> None: ...
    def on_tick(self, tick: object) -> None: ...
    def on_order_event(self, event: OrderEvent) -> None: ...
    def on_stop(self) -> None: ...

    # -- execution ----------------------------------------------------------
    def buy(
        self, instrument: str, quantity: Decimal | int | str, limit_price: Decimal | None = None
    ) -> OrderEvent:
        return self.submit(
            OrderRequest(
                instrument=instrument,
                side=OrderSide.BUY,
                quantity=self._qty(quantity),
                order_type=OrderType.MARKET if limit_price is None else OrderType.LIMIT,
                limit_price=limit_price,
                tag="strategy.buy",
            )
        )

    def sell(
        self, instrument: str, quantity: Decimal | int | str, limit_price: Decimal | None = None
    ) -> OrderEvent:
        return self.submit(
            OrderRequest(
                instrument=instrument,
                side=OrderSide.SELL,
                quantity=self._qty(quantity),
                order_type=OrderType.MARKET if limit_price is None else OrderType.LIMIT,
                limit_price=limit_price,
                tag="strategy.sell",
            )
        )

    def submit(self, request: OrderRequest) -> OrderEvent:
        context = self._require_context()
        event = context.submit(request)
        self.on_order_event(event)
        return event

    def position(self, instrument: str) -> Decimal:
        context = self._require_context()
        return context.position(instrument)

    def current_price(self, instrument: str) -> Decimal:
        return self._require_context().current_price(instrument)

    @property
    def indicators(self) -> IndicatorRegistry:
        return self._indicators

    @property
    def logger(self) -> logging.Logger:
        return self._logger

    # -- harness ------------------------------------------------------------
    def run(self, context: StrategyContext, bars: list[Bar]) -> None:
        """Drive the strategy through a bar sequence (sim or live parity)."""
        if isinstance(context, SimulatedContext):
            context.run(self, bars)
        else:
            self._context = context
            self.on_start()
            for bar in bars:
                self.on_bar(bar)
            self.on_stop()

    def _require_context(self) -> StrategyContext:
        if self._context is None:
            raise RuntimeError("strategy has no execution context; call run(context, bars)")
        return self._context

    @staticmethod
    def _qty(value: Decimal | int | str) -> Decimal:
        return value if isinstance(value, Decimal) else Decimal(str(value))
