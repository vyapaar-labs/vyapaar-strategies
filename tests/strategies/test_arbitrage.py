"""Cash-futures arbitrage: fade the basis between cash and future legs."""

from __future__ import annotations

from decimal import Decimal

from conftest import make_bars

from vyapaar_strategies import Bar, CashFuturesArbitrage, SimulatedContext

CASH = "NSE:RELIANCE-EQ"
FUT = "NFO:RELIANCE24DECFUT"


def _cash_bars(closes: list[Decimal]) -> list[Bar]:
    return make_bars(closes, instrument=CASH)


def _fut_bars(closes: list[Decimal]) -> list[Bar]:
    return make_bars(closes, instrument=FUT)


def test_enters_hedged_when_futures_premium_grows() -> None:
    context = SimulatedContext()
    strategy = CashFuturesArbitrage(entry_threshold="0.50", exit_threshold="0.10", quantity=10)

    cash = _cash_bars([Decimal(100)] * 4)
    futures = _fut_bars([Decimal(100), Decimal("100.25"), Decimal("100.60"), Decimal("100.90")])
    bars = [item for pair in zip(cash, futures, strict=True) for item in pair]
    strategy.run(context, bars)

    # Hedge: long cash, short futures.
    assert context.position(CASH) == Decimal(10)
    assert context.position(FUT) == Decimal(-10)


def test_unwinds_when_basis_reverts() -> None:
    context = SimulatedContext()
    strategy = CashFuturesArbitrage(entry_threshold="0.50", exit_threshold="0.10", quantity=10)

    cash = _cash_bars([Decimal(100)] * 6)
    futures = _fut_bars(
        [
            Decimal(100),
            Decimal("100.25"),
            Decimal("100.60"),
            Decimal("100.90"),
            Decimal("100.05"),
            Decimal(100),
        ]
    )
    bars = [item for pair in zip(cash, futures, strict=True) for item in pair]
    strategy.run(context, bars)

    assert context.position(CASH) == 0
    assert context.position(FUT) == 0


def test_no_trade_when_basis_narrow() -> None:
    context = SimulatedContext()
    strategy = CashFuturesArbitrage(entry_threshold="0.50", exit_threshold="0.10", quantity=10)
    cash = _cash_bars([Decimal(100)] * 2)
    futures = _fut_bars([Decimal(100), Decimal("100.20")])
    strategy.run(context, [item for pair in zip(cash, futures, strict=True) for item in pair])
    assert len(context.orders) == 0
