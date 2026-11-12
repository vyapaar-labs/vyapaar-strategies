# `vyapaar-strategies` — Strategy SDK Reference

Documents `vyapaar_strategies/sdk/`: the pure-Python strategy authoring SDK with
Jesse-style lifecycle hooks, streaming `Decimal` indicators, a declarative
`Parameter` descriptor, and a deterministic simulated execution context.

## `Strategy` Base Class (`sdk/strategy.py`)

```python
class Strategy:
    def __init__(self, **overrides: object) -> None: ...
```

Constructor creates an `IndicatorRegistry`, a module-qualified logger, and
applies any `**overrides` with `setattr` (values are validated when they hit a
`Parameter` descriptor). There is **no** `stop_loss()` helper and no
`self.sma` sugar — indicators live in `self.indicators`.

### Lifecycle hooks (overridable, no-ops by default)

| Hook | Signature | Notes |
|------|-----------|-------|
| `on_start` | `(self) -> None` | Once per run, before the first bar. Declare indicators here. |
| `on_bar` | `(self, bar: Bar) -> None` | Main strategy logic; driven by `run()`. |
| `on_tick` | `(self, tick: object) -> None` | **Stub — never dispatched.** Neither `Strategy.run` nor `SimulatedContext.run` feeds ticks, only bars. See [gap 0001](../gaps/0001-on-tick-not-dispatched.md). |
| `on_order_event` | `(self, event: OrderEvent) -> None` | Called for every order event (immediately in `submit()`, plus per-bar outbox fills under `SimulatedContext`). |
| `on_stop` | `(self) -> None` | Once per run, after the last bar. |

### Execution helpers

| Method | Signature | Behavior |
|--------|-----------|----------|
| `buy` | `buy(instrument, quantity, limit_price=None) -> OrderEvent` | `OrderType.MARKET` unless `limit_price` is given (then `LIMIT`); tag `"strategy.buy"`. |
| `sell` | `sell(instrument, quantity, limit_price=None) -> OrderEvent` | Same, tag `"strategy.sell"`. |
| `submit` | `submit(request: OrderRequest) -> OrderEvent` | Requires a context; forwards to `context.submit` and dispatches `on_order_event`. |
| `position` | `position(instrument) -> Decimal` | Requires a context; context positions are exact `Decimal`. |
| `current_price` | `current_price(instrument) -> Decimal` | Requires a context. |
| `run` | `run(context: StrategyContext, bars: list[Bar]) -> None` | Harness (see below). |
| `indicators` | property | The `IndicatorRegistry`. |
| `logger` | property | `logging.Logger` named `<module>.<ClassName>`. |

Calling `buy`/`sell`/`submit`/`position`/`current_price` before `run()` raises
`RuntimeError("strategy has no execution context; call run(context, bars)")`.

`_qty(value)` is a static helper converting `int`/`str` to `Decimal` via
`Decimal(str(value))`; the public helpers pass quantities through it.

### `run(context, bars)` harness

```python
def run(self, context: StrategyContext, bars: list[Bar]) -> None:
    if isinstance(context, SimulatedContext):
        context.run(self, bars)          # feed -> outbox events -> on_bar per bar
    else:
        self._context = context
        self.on_start()
        for bar in bars:
            self.on_bar(bar)
        self.on_stop()
```

For a `SimulatedContext` the context drives the loop and dispatches order events
from the per-bar fill outbox. For any other `StrategyContext`, the strategy
drives itself and events arrive synchronously from `submit()`.

### `IndicatorRegistry`

Per-`(kind, instrument, period, deviations)` streaming store — requesting the
same indicator twice returns the same instance, so a strategy declares once in
`on_start` and the instance is fed by every bar.

| Method | Returns |
|--------|---------|
| `sma(instrument, period)` | `SMA` |
| `ema(instrument, period)` | `EMA` |
| `rsi(instrument, period=14)` | `RSI` |
| `atr(instrument, period=14)` | `ATR` |
| `bollinger(instrument, period=20, deviations=2)` | `BollingerBands` |

## Streaming Indicators (`sdk/indicators.py`)

Base class `Indicator(period)` raises `ValueError` for `period <= 0`; the
`ready`/`value` properties raise `NotImplementedError` on the base (abstract by
design — subclasses implement them).

| Class | Update input | Ready when | Value |
|-------|-------------|------------|-------|
| `SMA(period)` | `Decimal` | `len(history) >= period` | mean of trailing `period` values; `previous_value` = mean one step ago (or `None` until `period + 1` samples) — the cross-detection hook. |
| `EMA(period)` | `Decimal` | first update (seeded) | recursive; multiplier `2 / (period + 1)`; `value` raises `ValueError` before ready. |
| `RSI(period=14)` | `Decimal` | Wilder average gain set | `100` when average loss is zero, else `100 - 100/(1 + RS)`; raises `ValueError` before ready. |
| `ATR(period=14)` | `Bar` | Wilder `_atr` set | true range max of `high-low`, `\|high-prev_close\|`, `\|low-prev_close\|`, Wilder-smoothed; raises `ValueError` before ready. |
| `BollingerBands(period=20, deviations=2)` | `Decimal` | `len(history) == period` | `middle` / `upper` / `lower`; stddev via `Decimal.sqrt` on the variance. |

