# Concrete Trading Rules and Market Effects: The Complete TurtleTrader (Michael W. Covel, 2007)

**Book**: *The Complete TurtleTrader: How 23 Novice Investors Became Overnight Millionaires*  
**Author**: Michael W. Covel  
**Publisher**: Collins / HarperBusiness, 2007 (ISBN: 978-0-06-124170-3)  
**Short Name**: `covel_turtletrader`  

---

### 1. Richard Donchian's Weekly Trading Rule (2-Week Channel Breakout)
- Where: Chapter 4: The Philosophy, pp. 52–53
- Quote: "In 1960, Donchian reduced this philosophy to what he called his 'weekly trading rule.' The rule was brutally utilitarian: 'When the price moves above the high of two previous calendar weeks (the optimum number of weeks varies by commodity), cover your short positions and buy. When the price breaks below the low of the two previous calendar weeks, liquidate your long position and sell short.'"
- Rule as written:
  - Entry: Buy long when price exceeds the highest high of the previous 2 calendar weeks. Sell short when price breaks below the lowest low of the previous 2 calendar weeks.
  - Exit: Pure stop-and-reverse (SAR). Liquidate short and buy long on a 2-week high; liquidate long and sell short on a 2-week low.
  - Sizing: Not stated.
  - Markets: Commodities and futures.
  - Bar size: Weekly / daily bars.
  - Holding time: Multi-week to multi-month trend holding period.
