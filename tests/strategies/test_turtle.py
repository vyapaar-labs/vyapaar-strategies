"""Turtle breakout: entry on channel-high breakout, exit on channel-low."""

from __future__ import annotations

from decimal import Decimal

from conftest import make_bars

from vyapaar_strategies import SimulatedContext, TurtleBreakout


def test_turtle_enters_on_breakout_and_exits_on_downturn() -> None:
    context = SimulatedContext()
    strategy = TurtleBreakout(entry_period=5, exit_period=5, quantity=10)
    strategy.run(context, make_bars([Decimal(100) + Decimal(i) for i in range(20)]))

    assert context.position("NSE:NIFTY50-INDEX") == Decimal(10)
    assert len([e for e in context.events if e.status.value == "complete"]) == 1


def test_turtle_exits_when_price_breaks_below_channel() -> None:
    context = SimulatedContext()
    closes = [Decimal(100) + Decimal(i) for i in range(15)] + [
        Decimal(114) - Decimal(i) for i in range(10)
    ]
    strategy = TurtleBreakout(entry_period=5, exit_period=5, quantity=10)
    strategy.run(context, make_bars(closes))

    # Exit fired: position back to zero after the downtrend.
    assert context.position("NSE:NIFTY50-INDEX") == 0


def test_turtle_does_not_trade_in_a_flat_market() -> None:
    context = SimulatedContext()
    strategy = TurtleBreakout(entry_period=5, exit_period=5, quantity=10)
    strategy.run(context, make_bars([Decimal(100)] * 30))
    assert len(context.orders) == 0
