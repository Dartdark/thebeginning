# MultiCharts / PowerLanguage pitfalls (error log)

Read before writing or changing any MultiCharts code. **After every compile error, runtime bug or
MultiCharts-vs-Python mismatch is solved, add it here** (symptom → cause → fix), so it is not repeated.

## Compile errors
- **"Unknown Function" on `IIFString`** (NQ_Vault_Break_SP, line 199): not a built-in in our MultiCharts.
  Use an if / else with two `Print` statements (or `IFF` for numbers only).
- **"unverified function"**: every OFB_* function must be compiled once before a signal that calls it.
- **"OLD DLL"**: restart MultiCharts after any DLL or data change.

## Logic bugs found in our code
- **Sunday session wipes daily flags** (single-print flag in NQ_Vault_Break_SP): a flag reset at the first bar of a
  new session also fires on the Sunday 17:00 CT open, so Monday lost Friday's value. Fix: compute the flag once at the
  15:00 CT bar into a separate `Computed` variable and handle half-days explicitly; never reset on "first bar of session".
- **`SetExitOnClose` on a 24-hour chart** closes at the session end (midnight on our sessions), not 15:59 CT. It closed
  47 evening Twin Continuation trades early and made MultiCharts disagree with Python. Fix: remove it and flatten with an
  explicit time exit (`if Time >= FlatTime then Sell/BuyToCover next bar at market`).
- **Holidays / early closes**: hard-coded times (e.g. last entry 14:30, flatten 15:55) trade into a 12:00 CT close.
  Fix: the `IsEarlyClose` date list + `UseHolidayTimes`, `EarlyLastEntry 1100`, `EarlyFlatten 1130` (as in Vault Break
  and Twin Continuation v2.1).
- **Old input values survive a code replace**: pasting new code into an existing signal keeps inputs with the same name
  (an old ExitTime 1100 broke a backtest). Check the report's Settings sheet after every change.
- **Bar-time minutes vs HHMM**: when porting, 15:30 CT is minute 1350 / HHMM 1530, not 1290 (a Python port bug,
  FillEnd 1290). Convert with one helper (`jof` in `analysis/grid24.py`), never by hand.

## Live order rejections
- **'Invalid StopMarket order parameters' on a protective stop** (EOS, 2026-10-16, 6:34 PT = 8:34 CT: "Buy Stop 1 @MNQ @ 30168"
  rejected): the short filled at the 8:30 open, price ran up through the stop level before the stop order reached Rithmic,
  and a buy stop below the market is invalid, so the position was left without its stop. Same family as the Overnight
  Bias entry rejection of 10/14. Fix (EOS): keep `SetStopLoss`, and add a bar-close guard that exits at market when the bar
  trades at or through the stop level and the position is still open (`Exp Open SG`). **Applied to every live / funded
  strategy using `SetStopLoss` (2026-10-17):** VB, VB SP (`VB SG`), Overnight Bias / ADX30 / ML (`ON Bias LSG / SSG`),
  Monday (`Monday SG`), LDF (`LateFlow LSG / SSG`), NFP (`NFP Fade LSG / SSG`), CL fade (`SunGap LSG / SSG`); the
  condition is the bar's Low / High (not Close: a spike through the stop that closes back inside would otherwise stay
  unprotected). Backtests are unchanged (the stop always fills inside that bar first). The Bridge Monday Long can't be
  edited: add `apex_strategies/Apex_Stop_Guard.txt` to its chart with `StopPoints` a few ticks wider than its stop.
  Limitation: the guard acts at bar close, so on a 30-minute chart (VB) an unprotected position can run up to one bar.
