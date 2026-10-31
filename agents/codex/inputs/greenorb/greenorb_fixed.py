"""15-minute Green ORB Strategy, FIXED-SIZE version (the research books' GreenORB).

The same rules as ``green_ORB_new_bracket.py`` (the production version,
which sizes with ``risk_based``), but sized with a flat ``fixed_contracts`` (default
1 lot), plus a limit-entry option and three ablation switches whose defaults keep
the rules. Every MNQ research book measured since 2026-09-21 (R3T+OB, Robust4,
R3T+OB + MRburni, ...) uses this class. Split out on 2026-10-06 so that the
production portfolio keeps its risk-sized GreenORB under the original name.

This strategy builds a 15-minute opening range (ORB) and uses the three 5-minute
candles inside that window to confirm direction. After the ORB is established, it
waits for a 5-minute candle to close beyond the ORB in the same direction and then
opens a bracketed position.

Trade rules:
1. Create an ORB from 9:30 to 9:45 NY time (15-minute opening range);
2. Require the three 5-minute candles within 9:30-9:45 to all be bullish (long bias)
   or all be bearish (short bias);
3. After 9:45, wait for a 5-minute candle close to break above the ORB high (long)
   or below the ORB low (short);
4. Enter on the qualifying break and place a bracket with SL at the opposite side of
   the ORB and TP at 1.5R;
5. Close the position before the regular session close.

"""

import copy
from dataclasses import dataclass
from datetime import UTC, date, datetime, time, timedelta
from decimal import Decimal
from zoneinfo import ZoneInfo

from loguru import logger

from liqport import (
    Bracket,
    BracketStatus,
    Candle,
    Instrument,
    OrderType,
    Run,
    Side,
    SliceableDeque,
    Strategy,
    StrategyConfig,
    close_and_cancel,
    fixed_size,
    rr,
)
from liqport.auto_rules import CloseAtTimeRule, TradeWindowRule
from liqport.indicators import ATRIndicator, DebugIndicator, TBLIndicator, VWAPIndicator

# Live-only log window (minutes): feature and bracket logs fire only when the
# candle is within this window of wallclock (so backtests stay silent).
_LIVE_LOG_WINDOW_MINUTES = 15


@dataclass
class GreenORBFixedConfig(StrategyConfig):
    """Configuration for 15-minute Green ORB Strategy."""

    # Full symbol
    full_symbol: str = "CME:MNQ.V.0"

    # Timezone
    timezone: str = "America/New_York"

    # Trading session times
    close_before_close_time: time = time(15, 58, tzinfo=ZoneInfo("America/New_York"))

    # Opening range breakout (ORB)
    orb_start: time = time(9, 30, tzinfo=ZoneInfo("America/New_York"))
    orb_end: time = time(9, 45, tzinfo=ZoneInfo("America/New_York"))

    trading_time_start: time = time(9, 45, tzinfo=ZoneInfo("America/New_York"))
    trading_time_end: time = time(12, 0, tzinfo=ZoneInfo("America/New_York"))

    # Risk management
    risk_reward_ratio: Decimal = Decimal("1.5")

    # Subscriptions
    base_timeframe: str = "1m"  # tick/base
    entry_timeframe: str = "5m"  # main entry confirmation

    # Sizing: a flat fixed_contracts. The original "risk" mode
    # (risk_based(max_risk_per_trade), removed - ledger 2p) ROUND_DOWNs to 0
    # contracts once one contract's risk exceeds the budget,
    # silently skipping the widest-stop (highest-volatility) days - so the
    # true minimum-risk configuration is a flat 1 lot, not a small risk %.
    # WINNER: flat 1 contract. Risk sizing earns more gross but more than
    # DOUBLES time underwater (398 -> 898 days) and drops Ret/DD 11.13 -> 4.24.
    fixed_contracts: int = 1

    # Entry mechanics. MARKET pays slippage at the next bar's open; "limit"
    # rests a LIMIT at the signal bar's close, which pays none. These two
    # strategies evaluate on 1-MINUTE ticks, so validity is counted in minutes,
    # not decision bars - getting that wrong is what made an earlier attempt
    # raise on every tick (swallowed by Observer.notify into a 13 GB traceback
    # flood). Re-entry is already blocked by is_traded_long/short, which is set
    # on PLACEMENT, so ageing out an unfilled limit cannot cause a re-place.
    entry_order_type: str = "market"
    limit_valid_minutes: int = 5
    # Ablation switches (2026-09-23). Defaults reproduce the shipped rules.
    require_orb_color: bool = True  # all 3 ORB bars green (long) / red (short)
    use_vwap_filter: bool = True  # entry close must be beyond VWAP
    max_stop_pct: Decimal = Decimal("0.01")  # skip if stop > share of price; 0 = off


