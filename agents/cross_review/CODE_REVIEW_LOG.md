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
