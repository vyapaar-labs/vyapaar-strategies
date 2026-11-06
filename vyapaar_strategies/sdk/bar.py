"""Canonical bar model with exact ``Decimal`` OHLCV."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal


@dataclass(frozen=True, slots=True)
class Bar:
    """One OHLCV bar (zero-floats: every price is an exact ``Decimal``)."""

    instrument: str
    ts: datetime
    open: Decimal
    high: Decimal
    low: Decimal
    close: Decimal
    volume: int = 0
    interval: str = "1d"

    def __post_init__(self) -> None:
        for field in ("open", "high", "low", "close"):
            value = getattr(self, field)
            if not isinstance(value, Decimal):
                object.__setattr__(self, field, Decimal(str(value)))
        if self.high < self.low:
            raise ValueError("high must be >= low")

    def to_dict(self) -> dict[str, object]:
        return {
            "instrument": self.instrument,
            "ts": self.ts.isoformat(),
            "open": str(self.open),
            "high": str(self.high),
            "low": str(self.low),
            "close": str(self.close),
            "volume": self.volume,
            "interval": self.interval,
        }
