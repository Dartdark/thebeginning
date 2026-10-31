# Task: read-only execution diagnostics for VB, ONB ADX30 and Bridge Monday (agreed by Codex and Claude, 2026-10-22)

Branch `codex/work`. Observation only: entry rules stay fixed. A timing change would need its own frozen test later.
Two accounts taking the same signal count as ONE market event in any evidence summary.

## What to record per entry (filled, missed and rejected alike)
- Signal time (bar close), order submission time, broker fill time; account, contract, side, quantity, order type,
  order status (filled / rejected + full reason / cancelled), fill price, broker order ID.
- Prices at −5, −2, −1, 0, +1, +2, +5 minutes around the signal and around the fill (1-minute bars).
- Bid / ask at submission and at fill where available. Sunday 17:00 CT reopen: pre-open observations = "unavailable".
- Separate three effects: spread paid, delay / slippage (fill vs signal price), and market moving against a correctly
  executed entry.

## Sources (and what's missing)
1. Broker side: the MultiCharts Order and Position Tracker (VPS), exported weekly by the user as CSV
   (`live/orders/YYYYMMDD_orders.csv`); `live/orders_20261020_21.md` is the first, transcribed by hand.
2. Chart side: `live/trades/*.csv` (the logger: chart state, not fills).
3. 1-minute bars: `data/NQ_1min_*.csv` end 2026-10-09: the user exports the latest bars weekly (see TODO).
4. Bid / ask: not recorded anywhere yet. Draft (don't deploy) a change to `apex_strategies/Apex_Trade_Logger.txt`
   that writes `InsideBid`, `InsideAsk`, `Close` and the PC clock time (`ComputerDateTime`) on every OPEN / CLOSE
   in real time only, as a NEW proposal file `agents/codex/proposals/Apex_Trade_Logger_bidask.txt` for Claude's review.
   Note anything PowerLanguage can't give (e.g. the exact fill time is only in the order tracker).

## Output
Extend `analysis/codex_live_reconcile.py` (offline) and write `agents/codex/results/execution_diagnostics.md`
(5-line Summary first): the schema, the first table for 10/19-10/23 with what is and isn't measurable, and what the
user must export each week. No live / VPS / logger deployment.
