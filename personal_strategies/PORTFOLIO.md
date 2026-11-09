# Personal-account portfolio (2026-10-23; noise-area 15-min longs added 2026-11-03; Dual Thrust, Kusho v9, S47 v2, S30 IBS and Overnight Tick / VIX added 2026-10-24; Overnight Anomaly replaced; BB_MRM added and removed 2026-10-25; Swing Target v3 and PAPERTREND v2 added 2026-10-25)

From everything tested so far; numbers from `analysis/personal_portfolio.py` (output in
`analysis/outputs/personal_portfolio_output.txt`). Backtest 2018-01 → 2026-10, after costs, micro commissions charged at
~$1.25 a round trip. No Apex rules: overnight holds allowed, no trailing limit, no payout cap.

## The pieces (1 micro each)
| Piece | Market | $ a year | 2023+ a year | Max DD | Sharpe | Status |
|---|---|---|---|---|---|---|
| S30 IBS reversal (NQ + ES, long only, holds days, no stop) | MNQ + MES | $5,966 | $5,815 | $8,704 | 0.90 | B; personal only (user 2026-10-24); **still on the forward log**; `checks/candidates/s30_ibs/S30_IBS.txt` |
| Relative Strength (both sides) | MNQ | $3,889 | $4,900 | $2,871 | 1.30 | B, MC-confirmed; funded plan (longs) |
| Kusho v9 (21:00 exit, weekend holds) | MNQ | $3,573 | $3,398 | $1,757 | 1.68 | B; personal only (user 2026-10-24); **still on the forward log**; roll-adjusted rule `checks/candidates/kusho/Kusho_v9.txt` |
| Twin Continuation v2.1 | MNQ | $3,673 | $5,711 | $1,629 | 1.77 | A, MC-confirmed, personal only (overnight, wide stop) |
| Dual Thrust v4 | MNQ | $2,422 | $2,879 | $2,010 | 1.41 | A, checker PASS WITH CONCERNS; MultiCharts-confirmed (report in mc_reports/, 99.9% of fills match the rebuild); also 150K funded at 2 MNQ (user 2026-10-24) |
| S47 v2 (Europe-open impulse) | MNQ | $2,705 | $2,638 | $1,583 | 1.33 | B; personal only (user 2026-10-24); **still on the forward log**; `checks/candidates/s47_v2/S47_v2_fixed.txt` |
| ONB ML | MNQ | $2,410 | $2,773 | $1,564 | 1.62 | S; funded plan (the combine runs plain ONB ADX30) |
| FC 2B v2 | MNQ | $2,366 | $2,213 | $1,534 | 1.33 | A, MC-confirmed, **forward log first** |
| Monday Long | MNQ | $2,104 | $3,912 | $2,086 | 1.09 | funded plan |
| Vault Break | MNQ | $1,723 | $2,237 | $1,385 | 1.30 | live on Apex (combine) |
| Overnight Tick / VIX (long 17:05 → 03:00 CT after a down day, order-flow × VIX filter) | MNQ | $2,201 | $2,838 | $1,283 | 1.68 | A, MC-confirmed; personal + funded (50K 1, 150K 2) since 2026-10-24 (user); replaced Overnight Anomaly (C); data to 2026-07-07; **personal at 2 MNQ (user 2026-11-08)** |
| Bridge Monday | MNQ | $1,295 | $1,478 | $1,689 | 1.39 | live on Apex (combine) |
| Late-Day Flow | MNQ | $889 | $1,171 | $1,590 | 1.10 | funded plan |
| CL Sunday fade | MCL | $692 | $1,042 | $518 | 1.01 | funded plan |
| EOS | MNQ | $548 | $798 | $746 | 0.83 | live on Apex (combine) |
| ES MOC | MES | $342 | $172 | $701 | 1.09 | funded plan |
| Swing Target v3 (prior 2-day RTH level break, target 0.35 / stop 0.7 x range, BE, flat 14:59) | MNQ | $1,932 | $2,642 | $1,446 | 1.43 | B, MC-confirmed (t 4.55); personal (user 2026-10-25) + funded swaps; `funded_strategies/NQ_Swing_Target_v3.txt` |
| PAPERTREND v2 (RTH open ± 0.5 ATR break at 15-min marks, gap side only, flat 14:55, 2 x ATR disaster stop) | MNQ | $2,453 | $2,528 | $2,647 | 1.42 | B, MC-confirmed (Claude's code, t 4.35); personal only (user 2026-10-25); `checks/candidates/papertrend/PAPERTREND_v2_claude.txt` |
| NFP Fade | MNQ | $291 | $467 | $826 | 0.60 | funded plan |
| **Noise-area 15-min, longs only** (The Bridge's code, RTH-anchored; band from the 08:30 open, follow closes beyond it, stop 50 / target 25, flat 14:45) | MNQ | $1,637 | $2,585 | $1,245 | 1.54 | B, MC-confirmed (t 5.4, checker PASS WITH CONCERNS); **personal (user 2026-11-03)**: book return/DD 9.0 -> 9.3. Before live: early-close flat + fill-latency check (1 min late halves it). `checks/candidates/bridge_noise_15m/NQ_Noise_RTH_Anchor.txt` (LongTrade only) |
| **FINRA short-volume longs (PENDING forward log, user 2026-11-08)** (long NQ the day after the Nasdaq off-exchange short-volume ratio is >= 1 sd above its 60-day mean; 08:31 -> 14:55, stop 0.5 ATR) | MNQ | $2,746 | $4,844 | n/a | n/a | C, MultiCharts-confirmed (373/374 trades, MC $668 per NQ, t 3.54); post hoc split, so it waits for WATCHLIST #32 (~6 months of new signal days, edge >= $300 a trade over every-day longs). **If it clears: 1 MNQ** (book median year $28.5k -> $31.0k, DD p95 $4.90k -> $5.17k, return/DD 5.81 -> 6.01; capital +$1.3k); 2 MNQ only adds money by needing capital. Half its money is 2025-26. `checks/candidates/finra_longs/NQ_FINRA_Short_Volume_Longs.txt` (dates embedded; refresh with `analysis/finra_mc_export.py`) |
| **ZT continuation, EntryZ 1.25 (IN, watched: WATCHLIST #36; user 2026-11-09)** (15-min NQ: ZT = (close − EMA32) / (close × sd(returns, 32) × √32); flat and ZT ≥ 1.25 → long next bar, ≤ −1.25 short; out when \|ZT\| ≤ 0.25 or 8 bars or a bar closes after 14:45; entries 08:35-14:45 CT) | MNQ | $1,574 | $2,248 | $1,732 | 1.07 | C, post hoc (threshold plateau 1.05-1.30, t 3.50); same engine as Twin (corr 0.41 with the book; earns on Twin-active days). Book at 1 MNQ: median year $26.3k → $27.7k, DD p95 $4.86k → $5.05k, return/DD 5.42 → 5.48 (2018-22 +0.11, 2023+ +0.12). **1 MNQ, no more.** User's paste with EntryZ 1.25, SignalMode 1, UseTimeFilter true, StartTime 835, EndTime 1445 (StopZ / MaxHoldingBars 8 / ExitZ 0.25 as is); **MultiCharts-confirmed 2026-11-09 (604 / 604 identical; report in mc_reports/)**; Python trades `checks/candidates/zt_continuation/python_trades_z125.csv`. Out if WATCHLIST #36 fails |

## Whole portfolio, every piece at 1 micro (19 pieces since 2026-10-25: Swing Target and PAPERTREND in, BB_MRM out)
- **$41,500 a year**, every year positive.
- Sharpe 3.15, Sortino 6.88, PF 1.90, Calmar 6.3, Ulcer 0.90; max DD $6,592; worst month −$2,739; 13% losing months.
- Monte Carlo, 1 year: p5 $22,800 / p50 $40,500 / p95 $61,100; P(losing year) 0.0%; max DD p50 $4,490 / p95 $7,280;
  return / DD 9.0.
- **Needs about $36,400** to keep the 1-year p95 drawdown at 20% of the account.
- **PAPERTREND's effect (18 → 19 pieces, user 2026-10-25, `analysis/papertrend_personal18.py`):** +$2,450 a year, Sharpe 3.12 → 3.15,
  return/DD 8.5 → 9.0, capital $34.4k → $36.4k; corr with the book +0.31 (Swing Target +0.12, Dual Thrust +0.18). In place of
  Dual Thrust 8.3, of Swing Target 8.75: an addition, not a swap.
- **Swing Target's effect (17 → 18 pieces, user 2026-10-25):** +$1,900 a year, Sharpe 3.04 → 3.12, return/DD 8.3 → 8.5, max DD
  $5,903 → $6,256, capital $33.6k → $34.4k (MultiCharts trades; Codex's ledger gave 8.6). Corr with the rest +0.20 but it loses
  on the book's bad days (Codex): return, not protection.
- **BB_MRM removed (user, 2026-10-25), forward log only.** It went in the same morning on the Python rebuild (t 3.4, +$900 a year,
  return/DD 8.3 → 8.7). The MultiCharts report 2018-26 (user's run, Exchange clock) showed the rebuild overstated it: 1,657 trades vs
  1,704, the rebuild's 49 extra trades were mostly winners (+$13.9k gross per NQ). On the real trade list: $40.6 a trade per NQ net,
  PF 1.17, t 2.5 (below the 3.58 bar), 2023+ t 1.2 carried by 2026 alone (2024 −$11.0k, 2025 −$4.8k, 2026 +$41.1k per NQ), max DD
  $32.7k per NQ, 5/9 years up, and fragile to the band settings. Back in only if the forward log clears its checkpoint (TIER_LIST C).
- **Overnight Tick at 2 MNQ in the personal account (user, 2026-11-08):** book 1-year MC (to 2026-07-07) median $26.0k -> $28.2k,
  p5 $14.0k -> $15.4k, DD p95 $4.82k -> $4.93k, return/DD 5.39 -> 5.72 (2023+ 6.65 -> 6.96); OT's daily corr with the rest 0.06.
  OT alone at 2 MNQ: 1-year DD p95 $2.6k, worst night about -$1,758 (the largest single-night risk in the book). The ladder rows
  below are still at 1 micro each (re-run `analysis/personal_ladder.py` before the account opens). `analysis/outputs/noise_calm_test_output.txt`.
- Overnight Tick / VIX in place of Overnight Anomaly (user, 2026-10-24): 17 pieces $36.6k → $37.1k a year, Sharpe 2.96 → 3.04,
  return/DD 7.7 → 8.3, capital $35.6k → $33.6k; core 16: Sharpe 3.17 → 3.24, return/DD 9.2 → 9.6 (`analysis/overnight_tick_bench.py`).
- S30's effect (16 → 17 pieces, user 2026-10-24): +$6,000 a year, but Sharpe 3.17 → 2.96, return/DD 9.2 → 7.7, max DD
  $4,590 → $6,182, capital $26.2k → $35.6k: more money, less per unit of risk. Below ~$35.6k run the 16 without S30.
- Kusho v9 + S47 v2's effect (14 → 16 pieces, user 2026-10-24): +$6,300 a year, Sharpe 3.00 → 3.17, return/DD 8.2 → 9.2,
  max DD $5,001 → $4,590, capital $25.0k → $26.2k (`analysis/forward_log_plans_test.py`). Both stay on the forward log;
  Kusho's overnight / weekend holds are booked on the exit day (not marked daily), so its drawdown may be understated.
- Dual Thrust's effect (13 → 14 pieces, user 2026-10-24): +$2,400 a year, Sharpe 2.97 → 3.00, return/DD 7.8 → 8.2, max DD
  $4,331 → $5,001, capital $23.0k → $25.0k (corr +0.33 with the rest: it trades the same RTH hours as VB / RS / FC 2B).
- (History) Overnight Anomaly's effect (12 → 13 pieces), replaced 2026-10-24: +$1,700 a year, max DD $4,663 → $4,331, Sharpe 2.84 → 2.97, capital
  $23.4k → $23.0k. It barely moves with the rest (corr +0.02), so it adds profit without adding drawdown.

## Growing into it (capital at the 20% rule; rebuilt 2026-10-31 on the 19-piece book)
`analysis/personal_ladder.py` (output `analysis/outputs/personal_ladder_output.txt`): greedy, each step adds the piece that keeps
1-year MC median $ / DD p95 highest; capital = DD p95 / 0.20. Cleared pieces first; the four forward-log pieces only once they
clear. (Codex audit 2026-10-31: the old table's '16-piece core' predated Swing Target and PAPERTREND, and its rows were not
re-ranked.) ret/DD here = median year / DD p95 (stricter than the old median / median-DD figure: the full book is 5.6 here, 9.0 there).

| Account | Set (1 micro each) | $ a year (MC p50) | Bad year (p5) | DD p95 | ret/DD |
|---|---|---|---|---|---|
| ~$10,200 | **1**: Overnight Tick / VIX + Twin Continuation | $5,600 | $1,900 | $2,040 | 2.75 |
| ~$10,900 | **2**: 1 + ONB ML + Late-Day Flow | $8,800 | $3,800 | $2,190 | 4.01 |
| ~$12,600 | **3**: 2 + Dual Thrust + Bridge Monday | $12,500 | $6,500 | $2,520 | 4.95 |
| ~$13,300 | **4**: 3 + Swing Target, CL Sunday fade, EOS, NFP fade, ES MOC (11 pieces) | $16,300 | $9,000 | $2,640 | 6.18 |
| ~$14,900 | **5 (best ratio)**: 4 + PAPERTREND (12 pieces) | $18,700 | $10,200 | $2,980 | 6.29 |
| ~$16,600 | 5 + Monday Long (13) | $20,800 | $11,400 | $3,320 | 6.27 |
| ~$18,900 | + Vault Break (14) | $22,500 | $12,400 | $3,780 | 5.94 |
| ~$24,300 | **All 15 cleared pieces** (+ Relative Strength) | $26,300 | $14,300 | $4,860 | 5.42 |
| ~$25,200 | + Kusho v9 once its forward log clears (16) | $29,800 | $16,200 | $5,040 | 5.91 |
| ~$26,600 | + S47 v2 once cleared (17) | $32,700 | $17,600 | $5,310 | 6.16 |
| ~$28,800 | + FC 2B v2 once cleared (18) | $35,000 | $19,100 | $5,770 | 6.07 |
| ~$36,100 | + S30 IBS once cleared (19 = full book) | $40,500 | $22,600 | $7,220 | 5.61 |

**From ~$31k up: capped inverse-vol weights (adopted by the user 2026-11-01).** Micros per piece = weight x size, weight =
1 / 2018-25 daily stdev, capped at 2x equal, rounded to whole micros; re-estimate the weights each January. Exact generator:
`analysis/personal_invvol_ladder.py` (output `analysis/outputs/personal_invvol_ladder_output.txt`). The micros column is the
forward DEPLOY vector (2018-25 weights, on purpose). The $ / DD columns are the CAUSAL yearly walk-forward on 2023+ (each year
sized from earlier years only); corrected 2026-11-01 (Codex review #7): the first version showed the 2018-25 vector scored on
2023+, whose weights had seen 2023-25 (in-sample sizing; up to +4% on the big rows). 2023+ was already seen when the method,
cap and sizes were chosen: not an untouched holdout. Forward-log pieces join only once cleared.

| Account | Book | $ a year (MC p50, 2023+) | DD p95 | Micros per piece |
|---|---|---|---|---|
| ~$31k | 15 cleared, ~2 a piece | $48,200 | $6,270 | VB 1, ONB ML 1, Monday 1, EOS 3, LDF 2, NFP 4, Bridge 2, CL fade 4 MCL, ES MOC 4 MES, RS 1, Twin 1, OT 2, DT 1, ST 1, PT 1 |
| ~$43k | full 19, ~2 a piece | $65,300 | $8,580 | as above but VB 2, ONB 2, EOS 4, LDF 3, ST 2; + FC 2B 1, Kusho 1, S47 1 (S30 0) |
| ~$63k | 15 cleared, ~4 a piece | $94,400 | $12,600 | VB 3, ONB 3, Monday 2, EOS 6, LDF 5, NFP 8, Bridge 4, CL 8, ES MOC 8, RS 1, Twin 2, OT 3, DT 2, ST 3, PT 2 |
| ~$83k | full 19, ~4 a piece | $140,300 | $16,600 | VB 4, ONB 3, Monday 3, EOS 7, LDF 6, NFP 8, Bridge 5, CL 8, ES MOC 8, RS 2, Twin 2, OT 4, DT 3, ST 4, PT 3, FC 2B 3, Kusho 2, S47 2, S30 1 |
| ~$206k | full 19, ~10 a piece | $346,500 | $41,130 | VB 9, ONB 8, Monday 7, EOS 18, LDF 15, NFP 20, Bridge 12, CL 20, ES MOC 20, RS 4, Twin 6, OT 9, DT 7, ST 9, PT 7, FC 2B 7, Kusho 5, S47 6, S30 2 |

Below ~$31k the table above (equal, 1 micro each) stands: rounding makes inverse vol useless at ~1 micro a piece. 10 MNQ
can be traded as 1 NQ (lower commissions). Re-run the ladder and the 'Capital-expansion bench' at each step.
**Reading it:** with ~$10-11k start at row 2 (4 pieces); ~$13.3k already carries 11 pieces, because the small pieces add profit
without adding drawdown. Monday Long, Vault Break and Relative Strength are the last cleared pieces in: in a personal book they
add money at lower return per risk (they overlap the RTH NQ pieces). Twin holds overnight with a wide stop (check overnight
margin). Add a row only at its line; drop back one after a 20% drawdown. Live expectation: >= 75% of these backtests.
**Holdout check (Codex 2026-10-31: the ladder picks and reports on the same history):** order chosen on 2018-22 only, scored on
2023+. Small rows are NOT stable: the 2018-22 pick shares only 2 of its first 4 pieces with the table (Twin comes 13th there),
and its 4-piece set made $8.3k at ret/DD 3.25 on 2023+ vs the table's set $12.4k / 5.58. From ~12 pieces it is stable (11 of 12
the same; 2023+ ret/DD 6.3 vs 7.0, capital line $16.6k vs $17.4k). The 2023+ capital lines run higher than the table: 12 pieces
~$15-17k (table $14.9k), all 15 cleared ~$29k (table $24.3k). **So: plan the personal start at the ~12-piece row with ~$15-17k;
rows below 12 pieces are history-fitted guesses, not tested sets.** Capital lines stay research estimates.
Old table (2026-10-24, 16-piece core, before Swing Target / PAPERTREND): in git history.

**Units:** every '$ a year' is the backtest at the sizes in its row; '1 micro' = 1 MNQ / MES / MCL per piece, so the core
at 1 micro is ~$2,500 a month and at 1 mini per piece ~$25,000 a month (not $300k a month), with drawdowns 10x as large.
**S30's weight (2026-10-24):** at full weight it lowers return per risk (Sharpe 3.17 -> 2.96); at a quarter to half of the
other pieces' size it raises it (quarter: Sharpe 3.21, return/DD 9.44), because it barely moves with them (corr +0.11).
So it runs at full weight only between ~$33.6k and ~$54.1k, then at half, then a quarter. **Minis** change costs only:
1 NQ ~$4-5 commission vs ~$10-12 for 10 MNQ (very roughly +3% at 1 NQ per piece); mix them freely (1 NQ + 3 MNQ = 13).
**Live expectation:** these are in-sample backtests; our rule expects live >= 75% of them (the 1-mini row ~$240k a year at
75%, ~$190k at 60%).


Pre-screen before sending a strategy: `DEVELOPMENT_PROCESS.md` "Pre-screen" (soft guide: Sharpe > ~3.15 x correlation with the book).

## Capital-expansion bench (user, 2026-10-24)
Strategies that add money only by needing more capital (lower return per unit of drawdown at the current size) go here,
not into the plan, for later when the account is large enough or sizes can be weighted finely (minis / many micros).
| Strategy | Tier | Effect when added | Why it waits | Source |
|---|---|---|---|---|
| Ricochet 1144 (long after a red day, S1 re-entries) | C | +$1,953 a year at 1 MNQ, return/DD 9.3 -> 9.1 | OOS t 1.93, signal adds little over overnight drift; DD $2.7k per MNQ | `analysis/outputs/ricochet_1144_test_output.txt`; skipped for now, last in line (user 2026-11-04) |
| S30 IBS reversal (NQ + ES) | B | +$6k a year, return/DD 9.6 → 8.3, capital +$7.4k | in the ladder only from ~$33.6k, at reduced weight above ~$54k | `analysis/forward_log_plans_test.py` |
| FVB First Valid Breakout (whole rule) | B | +$3.8k a year, Sharpe 3.04 → 3.01, return/DD 8.3 → 8.2, capital +$3.9k (shorts only: return/DD 8.9, but a post-hoc split) | fat tail, longs weak (PF 1.13) | `analysis/fvb_bench.py` |
| Swing Target v3, 2nd MNQ | B | 1 → 2 MNQ: +$2.2k a year, return/DD 8.6 → 8.3, capital +$1.8k (Codex ledger) | the 2nd contract lowers return per drawdown; it also loses on the book's bad days | `analysis/swing_target_bench.py` personal |
| Swing Target v3, 2nd MNQ on the SHORTS only (2026-11-08) | B | median year +$1.3k ($28.5k -> $29.9k), return/DD 5.77 -> 5.63, capital +$1.8k ($24.7k -> $26.5k); better than a 2nd MNQ on both sides (5.52, +$3.0k capital) | the shorts earn 3x the longs ($486 vs $168 a trade), but the extra contract still lowers return per drawdown | `analysis/st_short_size_test.py` |
| Prior VWAP Trap (NQ) | B | +$3.0k a year, Sharpe 3.15 → 3.10, return/DD 9.0 → 8.6, capital +$3.5k; in place of Dual Thrust / Swing Target worse | placebo levels as good (momentum + trailing stop); every Apex bench worse | `analysis/prior_vwap_trap_bench.py` personal |
| RollZone 24h NQ Long (plain-stop version; note's $150-budget version weaker) | C | +$4.9k a year, Sharpe 3.15 → 2.95, return/DD 9.0 → 7.5, capital +$12.5k (note's version +$2.6k, 9.0 → 8.7, +$5.1k); in place of Overnight Tick / Dual Thrust worse | regime-bound (edge 2023+), corr +0.44 with the book; every Apex bench worse | `analysis/rollzone_bench.py` personal |
| Futures trend (QuantJourney example 25: 6-market SMA 63/252 trend, inverse-vol, monthly) | C (not tested by us) | their run 2019-26: CAGR 5.9%, Sharpe 0.62, max DD -9.7%, beta 0.04 | multi-day (personal only), low Sharpe, needs ~$150k+ (one contract per market); test with proper rolls at that ladder row | `checks/candidates/futures_trend/README.md` |
| S03 Noise Area v2 | B | personal gains need more capital (Codex); Apex plans worse | thinned since mid-2024 | `agents/codex/results/s03_v2.md` (codex/work) |
| Anson momentum (4.5 / 20) | D | full + 1 MNQ: median year $23.7k → $25.6k, p95 DD $5.0k → $6.1k, capital $25.0k → $30.4k | weak standalone (2025+ t 0.97) | `agents/codex/results/anson_personal.md` |
| R2Vault | C | personal CT gains small at equal drawdown | weak standalone (t 2.9, DSR 0.5) | `agents/codex/results/r2vault.md` |
| DriftPullBack (user's simplified v3 of DriftPullback v2.1) | C | + all: +$2.9k a year, return/DD 8.3 → 8.0, capital $33.6k → $38.8k; shorts only 8.3 → 8.5 (+$1k) but shorts earn $9 a trade since 2023 | funded: blow-ups 3% → 13% (v2.1, 10/13) | `analysis/drift_pullback_v3_test.py` |
Review this list whenever the account steps up a ladder row: re-test each at that size before adding.

**Retest vs the current book (2026-11-08, `analysis/capex_retest.py`, OT 2 MNQ; base median $28.5k, DD p95 $4.9k, return/DD 5.81):** no
piece improves return/DD in BOTH periods, so all stay here. 2018-26 (median / DD / return/DD / capital): Ricochet 1144 +$2.0k / +$0.2k /
5.93 (+0.13; 2018-22 -0.26, 2023+ +0.32; trades carry commission only) / +$1.2k; Swing Target 2nd both sides +$2.0k / 5.67 / +$2.4k;
FVB +$4.2k / 5.66 / +$4.4k; ST 2nd shorts only +$1.3k / 5.66 / +$1.8k (2018-22 +0.18); S30 +$5.5k / 5.39 / +$7.0k (2023+ +0.09);
RollZone +$4.6k / 5.31 / +$6.7k; Prior VWAP Trap +$3.0k / 5.29 / +$5.2k; DriftPullBack v3 +$3.1k / 5.07 / +$6.6k. **Median $ per $ of
extra capital (add order when capital grows):** Ricochet 1.7, FVB 1.0, ST both 0.9, S30 0.8, ST shorts 0.7, RollZone 0.7, PVT 0.6,
DP 0.5. **Ricochet plateau check (2026-11-09, `analysis/ricochet_plateau_test.py`): 6 of 7 neighbouring settings raise the book overall (+0.07 to
+0.43), but none fixes 2018-22 beyond noise (stop 60: +0.02): robust but recent-weighted; first in the add order. **User 2026-11-09: the bench version is now TARGET 80** (better than target 100 in every period: 2018-26 6.24 vs 5.93, 2018-22 5.64 vs 5.52,
2023+ 6.97 vs 6.86 with OT 2; max DD $16.9k vs $26.8k per NQ; chosen among 7 neighbours, so post hoc: still a bench piece, re-test at the next capital step).** **Book test of four leads (2026-11-08, `analysis/bench_leads_book_test.py`): S30 NQ with entry IBS < 0.10 improves the book in BOTH
periods (5.81 -> 6.61; 2018-22 +0.16, 2023+ +1.30; +$4.3k a year at +$58 DD) -> WATCHLIST #34 (forward log; ES leg tested 11/08: replicates alone but duplicates NQ, corr 0.80 -> NQ only). FVB shorts only
6.12 (+0.31, but 2018-22 -0.23; capital +$1.2k): replaces FVB both sides on this bench. S03 longs 5.77, Anson longs 5.49: stay.** DP 0.5. Added the same day from Codex's ledgers: R2Vault +$1.8k / 5.62 (-0.19) / +$2.4k (0.7 $ per $ of capital); S03 v2 +$2.9k / 5.46 (-0.35;
2018-22 +0.05) / +$4.2k (0.7); Anson +$2.1k / 5.17 (-0.64, worse in both periods) / +$5.0k (0.4). Futures trend: never built, not retested.

## Read this before trusting the numbers
- **These are backtests on the years the strategies were chosen on.** Expect live results lower; our rule is live ≥ 75%
  of the backtest (`DEVELOPMENT_PROCESS.md`). At 60% of the backtest the full portfolio is ~$13k a year at 1 micro.
- **FC 2B is not cleared yet:** forward log until 40-80 signals. Without it the full set is ~$19.6k a year.
- **Twin Continuation holds overnight with a wide swing stop** (worst trade −$1,172 per MNQ); needs overnight margin
  (check the broker). Without Twin the full set is $18.3k a year, DD p95 $4.4k. Since 2026-10-24 its overnight holds are
  marked at each 16:00 CT close instead of booked at exit (cross-review item): no material change (max DD $4,663, MC p95
  DD $4,687, capital $23.4k, all as before; only 50 of 1,074 trades hold overnight).
- **Overnight Tick / VIX holds 17:05 → 03:00 CT with no stop** (A, MultiCharts-confirmed; replaced Overnight Anomaly, C, on
  2026-10-24). Code: `funded_strategies/NQ_Overnight_Tick_VIX.txt` (5-min MNQ, VIX daily as Data2: `C:\TradingData\VIX\VIX_daily.csv`
  via Map ASCII, refreshed daily by `tools/vix_update.ps1`; if the day's VIX is missing it uses the previous day's, which
  earned $309 vs $374 per NQ). Its backtest ends 2026-07-07 (order-flow data); the 24 MultiCharts trades after that
  averaged −$280 per NQ (watch).
- RS and FC 2B overlap (both enter at 09:01 in the opening drive's direction, corr +0.36): they can lose together.
- When to start (`DEVELOPMENT_PROCESS.md` lifecycle): from Apex payouts, after the live record matches the backtest
  (early start from ~month 3 at small size if ≥ 100 live trades, live ≥ 75% of backtest, no drift alarm).
- Not included (too weak or untested): Gold Breakout (C), plain every-night overnight long, turn of month, trend portfolio, the untested
  ideas in `IDEAS.md` (all-weather ETFs, Weekend Trend Trader, Davey's ES Keltner).

## Conservative / current / aggressive versions (user, 2026-10-25; `analysis/personal_variants.py`)
| Version | Pieces / micros | $ a year | Sharpe | Max DD | MC DD p95 | Return/DD | Capital (DD p95 / 0.2) |
|---|---|---|---|---|---|---|---|
| Conservative: proven pieces only (no forward-log pieces S30, Kusho, S47, FC 2B; Dual Thrust kept out here; Swing Target and PAPERTREND in) | 14 / 14 | $24.4k | 3.20 | $5.4k | $4.6k | 9.0 | ~$23k |
| Current (Swing Target, PAPERTREND in, BB_MRM out, 2026-10-25) | 19 / 19 | $41.5k | 3.15 | $6.6k | $7.3k | 9.0 | ~$36k |
| Aggressive: 2 micros on the five pieces with Sharpe >= 1.4 (Twin, Overnight Tick, Kusho, Overnight Bias ML, Dual Thrust) | 19 / 24 | $55.8k | 3.29 | $7.3k | $8.3k | 10.0 | ~$41k |
**User 2026-10-25: Swing Target stays at 1 MNQ; plans to switch to the aggressive version eventually.** Keep the aggressive row current whenever the book changes, and before the switch re-check its five 2-micro pieces on live and forward-log results, not only backtest Sharpe.
The aggressive weights pick pieces by their backtest Sharpe, so part of its edge over 'current' is hindsight; two of the five
(Kusho, Dual Thrust) are not live-proven yet. Pieces promote from conservative to current as they clear the forward log.

## Inverse-volatility weights (tested 2026-11-01, `analysis/personal_invvol_test.py`; awaiting the user's decision)
Weights set on 2018-22 (w ~ 1 / daily stdev per micro), scored on 2023+ (never seen), same total micros, whole micros.
15 cleared pieces: ret/DD 6.10 (equal) -> 6.53 at ~1 micro a piece (drops Relative Strength and Twin), 7.32 at 2, 7.46 at
4+; Sharpe 3.58 -> 3.76-3.99; capital for the same micros $57.6k -> $32.0k at 2 a piece. Full 19: 6.69 -> 7.74 (2) /
8.50 (4+). Per $ of capital, inverse-vol at ~$32k earns ~20% more than the equal book at ~$29k. It shrinks the high-vol
pieces (S30 0.18x, Relative Strength 0.34-0.39x, Twin, Kusho ~0.45x) and grows the quiet ones (ES MOC 2.5-2.9x, NFP fade,
CL fade, EOS ~1.5-2x), so the book leans harder on smaller, weaker-per-trade pieces (ES MOC is on the watchlist, #20).
Rounding makes it useless at ~1 micro a piece; it only works from ~2 micros a piece (the ~$31k+ rows).
**Confirmation (2026-11-01, `analysis/personal_invvol_confirm.py`):** weights re-estimated every year from earlier years only
(walk-forward 2020-26) and capped at 2x equal. 15 cleared, ~2 micros a piece: ret/DD 2020-26 6.54 (equal) -> 7.82
(inv-vol) -> 8.12 (capped); 2023+ 6.10 -> 7.33 -> 7.69; capital ~$57.6k -> ~$31.4k for the same micros. ~4 a piece: 6.54 ->
8.26 / 8.50. Full 19: 6.71 -> 8.27 / 8.60 at ~2; at ~4 the cap costs a little (8.99 -> 8.45 on 2023+) but stays well above
equal. The gain survives yearly re-estimation; the 2x cap costs nothing on the cleared book. Proposed: capped inverse-vol
from the ~$31k row up (cleared book), equal weights below; ADOPTED by the user 2026-11-01 (ladder rows above).

## Idle cash idea (saved 2026-11-08, user): JPMorgan Efficiente 5 replication

For personal-account cash the futures pieces don't use (margin needs only a fraction of the account): a monthly 13-ETF
mean-variance allocation (6-month lookback, 5% target vol, caps per asset / class), open-source Python replication
(Jungle Rock Capital 2025, SSRN 7633178, `../papers/ssrn-7633178.pdf`). Replication 2008-25: +3.5% a year over cash, vol 6%,
Sharpe 0.58, max DD -19%, turnover 42% a month. An investing choice, not a trading piece (TIER_LIST F as a strategy).
Before using: rerun the open-source code on fresh data, compare with a simple 60/40 or T-bills after costs and taxes, and
check margin rules (ETFs held as collateral vs cash).

## Candidates from the 2026-11-08 'new sources' test (`../analysis/new_sources_personal.py`; not added yet, user decides)

Personal book (cleared pieces, 1 micro each) return/DD 5.42 (2018-22 5.45, 2023+ 6.10). Adding at 1 micro:
- **Turn of the month** (long NQ 08:30 -> 15:00 on the last trading day of a month and the first 3 of the next, stop 0.5 x ATR):
  6.01 (+0.59), better in both periods (+0.17 / +0.80), +$1.7k a year, DD p95 $4,857 -> $4,665. Per NQ $372 a trade, t 2.5 (427 trades).
  **Checker 2026-11-08 (checks/candidates/turn_of_month/): FAIL 6/8** (t 2.53 below the multiple-testing bar; without its best 5% of
  trades -$33 a trade; 2018-22 t 1.2). Not added; forward log only.
- **Vol-Control Sell Flow** (MC trades, in the funded plan until October): 5.50 (+0.08), better in both periods; small.
  **Checker 2026-11-08: FAIL 7/8, only significance** (t 2.14 on 71 trades; placebo p 0.005, concentration PASS). Closest to clearing;
  forward log, recheck as trades accumulate (~9 a year).
- Not: double top / bottom (+0.53 overall but -0.09 in 2018-22), long after a green day full rule (-0.54), gold Asian range (-0.73).
