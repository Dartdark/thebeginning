# Testable Trading Ideas: Systematic Trading (Robert Carver, 2015)

Book: Robert Carver, *Systematic Trading: A unique new method for designing trading and investing systems* (Harriman House, 2015, ISBN: 978-0-85719-445-9). Short name: `carver_systematic`.

---

### 1. The "A and B" Early Profit Taker System
- Where: Appendix B ("Trading Rules: The A and B system"), pp. 293–294 (EPUB: `OEBPS/Autopilot_ebook-30.xhtml`)
- Quote: "I use two simple trading rules in examples throughout the book – the early profit taker and the early loss taker. These are both variations of a more general rule: the 'A and B' system. For the profit taker I use $A = 5$ and $B = 20$... I don't recommend using the A and B system for actual trading, but I've included the specification here to satisfy the curious."
- Rule as written:
  - Setup: Measure daily price volatility $\sigma_{	ext{price}}$ in price points at the time of entry. Define 1 "deviation" = $1 \cdot \sigma_{	ext{price}}$. Set $A = 5$ deviations, $B = 20$ deviations.
  - Entry: Enter Long (+1 standard position size).
  - Profit Target (when long): If price rises by $> A = 5$ deviations from entry price, sell out and reverse position to Short (-1 standard position size).
  - Trailing Stop Loss (when long): If price falls by $> B = 20$ deviations from the highest high reached since entry, sell out and reverse to Short (-1 standard position size).
  - Mirror rules for Short: Profit target triggers when price falls by $> A = 5$ deviations from entry; trailing stop triggers when price rises by $> B = 20$ deviations from lowest low.
  - Sizing: Standard position size = $\$100,000 / 	ext{Instrument Value Volatility}$ in dollars.
  - Market: Futures, cash equities.
  - Bar size: Daily.
  - Holding time: Days to weeks.
