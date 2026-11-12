# `vyapaar-strategies` — Ported Strategies Reference

Documents `vyapaar_strategies/strategies/`: ten strategy classes in nine
modules, ported from the StockSharp idea-inheritance catalog, all subclasses of
`Strategy` (two also mix in `QuoteState`). Every strategy is driven the same
way:

```python
from vyapaar_strategies import SimulatedContext, TurtleBreakout

strategy = TurtleBreakout(entry_period=20, exit_period=10)
context = SimulatedContext()
strategy.run(context, bars)   # bars: list[Bar]
```

## Strategy classes

| Class | Module | Base | Description |
|-------|--------|------|-------------|
| `TurtleBreakout` | `turtle.py` | `Strategy` | Donchian-channel breakout trend follower. |
| `BollingerMeanReversion` | `mean_reversion.py` | `Strategy` | Fade lower-band tags back to the mid-band. |
| `MarketMakingStrategy` | `market_making.py` | `QuoteState, Strategy` | Two-sided maker around the last close, inventory-aware. |
| `QuotingStrategy` | `quoting.py` | `QuoteState, Strategy` | Two-sided quoting around an EMA fair value. |
| `CashFuturesArbitrage` | `arbitrage.py` | `Strategy` | Pairs trade on the cash–futures basis. |
| `RiskParity` | `risk_parity.py` | `Strategy` | Inverse-volatility allocation with periodic rebalance. |
| `TWAPSlicer` | `execution.py` | `Strategy` | Time-weighted order slicing. |
| `VWAPSlicer` | `execution.py` | `Strategy` | Volume-profile-weighted order slicing. |
| `CoveredCallWriter` | `options.py` | `Strategy` | Own the underlying, write OTM calls, buy back on appreciation. |
| `FixedFractional` | `sizing.py` | `Strategy` | SMA cross entries sized as a fixed fraction of notional risked. |

All `Parameter` defaults/bounds below match both the class descriptors and the
corresponding `catalog/*.toml` step manifests.

## Per-strategy semantics

### `TurtleBreakout` (`turtle.py`)

- Parameters: `instrument` (`"NSE:NIFTY50-INDEX"`), `entry_period` (20, 5–60),
  `exit_period` (10, 5–60), `quantity` (10, 1–1000).
- Maintains rolling high/low lists; **Donchian channels exclude the current
  bar** (`self._highs[-entry_period - 1 : -1]`, same for lows).
- Flat + `close > channel_high` → `buy`; long + `close < channel_low` → `sell`
  the full position. Ignores bars for other instruments.

### `BollingerMeanReversion` (`mean_reversion.py`)

- Parameters: `instrument` (`"NSE:RELIANCE-EQ"`), `period` (20, 5–100),
  `deviations` (2, 1–4), `quantity` (10, 1–1000).
- `on_start` declares `self.indicators.bollinger(...)`; each bar feeds the
  close.
- Buy when flat, `close <= lower`, **and `lower < middle`** (zero-volatility
  guard against buy/sell oscillation when bands collapse). Exit when long and
  `close >= middle`.

### `MarketMakingStrategy` (`market_making.py`)

- Parameters: `instrument` (`"NSE:RELIANCE-EQ"`), `spread` (`"0.50"`),
  `quote_quantity` (5), `max_position` (50).
- Quotes `close ± spread/2`. Flat → both sides; long below `max_position` →
  ask only; short above `-max_position` → bid only (inventory bleed).
- `QuoteState` + `on_order_event` guarantee at most one resting quote per side.

### `QuotingStrategy` (`quoting.py`)

- Parameters: `instrument` (`"NSE:NIFTY50-INDEX"`), `fast_ema` (20, 5–100),
  `spread` (`"1.00"`), `quantity` (5).
- EMA fair value fed by every close; quotes `fair ± spread/2`; flat → both
  sides, else the position-reducing side only. `QuoteState` prevents stacking.

