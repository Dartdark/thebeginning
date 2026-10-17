# Common rules for the NQ tasks (02-08). Read this before any NQ task.

You are a blind checker. Rebuild each rule from its task file and this page only, run it in Jesse, and report exactly what
you get. Do not search for, open or use any other code, report or result about these rules. Do not optimise or change
any parameter. If something is ambiguous, pick the most literal reading, keep going, and list it in your report. A task
is only done when a backtest has actually run and the trade list exists.

## Data (E-mini Nasdaq-100 futures, continuous contract, not back-adjusted)

`research_scripts/data/` holds two sets of 1-minute files, columns `date,time,open,high,low,close,volume`:
- `NQ_1min_<year>.csv`: the day session, 08:00 to 15:15.
- `NQ_1min_ON_<year>.csv`: the rest of the 24-hour session, 15:16 to 07:59 (Sunday evening to Friday).

Use these files (or identical copies already imported from `C:\NQData`: check that a few rows match exactly and that the weekday break is 16:00-17:00, i.e. Central time; report what you used). Import only what the task needs. Merge both sets into one series. If a (date, time) appears in both, keep the row from the day file.
- `date` = YYYYMMDD, `time` = HHMM, in **US Central time (America/Chicago)**.
- Each row is stamped with the bar's **closing** minute: `20190102,801` is the bar from 08:00 to 08:01 CT.
- Minutes without trades are missing. The market is closed 16:00 to 17:00 CT on weekdays and from Friday 16:00 to
  Sunday 17:00.

Import as Jesse custom data, converting to UTC open times with daylight saving handled. You may instead keep Central
time as the clock throughout (e.g. writing CT times as if they were UTC); if you do, say so. Make sure 5 / 15 / 30-minute
bars line up with the clock (:00, :05 ... / :00, :15 ... / :00, :30), and that a missing minute can't move a bar's open,
high, low or close. Jesse groups 1-minute candles by count, so a gap shifts every later bar unless handled. Report how
you did it.

## Conventions used by every NQ task

- **Clock.** All times are **US Central**. Bars are stamped at their **close** (the bar stamped 08:30 is 08:25-08:30 on
  a 5-minute chart). A bar stamped 00:00 belongs to the new date.
- **Bars.** A bar exists only if at least one trade happened inside it. Bars with no trades don't count for anything.
- **"Next bar at market"** means filled at the open of the next bar.
- **"At this bar's close"** means filled at that bar's close.
- **Stops and targets** are checked on 1-minute bars inside each bar.
  - A stop fills at its price, or at a 1-minute bar's open if that bar opens beyond it.
  - A target (limit) fills at its price.
  - If one 1-minute bar touches both the stop and the target, assume the stop filled first and say how often it happened.
- **Stop / target distances** are measured from the actual entry fill price.
- **Daily ATR (15 days).** A "day" is a Central calendar date that has bars.
  - When a new date starts, the date that just ended is scored, if it was **Monday-Friday**:
    TR = max(day high, previous date's last close) − min(day low, previous date's last close).
  - The "previous date's last close" is the last close of the date before it that had bars, whatever weekday it was.
  - ATR = the average of the last 15 scored TRs. A rule that uses the ATR doesn't trade until 15 TRs exist.
  - Day high / low / close use all bars of that date, overnight included.
- **Early-close days** (`EARLY` below; a weekday is Monday-Friday):
  - Jan 1 on a weekday, or Jan 2 if it is a Monday.
  - the 3rd Monday of January (any Monday Jan 15-21), and any Monday Feb 15-21.
  - any Monday from May 25 on.
  - from 2022: Jun 19 on a weekday, Jun 18 if it is a Friday, Jun 20 if it is a Monday.
  - Jul 3 or Jul 4 on a weekday, or Jul 5 if it is a Monday.
  - any Monday Sep 1-7.
  - any Thursday Nov 22-28, and any Friday Nov 23-29.
  - Dec 24 or Dec 25 on a weekday, or Dec 26 if it is a Monday.
- One position at a time. Size 1 contract ($20 per point, tick 0.25). Jesse fees 0. Trades from 2018-01-02 to the end
  of the data.

## Output for every task (save in `tasks/out_<NN>/`)

1. **`trades.csv`**, one row per trade with these columns:
   - `date` (Central date of the entry), `side` (`long` / `short`)
   - `entry_time_ct`, `entry_price`
   - `exit_time_ct`, `exit_price`
   - `exit_reason` (`stop` / `target` / `time` / other, named)
   - `points` (exit − entry for longs, entry − exit for shorts)
2. **`strategy.py`**: the Jesse strategy you ran.
3. **`report.md`**, covering:
   - number of trades (longs / shorts), average points, win rate, total points by year
   - how you handled time zones and missing minutes
   - every ambiguity and how you resolved it
   - anything odd in the data
   Do not compare with any outside result.
