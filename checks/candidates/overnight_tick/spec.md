# Overnight TickRSV / VIX, NQ long only (candidate, 2026-10-24)

Source: the user's written specification 'NQ Overnight Anomaly Strategy Optimized' (copied in `SOURCE_SPEC.md` here) and
the PowerLanguage assembled from it (`NQ_Overnight_Tick_VIX.txt`, the BASE strategy; you may read both).

## Data
- NQ 1-minute bars, Central time, stamped at the bar CLOSE: the 24-hour grid in `scratch_data/g24.pkl`
  (`analysis/grid24.py`; built from `data/NQ_1min_20*.csv` day files + `data/NQ_1min_ON_*.csv` night files).
- Order flow: `data/OF_1min_<year>_<part>.csv` (The Bridge export, times in EASTERN time, 09:30-16:15 ET, to 2026-07-07);
  columns `upvol` = aggressor buy volume, `downvol` = aggressor sell volume. Used as the UpTicks / DownTicks of the spec.
- VIX: `data/VIX_daily.csv` (DATE, CLOSE).

## Rule (times CT)
- Regular session of day D: bars stamped 08:31-15:00 CT. Open = open of its first bar, close = close of its last bar.
  Early close if its last bar is before 14:00 CT -> no trade.
- TickRSV(D) = (sum upvol - sum downvol) / (sum upvol + sum downvol) over order-flow bars stamped 15:16-16:15 ET
  (= 14:16-15:15 CT). Missing / zero -> no trade.
- VIX(D) = VIX daily close of D; SMA = mean of the last 25 daily VIX closes up to and including D. High regime: close > SMA.
- Enter if close(D) < open(D) AND not early AND ((RSV < 0 and high) or (RSV >= 0 and not high)).
- Entry: the next evening session after D (D's evening Mon-Thu; Sunday evening for a Friday D), at the OPEN of the 1-minute
  bar stamped 17:06 CT. Exit: the OPEN of the bar stamped 03:01 CT the next calendar day. Long 1 NQ, no stop.
- One trade per regular session (a holiday evening with no new session does not trade again). Nights whose 17:06-03:01 span
  contains a contract roll switch are excluded (as in the Overnight Anomaly rebuild; the price jump is not a return).
- Trades dated by the exit date. 2018-01-01 onward.

## Costs
$7.25 round trip + 1 tick ($5) per fill, both fills market: $17.25 per trade.

## Mechanism (the author's view)
Overnight-drift anomaly after a down cash session, filtered by an interaction between closing order-flow imbalance and the
VIX regime (negative flow in high VIX = forced selling that reverses overnight; non-negative flow in calm VIX = orderly
continuation). The interaction was found empirically by the author.

## Variants tried
The author's own search (several filters, stop and sizing variants, VIX SMA 20 vs 25, the four-cell interaction chosen
empirically): count unknown, assume ~30. The maker ran 5 VIX lengths and 1 alternative RSV proxy as sensitivity.
Not pre-registered. `placebo.csv` = 20 runs with the VIX regime shuffled across nights (same RSV and down-day filter).

## trades.csv
date (exit date), side (+1), net ($ per NQ after costs).
