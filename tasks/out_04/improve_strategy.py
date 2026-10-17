from datetime import datetime, timedelta
import math
import os
from zoneinfo import ZoneInfo
from jesse.strategies import Strategy
import jesse.indicators as ta
from jesse import utils

CT_TZ = ZoneInfo("America/Chicago")


class NQOvernightBiasML(Strategy):
    """
    NQOvernightBiasML - Retained Baseline (Guardrail 5 Winner)
    Also includes parameter switches for NQONBiasMLV5 (Funded Account low-DD variant).
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

        # Daily ML tracking
        self.had_rth_bar = False
        self.day_open830 = None
        self.day_close1500 = None
        self.stored_days = []  # list of dicts: {'date': date, 'C': close1500, 'O': open830, 'A': last_bar_atr}
        self.today_score = None
        self.daily_scores = {}  # date -> score

        # Overnight & Opening Range
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

    def _compute_score_for_date(self, bar_date):
        if len(self.stored_days) < 59 or len(self.daily_trs) < 15:
            return None

        today_atr = sum(self.daily_trs[-15:]) / 15.0

        C0 = self.stored_days[0]['C']
        O0 = self.stored_days[0]['O']

        ret1 = math.log(C0 / self.stored_days[1]['C'])
        ret5 = math.log(C0 / self.stored_days[5]['C'])
        ret20 = math.log(C0 / self.stored_days[20]['C'])
        rth1 = math.log(C0 / O0)

        sum_A59 = sum(self.stored_days[k]['A'] for k in range(59))
        atr_ratio = today_atr / ((today_atr + sum_A59) / 60.0)

        avg_C50 = sum(self.stored_days[k]['C'] for k in range(50)) / 50.0
        dist50 = math.log(C0 / avg_C50)

        r = [math.log(self.stored_days[k]['C'] / self.stored_days[k + 1]['C']) for k in range(20)]
        r_short = r[:5]
        m_short = sum(r_short) / 5.0
        s_short = math.sqrt(sum((x - m_short) ** 2 for x in r_short) / 4.0)

        r_long = r[:20]
        m_long = sum(r_long) / 20.0
        s_long = math.sqrt(sum((x - m_long) ** 2 for x in r_long) / 19.0)

        rv = (s_short / s_long) if s_long > 0 else 1.0

        dow = bar_date.weekday() + 1
        dow1 = 1.0 if dow == 1 else 0.0
        dow2 = 1.0 if dow == 2 else 0.0
        dow3 = 1.0 if dow == 3 else 0.0
        dow4 = 1.0 if dow == 4 else 0.0
        dow5 = 1.0 if dow == 5 else 0.0

        last_stored_date = self.stored_days[0]['date']
        if last_stored_date.year != bar_date.year or last_stored_date.month != bar_date.month:
            today_tdm = 1
        else:
            cnt = 0
            for d in self.stored_days:
                if d['date'].year == bar_date.year and d['date'].month == bar_date.month:
                    cnt += 1
                else:
                    break
            today_tdm = cnt + 1
        tdm3 = 1.0 if today_tdm <= 3 else 0.0

        if bar_date.weekday() < 5:
            friday_date = bar_date + timedelta(days=(4 - bar_date.weekday()))
            opex = 1.0 if 15 <= friday_date.day <= 21 else 0.0
        else:
            opex = 0.0

        score = (
            0.05535517974
            + 2.550842376 * ret1
            + 0.05697325462 * ret5
            - 0.08269967616 * ret20
            + 1.729498386 * rth1
            - 0.03608247696 * atr_ratio
            - 0.3355796551 * dist50
            - 0.03976333906 * rv
            + 0.07809504609 * dow1
            - 0.008560935801 * dow2
            - 0.02267574106 * dow3
            - 0.03459885088 * dow4
            - 0.005544247888 * dow5
            + 0.1654566373 * tdm3
            - 0.003794081905 * opex
        )
        return score

    def _process_15m_candle(self, candle):
        open_ts_ms = int(candle[0])
        close_ts_ms = open_ts_ms + 900_000
        b_open = float(candle[1])
        b_high = float(candle[3])
        b_low = float(candle[4])
        b_close = float(candle[2])

        close_dt_ct = datetime.fromtimestamp(close_ts_ms / 1000.0, tz=CT_TZ)
        bar_date = close_dt_ct.date()
        hour = close_dt_ct.hour
        minute = close_dt_ct.minute

        if bar_date != self.current_ct_date:
            if self.current_ct_date is not None:
                if len(self.daily_trs) >= 15:
                    last_bar_atr = sum(self.daily_trs[-15:]) / 15.0
                elif len(self.daily_trs) > 0:
                    last_bar_atr = sum(self.daily_trs) / float(len(self.daily_trs))
                else:
                    last_bar_atr = 0.0

                if self.current_ct_date.weekday() < 5 and self.prev_date_last_close is not None:
                    tr = max(self.day_high, self.prev_date_last_close) - min(self.day_low, self.prev_date_last_close)
                    self.daily_trs.append(tr)
                self.prev_date_last_close = self.day_close

                if (self.current_ct_date.weekday() < 5 and
                    self.had_rth_bar and
                    self.day_close1500 is not None and
                    self.day_open830 is not None):
                    self.stored_days.insert(0, {
                        'date': self.current_ct_date,
                        'C': self.day_close1500,
                        'O': self.day_open830,
                        'A': last_bar_atr
                    })

            self.current_ct_date = bar_date
            self.day_high = b_high
            self.day_low = b_low
            self.day_close = b_close
            self.had_rth_bar = False
            self.day_open830 = None
            self.day_close1500 = None

            self.trade_taken_today = False
            self.or_complete = False
            self.bias = 0
            self.signal_long = None
            self.signal_short = None
            self.signal_atr = None

            self.today_score = self._compute_score_for_date(bar_date)
            if self.today_score is not None and bar_date.weekday() < 5:
                self.daily_scores[bar_date] = self.today_score
        else:
            if b_high > self.day_high:
                self.day_high = b_high
            if b_low < self.day_low:
                self.day_low = b_low
            self.day_close = b_close

        if (11, 0) <= (hour, minute) <= (15, 15):
            self.had_rth_bar = True

        if (8, 30) < (hour, minute) <= (8, 45):
            if self.day_open830 is None:
                self.day_open830 = b_open

        if (hour, minute) <= (15, 0):
            self.day_close1500 = b_close

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

        self.signal_long = None
        self.signal_short = None
        if bar_date >= datetime(2018, 1, 2).date():
            is_early = self._is_early_day(bar_date)
            last_entry_time = (11, 0) if is_early else (14, 0)
            bar_time = (hour, minute)

            if (8, 45) <= bar_time < last_entry_time:
                if self.bias != 0 and self.or_complete and len(self.daily_trs) >= 15:
                    if not self.is_open and not self.trade_taken_today:
                        if self.today_score is not None:
                            adx = ta.adx(self.candles, period=14)
                            if adx > 20.0:
                                self.signal_atr = sum(self.daily_trs[-15:]) / 15.0
                                if self.bias == 1 and self.today_score >= 0.03:
                                    if b_close >= self.or_high - 0.50:
                                        self.signal_long = 'market'
                                    else:
                                        self.signal_long = 'stop'
                                elif self.bias == -1 and self.today_score >= 0.0:
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
            stop_dist = 0.30 * self.signal_atr
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