class GreenORBFixedStrategy(Strategy):
    """15-minute Green ORB Strategy."""

    def __init__(
        self,
        config: GreenORBFixedConfig = GreenORBFixedConfig(),
    ) -> None:
        """Initialize the strategy."""
        super().__init__()

        self.config = config

        # Cache the tz instance. ZoneInfo is C-backed; skipping per-tick
        # ZoneInfo lookups also saves ~700k calls per backtest.
        self._tz = ZoneInfo(self.config.timezone)

        self._long_bracket: Bracket | None = None
        self._short_bracket: Bracket | None = None
        self._limit_age: dict[str, int] = {}

        self._full_symbol = self.config.full_symbol

        self.is_traded_long = False
        self.is_traded_short = False

        self.current_trading_day_date: date | None = None

        self.current_dt = None

        self._last_ltf_candles: SliceableDeque = SliceableDeque(maxlen=3)

        self.long_trade_allowed = False
        self.short_trade_allowed = False

    def on_start(self, run: Run) -> None:
        """Called when the strategy is started."""
        self.run = run

        self.base_tf = self.run.subscribe(
            Instrument(self.config.full_symbol, timeframe=self.config.base_timeframe),
            callback=self.on_tick,
        )

        self.ltf = self.run.subscribe(
            Instrument(self.config.full_symbol, timeframe=self.config.entry_timeframe),
            callback=self.check_entry,
        )

        self.orb = self.run.subscribe(
            TBLIndicator(
                from_time=self.config.orb_start,
                to_time=self.config.orb_end,
                tzname=self.config.timezone,
            ),
            apply_to=self.base_tf,
            alias="ORB",
        )

        self.atr = self.run.subscribe(
            ATRIndicator(
                length=14,
                draw_on_plot=True,
            ),
            apply_to=self.ltf,
            alias="ATR",
        )

        self.vwap = self.run.subscribe(
            VWAPIndicator(
                draw_on_plot=True,
                std_multipliers=[1, 4],
            ),
            apply_to=self.base_tf,
            alias="VWAP",
        )

        self.debug = self.run.subscribe(
            DebugIndicator(),
            apply_to=self.ltf,
            alias="DEBUG",
        )

        # Register auto rule to close positions before market close
        self.register_auto_rule(
            CloseAtTimeRule(
                full_symbol=self.config.full_symbol,
                close_time=self.config.close_before_close_time,
                timezone=self.config.timezone,
                order_comment="Close before close",
            )
        )

        # Register trading window rule
        self.register_auto_rule(
            TradeWindowRule(
                full_symbol=self.config.full_symbol,
                windows=[
                    (self.config.trading_time_start, self.config.trading_time_end)
                ],
                timezone=self.config.timezone,
            )
        )

    def check_direction_bias(self, candle: Candle) -> None:
        """Check direction bias on ORB end."""
        if len(self._last_ltf_candles) < 3:
            return

        if not self.config.require_orb_color:
            self.long_trade_allowed = self.short_trade_allowed = True
            return

        self.long_trade_allowed = all(c.open < c.close for c in self._last_ltf_candles)
        self.short_trade_allowed = all(c.open > c.close for c in self._last_ltf_candles)

    def _stop_ok(self, frac: Decimal) -> bool:
        """Max-stop filter: stop distance as a share of price under the cap."""
        cap = self.config.max_stop_pct
        return cap <= 0 or frac < cap

    def reset_daily_trade_state(self) -> None:
        """Reset daily trade state."""
        self.is_traded_long = False
        self.is_traded_short = False

    def _age_out_limits(self) -> None:
        """Cancel an unfilled resting LIMIT entry after limit_valid_minutes."""
        if self.config.entry_order_type != "limit":
            return
        for attr in ("_long_bracket", "_short_bracket"):
            b = getattr(self, attr, None)
            if b is None or b.status != BracketStatus.ENTRY_PENDING:
                continue
            n = self._limit_age.get(attr, 0) + 1
            if n > self.config.limit_valid_minutes:
                b.cancel()
                setattr(self, attr, None)
                self._limit_age[attr] = 0
            else:
                self._limit_age[attr] = n

    def on_tick(self, candle: Candle) -> None:
        """Called when the tick is received."""
        self._age_out_limits()
        self.current_dt = candle.dt

        if (
            self.current_trading_day_date is None
            or candle.dt.astimezone(self._tz).date() > self.current_trading_day_date
        ):
            self.current_trading_day_date = candle.dt.astimezone(self._tz).date()

            logger.debug(
                f"GreenORB: New trading day {self.current_trading_day_date}. "
                f"Resetting daily trade state."
            )
            self.reset_daily_trade_state()

        if self.current_dt.astimezone(self._tz).time() == self.config.orb_end:
            self.check_direction_bias(candle)

    def long_entry_check(self) -> bool:
        """Long entry check."""
        return (
            self.long_trade_allowed
            and self.ltf.candle.close > self.orb.high
            and not self.is_traded_long
            and (
                not self.config.use_vwap_filter
                or self.ltf.candle.close > self.vwap.vwap
            )
            # and not self.orb.is_low_taken
        )

    def short_entry_check(self) -> bool:
        """Short entry check."""
        return (
            self.short_trade_allowed
            and self.ltf.candle.close < self.orb.low
            and not self.is_traded_short
            and (
                not self.config.use_vwap_filter
                or self.ltf.candle.close < self.vwap.vwap
            )
            # and not self.orb.is_high_taken
        )

    def long_entry(self, stop_price: Decimal) -> None:
        """Entry long with market order."""
        logger.debug(
            f"GreenORB: Long entry: dt: {self.current_dt}, "
            f"stop_price: {stop_price}, "
            f"contracts: {self.config.fixed_contracts}"
        )

        self._long_bracket = self.bracket_manager.place_bracket(
            Bracket(
                full_symbol=self.config.full_symbol,
                side=Side.LONG,
                entry_type=(
                    OrderType.LIMIT if self.config.entry_order_type == "limit" else None
                ),
                stop_price=stop_price,
                take_price=rr(self.config.risk_reward_ratio),
                sizing=fixed_size(self.config.fixed_contracts),
                on_reject=close_and_cancel(),
            )
        )
        if datetime.now(UTC) - self.current_dt < timedelta(
            minutes=_LIVE_LOG_WINDOW_MINUTES
        ):
            logger.info(
                f"GreenORB bracket placed: "
                f"side=LONG, "
                f"entry={self._long_bracket.get_entry_price()}, "
                f"stop={self._long_bracket.get_stop_price()}, "
                f"take={self._long_bracket.get_take_price()}, "
                f"bracket_id={str(self._long_bracket.id)[:8]}"
            )

    def short_entry(self, stop_price: Decimal) -> None:
        """Entry short with market order."""
        logger.debug(
            f"GreenORB: Short entry: dt: {self.current_dt}, "
            f"stop_price: {stop_price}, "
            f"contracts: {self.config.fixed_contracts}"
        )

        self._short_bracket = self.bracket_manager.place_bracket(
            Bracket(
                full_symbol=self.config.full_symbol,
                side=Side.SHORT,
                entry_type=(
                    OrderType.LIMIT if self.config.entry_order_type == "limit" else None
                ),
                stop_price=stop_price,
                take_price=rr(self.config.risk_reward_ratio),
                sizing=fixed_size(self.config.fixed_contracts),
                on_reject=close_and_cancel(),
            )
        )
        if datetime.now(UTC) - self.current_dt < timedelta(
            minutes=_LIVE_LOG_WINDOW_MINUTES
        ):
            logger.info(
                f"GreenORB bracket placed: "
                f"side=SHORT, "
                f"entry={self._short_bracket.get_entry_price()}, "
                f"stop={self._short_bracket.get_stop_price()}, "
                f"take={self._short_bracket.get_take_price()}, "
                f"bracket_id={str(self._short_bracket.id)[:8]}"
            )

    def check_entry(self, candle: Candle) -> None:
        """Called when the low timeframe candle is received."""
        self._last_ltf_candles.append(copy.copy(candle))
        self.current_dt = candle.dt
        _recent = datetime.now(UTC) - candle.dt < timedelta(
            minutes=_LIVE_LOG_WINDOW_MINUTES
        )

        if (
            self.orb.high is None
            or self.orb.low is None
            or self.orb.high_dt.date().day != candle.dt.date().day
        ):
            if _recent:
                logger.info(
                    f"GreenORB check_entry SKIP: "
                    f"dt={candle.dt}, "
                    f"orb_h={self.orb.high}, "
                    f"orb_l={self.orb.low}, "
                    f"orb_h_dt={getattr(self.orb, 'high_dt', None)}, "
                    f"candle_day={candle.dt.date().day}"
                )
            return

        ny_time = self.current_dt.astimezone(self._tz).time()
        if _recent:
            logger.info(
                f"GreenORB check_entry: "
                f"dt={candle.dt}, ny={ny_time}, "
                f"ltf_c={self.ltf.candle.close}, "
                f"orb=[{self.orb.low}, {self.orb.high}], "
                f"vwap={self.vwap.vwap}, "
                f"long_ok={self.long_trade_allowed}, "
                f"short_ok={self.short_trade_allowed}, "
                f"traded_L={self.is_traded_long}, "
                f"traded_S={self.is_traded_short}"
            )

        if self.long_entry_check():
            if _recent:
                logger.info(f"GreenORB: Long entry check PASSED for {candle}")
            stop_price = self.orb.low
            frac = (self.ltf.candle.close - stop_price) / self.ltf.candle.close
            if self._stop_ok(frac):
                self.long_entry(stop_price)
                self.is_traded_long = True

        if self.short_entry_check():
            if _recent:
                logger.info(f"GreenORB: Short entry check PASSED for {candle}")
            stop_price = self.orb.high
            frac = (stop_price - self.ltf.candle.close) / self.ltf.candle.close
            if self._stop_ok(frac):
                self.short_entry(stop_price)
                self.is_traded_short = True
