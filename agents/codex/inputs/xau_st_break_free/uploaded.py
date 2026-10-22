from jesse.strategies import Strategy, cached
import jesse.indicators as ta
from jesse import utils


class XAUSTBreakFree(Strategy):
    """
    prompt used to develop this strategy:

        Hey there,
        
        Research and find a trend-following strategy for trading XAU-USD on Custom Data. Use SuperTrend and whichever else indicators that you find suitable for this strategy.
        
        I need the results to have a Sharpe ratio of at least 1.5 in 2024-2026 (2 years)
        
        -  Risk 3% of the account on each trade.
        -  Use optimization to improve the results.
        -  At the end, apply Monte Carlo simulations to ensure the results are not overfit.
        -  Continue until you find strategies that fully meet the requested criteria.
        - Use the hourly timeframe for the trading side and 4 hours as the anchor timeframe
        - The strategy must take both long and short trades
        - Ensure the configuration is also in the futures mode and not spot
        
        - Set the trading fees to 0.02%
        
        Continue until you either reach the results that I asked for or trying at least 200 strategy variations (and then backtest, etc on each) before stopping. 
    """

    RISK_PCT = 3.0
    MAX_LEV = 4.0

    def trading_hours(self):
        # CME/Globex metals session, verified against the Custom Data XAU-USD history.
        # Holiday entries cover 2026-09 .. 2027-09 only. Patterns observed in the data:
        #   Monday holidays: early close 14:00, evening session reopens 18:00
        #   Juneteenth / Independence Day / Dec 24 / Dec 31: early close 13:00, no evening session
        #   Christmas / New Year on a Friday, Good Friday: closed all day
        # Entries marked (projected) follow the observed pattern for a date not yet in the data;
        # confirm them against the published CME holiday calendar before they occur.
        return {
            'timezone': 'America/New_York',
            'hours': {
                'Sun': '18:00-24:00',
                'Mon-Thu': ['00:00-17:00', '18:00-24:00'],
                'Fri': '00:00-17:00',
            },
            'closed': [
                '2026-12-25',  # Christmas (Fri)
                '2027-01-01',  # New Year (Fri)
                '2027-03-26',  # Good Friday
            ],
            'overrides': {
                '2026-11-26': ['00:00-14:00', '18:00-24:00'],  # Thanksgiving (projected)
                '2026-11-27': '00:00-14:00',                   # day after Thanksgiving (projected)
                '2026-12-24': '00:00-13:00',                   # Christmas Eve, no evening session
                '2026-12-31': '00:00-13:00',                   # New Year's Eve, no evening session
                '2027-01-18': ['00:00-14:00', '18:00-24:00'],  # MLK Day
                '2027-02-15': ['00:00-14:00', '18:00-24:00'],  # Presidents Day
                '2027-03-25': '00:00-17:00',                   # Thursday before Good Friday
                '2027-05-31': ['00:00-14:00', '18:00-24:00'],  # Memorial Day
                '2027-06-18': '00:00-13:00',                   # Juneteenth observed (Fri)
                '2027-07-05': ['00:00-13:00', '18:00-24:00'],  # Independence Day observed (Mon, projected)
                '2027-09-06': ['00:00-14:00', '18:00-24:00'],  # Labor Day
            },
        }

    @property
    @cached
    def anchor(self):
        # 4h candles inside the gold session. get_candles() also returns the still-forming 4h
        # bucket as its last row; [:-1] drops it so the regime uses completed 4h candles only,
        # as in the research. (This is a design choice, not a lookahead-bias fix.)
        candles = self.get_candles(self.exchange, self.symbol, '4h')[:-1]
        return utils.filter_candles_by_hours(candles, self.trading_hours())

    @property
    @cached
    def session_candles(self):
        # 1h candles inside the gold session, EXCLUDING the current candle. Required for the
        # Donchian breakout: the channel must be the PRIOR don_period bars. If the current candle
        # were included, the upper band would be >= its own high and a close could never break it.
        return utils.filter_candles_by_hours(self.candles[:-1], self.trading_hours())

    def st_line(self) -> float:
        return ta.supertrend(self.anchor, period=self.hp['st_period'], factor=self.hp['st_factor']).trend

    def regime(self) -> int:
        line = self.st_line()
        if line <= 0:
            return 0
        d = 1 if self.close > line else -1
        if self.hp['ema4'] > 0:
            e = ta.ema(self.anchor, self.hp['ema4'])
            if d == 1 and self.close < e:
                return 0
            if d == -1 and self.close > e:
                return 0
        return d

    @property
    def atr4(self):
        a = ta.atr(self.anchor)
        return a if a > 0 else ta.atr(self.session_candles) * 4

    @property
    def channel(self):
        return ta.donchian(self.session_candles, self.hp['don_period'])

    def should_long(self) -> bool:
        if not self.is_trading_hours:
            return False
        if self.regime() != 1:
            return False
        if self.hp['l_adx'] > 0 and ta.adx(self.anchor) < self.hp['l_adx']:
            return False
        return self.close > self.channel.upperband

    def should_short(self) -> bool:
        if not self.is_trading_hours:
            return False
        if self.regime() != -1:
            return False
        if self.hp['s_adx'] > 0 and ta.adx(self.anchor) < self.hp['s_adx']:
            return False
        return self.close < self.channel.lowerband

    def should_cancel_entry(self) -> bool:
        return True

    def _qty(self, entry: float, stop: float) -> float:
        margin = self.available_margin
        risk_size = (self.RISK_PCT / 100.0) * margin / abs(entry - stop) * entry
        lev_size = margin * self.MAX_LEV
        hard_size = margin * self.leverage * 0.95
        return utils.size_to_qty(min(risk_size, lev_size, hard_size), entry, fee_rate=self.fee_rate)

    def go_long(self):
        entry = self.price
        stop = entry - self.atr4 * self.hp['atr_stop']
        self.vars['stop'] = stop
        self.vars['tp'] = None
        self.buy = self._qty(entry, stop), entry

    def go_short(self):
        entry = self.price
        stop = entry + self.atr4 * self.hp['s_stop']
        self.vars['stop'] = stop
        self.vars['tp'] = entry - self.atr4 * self.hp['s_tp'] if self.hp['s_tp'] > 0 else None
        self.sell = self._qty(entry, stop), entry

    def on_open_position(self, order) -> None:
        self.vars['best'] = self.close
        if self.is_long:
            self.stop_loss = self.position.qty, self.vars['stop']
        elif self.is_short:
            self.stop_loss = abs(self.position.qty), self.vars['stop']
            if self.vars.get('tp'):
                self.take_profit = abs(self.position.qty), self.vars['tp']

    def update_position(self) -> None:
        if self.is_long:
            if self.hp['exit_on_flip'] == 1 and self.regime() != 1:
                self.liquidate()
                return
            self.vars['best'] = max(self.vars.get('best', self.close), self.close)
            trail = self.vars['best'] - self.atr4 * self.hp['trail_atr']
            if self.average_stop_loss < trail < self.close:
                self.stop_loss = self.position.qty, trail
        elif self.is_short:
            if self.hp['exit_on_flip'] == 1 and self.regime() != -1:
                self.liquidate()
                return
            self.vars['best'] = min(self.vars.get('best', self.close), self.close)
            trail = self.vars['best'] + self.atr4 * self.hp['s_trail']
            if self.close < trail < self.average_stop_loss:
                self.stop_loss = abs(self.position.qty), trail

    def update_chart(self) -> None:
        # main chart: 4h regime lines, 1h breakout channel, live exit levels
        line = self.st_line()
        if line > 0:
            self.add_line_to_candle_chart('4h SuperTrend', line, color='orange')
        if self.hp['ema4'] > 0:
            self.add_line_to_candle_chart('4h EMA', ta.ema(self.anchor, self.hp['ema4']), color='purple')
        channel = self.channel
        self.add_line_to_candle_chart('Donchian high', channel.upperband, color='green')
        self.add_line_to_candle_chart('Donchian low', channel.lowerband, color='red')
        if self.is_open:
            self.add_line_to_candle_chart('stop', self.average_stop_loss, color='gray')
            if self.is_short and self.vars.get('tp'):
                self.add_line_to_candle_chart('take profit', self.average_take_profit, color='blue')

        # entry-strength pane: 4h ADX with the long / short entry thresholds
        self.add_extra_line_chart('ADX (4h)', 'ADX', ta.adx(self.anchor), color='orange')
        self.add_horizontal_line_to_extra_chart('ADX (4h)', 'long min', self.hp['l_adx'], color='green', line_style='dotted')
        self.add_horizontal_line_to_extra_chart('ADX (4h)', 'short min', self.hp['s_adx'], color='red', line_style='dotted')

        # regime pane: +1 bull, 0 neutral, -1 bear
        self.add_extra_line_chart('Regime', 'regime', self.regime(), color='blue')
        self.add_horizontal_line_to_extra_chart('Regime', 'neutral', 0, color='gray', line_style='dotted')

        # session pane: 1 = gold session open (entries allowed), 0 = closed
        self.add_extra_line_chart('Session', 'gold session open', 1 if self.is_trading_hours else 0, color='green')

    def hyperparameters(self) -> list:
        return [
            {'name': 'st_period', 'type': int, 'min': 7, 'max': 40, 'default': 24},
            {'name': 'st_factor', 'type': float, 'min': 1.5, 'max': 5.0, 'step': 0.5, 'default': 4.0},
            {'name': 'ema4', 'type': int, 'min': 0, 'max': 100, 'step': 10, 'default': 10},
            {'name': 'don_period', 'type': int, 'min': 10, 'max': 100, 'step': 5, 'default': 85},
            {'name': 'atr_stop', 'type': float, 'min': 1.0, 'max': 5.0, 'step': 0.5, 'default': 3.0},
            {'name': 'trail_atr', 'type': float, 'min': 1.5, 'max': 8.0, 'step': 0.5, 'default': 6.5},
            {'name': 'exit_on_flip', 'type': int, 'min': 0, 'max': 1, 'default': 0},
            {'name': 'l_adx', 'type': int, 'min': 0, 'max': 40, 'default': 10},
            {'name': 's_adx', 'type': int, 'min': 0, 'max': 40, 'default': 15},
            {'name': 's_stop', 'type': float, 'min': 0.5, 'max': 4.0, 'step': 0.5, 'default': 4.0},
            {'name': 's_trail', 'type': float, 'min': 1.0, 'max': 6.0, 'step': 0.5, 'default': 3.5},
            {'name': 's_tp', 'type': float, 'min': 0.0, 'max': 6.0, 'step': 0.5, 'default': 5.0},
        ]