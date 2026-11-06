"""Risk parity: inverse-volatility portfolio weights with periodic rebalance."""

from __future__ import annotations

from decimal import Decimal

from vyapaar_strategies.sdk import Bar, Parameter, Strategy


class RiskParity(Strategy):
    """Inverse-volatility risk-parity allocator.

    Every ``rebalance_period`` bars the strategy recomputes each leg's rolling
    volatility (standard deviation of returns) and targets an allocation
    inversely proportional to it — higher-volatility legs receive smaller
    notional weights. Weights always sum to 1.
    """

    instruments = Parameter(default="NSE:NIFTY50-INDEX,NSE:BANKNIFTY-INDEX")
    lookback = Parameter(default=20, min=2, max=100, step=1)
    rebalance_period = Parameter(default=5, min=1, max=50, step=1)
    notional = Parameter(default=100000, min=1000, max=100000000, step=1000)

    def __init__(self, **overrides: object) -> None:
        super().__init__(**overrides)
        self._returns: dict[str, list[Decimal]] = {}
        self._last: dict[str, Decimal] = {}
        self._bar_count = 0

    def on_bar(self, bar: Bar) -> None:
        legs = [leg.strip() for leg in str(self.instruments).split(",")]
        if bar.instrument not in legs:
            return
        previous = self._last.get(bar.instrument)
        self._last[bar.instrument] = bar.close
        if previous is not None and previous != 0:
            self._returns.setdefault(bar.instrument, []).append(bar.close / previous - Decimal(1))
        if len(legs) < 2 or any(len(self._returns.get(leg, [])) < self.lookback for leg in legs):
            return
        self._bar_count += 1
        if self._bar_count % self.rebalance_period != 0:
            return
        weights = self._weights(legs)
        for leg, weight in zip(legs, weights, strict=True):
            target_qty = (self.notional * weight / self.current_price(leg)).quantize(
                Decimal("0.01")
            )
            current_qty = self.position(leg)
            delta = target_qty - current_qty
            if delta > 0:
                self.buy(leg, abs(delta))
            elif delta < 0:
                self.sell(leg, abs(delta))

    def _weights(self, legs: list[str]) -> list[Decimal]:
        volatilities = [self._volatility(leg) for leg in legs]
        inverse = [Decimal(1) / vol for vol in volatilities]
        total = sum(inverse, Decimal(0))
        return [value / total for value in inverse]

    def _volatility(self, instrument: str) -> Decimal:
        returns = self._returns.get(instrument, [])[-self.lookback :]
        mean = sum(returns, Decimal(0)) / Decimal(len(returns))
        variance = sum((value - mean) ** 2 for value in returns) / Decimal(len(returns))
        return variance.sqrt()
