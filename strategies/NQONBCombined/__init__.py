from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
from jesse.strategies import Strategy
import jesse.indicators as ta
from jesse import utils

CT_TZ = ZoneInfo("America/Chicago")


class NQONBCombined(Strategy):
    def __init__(self):
        super().__init__()
        self._initialized_warmup = False
        self.current_ct_date = None
        self.day_high = None
        self.day_low = None
        self.day_close = None
        self.prev_date_last_close = None
        self.daily_trs = []
        self.current_close_dt_ct = None

        self.cum_pv = 0.0
        self.cum_vol = 0.0
        self.current_vwap = None

        self.on_high = None
        self.on_low = None
        self.or_high = None
        self.or_low = None
        self.or_complete = False
        self.bias = 0  # +1 for long, -1 for short, 0 for none

        self.signal_long = None   # 'market' or 'stop'
        self.signal_short = None  # 'market' or 'stop'
        self.signal_atr = None
        self.trade_taken_today = False

    def _is_early_day(self, d):
        w = d.weekday()
        m = d.month
        day = d.day
        y = d.year
        if m == 1:
            if day == 1 and w < 5:
                return True
            if day == 2 and w == 0:
                return True
            if w == 0 and 15 <= day <= 21:
                return True
        if m == 2 and w == 0 and 15 <= day <= 21:
            return True
        if m == 5 and w == 0 and day >= 25:
            return True
        if y >= 2022 and m == 6:
            if day == 19 and w < 5:
                return True
            if day == 18 and w == 4:
                return True
            if day == 20 and w == 0:
                return True
        if m == 7:
            if (day == 3 or day == 4) and w < 5:
                return True
            if day == 5 and w == 0:
                return True
        if m == 9 and w == 0 and 1 <= day <= 7:
            return True
        if m == 11:
            if w == 3 and 22 <= day <= 28:
                return True
            if w == 4 and 23 <= day <= 29:
                return True
        if m == 12:
            if (day == 24 or day == 25) and w < 5:
                return True
            if day == 26 and w == 0:
                return True
        return False

    def _process_15m_candle(self, candle):
        open_ts_ms = int(candle[0])
        close_ts_ms = open_ts_ms + 900_000
        b_open = float(candle[1])
        b_high = float(candle[3])
        b_low = float(candle[4])
        b_close = float(candle[2])
        b_volume = float(candle[5])

        close_dt_ct = datetime.fromtimestamp(close_ts_ms / 1000.0, tz=CT_TZ)
        bar_date = close_dt_ct.date()
        hour = close_dt_ct.hour
        minute = close_dt_ct.minute

        if bar_date != self.current_ct_date:
            if self.current_ct_date is not None:
                if self.current_ct_date.weekday() < 5 and self.prev_date_last_close is not None:
                    tr = max(self.day_high, self.prev_date_last_close) - min(self.day_low, self.prev_date_last_close)
                    self.daily_trs.append(tr)
                self.prev_date_last_close = self.day_close
            self.current_ct_date = bar_date
            self.day_high = b_high
            self.day_low = b_low
            self.day_close = b_close

            # Reset daily trade state & VWAP
            self.cum_pv = 0.0
            self.cum_vol = 0.0
            self.trade_taken_today = False
            self.or_complete = False
            self.bias = 0
            self.signal_long = None
            self.signal_short = None
            self.signal_atr = None
        else:
            if b_high > self.day_high:
                self.day_high = b_high
            if b_low < self.day_low:
                self.day_low = b_low
            self.day_close = b_close

        # Update cumulative VWAP
        typical_price = (b_high + b_low + b_close) / 3.0
        self.cum_pv += typical_price * b_volume
        self.cum_vol += b_volume
        self.current_vwap = (self.cum_pv / self.cum_vol) if self.cum_vol > 0 else typical_price

        # Track overnight range (starts at first bar stamped after 23:00, i.e. 23:15, up to 08:30)
        if hour == 23 and minute == 15:
            self.on_high = b_high
            self.on_low = b_low
        elif (hour == 23 and minute > 15) or hour < 8 or (hour == 8 and minute <= 30):
            if self.on_high is not None:
                if b_high > self.on_high:
                    self.on_high = b_high
                if b_low < self.on_low:
                    self.on_low = b_low
            else:
                self.on_high = b_high
                self.on_low = b_low

        # 08:45 bar: opening range and bias calculation
        if hour == 8 and minute == 45:
            self.or_high = b_high
            self.or_low = b_low
            self.or_complete = True
            if self.on_high is not None and self.on_low is not None and self.on_high > self.on_low:
                pos = (b_open - self.on_low) / (self.on_high - self.on_low)
                if pos >= 0.6667:
                    self.bias = 1
                elif pos <= 0.3333:
                    self.bias = -1
                else:
                    self.bias = 0

        self.current_close_dt_ct = close_dt_ct

        # Signal check inside entry window (09:00 CT DELAY + VWAP ALIGNMENT)
        self.signal_long = None
        self.signal_short = None
        if bar_date >= datetime(2018, 1, 2).date():
            is_early = self._is_early_day(bar_date)
            last_entry_time = (11, 0) if is_early else (14, 0)
            bar_time = (hour, minute)

            # Start entry window from 09:00 CT bar close onward:
            if (9, 0) <= bar_time < last_entry_time:
                if self.bias != 0 and self.or_complete and len(self.daily_trs) >= 15:
                    if not self.is_open and not self.trade_taken_today:
                        adx = ta.adx(self.candles, period=14)
                        if adx > 30.0 and self.current_vwap is not None:
                            self.signal_atr = sum(self.daily_trs[-15:]) / 15.0
                            # VWAP alignment: Longs above VWAP, Shorts below VWAP
                            if self.bias == 1 and b_close > self.current_vwap:
                                if b_close >= self.or_high - 0.50:
                                    self.signal_long = 'market'
                                else:
                                    self.signal_long = 'stop'
                            elif self.bias == -1 and b_close < self.current_vwap:
                                if b_close <= self.or_low + 0.50:
                                    self.signal_short = 'market'
                                else:
                                    self.signal_short = 'stop'

    def before(self):
        if not self._initialized_warmup:
            self._initialized_warmup = True
            if len(self.candles) > 1:
                for c in self.candles[:-1]:
                    self._process_15m_candle(c)
        self._process_15m_candle(self.current_candle)

    def should_long(self) -> bool:
        return self.signal_long is not None

    def should_short(self) -> bool:
        return self.signal_short is not None

    def go_long(self):
        notional_one_contract = min(self.available_margin * 0.5, self.price)
        qty = utils.size_to_qty(notional_one_contract, self.price, fee_rate=self.fee_rate)
        if self.signal_long == 'market':
            self.buy = qty, self.price
        elif self.signal_long == 'stop':
            self.buy = qty, self.or_high

    def go_short(self):
        notional_one_contract = min(self.available_margin * 0.5, self.price)
        qty = utils.size_to_qty(notional_one_contract, self.price, fee_rate=self.fee_rate)
        if self.signal_short == 'market':
            self.sell = qty, self.price
        elif self.signal_short == 'stop':
            self.sell = qty, self.or_low

    def on_open_position(self, order):
        self.trade_taken_today = True
        self.signal_long = None
        self.signal_short = None
        if self.signal_atr is not None:
            stop_dist = 0.25 * self.signal_atr
            target_dist = 3.0 * stop_dist
            if self.is_long:
                self.stop_loss = self.position.qty, self.position.entry_price - stop_dist
                self.take_profit = self.position.qty, self.position.entry_price + target_dist
            elif self.is_short:
                self.stop_loss = self.position.qty, self.position.entry_price + stop_dist
                self.take_profit = self.position.qty, self.position.entry_price - target_dist

    def should_cancel_entry(self) -> bool:
        return True

    def update_position(self):
        if self.is_open and self.current_close_dt_ct is not None:
            is_early = self._is_early_day(self.current_ct_date)
            exit_time = (11, 30) if is_early else (14, 30)
            bar_time = (self.current_close_dt_ct.hour, self.current_close_dt_ct.minute)
            if bar_time >= exit_time:
                self.liquidate()