### `CashFuturesArbitrage` (`arbitrage.py`)

- Parameters: `cash_instrument` (`"NSE:RELIANCE-EQ"`),
  `futures_instrument` (`"NFO:RELIANCE24DECFUT"`), `entry_threshold` (`"0.50"`),
  `exit_threshold` (`"0.10"`), `quantity` (10).
- `basis = futures_close - cash_close`. Flat + `basis > entry` → sell futures +
  buy cash; flat + `basis < -entry` → buy futures + sell cash; positioned +
  `|basis| <= exit` → unwind both legs.

### `RiskParity` (`risk_parity.py`)

- Parameters: `instruments` (comma-separated, default
  `"NSE:NIFTY50-INDEX,NSE:BANKNIFTY-INDEX"`), `lookback` (20), `rebalance_period`
  (5), `notional` (100000).
- Accumulates per-leg returns; needs ≥ 2 legs and `lookback` returns each.
- Every `rebalance_period` bars computes inverse-volatility weights (they sum to
  1) and rebalances to `target_qty = notional * weight / current_price`
  quantized to `0.01`, buying/selling the delta per leg. Volatility is the
  `Decimal.sqrt` of the return variance.

### `TWAPSlicer` (`execution.py`)

- Parameters: `instrument` (`"NSE:RELIANCE-EQ"`), `total_quantity` (100),
  `slices` (10), `side` (`"buy"`).
- `slice_size = total / slices`; one child order per bar; the final slice
  absorbs any rounding remainder so the parent quantity is conserved exactly.
- Note: `side` is a plain `Parameter` string, `"buy"` or `"sell"` — any other
  value routes to `sell`.

### `VWAPSlicer` (`execution.py`)

- Parameters: `instrument`, `total_quantity`, `slices`, `side`, and `profile`
  (default `"15,13,12,11,10,9,8,7,8,7"`).
- `on_start` normalizes the comma-separated profile into weights
  (`weight = part / total`). Per bar: `target = total * weight` quantized to
  `0.01`; the last slice absorbs rounding remainder (quantity conserved).
- Deterministic offline (fixed profile). The profile must have at least
  `slices` entries — indexing past the profile raises `IndexError` (no
  validation couples `slices` to profile length).

### `CoveredCallWriter` (`options.py`)

- Parameters: `underlying` (`"NSE:RELIANCE-EQ"`), `call_instrument`
  (`"NFO:RELIANCE24DEC2500CE"`), `quantity` (10), `roll_back_percent` (`"1.05"`).
- Buys the underlying when flat; on the next call bar writes the call at market
  (records the write price); buys the call back when its close reaches
  `write_price * roll_back_percent`.

### `FixedFractional` (`sizing.py`)

- Parameters: `instrument` (`"NSE:RELIANCE-EQ"`), `notional` (100000),
  `risk_percent` (`"1"`), `stop_distance` (`"5"`), `fast_period` (10),
  `slow_period` (30).
- Fast SMA crossing above slow SMA → buy
  `(notional * risk_percent / 100) / stop_distance` rounded **down** to whole
  shares (only if `> 0`); cross back below → sell the position.

## Research–Live Parity

The exact same strategy class runs offline through `Strategy.run(context, bars)`
with `SimulatedContext`. Running the same class against a live/feed-backed
`StrategyContext` is a cross-repo concern (`vyapaar-runtime` / `vyapaar-exec`);
no such context exists in this repo — see
[gap 0002](../gaps/0002-no-live-strategy-context.md).

## Zero-Floats Policy

All prices, spreads, thresholds, quantities, weights, and indicator values are
`decimal.Decimal`; string parameter defaults are converted exactly
(`Decimal(str(value))`).

## Related

- `vyapaar_strategies/sdk/` — base classes and primitives (`code-sdk.md`)
- `catalog/` — step.toml manifests naming each strategy (`module:Class`)
- `tests/strategies/` — one lifecycle test file per strategy
