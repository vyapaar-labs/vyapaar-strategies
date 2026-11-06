"""vyapaar-strategies — Production Strategy SDK & Declarative Step Catalog.

Tier 6C bounded context. Jesse-style strategy authoring with declarative
``Parameter`` descriptors, ``decimal.Decimal`` arithmetic, and a deterministic
simulated context for research-live parity testing.
"""

from __future__ import annotations

from vyapaar_strategies._compat import VYAAPAAR_AVAILABLE
from vyapaar_strategies.manifest import (
    BasketManifest,
    CapitalAllocation,
    InstrumentSelector,
    MemberStrategyRef,
    ParameterSpec,
    PromotionRecord,
    PromotionStatus,
    RiskBudget,
    StrategyManifest,
)
from vyapaar_strategies.sdk import (
    Bar,
    OrderEvent,
    OrderRequest,
    OrderSide,
    OrderStatus,
    OrderType,
    Parameter,
    SimulatedContext,
    Strategy,
    TimeInForce,
)
from vyapaar_strategies.strategies.arbitrage import CashFuturesArbitrage
from vyapaar_strategies.strategies.execution import TWAPSlicer, VWAPSlicer
from vyapaar_strategies.strategies.market_making import MarketMakingStrategy
from vyapaar_strategies.strategies.mean_reversion import BollingerMeanReversion
from vyapaar_strategies.strategies.options import CoveredCallWriter
from vyapaar_strategies.strategies.quoting import QuotingStrategy
from vyapaar_strategies.strategies.risk_parity import RiskParity
from vyapaar_strategies.strategies.sizing import FixedFractional
from vyapaar_strategies.strategies.turtle import TurtleBreakout

__version__ = "0.1.0"

__all__ = [
    "VYAAPAAR_AVAILABLE",
    "Bar",
    "BasketManifest",
    "BollingerMeanReversion",
    "CapitalAllocation",
    "CashFuturesArbitrage",
    "CoveredCallWriter",
    "FixedFractional",
    "InstrumentSelector",
    "MarketMakingStrategy",
    "MemberStrategyRef",
    "OrderEvent",
    "OrderRequest",
    "OrderSide",
    "OrderStatus",
    "OrderType",
    "Parameter",
    "ParameterSpec",
    "PromotionRecord",
    "PromotionStatus",
    "QuotingStrategy",
    "RiskBudget",
    "RiskParity",
    "SimulatedContext",
    "Strategy",
    "StrategyManifest",
    "TWAPSlicer",
    "TimeInForce",
    "TurtleBreakout",
    "VWAPSlicer",
    "__version__",
]