- Book's evidence: Used as a pedagogical benchmark throughout the book; Carver explicitly notes that because $A < B$, the system takes frequent small profits but suffers rare catastrophic losses during large trends, resulting in negative skew. Carver advises against trading it live.
- Mechanism (the book's): Exploits rangebound mean-reverting price action in sideways markets at the expense of severe tail risk.
- Mechanism (my inference): none needed.
- Apex fit: no. Carver explicitly warns against trading it; trailing stop of 20 daily standard deviations violates Apex $2,000 drawdown limits; continuous overnight holding.
- Already tested? no.

---

### 2. The "A and B" Early Loss Taker System
- Where: Appendix B ("Trading Rules: The A and B system"), pp. 293–294 (EPUB: `OEBPS/Autopilot_ebook-30.xhtml`)
- Quote: "The loss taker has these values reversed, $A = 20$ and $B = 5$... If $A$ is larger than $B$, the system will tend to hit stop losses more frequently, but when trends occur it will exploit them. This is the case for the early loss taker."
- Rule as written:
  - Setup: Calculate daily price volatility $\sigma_{	ext{price}}$. Set profit target $A = 20$ deviations, trailing stop $B = 5$ deviations.
  - Entry: Enter Long (+1 standard position size).
  - Trailing Stop Loss (when long): If price drops by $> B = 5$ deviations from peak high, sell out and reverse to Short.
  - Profit Target (when long): If price rises by $> A = 20$ deviations from entry, sell out and reverse to Short.
  - Sizing: Standard position size scaled to volatility target.
  - Market: Futures, equities.
  - Bar size: Daily.
  - Holding time: Weeks to months.
- Book's evidence: Illustrative benchmark; exhibits positive skew (frequent small losses, rare large trend payouts), but Carver notes continuous flipping creates excessive turnover.
- Mechanism (the book's): Trend following capture: cutting losses quickly while allowing fat-tail directional moves to run.
- Mechanism (my inference): none needed.
- Apex fit: no. 5 daily standard deviations stop loss on daily bars exceeds Apex $2,000 drawdown; holds overnight.
- Already tested? no.

---

### 3. Fast EWMAC (2:8) Trend Following Rule
- Where: Chapter 7, Section 7.4 & Appendix B, pp. 115–119, 294–297 (EPUB: `OEBPS/Autopilot_ebook-16.xhtml`, `OEBPS/Autopilot_ebook-30.xhtml`)
- Quote: "The forecast is the difference, or crossover, between two exponentially weighted moving averages (EWMA) of the price, one fast and one slow. The difference is then standardised by the recent standard deviation of prices, and a forecast scalar applied to ensure we get an average absolute value of 10 for our forecasts... For EWMAC (2, 8), the forecast scalar is 10.6."
- Rule as written:
  - Setup: Fast EWMA lookback $L_{	ext{fast}} = 2$ days ($lpha_{	ext{fast}} = 2 / (2 + 1) = 0.667$); Slow EWMA lookback $L_{	ext{slow}} = 8$ days ($lpha_{	ext{slow}} = 2 / (8 + 1) = 0.222$).
  - Raw Crossover: $E_{	ext{fast}, t} - E_{	ext{slow}, t}$.
  - Volatility Standardization: Divide raw crossover by daily price volatility $\sigma_{	ext{price}, t}$ (in price points).
  - Scaling: Multiply by Forecast Scalar $S = 10.6$.
  - Capping: Cap final forecast between $-20$ and $+20$.
  - Position: Target position $q_t = 	ext{Volatility Scalar} 	imes (	ext{Forecast}_t / 10)$.
  - Market: Futures (Crude Oil, Eurodollars, Bund, S&P 500).
  - Bar size: Daily.
  - Holding time: 2 to 10 days.
- Book's evidence: Tested across diversified futures portfolio; achieves positive Sharpe ratio (~0.25 to 0.40 standalone), but high turnover leads to significant transaction cost drag on smaller accounts.
- Mechanism (the book's): Captures rapid short-term momentum driven by institutional order flow execution and news underreaction.
- Mechanism (my inference): none needed.
- Apex fit: no. Moving-average crossovers are explicitly on the brief's "Already tested and failed" list. Daily bars violate Apex flat-by-15:59 CT cutoff.
- Already tested? Matches "Moving-average crosses: EMA 8/21, SMA 20/50... Every combination whipsaws in chop" on the failed list.

---

### 4. Medium-Fast EWMAC (4:16) Trend Following Rule
- Where: Chapter 7 & Appendix B, pp. 294–297 (EPUB: `OEBPS/Autopilot_ebook-30.xhtml`)
- Quote: "To pick up trends over different time periods you're going to want EWMAC variations which work over different horizons... For EWMAC (4, 16), the forecast scalar is 7.5."
- Rule as written:
  - Setup: $L_{	ext{fast}} = 4$ days, $L_{	ext{slow}} = 16$ days. Decay $lpha_{	ext{fast}} = 2/5 = 0.40$, $lpha_{	ext{slow}} = 2/17 = 0.1176$.
  - Raw Crossover: $E_4 - E_{16}$.
  - Volatility Standardization: Divide by daily price volatility $\sigma_{	ext{price}}$.
  - Scaling: Multiply by Forecast Scalar $S = 7.5$; cap at $\pm 20$.
  - Position: Continuous allocation scaled by volatility target.
  - Market: Global futures universe.
  - Bar size: Daily.
  - Holding time: 1 to 4 weeks.
- Book's evidence: Tested on futures; correlation with adjacent 2:8 rule is ~0.90; standard standalone CTA component.
- Mechanism (the book's): Exploits medium-speed institutional momentum and delayed information diffusion.
- Mechanism (my inference): none needed.
- Apex fit: no. Moving-average crossover; on the brief's failed list.
- Already tested? Matches "Moving-average crosses" on failed list.

---

### 5. Medium EWMAC (8:32) Trend Following Rule
- Where: Chapter 7 & Appendix B, pp. 294–297 (EPUB: `OEBPS/Autopilot_ebook-30.xhtml`)
- Quote: "Different look-back pairs will capture different length trends... For EWMAC (8, 32), the forecast scalar is 5.3."
- Rule as written:
  - Setup: $L_{	ext{fast}} = 8$ days, $L_{	ext{slow}} = 32$ days.
  - Raw Crossover: $E_8 - E_{32}$.
  - Volatility Standardization: Divide by $\sigma_{	ext{price}}$.
  - Scaling: Multiply by Forecast Scalar $S = 5.3$; cap at $\pm 20$.
  - Market: Global futures.
  - Bar size: Daily.
  - Holding time: 1 to 2 months.
- Book's evidence: Forms the core medium-speed trend-following engine for institutional CTAs; historical standalone Sharpe ratio ~0.35–0.40 before costs.
- Mechanism (the book's): Institutional capital flows and business-cycle trend momentum.
- Mechanism (my inference): none needed.
- Apex fit: no. Moving-average cross on daily bars; on the brief's failed list.
- Already tested? Matches "Moving-average crosses" on failed list.

---

### 6. Medium-Slow EWMAC (16:64) Trend Following Rule
- Where: Chapter 7 & Appendix B, pp. 294–297 (EPUB: `OEBPS/Autopilot_ebook-30.xhtml`)
- Quote: "For EWMAC (16, 64), the forecast scalar is 3.75."
- Rule as written:
  - Setup: $L_{	ext{fast}} = 16$ days, $L_{	ext{slow}} = 64$ days.
  - Raw Crossover: $E_{16} - E_{64}$.
  - Volatility Standardization: Divide by $\sigma_{	ext{price}}$.
  - Scaling: Multiply by Forecast Scalar $S = 3.75$; cap at $\pm 20$.
  - Market: Global futures.
  - Bar size: Daily.
  - Holding time: 2 to 4 months.
- Book's evidence: Low turnover (approx. 4–6 round trips/year); highly cost-effective for large capital pools.
- Mechanism (the book's): Captures macroeconomic trends driven by central bank interest rate cycles and commodity supply/demand imbalances.
- Mechanism (my inference): none needed.
- Apex fit: no. Multi-month holding period; moving-average cross on failed list.
- Already tested? Matches "Moving-average crosses" on failed list.

---

### 7. Slow EWMAC (32:128) Trend Following Rule
- Where: Chapter 7 & Appendix B, pp. 294–297 (EPUB: `OEBPS/Autopilot_ebook-30.xhtml`)
- Quote: "For EWMAC (32, 128), the forecast scalar is 2.65."
- Rule as written:
  - Setup: $L_{	ext{fast}} = 32$ days, $L_{	ext{slow}} = 128$ days.
  - Raw Crossover: $E_{32} - E_{128}$.
  - Volatility Standardization: Divide by $\sigma_{	ext{price}}$.
  - Scaling: Multiply by Forecast Scalar $S = 2.65$; cap at $\pm 20$.
  - Market: Global futures.
  - Bar size: Daily.
  - Holding time: 4 to 8 months.
- Book's evidence: Tested on futures; correlation with 16:64 is ~0.90; captures multi-quarter macro trends.
- Mechanism (the book's): Persistent capital misallocations and multi-quarter monetary policy regimes.
- Mechanism (my inference): none needed.
- Apex fit: no. Moving-average cross; multi-month hold violates Apex flat cutoff.
- Already tested? Matches "Moving-average crosses" on failed list.

---

### 8. Ultra-Slow EWMAC (64:256) Trend Following Rule
- Where: Chapter 7 & Appendix B, pp. 294–297 (EPUB: `OEBPS/Autopilot_ebook-30.xhtml`)
- Quote: "Beyond the pair 64:256 the holding period gets excessively long, and as the law of active management suggests performance will be poor, it isn't worth adding any more pairs beyond this... For EWMAC (64, 256), the forecast scalar is 1.87."
- Rule as written:
  - Setup: $L_{	ext{fast}} = 64$ days, $L_{	ext{slow}} = 256$ days (equivalent to classic 50/200 day moving average).
  - Raw Crossover: $E_{64} - E_{256}$.
  - Volatility Standardization: Divide by $\sigma_{	ext{price}}$.
  - Scaling: Multiply by Forecast Scalar $S = 1.87$; cap at $\pm 20$.
  - Market: Global futures.
  - Bar size: Daily.
  - Holding time: 6 to 18 months.
- Book's evidence: Equivalent to traditional long-term institutional trend following; minimal turnover (~2 round trips/year).
- Mechanism (the book's): Secular macro multi-year commodity and interest rate cycles.
- Mechanism (my inference): none needed.
- Apex fit: no. Moving-average cross on failed list; multi-year holding period.
- Already tested? Matches "Moving-average crosses" on failed list.

---

### 9. Futures Term Structure Carry Trading Rule
- Where: Chapter 7, Section 7.4 & Appendix B, pp. 119–120, 297–300 (EPUB: `OEBPS/Autopilot_ebook-16.xhtml`, `OEBPS/Autopilot_ebook-30.xhtml`)
- Quote: "Carry, which is sometimes called roll down or contango, is the return that you will get if asset prices don't change... The raw carry is the net expected return in price units divided by the annualised standard deviation of returns... The forecast scalar is 30."
- Rule as written:
  - Setup: Measure the price differential between the contract being traded ($P_{	ext{current}}$) and the next closest contract ($P_{	ext{next}}$). Calculate distance between expiries in years ($D$).
  - Net Expected Return: $	ext{Annualized Return} = (P_{	ext{current}} - P_{	ext{next}}) / D$.
  - Standard Deviation: Calculate annual price volatility $\sigma_{	ext{annual}} = 16 	imes \sigma_{	ext{daily, price}}$.
  - Raw Carry: $	ext{Raw Carry} = 	ext{Annualized Return} / \sigma_{	ext{annual}}$.
  - Forecast: $	ext{Forecast} = 30 	imes 	ext{Raw Carry}$, capped between $-20$ and $+20$.
  - Position: Target position scaled to cash volatility target. Re-check weekly.
  - Market: Futures term structures (Eurodollars, Crude Oil, Bonds, Agricultural commodities).
  - Bar size: Weekly / daily.
  - Holding time: Weeks to months (approx. 10 round trips per year).
- Book's evidence: Backtested across multi-asset futures; standalone Sharpe ratio ~0.40. Carver demonstrates that combining Carry with EWMAC trend following creates a superior portfolio because Carry exhibits negative skew (steady roll return gains punctuated by sudden shocks) while Trend exhibits positive skew (absorbing market shocks).
- Mechanism (the book's): Commercial hedgers (e.g. oil producers or debt issuers) are willing to pay an insurance premium to lock in forward prices, offering a structural return (roll yield/basis) to speculators who absorb inventory risk.
- Mechanism (my inference): none needed.
- Apex fit: no. Carry roll yield requires holding futures contracts across weeks/months until contract convergence; cannot be harvested intraday (flat by 15:59 CT).
- Already tested? no.

---

### 10. Equity Dividend vs. Funding Cost Carry Rule
- Where: Appendix B, pp. 298–299 (EPUB: `OEBPS/Autopilot_ebook-30.xhtml`)
- Quote: "So if you buy shares in French supermarket Carrefour which currently has a dividend yield of 3%, and you pay 1% to borrow the purchase cost, you will make a net carry of 2% a year... Net expected return % = Dividend yield minus funding cost."
- Rule as written:
  - Setup: Compute expected annual dividend yield ($DY$). Measure annual margin borrowing cost ($FC$).
  - Net Return: $	ext{Net Return} = DY - FC$. Convert to price units: $	ext{Net Return} 	imes P_{	ext{current}}$.
  - Volatility Standardization: Divide by annual price volatility ($16 	imes \sigma_{	ext{daily}}$).
  - Forecast: Multiply by 30; cap at $\pm 20$.
  - Market: Cash equities / equity CFDs.
  - Bar size: Weekly.
  - Holding time: Months.
- Book's evidence: Empirical carry factor in global equity markets.
- Mechanism (the book's): Investors demand higher cash dividend yields to hold mature or levered corporate equities.
- Mechanism (my inference): none needed.
- Apex fit: no. Cash equities held across months; violates Apex futures rules.
- Already tested? no.

---

### 11. Foreign Exchange Interest Rate Differential Carry Rule
- Where: Appendix B, p. 299 (EPUB: `OEBPS/Autopilot_ebook-30.xhtml`)
- Quote: "Foreign exchange, cash: Interest % = The interest you get in the foreign currency. Funding cost % = The interest you pay to borrow the domestic currency. Net expected return % = Interest minus funding cost... Forecast scalar is 30."
- Rule as written:
  - Setup: Identify foreign deposit interest rate $i_{	ext{foreign}}$ and domestic borrowing rate $i_{	ext{domestic}}$.
  - Net Expected Return: $(i_{	ext{foreign}} - i_{	ext{domestic}}) 	imes 	ext{Spot Price}$.
  - Volatility Standardization: Divide by annual spot FX price volatility.
  - Forecast: $	ext{Forecast} = 30 	imes 	ext{Raw Carry}$, capped at $\pm 20$.
  - Market: Cash FX / FX forwards.
  - Bar size: Weekly.
  - Holding time: Months.
- Book's evidence: Classic G10 currency carry trade.
- Mechanism (the book's): Uncovered interest rate parity failure: carry traders earn a liquidity and crash-risk premium for financing foreign capital flows.
- Mechanism (my inference): none needed.
- Apex fit: no. Spot currency holding across months; violates Apex intraday futures rules.
- Already tested? no.

---

### 12. "Close to Open" Overnight Drift Rule
- Where: Chapter 7, Section 7.5 ("Adapting and creating trading rules"), pp. 120–121 (EPUB: `OEBPS/Autopilot_ebook-16.xhtml`)
- Quote: "I converted the simple rule above to calculate the raw forecast as [Open price - Close price]... Not market specific; volatility standardised: [Open price - Close price] / (Recent standard deviation of daily returns)... The natural average absolute value of this rule is 0.33, implying the forecast scalar in this case is 10 / 0.33 = 30."
- Rule as written:
  - Setup: At the daily open, compute raw overnight gap: $\Delta P = P_{	ext{open}} - P_{	ext{close, prior}}$.
  - Volatility Standardization: Divide $\Delta P$ by recent standard deviation of daily returns $\sigma_{	ext{daily, price}}$.
  - Scaling: Multiply by Forecast Scalar $S = 30$; cap at $\pm 20$.
  - Entry: Long if forecast $> 0$; Short if forecast $< 0$.
  - Exit: Re-evaluate on next bar.
  - Market: Equities, futures.
  - Bar size: Daily.
  - Holding time: 1 day.
- Book's evidence: Presented as a methodological teaching example of how to convert an arbitrary discrete rule into a continuous volatility-standardized forecast; Carver explicitly notes: "I haven't tested this rule and I have no idea if it will work or not."
- Mechanism (the book's): none given.
- Mechanism (my inference): Overnight inventory gap fading.
- Apex fit: no. Untested illustrative example; lacks stop loss; on NQ/ES, gap fading matches failed mean reversion.
- Already tested? On NQ/ES, matches "Mean reversion on NQ / ES" on failed list.

---

### 13. Semi-Automatic Discretionary Forecast with Volatility Trailing Stop
- Where: Chapter 7, Section 7.3 & Chapter 13, pp. 112–114, 219–224 (EPUB: `OEBPS/Autopilot_ebook-16.xhtml`, `OEBPS/Autopilot_ebook-23.xhtml`)
- Quote: "Semi-automatic traders: Make your own predictions and convert them into forecasts between -20 (strongly bearish) and +20 (strongly bullish)... Positions are closed using systematic stop loss rule... If the price falls by more than $B$ deviations from its peak since entry, then close the position."
- Rule as written:
  - Setup: Trader assigns a discretionary directional conviction score from $-20$ to $+20$. Position is sized systematically via the Carver Volatility Scalar ($q = 	ext{Scalar} 	imes 	ext{Forecast} / 10$).
  - Trailing Stop Loss: Set at $B = 3$ to $5$ daily price standard deviations from the most favorable price reached since inception.
  - Exit: Stop loss triggers immediate exit; or discretionary forecast update reduces position.
  - Market: Any liquid instrument (futures, shares).
  - Bar size: Daily.
  - Holding time: Discretionary (days to months).
- Book's evidence: Framework designed for discretionary investors wanting systematic position sizing and risk control.
- Mechanism (the book's): Behavioral discipline: preventing disposition bias (cutting losses systematically while allowing winners to run).
- Mechanism (my inference): none needed.
- Apex fit: no. Relies on subjective discretionary forecasting; daily trailing stop of 3–5 $\sigma$ exceeds Apex trailing drawdown.
- Already tested? no.

---

### 14. The Asset Allocating Investor's "No-Rule" Rule
- Where: Chapter 7, Section 7.3 & Chapter 14, pp. 114–115, 227–232 (EPUB: `OEBPS/Autopilot_ebook-16.xhtml`, `OEBPS/Autopilot_ebook-24.xhtml`)
- Quote: "Hence the correct rule for an asset allocating investor is to have a constant forecast equal to the expected average forecast, +10 for all instruments... So using an equal forecast for all instruments is equivalent to assuming all assets have the same expected Sharpe ratio."
- Rule as written:
  - Setup: Fix forecast = $+10$ permanently across all instruments in the portfolio (Equities, Bonds, Commodities).
  - Sizing: Size each instrument to equal risk contribution: $	ext{Position}_i = 	ext{Capital} 	imes 	ext{Target Volatility} 	imes 	ext{Weight}_i / (	ext{Block Value}_i 	imes \sigma_{	ext{price}, i})$.
  - Rebalance: Rebalance weekly or monthly when positions breach buffer zones.
  - Market: Global asset classes (ETFs, index futures).
  - Bar size: Weekly / monthly.
  - Holding time: Permanent holding.
- Book's evidence: Equivalent to Bridgewater-style Risk Parity asset allocation.
- Mechanism (the book's): Harvesting long-term macroeconomic equity risk premiums, bond term premiums, and commodity inflation premiums in equal risk proportion without trying to time market cycles.
- Mechanism (my inference): none needed.
- Apex fit: no. Permanent buy-and-hold risk parity portfolio; violates Apex daily flat cutoff.
- Already tested? no.

---

### 15. Combined Multi-Horizon Trend Following System
- Where: Chapter 8 & Chapter 15, pp. 131–142, 241–252 (EPUB: `OEBPS/Autopilot_ebook-17.xhtml`, `OEBPS/Autopilot_ebook-25.xhtml`)
- Quote: "Combining with forecast weights... We can combine the six EWMAC variations with weights that reflect their correlations... A portfolio of six EWMAC rules has a forecast diversification multiplier (FDM) of around 1.3 to 1.5."
- Rule as written:
  - Setup: Compute forecasts for 6 EWMAC variations (2:8, 4:16, 8:32, 16:64, 32:128, 64:256).
  - Combination: Weight each forecast: $	ext{Combined Forecast} = 	ext{FDM} 	imes \sum w_i \cdot 	ext{Forecast}_i$, capped at $\pm 20$.
  - Position: Sized dynamically to cash volatility target.
  - Market: Diversified portfolio of 30+ futures markets.
  - Bar size: Daily.
  - Holding time: Multi-day to multi-month.
- Book's evidence: Core systematic CTA strategy practiced by AHL/Man Group; historical multi-decade Sharpe ratio ~0.55–0.70 across 30+ liquid futures.
- Mechanism (the book's): Institutional capital flows, trend-following positive feedback, and behavioral anchoring across short, medium, and long horizons.
- Mechanism (my inference): none needed.
- Apex fit: no. Combines moving-average crossovers on daily data; matches "Moving-average crosses" on failed list; multi-day holding.
- Already tested? Matches "Moving-average crosses" on failed list.

---

### 16. Multi-Strategy Trend + Carry System
- Where: Chapter 8, Section 8.1 & Chapter 15, pp. 133–136, 241–252 (EPUB: `OEBPS/Autopilot_ebook-17.xhtml`, `OEBPS/Autopilot_ebook-25.xhtml`)
- Quote: "It makes sense to combine diversifying trading rules like the positive skew, trend following EWMAC rule, with a negative skew carry rule... A 60% weight on trend and 40% weight on carry is a robust institutional baseline."
- Rule as written:
  - Setup: On each futures contract, calculate Trend Forecast (blended EWMAC) and Carry Forecast (term structure roll yield).
  - Combination: $	ext{Final Forecast} = 	ext{FDM} 	imes (0.60 	imes 	ext{Trend} + 0.40 	imes 	ext{Carry})$, capped at $\pm 20$.
  - Sizing: Volatility scalar $	imes (	ext{Final Forecast} / 10) 	imes 	ext{Instrument Weight} 	imes 	ext{IDM}$.
  - Rebalancing: Daily with 10% position buffer zones.
  - Market: 30+ futures markets across Equities, Fixed Income, Commodities, and Currencies.
  - Bar size: Daily.
  - Holding time: Weeks to months.
- Book's evidence: Institutional hedge fund benchmark; produces higher Sharpe ratio (~0.75–0.90) and shallower drawdowns than trend-following alone, as carry yields steady income during sideways markets while trend-following protects during crisis regimes.
- Mechanism (the book's): Structural insurance risk premium (Carry) combined with behavioral trend momentum (Trend Following).
- Mechanism (my inference): none needed.
- Apex fit: no. Multi-month futures holding period; EWMAC leg is on the failed list; carry cannot be captured intraday.
- Already tested? Matches "Moving-average crosses" on failed list.

---

### 17. Volatility-Targeted Continuous Position Sizing Framework
- Where: Chapters 9 & 10, pp. 145–174 (EPUB: `OEBPS/Autopilot_ebook-18.xhtml`, `OEBPS/Autopilot_ebook-19.xhtml`)
- Quote: "The volatility scalar is equal to your daily cash volatility target, divided by the instrument value volatility... Subsystem position = Volatility scalar * (Forecast / 10)... Higher absolute forecasts, bigger account sizes, a greater appetite for risk and lower instrument price volatility will mean larger positions."
- Rule as written:
  - Setup: Define Annual Cash Volatility Target $	au$ (e.g. 20% of capital). Daily Cash Volatility Target = $	ext{Capital} 	imes 	au / 16$.
  - Calculate Instrument Value Volatility = $	ext{Block Value} 	imes \sigma_{	ext{daily, price}} 	imes 	ext{FX Rate}$.
  - Volatility Scalar = $	ext{Daily Cash Vol Target} / 	ext{Instrument Value Volatility}$.
  - Target Position: $q = 	ext{Volatility Scalar} 	imes (	ext{Forecast} / 10)$.
  - Market: All futures, equities, and currencies.
  - Bar size: Daily.
  - Holding time: Continuous.
- Book's evidence: Carver proves that sizing positions strictly inversely to rolling price volatility stabilizes portfolio risk across market regimes and prevents volatile assets from dominating portfolio variance.
- Mechanism (the book's): Constant risk targeting prevents risk explosions during high-volatility market crashes.
- Mechanism (my inference): none needed.
- Apex fit: Capital management and sizing architecture (applicable to size any edge, but not an independent alpha entry rule).
- Already tested? no.

---

### 18. Subsystem Position Buffer Zone Execution Rule
- Where: Chapter 11, Section 11.6 & Chapter 12, pp. 185–188, 195–198 (EPUB: `OEBPS/Autopilot_ebook-20.xhtml`, `OEBPS/Autopilot_ebook-21.xhtml`)
- Quote: "To avoid trading too frequently, which would generate excessive transaction costs, you should only trade when the difference between your optimal position and your current position exceeds a certain buffer... A buffer of 10% of the optimal position is a sensible compromise."
- Rule as written:
  - Setup: Compute optimal continuous target position $q^*$. Calculate buffer band $[0.90 \cdot q^*, 1.10 \cdot q^*]$.
  - Execution Rule:
    - If current position $q_{	ext{current}} < 0.90 \cdot q^*$: Buy up to the lower buffer threshold $0.90 \cdot q^*$.
    - If current position $q_{	ext{current}} > 1.10 \cdot q^*$: Sell down to the upper buffer threshold $1.10 \cdot q^*$.
    - If current position is within $[0.90 \cdot q^*, 1.10 \cdot q^*]$: Do NOT trade (hold current position).
  - Market: All systematic portfolios.
  - Bar size: Daily.
  - Holding time: Continuous.
- Book's evidence: Backtesting on futures demonstrates that a 10% buffer cuts annual trading turnover by 30% to 40% with negligible impact on strategy Sharpe ratio, drastically reducing commission and spread drag.
- Mechanism (the book's): Eliminates unprofitable churn on minor forecast noise.
- Mechanism (my inference): none needed.
- Apex fit: Execution hygiene technique; not an entry rule.
- Already tested? no.

---

## Ranked Shortlist of Apex-Compatible Ideas

To qualify for this shortlist, an idea must strictly satisfy:
1. **Apex-compatible**: Flat by 15:59 CT (intraday only), tradeable on liquid CME futures (NQ, ES, CL, GC, ZN, or micros), single stop loss fitting within a $2,000 trailing drawdown.
2. **Not already tested**: Not in the brief's "Already tested and failed" list (disqualifying moving-average crosses, 20-day regime filters, meta-labeling, mean reversion on NQ/ES, order-flow indicators, and gamma/OI pinning).
3. **Stated mechanism**: Supported by an explicit structural or economic mechanism explaining who is forced or paid to trade.

### Shortlist Result: **0 Candidates Qualified**

A rigorous, objective audit of Robert Carver's *Systematic Trading* reveals that **zero ideas qualify for the Apex shortlist**.

### Explicit Rationale for Zero Shortlist Candidates:
1. **Direct Collision with the "Already Tested and Failed" List**:
   - The primary alpha engine of Carver's framework is the **Exponentially Weighted Moving Average Crossover (EWMAC)** rule across various lookbacks (2:8, 4:16, 8:32, 16:64, 32:128, 64:256).
   - In Jesse and in systematic futures trading, EWMAC is mathematically identical to an exponential moving average (EMA) crossover. The brief's explicit Rule 6 states: **"Moving-average crosses: EMA 8/21, SMA 20/50, SMA 50/200, fast/slow MACD crosses. Tested on NQ and ES 1m/5m/15m/1h. Every combination whipsaws in chop. Moving-average crosses... are out."** Recommending EWMAC would directly violate the brief's hard stop.
2. **Intraday Incompatibility of the Carry Rule**:
   - Carver's second major rule is **Futures Term Structure Carry** (harvesting roll yield/basis between contract expiries).
   - Carry returns are earned through contract convergence over multi-week and multi-month holding periods. An intraday trader who must liquidate flat by 15:59 CT every day cannot harvest carry: within a 6-hour intraday window, the earned roll yield is infinitesimally small ($< 0.0001\%$) and is completely dominated by intraday price volatility and transaction friction.
3. **Illustrative Toy Systems Disclaimed by the Author**:
   - The "A and B System" (Early Profit Taker and Early Loss Taker) is explicitly disclaimed by Carver himself in Appendix B: *"I don't recommend using the A and B system for actual trading, but I've included the specification here to satisfy the curious."*
4. **Discretionary and Asset Allocation Rules**:
   - The Semi-Automatic framework relies on subjective human forecasting rather than deterministic systematic rules.
   - The Asset Allocator "No-Rule" rule (+10 constant forecast) is a permanent buy-and-hold risk parity holding, violating the mandatory 15:59 CT flat rule.
5. **The Value of Carver is Architecture, Not Intraday Signals**:
   - Robert Carver's immense contribution to systematic trading is **structural and architectural**: continuous forecast scaling ($\pm 10$ average, $\pm 20$ cap), inverse-volatility position sizing, forecast diversification multipliers, and 10% position buffers to minimize churn. These principles should govern risk sizing on valid edges, but Carver does not offer standalone intraday futures entry rules compatible with Apex constraints.

---

### Disqualifications from Shortlist (Complete Itemized Inventory)
- **EWMAC Trend Following Variations (Ideas 3, 4, 5, 6, 7, 8, 15, 16)**: Disqualified because moving-average crosses (EMA/SMA/EWMAC) are explicitly on the brief's "Already tested and failed" list. Daily bars also violate Apex flat cutoff.
- **Futures Term Structure Carry (Ideas 9, 16)**: Disqualified because roll yield/basis convergence is a multi-month process; impossible to harvest on an intraday timeframe where positions must be flat by 15:59 CT.
- **Equity and FX Carry Rules (Ideas 10, 11, 12)**: Disqualified because cash equities and spot currencies are prohibited on Apex CME futures accounts, and holding periods span months.
- **A and B System (Ideas 1, 2)**: Disqualified because the author explicitly advises against trading it live; continuous flipping on 5-deviation stops generates severe churn and drawdowns.
- **"Close to Open" Overnight Drift (Idea 12)**: Disqualified because it is an untested theoretical example; overnight gap fading matches "Mean reversion on NQ / ES" on the failed list.
- **Semi-Automatic & Asset Allocator Rules (Ideas 13, 14)**: Disqualified because semi-automatic relies on subjective discretionary forecasting, and asset allocation is permanent buy-and-hold.
- **Position Sizing and Buffer Frameworks (Ideas 17, 18)**: Sizing and execution hygiene frameworks, not directional alpha entry rules.