- Book's evidence: Reference to Richard Donchian's published trading rules from 1960 and decades of profitable trend trading track records; no specific backtest table provided in chapter 4.
- Mechanism (the book's): Pure price trend following based on mob psychology: "Everything known is reflected in the price... Abstractions like crop size, unemployment, and inflation are mere metaphysics to the trader... You don't get any profit from fundamental analysis. You get profit from buying and selling. So why stick with the appearance when you can go right to the reality of price?"
- Mechanism (my inference): None needed; book's mechanism is stated.
- Apex fit: No. Multi-week holding period held overnight; violates the mandatory Apex requirement to be flat by 15:59 CT daily.
- Already tested? No.

---

### 2. Mathematical Expectancy Model
- Where: Chapter 5: The Rules, pp. 68–70; Tables 5.1 & 5.2
- Quote: "The Turtle rules themselves had a positive expectation per trade because their winning trades were many multiples larger than their losing trades. Expectation (or edge, or expected value) is calculated with a straightforward formula: E = (PW X AW) - (PL X AL)... It's not about the frequency of how correct you are; it's about the magnitude of how correct you are."
- Rule as written:
  - Formula: $\text{Expectation} = (PW \times AW) - (PL \times AL)$, where $PW$ is winning percentage, $AW$ is average winning trade, $PL$ is losing percentage ($1 - PW$), and $AL$ is average losing trade.
  - Decision threshold: Only trade systems with positive expectancy where average winners are 3 to 4 times larger than average losers ($AW / AL \ge 3 \text{ to } 4$), allowing profitability even with win rates as low as 25%–35%.
  - Sizing: Bet sizing and trade selection must be grounded in mathematical edge rather than win rate.
  - Timeframe: Applicable across all bar sizes and instruments.
- Book's evidence: Historical performance tables from inception to August 2006 for major Turtle firms (Jerry Parker's Chesapeake Capital, Salem Abraham, Liz Cheval's EMC, Paul Rabar) showing monthly expectancy consistently outperforming buy-and-hold equity indexes (Tables 5.1 and 5.2).
- Mechanism (the book's): Casino house advantage: Dennis and Eckhardt taught the Turtles to operate like a casino house, absorbing frequent small losses (loss leaders) in exchange for massive positive-skew payouts on outlier trends.
- Mechanism (my inference): None needed; book's mechanism is explicit.
- Apex fit: Yes as an analytical framework and risk benchmark; but it is an evaluation formula, not an independent directional trading rule.
- Already tested? No.

---

### 3. System 1 (S1) 20-Day Donchian Breakout Entry
- Where: Chapter 5: The Rules, pp. 72–74; Chart 5.3
- Quote: "System One (S1) used a four-week price breakout for entry and a two-week price breakout in the opposite direction of the entry breakout for an exit. If a market made a new four-week high, the Turtles would buy. They would exit if/when it made a two-week low. A two-week low was a ten-day breakout—counting trading days only."
- Rule as written:
  - Long Entry: Buy 1 tick above the highest high of the previous 20 trading days (4 calendar weeks).
  - Short Entry: Sell short 1 tick below the lowest low of the previous 20 trading days.
  - Filter: Subject to the System 1 Last-Trade Winning Filter (Rule 4).
  - Protective Stop: Hard $2N$ stop loss placed at entry price $\mp 2N$ (Rule 10).
  - Sizing: 1 Unit based on $2\%$ account risk / $2N$ volatility (Rule 9).
  - Market: Diversified futures contracts (currencies, commodities, financials).
  - Bar size: Daily bars.
  - Holding time: Multi-week holding period (typically 30–60 days).
- Book's evidence: Illustrated with a September 1995 Japanese Yen trade (Chart 5.3) where a 4-week high breakout generated a major upward trend exiting on a 2-week low. Also referenced across individual Turtle track records 1984–1988 (Appendices III & IV).
- Mechanism (the book's): Trend following on structural capital imbalances. When prices breach multi-week highs or lows, market participants are forced to adjust hedges and commercial inventory, creating persistent directional momentum that overrides short-term noise.
- Mechanism (my inference): None needed; book's mechanism is stated.
- Apex fit: No. Held overnight for weeks; violates the mandatory Apex requirement to be flat by 15:59 CT daily.
- Already tested? No.

---

### 4. System 1 Last-Trade Winning Filter
- Where: Chapter 5: The Rules, pp. 72–73
- Quote: "The filter rule: The Turtles ignored the System One four-week breakout signal if the last four-week breakout signal was a winner. Even if they did not take the last four-week breakout signal, or even if it was just 'theoretically' a winning trade, the Turtles still didn't take the System One breakout. However, if the trade before a current four-week breakout was a 2N loss, they could take the breakout."
- Rule as written:
  - Condition: Check the outcome of the preceding 20-day (4-week) breakout signal in that specific market, whether actually traded or theoretical.
  - Action: If the preceding breakout trade was profitable (gain $> 0$), skip the current 20-day breakout signal (do not enter). If the preceding trade was a losing trade (specifically a $2N$ loss), take the breakout signal.
  - Symmetry: The direction of the previous trade does not matter (a prior short win filters out a new long breakout).
  - Failsafe override: If a skipped signal develops into a monster trend, enter via the System 2 55-day breakout (Rule 5).
  - Bar size: Daily bars.
- Book's evidence: Taught by Dennis and Eckhardt in the 1983–1984 Turtle classes; described as standard operating procedure for all Turtles trading S1.
- Mechanism (the book's): Filtering out whipsaws in range-bound markets. Winning trend breakouts are frequently followed by consolidations and false breakouts that chew up capital. By skipping breakouts immediately following a win, the system avoids predictable post-trend chop.
- Mechanism (my inference): None needed; book's mechanism is stated.
- Apex fit: No. Filter for a daily-bar swing breakout held overnight.
- Already tested? No.

---

### 5. System 2 (S2) 55-Day Donchian Breakout Entry (Failsafe Long-Term Entry)
- Where: Chapter 5: The Rules, p. 73
- Quote: "If the Turtles skipped a System One four-week breakout and the market kept trending, they could and would get back in at the System Two eleven-week breakout (see below). This fail-safe System Two breakout was how the Turtles kept from missing big trends that were filtered out. System Two was the Turtles' longer-term trading system. It used an eleven-week breakout (fifty-five days) for an entry signal and a four-week breakout (twenty days) in the opposite direction for an exit."
- Rule as written:
  - Long Entry: Buy 1 tick above the highest high of the previous 55 trading days (11 weeks).
  - Short Entry: Sell short 1 tick below the lowest low of the previous 55 trading days.
  - Filter: None. Take every 55-day breakout signal regardless of prior trade outcome.
  - Protective Stop: Hard $2N$ stop loss placed at entry price $\mp 2N$ (Rule 10).
  - Sizing: 1 Unit based on $2\%$ account risk / $2N$ volatility (Rule 9). Turtles typically allocated 50% of capital to S1 and 50% to S2.
  - Market: Diversified futures contracts.
  - Bar size: Daily bars.
  - Holding time: Multi-month holding period (typically 60–180 days).
- Book's evidence: Cited as the primary vehicle responsible for catching mega-trends (e.g. Liz Cheval's 1990 Crude Oil trade buying 350 contracts under $20 and exiting at $34.80 for multi-million dollar gains; Liz Cheval, Jerry Parker, and Paul Rabar performance tables in Appendix IV).
- Mechanism (the book's): Failsafe capture of secular macroeconomic trends. Breaking a 55-day extreme indicates an overwhelming structural imbalance (macro regime shift, supply crisis, monetary policy change) where institutional capital reallocations overpower all retail countertrend activity.
- Mechanism (my inference): None needed; book's mechanism is explicit.
- Apex fit: No. Held overnight for months; violates the mandatory Apex requirement to be flat by 15:59 CT daily.
- Already tested? No.

---

### 6. System 1 10-Day Trailing Breakout Liquidation Exit
- Where: Chapter 5: The Rules, pp. 72, 94; Chart 5.3
- Quote: "They would exit if/when it made a two-week low. A two-week low was a ten-day breakout—counting trading days only... The Turtles were instructed to take whichever stop hit first: The 2N stop or the S1 or S2 breakout exits."
- Rule as written:
  - Long exit: Liquidate long position immediately if price touches the lowest low of the previous 10 trading days (2 calendar weeks).
  - Short exit: Liquidate short position immediately if price touches the highest high of the previous 10 trading days.
  - Priority: Whichever occurs first between the 10-day trailing exit and the $2N$ stop loss.
  - Execution: Stop order placed at the 10-day price extreme.
  - Bar size: Daily bars.
- Book's evidence: Illustrated in the Japanese Yen trade (Chart 5.3) where exit occurred on a 2-week opposite low after a multi-month advance.
- Mechanism (the book's): Trend exhaustion and reversal. A 10-day counter-trend move signals that the immediate trend impulse has spent its momentum, allowing the trader to lock in the bulk of the move while accepting a mandatory giveback from the absolute high.
- Mechanism (my inference): None needed; book's mechanism is explicit.
- Apex fit: No. Multi-day trailing exit designed for overnight swing positions.
- Already tested? No.

---

### 7. System 2 20-Day Trailing Breakout Liquidation Exit
- Where: Chapter 5: The Rules, pp. 73, 94; Chart 5.4
- Quote: "System Two was the Turtles' longer-term trading system. It used an eleven-week breakout (fifty-five days) for an entry signal and a four-week breakout (twenty days) in the opposite direction for an exit... Turtles always exited after the market went against them, thus having to endure the painful experience of giving back profits. You can't pick the bottom and you can't pick the top, so trying to end up with the 'middle' of a trend was the goal."
- Rule as written:
  - Long exit: Liquidate long position immediately if price touches the lowest low of the previous 20 trading days (4 calendar weeks).
  - Short exit: Liquidate short position immediately if price touches the highest high of the previous 20 trading days.
  - Priority: Whichever occurs first between the 20-day trailing exit and the $2N$ stop loss.
  - Bar size: Daily bars.
- Book's evidence: Natural Gas example (Chart 5.4) and Liz Cheval's Crude Oil trade (pp. 77–78) holding from under $20 to above $40 and liquidating between $38 and $30 (average $34.80).
- Mechanism (the book's): Wide trailing stop to endure intermediate corrections. Giving trends room to breathe avoids premature shakeouts during normal retracements within a multi-month secular bull or bear campaign.
- Mechanism (my inference): None needed; book's mechanism is explicit.
- Apex fit: No. Multi-week trailing exit for overnight swing positions.
- Already tested? No.

---

### 8. Average True Range Volatility Metric ($N$ / ATR Calculation)
- Where: Chapter 5: The Rules, pp. 80–81; Table 5.6; Chart 5.7
- Quote: "Turtle risk management starts with the measurement of daily market volatility. The Turtles were taught to measure volatility in terms of 'daily ranges.' It was nicknamed 'N' (also known as the Average True Range, or ATR). They were taught to take the maximum of the following for any market to derive 'N': The distance from today's high to today's low; The distance from yesterday's close to today's high; The distance from yesterday's close to today's low... The Turtles then took a twenty-day moving average of true ranges."
- Rule as written:
  - True Range (TR) formula:
    $$TR = \max(High - Low, |High - Close_{-1}|, |Low - Close_{-1}|)$$
  - Volatility metric $N$: 20-day moving average of True Range. (Note: Tip #7 also notes a 15-day simple moving average as a practical retail alternative: $\sum_{i=1}^{15} TR_i / 15$).
  - Update frequency: Calculated daily on closed daily bars. Eckhardt noted that only 2–3 times per year did he make an intraday volatility adjustment.
- Book's evidence: Table 5.6 calculating Kansas City Wheat Futures ATR step-by-step; Chart 5.7 plotting ATR on Dell daily bars.
- Mechanism (the book's): Volatility normalization. Market volatility varies across commodities and time. By expressing price distance in multiples of $N$ rather than points or percentages, every market is mapped to an identical statistical scale.
- Mechanism (my inference): None needed; book's mechanism is explicit.
- Apex fit: Yes as a volatility measurement indicator on intraday or daily bars; not a standalone directional trading rule.
- Already tested? No.

---

### 9. Volatility-Adjusted Unit Position Sizing ($1\%$ to $2\%$ Account Risk)
- Where: Chapter 5: The Rules, pp. 81–84, 86–87; Table 5.8
- Quote: "The unit fluctuated so that every day the Turtles knew how many contracts to have on based on how much money they had in their trading account at that instant... Take your account (whatever size it is) and multiply by 2 percent... The number of contracts to buy or sell is determined by taking the 2 percent account risk and dividing it by the contract risk... The rules made a corn unit equal to a gold unit equal to a Coca-Cola unit."
- Rule as written:
  - Account Risk = Account Equity $\times$ Risk Fraction (Turtles used $2\%$; Covel notes conservative traders can use $1\%$ to $1.5\%$).
  - Contract Dollar Risk = $2N \times \text{Dollar Point Value}$ (or $1N \times \text{Dollar Point Value}$ if risking 1% on 1N).
  - Position Size (1 Unit) = $\lfloor \text{Account Risk} / \text{Contract Dollar Risk} \rfloor$ (rounded down to nearest whole contract).
  - Equalization: 1 Unit in Gold risks the exact same dollar amount as 1 Unit in Corn, S&P 500, or Swiss Francs.
- Book's evidence: Illustrated with Corn futures ($N = 7\text{ cents}$, point value $50\text{ cents}$, contract risk $2N = \$700$; on a $\$100,000$ account risking $2\% = \$2,000$, contracts to trade = $\lfloor 2000 / 700 \rfloor = 2$ contracts) (Table 5.8) and Swiss Francs (p. 86).
- Mechanism (the book's): Risk parity and equal conviction. Without volatility weighting, high-volatility commodities dominate portfolio variance while low-volatility assets have negligible impact. Equal dollar-volatility risk ensures that any trending market can generate meaningful profits without catastrophic single-market exposure.
- Mechanism (my inference): None needed; book's mechanism is explicit.
- Apex fit: Yes in principle (can be applied to size MNQ / MES / MCL contracts to risk e.g. $100–$200 per trade within Apex limits); but it is a sizing formula, not a directional trading setup.
- Already tested? No.

---

### 10. Primary Hard $2N$ Stop Loss Rule
- Where: Chapter 5: The Rules, pp. 84–85, 94; Tip #9
- Quote: "The Turtles used a 2N stop. This simply means that their primary stop, or hard stop, was two times the daily 'N.' For example, if there was a breakout in corn, and assuming a closing price of $250, Turtles quickly determined their 'N' stop. If the 'N' was 7 cents, a 2N stop would have been 14 cents... An entry at $250 would have a hard stop at $236 (250 - 14). You would exit if the stop at price level $236 was 'touched.' No second-guessing. No overthinking. Follow the rules."
- Rule as written:
  - Long Stop Price: $\text{Entry Price} - 2N$.
  - Short Stop Price: $\text{Entry Price} + 2N$.
  - Trigger: Stop order touched in real-time; immediate liquidation at market.
  - Adjustment: Placed at $2N$ from the initial entry; when pyramiding additional units, stops on all open units are raised/lowered to $2N$ behind the most recently executed unit (Rule 12).
- Book's evidence: Corn and Google examples (Tip #9: Google ATR = 20, 2ATR stop = 40 points); Liz Cheval risk management protocols.
- Mechanism (the book's): Capital protection against false breakouts. Normal market noise rarely exceeds $2N$ without a change in trend. Exiting at $2N$ cuts losses while the trade thesis is still invalid, preserving 98% of equity to trade future breakouts.
- Mechanism (my inference): None needed; book's mechanism is explicit.
- Apex fit: No for daily futures contracts ($2N$ on daily NQ is ~$600–$1,000 points = $12,000–$20,000, blowing Apex's $2,000 trailing drawdown instantly); concept can scale to intraday micros, but daily stop holds overnight.
- Already tested? No.

---

### 11. Alternative Initial $1/2 N$ Stop Loss Rule
- Where: Chapter 5: The Rules, p. 87
- Quote: "Turtles could pyramid a maximum of 5 units. They set their stops at 1/2N on the first day of trading and from that point forward, 2N stops were used. Then, once the second unit was bought, both stops were brought up to the new unit's 2N stop."
- Rule as written:
  - Setup: On the initial entry day (day 1 of the breakout), set the initial stop loss at $1/2 N$ (0.5 N) from the entry price.
  - Progression: If price does not get stopped out on day 1, expand the stop to the standard $2N$ stop from that point forward.
  - Pyramiding integration: When the second unit is purchased, bring the stops on both units up to $2N$ behind the second unit's entry price.
  - Bar size: Daily bars.
- Book's evidence: Described in the mechanics of pyramiding on p. 87.
- Mechanism (the book's): Minimizing immediate breakout failure costs. Many false breakouts fail immediately within the first trading day. Cutting losses aggressively at $1/2 N$ on day 1 reduces the initial dollar hit of whipsaws by 75% compared to a $2N$ stop.
- Mechanism (my inference): None needed; book's mechanism is stated.
- Apex fit: No. Daily bar stop strategy holding overnight.
- Already tested? No.

---

### 12. Pyramiding / Adding Units on Favorable $1N$ Price Moves
- Where: Chapter 5: The Rules, pp. 87–92; Tables 5.10–5.15
- Quote: "Once they understood S1 and S2 entry and exit rules, once they understood 'N' and units, Eckhardt then instructed the Turtles to pile profits back into winning trades. This maxing out of their big winners was part of what helped to create the Turtles' fantastic positive expectancy, or 'edge.'... Assume a long breakout entry at 100 with an 'N' value of 5. Assume that you will add another unit each 1N move. A new unit will be added at 105, 110, etc. Turtles could pyramid a maximum of 5 units."
- Rule as written:
  - Base Entry: Unit 1 entered at initial breakout price $P_0$.
  - Addition Trigger: Add 1 additional unit every time the market moves $1N$ in favor from the previous entry price ($P_k = P_{k-1} + 1N$ for longs, $P_k = P_{k-1} - 1N$ for shorts).
  - Maximum Units: Maximum of 4 to 5 units permitted per market.
  - Stop Trailing: Whenever an additional unit is added, all open units have their stops updated to $2N$ below the latest unit's purchase price ($P_k - 2N$).
  - Breakeven dynamics: With each $1N$ advance, the stop moves up by $1N$, effectively locking in open gains or moving the aggregate position stop to breakeven.
- Book's evidence: Comprehensive step-by-step Live Cattle trade example (Tables 5.10 to 5.15), purchasing 5 consecutive units from 74.00 to 77.00 as equity grew from $50,000 to $52,920, and finally liquidating at 84.50 for massive gains.
- Mechanism (the book's): Capitalizing on positive skew and geometric compounding. Compounding into strong trending moves magnifies returns on the few outlier trades that generate 80%+ of total system profits, while the trailing stop ensures aggregate risk remains strictly capped.
- Mechanism (my inference): None needed; book's mechanism is explicit.
- Apex fit: No for daily swing trades held overnight. Intraday pyramiding on micros is theoretically possible, but typical intraday range on NQ/MNQ rarely permits multiple $1N$ additions prior to 15:59 CT close.
- Already tested? No.

---

### 13. Portfolio Unit Limits and Market Correlation Caps
- Where: Chapter 5: The Rules, pp. 86, 95–96; Table 5.17
- Quote: "The Turtles had unit guidelines to keep them from overtrading. For example, they were limited to four to five units for any one market traded... However, it was critical to avoid having one of highly correlated markets. In simple terms, think of correlated markets typically moving together in lockstep. Too many potentially correlated markets in a portfolio and the Turtles increased their unit risk."
- Rule as written:
  - Single Market Limit: Maximum 4 to 5 units in any individual market.
  - Correlated Sector Limit: Strictly cap exposure across highly correlated markets (e.g. Corn and Soybeans, Gold and Silver, 10-Year Notes and 30-Year Bonds, Dow Jones and S&P 500).
  - Diversification Mandate: Maintain non-correlated exposure across diverse asset classes (energies, grains, currencies, meats, financials) (Table 5.17).
- Book's evidence: Table 5.16 (list of markets traded by Turtles) and Table 5.17 ("More Risk" vs. "Less Risk" portfolio comparison).
- Mechanism (the book's): Portfolio heat control and cross-asset de-correlation. Holding multiple units in correlated assets creates synthetic leverage that multiplies drawdowns during macroeconomic shocks. Capping correlated units isolates individual sector shocks.
- Mechanism (my inference): None needed; book's mechanism is explicit.
- Apex fit: Yes as a risk management principle across trading accounts/instruments; not an independent directional trading setup.
- Already tested? No.

---

### 14. Long/Short Portfolio Risk Netting Rule
- Where: Chapter 5: The Rules, pp. 96–97; Table 5.18
- Quote: "The Turtles were also taught that combining long and short units into their portfolio offered further diversification. In fact, when they combined long and short units, Dennis and Eckhardt discovered that they could actually trade more overall units... To calculate the total Turtle unit risk, you would take the smaller number and divide it by two. Then you would subtract that number from the larger number. In this example it would be 4 - (3/2), giving 2.5 units of risk."
- Rule as written:
  - Formula:
    $$\text{Net Unit Risk} = \text{Units}_{\text{dominant side}} - \frac{\text{Units}_{\text{minority side}}}{2}$$
  - Calculation: If a portfolio holds $L$ long units and $S$ short units across diverse markets, take $\max(L, S) - (\min(L, S) / 2)$.
  - Portfolio Capacity: By running both long and short positions simultaneously, the portfolio's effective net risk is discounted, allowing traders to hold more total units while keeping net equity variance constrained.
- Book's evidence: Example of 4 long units (Corn, Feeder Cattle, Gold, Swiss Francs) and 3 short units (British Pounds, Copper, Sugar) resulting in $4 - 1.5 = 2.5$ units of risk (p. 97; Table 5.18).
- Mechanism (the book's): Statistical hedge benefit. Macro shocks typically drive broad market correlations toward extremes (risk-on vs. risk-off). Holding opposing long and short positions across disparate commodities naturally dampens aggregate portfolio equity volatility.
- Mechanism (my inference): None needed; book's mechanism is stated.
- Apex fit: No. Applicable to multi-market commodity portfolios held overnight; Apex accounts trade a single instrument (e.g. MNQ) intraday.
- Already tested? No.

---

### 15. Account Drawdown Capital Reduction Rule (Risk of Ruin Prevention)
- Where: Chapter 5: The Rules, pp. 92–94
- Quote: "How did Eckhardt teach the Turtles to handle losing streaks and protect capital? They cut back their unit sizes dramatically. When markets turned around, this preventive behavior of reducing units increased the likelihood of a quick recovery... The rules were simple. For every 10 percent in drawdown in their account, Turtles cut their trading unit risk by 20 percent. For example, if they were trading a 2 percent unit and if an 11 percent drawdown happened, they would cut their trading size from 2 percent to 1.6 percent (2.0 x 80%). If their trading capital dropped down 22 percent, then they would cut their trading size by another 20 percent (1.6 x 80%), making each unit 1.28 percent."
- Rule as written:
  - Trigger: Cumulative drawdown in total account equity reaches 10% thresholds (10%, 20%, 30%, etc.).
  - Action: Immediately reduce the unit risk fraction by 20% compounding for each 10% increment of drawdown:
    $$\text{Unit Risk}_{\text{new}} = \text{Unit Risk}_{\text{base}} \times (0.80)^k \quad \text{where } k = \lfloor \text{Drawdown \%} / 10\% \rfloor$$
  - Sizing Recovery: Only increase unit sizes back toward the baseline after account equity rises above previous recovery watermark thresholds.
- Book's evidence: Historical performance of Turtles in 1984–1988 (Appendices III & IV) surviving prolonged 30%–40% drawdowns and rebounding to +100%–150% annual returns when trends materialized; Erle Keefer testimony.
- Mechanism (the book's): Halting geometric ruin. Drawdowns progress arithmetically or geometrically during choppy market regimes. Compounding position size reductions during drawdowns prevents capital exhaustion during adverse market regimes, ensuring the trader retains sufficient capital to exploit future trends.
- Mechanism (my inference): None needed; book's mechanism is explicit.
- Apex fit: Yes! This is directly compatible with and strongly reinforces the brief's own cushion rule for Apex 50K accounts ($2,000 trailing drawdown limit: "full size only with $1,500+ above the trailing drawdown, half size below"). It is a risk management framework, not a directional entry setup.
- Already tested? No.

---

## Ranked Shortlist (Apex-Compatible Candidates)

### Qualifying Candidates: 0 directional trade setups qualify.

Under the strict requirements of `tasks/TASK_BOOK_READING.md` and `tasks/ANTIGRAVITY_BRIEF.md` (mandatory flat by 15:59 CT daily, $2,000 trailing drawdown limit, traded on NQ/MNQ, and a stated market mechanism):

1. **Structural Disqualification of Turtle Directional Entries (Rules 1, 3, 4, 5, 6, 7)**:
   - The entire Turtle trading engine is an unoptimized, daily-bar, multi-week and multi-month trend-following system designed to capture large macroeconomic trends across 30+ physical commodities, currencies, and financials.
   - S1 (20-day breakout) and S2 (55-day breakout) hold positions for an average of 30 to 120 trading days. Liquidating positions daily by 15:59 CT destroys the positive-skew payoff distribution (where a small number of massive 100-day trends pay for frequent whipsaw losses).
   - In addition, a daily-bar $2N$ stop on full-sized futures contracts (e.g. NQ, ES, CL, GC) represents thousands of dollars per contract (e.g. $2N$ on daily NQ is ~$600–$1,000 points = $12,000–$20,000), which instantly violates Apex's $2,000 trailing drawdown.

2. **Institutional Risk Architecture Value for Apex Accounts**:
   While no directional entry qualifies as an intraday day-trading rule, the book's **risk management and position sizing architecture** provides foundational principles directly applicable to managing Apex evaluation and funded accounts:
   - **Volatility-Adjusted Unit Position Sizing (Rule 9)**: Normalizing position size by dollar volatility ($1\% / (N \times \text{Dollar Point Value})$) scales micro contracts (MNQ/MES) to exact dollar risk tolerances (e.g. risking $150 per trade).
   - **Account Drawdown Capital Reduction Rule (Rule 15)**: Cutting unit risk by 20% for every incremental drawdown directly mirrors and mathematically formalizes the brief's funded account cushion rule ("full size only with $1,500+ above trailing drawdown, half size below"), preventing account liquidation during adverse execution runs.
   - **Stop Trailing on Pyramids (Rule 12)**: Locking in open profits and moving aggregate position stops to breakeven as units are added preserves trailing equity thresholds.
