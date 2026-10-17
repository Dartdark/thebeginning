from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
from jesse.strategies import Strategy
import jesse.indicators as ta
from jesse import utils

CT_TZ = ZoneInfo("America/Chicago")


class NQNFPFade(Strategy):
    """
    NQNFPFade - Retained Baseline (Guardrail 5 Winner)
    Includes parameter switches for NQNFPFadeV1 (Funded Account low-DD variant).
    """
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

        self.reference_price = None
        self.ranges_history = []
        self.today_is_spike = False
        self.signal_direction = 0  # +1 for buy, -1 for short
        self.signal_atr = None
        self.trade_taken_today = False

    def _process_5m_candle(self, candle):
        open_ts_ms = int(candle[0])
        close_ts_ms = open_ts_ms + 300_000
        b_high = float(candle[3])
        b_low = float(candle[4])
        b_close = float(candle[2])

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

            self.reference_price = None
            self.today_is_spike = False
            self.trade_taken_today = False
            self.signal_direction = 0
            self.signal_atr = None
        else:
            if b_high > self.day_high:
                self.day_high = b_high
            if b_low < self.day_low:
                self.day_low = b_low
            self.day_close = b_close

        self.current_close_dt_ct = close_dt_ct

        # 1. Reference price = close of the bar stamped 07:30
        if close_dt_ct.hour == 7 and close_dt_ct.minute == 30:
            self.reference_price = b_close

        # 2. Release spike = range of bar stamped 07:35 on every Monday-Friday
        if close_dt_ct.hour == 7 and close_dt_ct.minute == 35:
            if bar_date.weekday() < 5:
                b_range = b_high - b_low
                if len(self.ranges_history) >= 20:
                    s = sorted(self.ranges_history[-20:])
                    med = (s[9] + s[10]) / 2.0
                    if med > 0 and b_range > 3.0 * med:
                        self.today_is_spike = True
                self.ranges_history.append(b_range)

        # 3. Entry = at close of bar stamped 07:45 on Friday with day-of-month <= 10
        if close_dt_ct.hour == 7 and close_dt_ct.minute == 45:
            if bar_date >= datetime(2018, 1, 2).date():
                if bar_date.weekday() == 4 and bar_date.day <= 10:
                    if self.today_is_spike and self.reference_price is not None and len(self.daily_trs) >= 15:
                        if not self.trade_taken_today:
                            reaction = b_close - self.reference_price
                            atr = sum(self.daily_trs[-15:]) / 15.0
                            if reaction > 0:
                                self.signal_direction = -1  # sell short
                                self.signal_atr = atr
                                self.trade_taken_today = True
                            elif reaction < 0:
                                self.signal_direction = 1   # buy long
                                self.signal_atr = atr
                                self.trade_taken_today = True

    def before(self):
        if not self._initialized_warmup:
            self._initialized_warmup = True
            if len(self.candles) > 1:
                for c in self.candles[:-1]:
                    self._process_5m_candle(c)
        self._process_5m_candle(self.current_candle)

    def should_long(self) -> bool:
        return self.signal_direction == 1

    def should_short(self) -> bool:
        return self.signal_direction == -1

    def go_long(self):
        notional_one_contract = min(self.available_margin * 0.5, self.price)
        qty = utils.size_to_qty(notional_one_contract, self.price, fee_rate=self.fee_rate)
        self.buy = qty, self.price
        self.signal_direction = 0

    def go_short(self):
        notional_one_contract = min(self.available_margin * 0.5, self.price)
        qty = utils.size_to_qty(notional_one_contract, self.price, fee_rate=self.fee_rate)
        self.sell = qty, self.price
        self.signal_direction = 0

    def on_open_position(self, order):
        if self.signal_atr is not None:
            if self.is_long:
                stop_price = self.position.entry_price - 0.50 * self.signal_atr
                self.stop_loss = self.position.qty, stop_price
            elif self.is_short:
                stop_price = self.position.entry_price + 0.50 * self.signal_atr
                self.stop_loss = self.position.qty, stop_price

    def should_cancel_entry(self) -> bool:
        return False

    def update_position(self):
        if self.current_close_dt_ct is not None:
            if (self.current_close_dt_ct.hour, self.current_close_dt_ct.minute) >= (9, 0):
                self.liquidate()