Module-level helpers (import from `vyapaar_strategies.sdk.indicators` — not
re-exported at `sdk`/package level):

```python
def crosses_above(fast: Indicator, slow: Indicator) -> bool: ...
def crosses_below(fast: Indicator, slow: Indicator) -> bool: ...
```

Both read `previous_value` off each indicator (returning `False` when either
indicator lacks it) and require both indicators `ready`. All arithmetic is exact
`Decimal`.

## `Parameter` descriptor (`sdk/parameter.py`)

```python
class Parameter:
    def __init__(self, default, min=None, max=None, step=None) -> None: ...
    def validate(self, value) -> None: ...
```

Jesse-style declarative hyperparameters. `__set__` validates on assignment:
- `value` must be `>= min` and `<= max` (bounds compared in `Decimal`);
- if both `step` and `min` are set, `(value - min) % step` must be zero.

Violations raise `ValueError`. Reading an unset instance attribute falls back to
`default`; class-level access returns the descriptor itself.

## Order domain (`sdk/order.py`)

All `StrEnum`s with lowercase values:

| Enum | Members |
|------|---------|
| `OrderSide` | `BUY="buy"`, `SELL="sell"` |
| `OrderType` | `LIMIT="limit"`, `MARKET="market"`, `STOP_LIMIT="stop_limit"`, `STOP_MARKET="stop_market"` |
| `OrderStatus` | `PENDING`, `OPEN`, `PARTIALLY_FILLED`, `COMPLETE`, `REJECTED`, `CANCELLED` |
| `TimeInForce` | `DAY="day"`, `IOC="ioc"`, `GTD="gtd"` |

```python
@dataclass(frozen=True, slots=True)
class OrderRequest:
    instrument: str
    side: OrderSide
    quantity: Decimal                  # coerced; must be > 0
    order_type: OrderType = OrderType.MARKET
    limit_price: Decimal | None = None # coerced
    tag: str | None = None

@dataclass(frozen=True, slots=True)
class OrderEvent:
    order_id: str
    instrument: str
    side: OrderSide
    status: OrderStatus
    quantity: Decimal
    filled_quantity: Decimal
    price: Decimal | None = None
    ts: datetime | None = None
```

## `Bar` (`sdk/bar.py`)

```python
@dataclass(frozen=True, slots=True)
class Bar:
    instrument: str
    ts: datetime
    open: Decimal
    high: Decimal
    low: Decimal
    close: Decimal
    volume: int = 0
    interval: str = "1d"
    def to_dict(self) -> dict[str, object]: ...
```

OHLC fields are coerced to `Decimal`; `high < low` raises `ValueError`.

## Execution contexts (`sdk/context.py`)

```python
@runtime_checkable
class StrategyContext(Protocol):
    def submit(self, request: OrderRequest) -> OrderEvent: ...
    def current_price(self, instrument: str) -> Decimal: ...
    def position(self, instrument: str) -> Decimal: ...
```

`SimulatedContext` is the only concrete context in-repo:

| Member | Semantics |
|--------|-----------|
| `feed(bar)` | Records the latest bar per instrument and re-evaluates resting limit orders at its close. |
| `current_price(instrument)` | Latest fed close; `KeyError` if no bar fed for that instrument. |
| `position(instrument)` | Net signed position (0 default). |
| `submit(request)` | Market orders fill immediately at the current close. Limit orders fill at `limit_price` when already crossed (BUY `price <= limit`, SELL `price >= limit`), else rest and are re-checked every bar. Order ids `SIM-00001`… |
| `run(strategy, bars)` | Drives `on_start` → per bar `feed` + outbox `on_order_event` + `on_bar` → `on_stop`. |
| `events` / `orders` | Recorded `OrderEvent`s and `OrderRequest`s (used by tests to assert fills). |

## `QuoteState` mixin (`sdk/quoting.py`)

Tracks whether a bid/ask quote is currently resting so quoting-style strategies
never stack duplicates:

```python
class QuoteState:
    def on_order_event(self, event: OrderEvent) -> None: ...
    @property
    def bid_open(self) -> bool: ...
    @property
    def ask_open(self) -> bool: ...
```

`OrderStatus.OPEN` sets the side open; `OrderStatus.COMPLETE` clears it.

## Zero-Floats / Decimal Policy

Every price, quantity, position, indicator value, and threshold in the SDK is
`decimal.Decimal`. `int`/`str` inputs are converted exactly with
`Decimal(str(value))`; float literals are avoided in financial paths.

## Related

- `vyapaar_strategies/strategies/` — the ported strategies (`code-strategies.md`)
- `vyapaar_strategies/manifest/` — versioned manifest models (`code-manifest.md`)
- `docs/gaps/0001-on-tick-not-dispatched.md`, `docs/gaps/0002-no-live-strategy-context.md`
