from datetime import datetime
from zoneinfo import ZoneInfo
from jesse.strategies import Strategy
from jesse import utils

CT_TZ = ZoneInfo("America/Chicago")


class NQVaultBreakV4(Strategy):
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

        self.session_open = None
        self.cum_pv = 0.0
        self.cum_vol = 0.0
        self.current_vwap = None
        self.trades_taken_today = 0
        self.signal_entry = False

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

    def _process_30m_candle(self, candle):
        open_ts_ms = int(candle[0])
        close_ts_ms = open_ts_ms + 1_800_000
        b_open = float(candle[1])
        b_high = float(candle[3])
        b_low = float(candle[4])
        b_close = float(candle[2])
        b_volume = float(candle[5])

        close_dt_ct = datetime.fromtimestamp(close_ts_ms / 1000.0, tz=CT_TZ)
        bar_date = close_dt_ct.date()

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

            self.session_open = b_open
            self.cum_pv = 0.0
            self.cum_vol = 0.0
            self.trades_taken_today = 0
            self.signal_entry = False
        else:
            if b_high > self.day_high:
                self.day_high = b_high
            if b_low < self.day_low:
                self.day_low = b_low
            self.day_close = b_close
            if self.session_open is None:
                self.session_open = b_open

        typical_price = (b_high + b_low + b_close) / 3.0
        self.cum_pv += typical_price * b_volume
        self.cum_vol += b_volume
        self.current_vwap = (self.cum_pv / self.cum_vol) if self.cum_vol > 0 else typical_price

        self.current_close_dt_ct = close_dt_ct

        self.signal_entry = False
        if bar_date >= datetime(2018, 1, 2).date():
            is_early = self._is_early_day(bar_date)
            last_entry_time = (11, 0) if is_early else (14, 30)
            bar_time = (close_dt_ct.hour, close_dt_ct.minute)

            if (10, 0) <= bar_time < last_entry_time:
                if len(self.daily_trs) >= 15 and self.session_open is not None:
                    if self.trades_taken_today < 3 and not self.is_long:
                        atr = sum(self.daily_trs[-15:]) / 15.0
                        noise_level = self.session_open + 0.30 * atr
                        if b_close > noise_level and b_close > self.current_vwap and b_close > b_open:
                            self.signal_entry = True

    def before(self):
        if not self._initialized_warmup:
            self._initialized_warmup = True
            if len(self.candles) > 1:
                for c in self.candles[:-1]:
                    self._process_30m_candle(c)
        self._process_30m_candle(self.current_candle)

    def should_long(self) -> bool:
        return self.signal_entry

    def should_short(self) -> bool:
        return False

    def go_long(self):
        notional_one_contract = min(self.available_margin * 0.5, self.price)
        qty = utils.size_to_qty(notional_one_contract, self.price, fee_rate=self.fee_rate)
        self.buy = qty, self.price
        self.trades_taken_today += 1
        self.signal_entry = False

    def go_short(self):
        pass

    def on_open_position(self, order):
        if self.is_long:
            self.take_profit = self.position.qty, self.position.entry_price + 40.0
            self.stop_loss = self.position.qty, self.position.entry_price - 75.0

    def should_cancel_entry(self) -> bool:
        return False

    def update_position(self):
        if self.is_long and self.current_close_dt_ct is not None:
            is_early = self._is_early_day(self.current_ct_date)
            flatten_time = (11, 30) if is_early else (14, 30)
            bar_time = (self.current_close_dt_ct.hour, self.current_close_dt_ct.minute)
            if bar_time >= flatten_time:
                self.liquidate()
