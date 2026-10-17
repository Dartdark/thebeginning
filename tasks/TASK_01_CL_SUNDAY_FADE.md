# Task 01: blind rebuild of a crude-oil rule in Jesse (written by Claude, 2026-10-17)

You are a blind checker. Rebuild the rule below from this text only, run it in Jesse, and report exactly what you get.
Do not search for, open or use any other code, report or result about this rule. Do not optimise or change any
parameter. If something in the text is ambiguous, pick the most literal reading, keep going, and list the ambiguity in
your report. The work is only done when a backtest has actually run and the trade list exists.

## Data

`research_scripts/data/CL_1min_2017.csv` ... `CL_1min_2026.csv`: CL (WTI crude futures, continuous contract, not
back-adjusted) 1-minute bars, columns `date,time,open,high,low,close,volume`.
- `date` = YYYYMMDD, `time` = HHMM, in **US Central time (America/Chicago)**.
- Each row is stamped with the bar's **closing** minute: `20190101,1701` is the bar from 17:00 to 17:01 CT.
- Minutes without trades are missing (no row).

Import them as Jesse custom data (`preview_custom_candle_csv`, then `clean_and_import_custom_candle_csv`). Jesse
timestamps are the bar's OPEN time in UTC, so convert with daylight saving handled. Check the conversion on a few rows
and report how you did it.

Jesse builds 5-minute bars by grouping 1-minute candles. Make sure your 5-minute bars line up with the clock (:00, :05,
...) and that a missing minute can't move a bar's open, high, low or close. Report how you handled missing minutes.

## The rule (one CL contract, $1,000 per point, tick 0.01)

All times below are **US Eastern (America/New_York)**, 5-minute bars stamped at their **close**. A bar stamped 00:00
belongs to the new date.

1. **Daily ATR (15 days).** A "day" is an Eastern calendar date (midnight to midnight) that has bars.
   - When a new date starts, the date that just ended is scored, if it was **Monday-Friday**:
     TR = max(day high, previous date's last close) − min(day low, previous date's last close).
   - The "previous date's last close" is the last close of the date before it that had bars, **whatever weekday it was**
     (a Sunday counts here).
   - ATR = the average of the last 15 scored TRs. No signal until 15 TRs exist.
2. **Signal.** On each **Sunday** (Eastern date), look at the **first 5-minute bar of that date**.
   - gap = that bar's **open** − the **close of the bar just before it** (the last bar of Friday's session).
   - If gap ≥ 0.10 × ATR, the signal is a short. ATR is the value as of that Sunday bar.
3. **Entry.** Sell short 1 contract at the **open of the next 5-minute bar**.
4. **Stop.** Buy back if price trades at or above entry + 0.75 × ATR (ATR from the signal bar), checked on 1-minute bars.
   - Fill at the stop price.
   - If a 1-minute bar opens beyond the stop, fill at that bar's open.
5. **Time exit.** Otherwise buy back at the **close of the first 5-minute bar of Monday stamped 10:00 or later**.
6. Only one position at a time. Trade every qualifying Sunday from 2018-01-01 to the end of the data. Roll weekends
   are included.

## Settings

- Jesse fees **0**. Size 1 contract. Report raw price points; costs are applied elsewhere.
- Starting balance large enough that margin never blocks a trade.

## Output (save in `tasks/out_01/`)

1. **`trades.csv`**, one row per trade with these columns:
   - `signal_date` (Sunday, Eastern)
   - `entry_time_et`, `entry_price`
   - `exit_time_et`, `exit_price`
   - `exit_reason` (`stop` / `time`)
   - `points` (entry − exit, since every trade is a short)
2. **`strategy.py`**: the Jesse strategy you ran (a copy).
3. **`report.md`**, covering:
   - number of trades, average points, win rate, total points by year
   - how you converted the time zones and handled missing minutes
   - every ambiguity you found and how you resolved it
   - anything that looked wrong in the data
   Do not compare with any outside result.

Then tell the user it is done. They commit `tasks/out_01/` and push to the `antigravity/jesse` branch.
