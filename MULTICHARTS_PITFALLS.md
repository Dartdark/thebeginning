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
  closes at or through the stop level (`Exp Open SG`). The other strategies that use `SetStopLoss` (VB, ONB, LDF, Monday,
  NFP, CL fade, Bridge Monday as shipped) can hit the same thing in a fast move; apply the same guard to each.
- After any rejection: check the Order and Position Tracker / the broker position at once; flatten by hand if the
  account holds a position the chart does not manage.

## Setup checklist
- A signal runs on data1 only; each strategy needs its own chart window.
- Report Settings sheet to check: name, inputs, Compression, Bar Magnifier, commission / slippage 0, fill limit +1 point.
- Data: Map ASCII with Exchange CME, time zone Exchange, start row 2, bar-close conversion unchecked.
- Auto trading: Format Signals > Properties > Auto Trading (broker, account), mode AA, initial position Flat, no automatic
  position sync, intra-bar order generation off. Tracker: Ctrl+Shift+O.
- Export "Export cancelled by user" in a report = the export did not finish; export again before sending.

## Reading MultiCharts reports
- No CSV conversion is needed: `analysis/portfolio.load_mc(g, "<report>.xlsx")` reads the "List of Trades" sheet
  directly (entry rows + exit rows), and `analysis/resampling.py` does the Monte Carlo / bootstrap.
