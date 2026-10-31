# Code review log (Code reviewer session)

One entry per review: scope, defects (reproduced with a fixture before fixing), fixes, decision impact.

## 2026-10-31: codex/work since the 10/30 cross-review (up to 1135499)

Scope: Codex's 10/30-10/31 commits. Most are paper reviews and research-only planners (commodity skewness, FX, Rad
double-sort), which feed no plan or live input. Read in depth: the extended-data rebuild audits (d5325da, c715d4d) and the
Swing Target exit-kind account replays (f30fcdf, d490607, 97666bd).

1. **CONFIRMED, FIXED (Claude's code, found by Codex): MC reports' unfinished trade booked as closed.** MultiCharts exports
   a position still open at the report's end as an Exit row with signal `open` (marked P&L, date 00:00). `portfolio.load_mc`,
   `prop_sim.load_trades` and `live_vs_backtest.read_trades` took it as a closed trade. Fixture
   (scratchpad `fx_open.py`): the open pair came back as a trade with j1 < j0 and $1,505 P&L, and `paths()` raised
   IndexError, which is the crash Codex hit in `build_lab.py` on the extended grid (ONB ML funded v2, 10/12 short).
   Fix: the three loaders drop `open` exit rows (load_mc prints what it dropped and asserts that the entry and exit
   counts match). After the fix the report loads 343 closed trades, matching Codex. Scan of every report in `mc_reports/`:
   only ONB ML funded v2 and ORB_Volatility_Filtered_GC_gross carry such a row.
   **Decision impact: none.** The old grid ended before 10/12, so `load_mc` had already filtered out that trade. Every
   live_vs_backtest comparison window starts 10/20. The fix unblocks the extended-data rebuild (TODO).
2. **No defect: Swing Target replay (Codex).** 50K VB 2/1 -> 1/1 + ST 1: two-year payout -$7 (95% interval -$260 to
   +$243); 150K DT 2 -> ST 2: -$7 (-$287 to +$280). These are ties, which matches today's revert (6082472). Codex
   contradicts our 10/30 line that the exit-kind fix "can only strengthen" adoption; that line has already been
   superseded by the revert.
3. **Open, not a code defect:** saved MC reports end 10/09-10/13, so the dashboard's `bt_cache.json` can't cover
   10/12-10/30 until fresh MC exports exist. Codex rightly left the cache alone. Running live_panels on old tickets would
   record unknown days as no-trade days.
