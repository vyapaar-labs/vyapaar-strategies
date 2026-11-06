"""Order domain: canonical enums, requests, and lifecycle events."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from enum import StrEnum


class OrderSide(StrEnum):
    BUY = "buy"
    SELL = "sell"


class OrderType(StrEnum):
    LIMIT = "limit"
    MARKET = "market"
    STOP_LIMIT = "stop_limit"
    STOP_MARKET = "stop_market"


class TimeInForce(StrEnum):
    DAY = "day"
    IOC = "ioc"
    GTD = "gtd"


class OrderStatus(StrEnum):
    PENDING = "pending"
    OPEN = "open"
    PARTIALLY_FILLED = "partially_filled"
    COMPLETE = "complete"
    REJECTED = "rejected"
    CANCELLED = "cancelled"


@dataclass(frozen=True, slots=True)
class OrderRequest:
    """A strategy-authored order submission."""

    instrument: str
    side: OrderSide
    quantity: Decimal
    order_type: OrderType = OrderType.MARKET
    limit_price: Decimal | None = None
    tag: str | None = None

    def __post_init__(self) -> None:
        object.__setattr__(
            self,
            "quantity",
            self.quantity if isinstance(self.quantity, Decimal) else Decimal(str(self.quantity)),
        )
        if self.quantity <= 0:
            raise ValueError("quantity must be positive")
        if self.limit_price is not None and not isinstance(self.limit_price, Decimal):
            object.__setattr__(self, "limit_price", Decimal(str(self.limit_price)))


@dataclass(frozen=True, slots=True)
class OrderEvent:
    """Execution lifecycle event delivered to ``Strategy.on_order_event``."""

    order_id: str
    instrument: str
    side: OrderSide
    status: OrderStatus
    quantity: Decimal
    filled_quantity: Decimal
    price: Decimal | None = None
    ts: datetime | None = None
