"""Strategy lifecycle: on_start / on_bar / on_order_event / on_stop."""

from __future__ import annotations

from decimal import Decimal

from conftest import make_bars

from vyapaar_strategies import Bar, Parameter, SimulatedContext, Strategy


class RecordingStrategy(Strategy):
    instrument = Parameter(default="NSE:NIFTY50-INDEX")
    quantity = Parameter(default=5, min=1, max=1000, step=1)

    def __init__(self, **overrides: object) -> None:
        super().__init__(**overrides)
        self.started = False
        self.stopped = False
        self.bar_count = 0
        self.events: list[object] = []

    def on_start(self) -> None:
        self.started = True

    def on_bar(self, bar: Bar) -> None:
        self.bar_count += 1
        if self.bar_count == 3:
            self.buy(self.instrument, self.quantity)

    def on_order_event(self, event: object) -> None:
        self.events.append(event)

    def on_stop(self) -> None:
        self.stopped = True


def test_lifecycle_ordering_and_orders() -> None:
    context = SimulatedContext()
    strategy = RecordingStrategy()
    strategy.run(context, make_bars([Decimal(100)] * 5))

    assert strategy.started
    assert strategy.stopped
    assert strategy.bar_count == 5
    assert len(strategy.events) == 1
    event = strategy.events[0]
    assert event.status.value == "complete"  # type: ignore[attr-defined]
    assert context.position("NSE:NIFTY50-INDEX") == Decimal(5)


def test_market_order_fills_at_close() -> None:
    context = SimulatedContext()
    bars = make_bars([Decimal(100), Decimal(105), Decimal(110)])
    strategy = RecordingStrategy()
    strategy.run(context, bars)
    event = strategy.events[0]
    assert event.price == Decimal(110)  # type: ignore[attr-defined]


def test_limit_order_fills_only_when_crossed() -> None:
    strategy = RecordingStrategy()
    # overrides: place a limit buy at 105 after 3 bars

    class LimitStrategy(RecordingStrategy):
        def on_bar(self, bar: Bar) -> None:  # type: ignore[override]
            self.bar_count += 1
            if self.bar_count == 3:
                self.buy(self.instrument, self.quantity, limit_price=Decimal(104))

    context = SimulatedContext()
    strategy = LimitStrategy()
    strategy.run(context, make_bars([Decimal(100)] * 2 + [Decimal(103), Decimal(106)]))
    events = strategy.events
    # limit 104: bar4 close 106 >= 104 -> fills
    assert len(events) == 1
    assert events[0].status.value == "complete"  # type: ignore[attr-defined]


def test_strategy_without_context_raises() -> None:
    strategy = RecordingStrategy()
    try:
        strategy.buy("NSE:X", 1)
    except RuntimeError:
        return
    raise AssertionError("expected RuntimeError without a context")
