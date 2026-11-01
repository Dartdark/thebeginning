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

## 2026-10-31 (2): codex/work 1135499..9f02f8d

Scope: about 45 Codex commits. All but one are paper reviews or source audits (`analysis/codex_*` audit scripts, evidence
notes, TODO entries in the data register). None of them touches a plan, the live guard, a MultiCharts strategy or
Claude's code.

1. **No defect: inverse Bitcoin strategy (SSRN 3441913, `analysis/codex_bitcoin_inverse_3441913_strategy.py`), built at
   the user's request for Claude's review.** Its own 20 tests pass. I checked the arithmetic independently with my own
   test cases:
   - **Adding in the same direction:** the combined entry price is the contract-weighted harmonic mean. Long 100 @ 40,000
     plus 100 @ 50,000 gives a basis of 44,444.44.
   - **Partial close:** selling 150 @ 45,000 realizes +4.17e-5 BTC and leaves +1.39e-5 BTC unrealized. The two add up to
     the whole position's P&L.
   - **Reversal:** long 50 @ 40,000 to short 30 @ 30,000 realizes -4.17e-4 BTC and resets the basis to 30,000.
   - **Fees:** charged in BTC as face / price x rate.
   - **Clocks:** naive, non-UTC and date-only timestamps are all rejected.
   - **Contract counts:** truncated toward zero to whole contracts.
   - **Cost reconciliation:** the drop in account value is checked against fees plus the gap between fill and mark
     prices; I traced the sign of that gap for both buys and sells.
   I did not re-derive the coefficient formula (Eq 4.4) from the paper; Codex's source audit covers it.
   Plan fit: none. The rule trades BitMEX-style inverse futures, held for days, which can't run on Apex (CME, flat by
   15:59). CME micro Bitcoin futures are linear, so the personal account couldn't trade it as written. It stays research
   only, gated on data.

## 2026-10-31 (3): codex/work 9f02f8d..192b697

New code: Codex's reinforcement-learning build (SSRN 3690996), in two versions: daily stocks and intraday MNQ
(`analysis/codex_rl3690996_core.py` / `_env.py` / `_train.py`). Codex's verdict is REJECT: neither selector passed its
frozen design gate. The other commits are the inverse Bitcoin packet, already reviewed in (2).

1. **No defect in the MNQ engine (read in full).**
   - **Clocks:** the arrays start at 08:31 CT (index 0 = minute 511), so the decision at k reads the bar that closes at
     08:35 + 5k, fills at the next minute's open (08:36 + 5k), and flattens at 14:56. Nothing is read ahead.
   - **Inputs:** the turbulence threshold uses only earlier scores (shifted), and the ATR is the prior 15 sessions
     (shifted).
   - **Stops:** a stop that gaps fills at the worse of the open and the stop, minus a tick of slippage. Stops are already
     live on the entry bar.
   - **Sizes and P&L:** positions are whole contracts (-1 / 0 / +1). The cost bridge reconciles: gross minus fees minus
     slippage equals net.
2. **Cost note, not a defect.** Codex charges $2.24 per MNQ round trip ($0.62 a side plus a tick a side). Our standard
   is about $1.73 ($0.725 plus a tick per fill). At our cost, the SELECTOR gains about $0.52 a trade x 3,538 trades, about
   +$1.8k over 2018-22: roughly $3.9k in five years, still below the passive long-RTH control ($5.4k) and nowhere near a
   pass (it averaged $0.59 a trade, NW t 0.35). The REJECT stands. Plan fit: none.

## 2026-10-31 (4): RollZone 24h NQ Long v1 (RZL1), user upload (PowerLanguage + 11-page research note)

1. **CONFIRMED (not our code, so not committed): Good Friday positions are held over the weekend.** In some years CME
   equity futures open an abbreviated session on Good Friday that halts at 08:15 CT; in our data that happened on
   2021-04-02, 2023-04-07 and 2026-04-03. The night exit fires on the bar ending 08:25, which never comes, so an open
   night position rides to the Sunday 17:05 bar (`RZL1.CarryLX`).
   - **Fixture:** the code's clock and exit block replayed on the real 2023-04-07 bar times. The last bar 08:15 has
     SM 915, and the night exit needs SM >= 925.
   - **Consequence:** an Apex violation, plus weekend gap risk. It is probably the note's "1 of 3,137 trades held past a
     session close".
   - **Fix:** no entries in the Good Friday session (Thursday 17:00 through Friday). Snippet given to the user; it uses
     the Easter algorithm from `NQ_NFP_Fade.txt`.
2. **Calendar checked against every early close in our NQ data, 2017-2026 (87 days).** The code's rules flag every
   holiday early close, and they never flag a full day. Besides the three Good Fridays, two unscheduled 08:30 CT closures
   (2018-12-05, 2025-01-09) aren't in the calendar, but the 08:25 night exit already fires before them.
3. **No other defect found.**
   - **Clocks:** Exchange CT, session clock 1..1440 from 17:00, and the first bar 1705 starts a new session (Sunday
     included).
   - **No look-ahead:** each slot's average uses earlier sessions only, the daily range comes from completed sessions,
     and the stop entry is placed for the next bar only after a bar that didn't touch the line.
   - **Exit times:** night exit 08:25, day exit 15:55 (before Apex's 15:59), half days 11:55.
   - **Stops:** the stop and target are in currency for the whole position.
   - **Loss budget:** the daily cap counts closed P&L only, so a gap through the stop can exceed it (the note's
     March 2020 case, -$3,680).
4. **Notes for any future test, not code defects:**
   - The note's $14.50 per round turn is lighter than our standard: $7.25 plus one tick per stop or market fill comes
     to about $17.25 per NQ.
   - On 1 NQ the $1,500 cap is above Apex's 50K daily loss limit ($1,000). On MNQ the 0.8 x range stop (median about
     $692) fits.
   - The note's own caveats: the 01:00-07:00 entry block was chosen after the 2023+ trades were seen, there's no
     walk-forward, and the night entries only pay since 2023.

## 2026-10-31 (5): RollZone 24h full test (user: "test it")

Ported to Python (`analysis/rollzone_24h_test.py`, Good Friday fix on); benches in `analysis/rollzone_bench.py`.
Verdict **C**: not for any Apex plan; it goes on the capital-expansion bench (personal). Details in
`checks/candidates/rollzone_24h/verdict.md`.

Found on the way:
- The `load_mc` open-trade fix (0928461) worked in a real `build_lab` run ("dropped 1 unfinished trade" on ONB ML funded v2).
- Rebuilding `scratch_data` also needs `gy.pkl` (YM) and `btc.pkl` (BTC) grids before `s_rank_gap_round2_test.py`, which
  writes `s_rank_gap2.pkl` for the bench lab. `build_lab` doesn't make those two grids; I built them with Grid24 on the
  full-day files.

## 2026-11-01: GC USA -> Asia continuation (user upload; code + paper; "one more variable to cut the drawdown")

- **Code review:** no logic defect found. The DST rule, weekend skip, regime / ATR buffers and fallbacks are causal.
- **Points to check:**
  - The chart clock: on a New York-time GC chart every window is one hour earlier. That reproduces the report best.
  - The 1-contract floor breaks the risk budget in volatile years.
- **Test:** four variables pre-registered, chosen on 2018-22. None cuts the 2023+ drawdown, and since 2023 the
  continuation condition adds nothing over Asia-hours drift. Tier D. Details in
  `checks/candidates/gc_asia_continuation/verdict.md`.
