"""Cash-futures arbitrage: fade the basis between a cash and its future."""

from __future__ import annotations

from decimal import Decimal

from vyapaar_strategies.sdk import Bar, Parameter, Strategy


class CashFuturesArbitrage(Strategy):
    """Pairs trade on the cash-futures basis.

    When the futures premium exceeds ``entry_threshold`` the strategy shorts the
    future and buys the cash leg; the reverse when the basis is deeply negative.
    The hedge unwinds when the basis returns inside ``exit_threshold``.
    """

    cash_instrument = Parameter(default="NSE:RELIANCE-EQ")
    futures_instrument = Parameter(default="NFO:RELIANCE24DECFUT")
    entry_threshold = Parameter(default="0.50", min="0.05", max="50.00", step="0.05")
    exit_threshold = Parameter(default="0.10", min="0.00", max="50.00", step="0.05")
    quantity = Parameter(default=10, min=1, max=1000, step=1)

    def __init__(self, **overrides: object) -> None:
        super().__init__(**overrides)
        self._cash_close: Decimal | None = None
        self._futures_close: Decimal | None = None

    def on_bar(self, bar: Bar) -> None:
        if bar.instrument == self.cash_instrument:
            self._cash_close = bar.close
        elif bar.instrument == self.futures_instrument:
            self._futures_close = bar.close
        else:
            return
        if self._cash_close is None or self._futures_close is None:
            return
        basis = self._futures_close - self._cash_close
        cash_position = self.position(self.cash_instrument)
        entry = Decimal(str(self.entry_threshold))
        exit_threshold = Decimal(str(self.exit_threshold))
        if cash_position == 0 and basis > entry:
            self.sell(self.futures_instrument, self.quantity)
            self.buy(self.cash_instrument, self.quantity)
        elif cash_position == 0 and basis < -entry:
            self.buy(self.futures_instrument, self.quantity)
            self.sell(self.cash_instrument, self.quantity)
        elif cash_position != 0 and abs(basis) <= exit_threshold:
            self.sell(self.cash_instrument, abs(cash_position))
            self.buy(self.futures_instrument, abs(self.position(self.futures_instrument)))