- **'Interactive Brokers: Unable to connect to TWS' (127.0.0.1 : 7497)** (2026-10-16, 8:37 CT): some chart or the Trading
  panel has its broker profile set to Interactive Brokers (MultiCharts' default) instead of Rithmic. Any strategy on that
  profile sends nothing to Apex. Fix: every strategy chart -> Format Signals -> Properties -> Auto Trading -> broker profile
  = Rithmic (the Apex account); also check the default broker in the Trading panel / DOM and new charts.
- **Every Rithmic (Apex) order so far was rejected; the only fills were on Paper Trader** (Order tracker, 2026-10-16): 10/12
  fills = Paper Trader dxFeed / SIM 001; 10/14 ONB entry stop and 10/16 EOS stop losses (20 retries in one second) = Rithmic
  'Invalid StopMarket order parameters', all with instrument `@MNQ`. `@MNQ` is the dxFeed continuous symbol; Rithmic needs the
  real contract (MNQZ26 until the December roll). Most likely fix: symbol mapping @MNQ -> current MNQ contract for the
  Rithmic profile (or chart the contract itself), update at every roll; then confirm with a 1-MNQ manual test order through
  MultiCharts before relying on auto-trading. **Confirmed and fixed 2026-10-16:** File -> Broker Profiles -> Symbol Mapping
  (Rithmic) had `@MNQ (dxFeed) -> @MNQ`; a manual Sell Limit was rejected the same way. Now `@MNQ (dxFeed) -> MNQZ6 (Rithmic,
  CME)`. In the Rithmic lookup search `MNQ` (no @; Rithmic uses one-digit years: MNQZ6). **Roll checklist:** change the
  broker symbol at every roll — MNQ / NQ quarterly (next ~2026-12-11: MNQZ6 -> MNQH7), MCL monthly once the CL fade is live.
- After any rejection: check the Order and Position Tracker / the broker position at once; flatten by hand if the
  account holds a position the chart does not manage.

## Apex daily loss limit vs the strategy (2026-10-19)
- Symptom: VB long 8 MNQ closed at -$1,017 mid-bar (11:01:41 CT), then dozens of 'Sell Stop 8 / Sell Limit 8 ... Rejected:
  Account is done for day' per second; the tracker shows those orders with price 0.00. Cause: Apex's $1,000 daily loss
  limit (50K evaluation) liquidated the account and locked it for the day; MultiCharts didn't see that exit, kept its
  position (long 8) and kept re-sending VB's stop / target. Not a MultiCharts bug.
- Danger: the chart still believes it's in a position. Next day the account reopens and those exits would be ACCEPTED,
  opening an unplanned short. Fix after any Apex liquidation / lock: with the account flat, turn auto-trading OFF and ON
  on every affected chart (initial position Flat) or reload it, and check Strategy Positions shows flat before the open.
- VB 8 MNQ has a $1,200 stop, above the $1,000 daily loss limit, so a full VB loss is cut by Apex at about -$1,000 and
  the account is done for the day (the combine simulator already models this: pass ~50% includes it).

## Rithmic connection errors (2026-10-19)
- "Trading System / Market Data / PnL Connection Login Failed. Please contact the FCM/IB who issued your login id
  (permission denied)" was simply a WRONG PASSWORD in the broker profile (File > Broker Profiles > Rithmic > Edit),
  not a machine lock. Check the password first, then System (working setup: Rithmic 01, Gateway Chicago Area, Reset
  reloads the server lines), then that no other machine is logged in with the same login.
- Never test a second machine's broker login during market hours or with a position open: a failed / duplicate login
  can disconnect the live machine.

## Setup checklist
- A signal runs on data1 only; each strategy needs its own chart window.
- Several signals on one chart form ONE strategy sharing one position: an exit-only signal (e.g. `Apex_Target_Guard`)
  added next to a strategy closes that strategy's position. It cannot see or close positions on other charts.
- Report Settings sheet to check: name, inputs, Compression, Bar Magnifier, commission / slippage 0, fill limit +1 point.
- Data: Map ASCII with Exchange CME, time zone Exchange, start row 2, bar-close conversion unchecked.
- Auto trading: Format Signals > Properties > Auto Trading (broker, account), mode AA, initial position Flat, no automatic
  position sync, intra-bar order generation off. Tracker: Ctrl+Shift+O.
- The ACCOUNT is behind the gear icon next to the broker plug-in (Strategy Properties > Auto Trading > Rithmic > gear).
  'Stop auto-trading after N rejected orders' was 102 (2026-10-19: ~100 rejections after the Apex lock): set it to 10.
  A second Apex account = a second set of charts with the other account selected (no copier yet).
- **New chart setup (user's note, 2026-10-20):** click the small side-arrow on the chart's right edge to open / activate
  Chart Trading, then set its broker drop-down (green dot) to Rithmic and pick the Apex account. Missed, the chart sat on
  'SIM 001' (Simulated Trading Profile) and didn't work. Also check Strategy Properties > Auto Trading > Rithmic > gear =
  the right Apex account: that one decides where the strategy's orders go.
- Export "Export cancelled by user" in a report = the export did not finish; export again before sending.

## Reading MultiCharts reports
- No CSV conversion is needed: `analysis/portfolio.load_mc(g, "<report>.xlsx")` reads the "List of Trades" sheet
  directly (entry rows + exit rows), and `analysis/resampling.py` does the Monte Carlo / bootstrap.
