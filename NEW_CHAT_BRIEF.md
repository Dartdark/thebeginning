# New-chat brief (updated 2026-10-17): read this first

Paste this into a new chat: *"Read `NEW_CHAT_BRIEF.md`, then `CLAUDE.md`, in github.com/Dartdark/thebeginning (branch
`claude/nq-trading-strategy-params-5h9d20`) and continue from there."*

## Who / what

- Algo trader running MultiCharts (PowerLanguage) on **Apex 50K** accounts via **Rithmic** (data dxFeed). Apex only
  (ignore Topstep). Flat by 15:59 CT; $2,000 end-of-day trailing drawdown (locks at $50,100); combine: $3,000 target,
  $1,000 daily loss limit.
- Goal: **funded payouts** (6 payouts = $13,000 per account), reached as fast as possible.
- **Business plan (2026-10-16): `reports/Trading_Business_Plan.pdf`** (rebuild: `python3 reports/build_business_plan.py`): account
  choice (test on single 50K EOD $59 -- 5-pack evals all start at purchase, so they'd share one outcome; scale with 150K no-activation), projections, roadmap, risks, settings per account type.
- Long-term path (user, 2026-10-15): Apex = live test bench and funding source; proven strategies and Apex payouts move to a
  personal account (`DEVELOPMENT_PROCESS.md` 'Strategy lifecycle').
- **The plan, in priority order (agreed 2026-10-16; full version `reports/Trading_Business_Plan.pdf`):**
  1. **Prove the edge live:** #1 50K EOD (since 10/12), #2 50K EOD Tue 10/20 ($59 single; 5-pack evals all start at purchase),
     #3 **150K No-Activation** ~10/27 ($249, tests the 150K settings / copier master early). Gate ~mid-December: ~40–70 live
     trades at ≥ 75% of backtest, no ALARM.
  2. **Scale Apex:** ~$20k set aside for evaluation fees; +2 x 150K No-Activation a week to 20; 50K slots keep cycling until
     their first funded account pays all 6 ($13,000) or blows, then switch to 150K; pause adding if cumulative cash < −$20k.
     Sim (`analysis/ramp150_test.py`): year 1 ~$175k, 3 years ~$1.03M (75% edge: ~$96k / $743k, bad case −$33k).
  3. **Personal account from the first Apex payouts** (expected ~mid/late Feb 2027), ~$10k at 1/10 size, not from savings;
     full 1-NQ size needs ~$100k (DD $24k); add Twin there (stop cap 1 ATR).
- Preferences: forced / scheduled flows (they work here; price patterns fail), low correlation, longs and shorts
  analysed separately. Always give **direct GitHub links + raw links** for code to paste into MultiCharts.
- Working rules, testing standard and branch rules are in `CLAUDE.md` (push every commit to
  `claude/nq-trading-strategy-params-5h9d20`, `claude/quirky-noether-4dla64` and the session's own branch).

## Latest (2026-10-17)

- **Account #1 (50K EOD evaluation): about +$1,500, $1,500 left to the $3,000 target.** The user entered the ONB trade
  manually after a rejection and closed it at +$1,500 (agreed afterwards: **no early exits, no re-entries** -- the Apex
  evaluation has no consistency rule; capping days at $1,500 cuts pass rate 50.1% → 45.3%, `analysis/profit_cap_test.py`).
- **Finish line:** `apex_strategies/Apex_Target_Guard.txt` (exit-only signal added next to each strategy on its chart;
  `StartBalance` = Apex balance before the session, `TargetBalance` 53050). Not yet compiled by the user; confirm it compiles
  and is on the VB, ONB and Bridge Monday charts before Monday. After the pass: auto-trading off on that account.
- Still waiting on the user: test order confirming real Rithmic fills (Sunday 17:00 CT), EOS stop-guard paste, weekly
  live reports into `live/`.
- **Research this week:** forced flows round 5 (`analysis/forced_flows_round5_test.py`): ES stocks-vs-bonds month-end
  rebalancing D (t 1.2), gold first-notice-day short F, CL holiday-reopen fade too rare. **Monte Carlo**
  (`analysis/montecarlo.py`, `MC.report(trades, daily, size=...)`) is now part of the testing standard (CLAUDE.md,
  DEVELOPMENT_PROCESS.md); CL Sunday fade at 2 MCL: P(losing year) 14%, P(hit $2,000 trailing) 0%.
- **Other AIs (user asked):** idea = a second, different-lab model (OpenAI reasoning model; Gemini runner-up, e.g. via
  Google Antigravity) as an extra blind checker of strategy specs in `checks/candidates/`. Needs an `OPENAI_API_KEY`
  in the environment's Network secrets (never pasted in chat). Not set up yet.
- **Next ideas:** run Monte Carlo on every strategy in the plan at plan size; more forced-flow candidates on ES / GC / CL;
  apply the stop-rejection guard to every strategy using SetStopLoss (offered, not done).

## Live status (2026-10-14)

- **2026-10-16 finding: nothing had traded on the Apex account yet.** The 10/12 fills were on Paper Trader (SIM 001); every
  Rithmic order (ONB 10/14, EOS 10/16 stops, a manual test) was rejected because Symbol Mapping sent `@MNQ` to Rithmic. Fixed:
  `@MNQ (dxFeed) -> MNQZ6`. Live start = first real Apex fill; confirm with a test order Sunday 17:00 CT before Bridge Monday
  (19:00 CT). Roll the mapping to MNQH7 ~Dec 11. Add account #2 only after a real fill. EOS got a stop guard (paste new code).
- **1 combine account live since Monday 2026-10-12** (user corrected 2026-10-15: running one account first as a shakedown
  week for errors / screen sleep; 2 of 2 trades so far). Plan: add accounts one at a time, 5–10 trading days apart.
  Next: EOS trades Fri 10/16 and Bridge Monday Sun 10/18 19:00 CT on account #1 (first live runs of both); if clean,
  **add account #2 Tue 10/20** (50K EOD), #3 about a week later (150K No-Activation). First live days:
  - **Monday 10/12:** a winning trade was missed because the connection dropped.
  - **Tuesday 10/14:** the Overnight Bias short (5 MNQ) was rejected by Rithmic: *"Invalid StopMarket order
    parameters"*, a sell stop placed above the market.
    - **Fixed:** all Overnight Bias versions now enter at market when price is already at / through the
      opening-range level (`EntryBufTicks` 2). The new order names are "ON Bias LM / SM".
    - **User must paste and compile the new code before the next open.**
  - Pass odds per account unchanged (~50%).
- **Evaluation finish line (2026-10-16):** `apex_strategies/Apex_Target_Guard.txt`, an exit-only signal added next to each
  strategy on its chart; set `StartBalance` (the Apex balance) before the session, `TargetBalance` 53050; it closes the
  position by limit when the account would reach the target. No consistency rule in the Apex evaluation and no early exits
  otherwise (`analysis/profit_cap_test.py`).
- **All strategy files were audited:** every other entry is a market order; order names are unique per file.
- **Combine set** (`apex_strategies/`, MNQ, 24-hour session, Exchange time CT):

  | Strategy | File | Chart | Live inputs |
  |---|---|---|---|
  | Vault Break | `NQ_Vault_Break.txt` | 30 min | `NumContracts` 8 |
  | Overnight Bias ADX30 | `NQ_Overnight_Bias_ADX30.txt` | 15 min | `RiskPerTrade` 1100, `NumContracts` 1, `ADXMin` 30, `StopAtrPct` 0.25, `ExitTime` 1430, `EarlyExitTime` 1130 |
  | Bridge Monday Long (ships with The Bridge, not in repo) | — | as shipped | 2 MNQ; enters Sunday 19:00 CT |
  | Expiration Open Short | `funded_strategies/NQ_Expiration_Open_Short.txt` | 5 min | `RiskPerTrade` 500; next trade **Fri 2026-10-16** (3rd Friday) |

  Backtest: pass 50.1% per try, median 6 trading days; combine sizing barely matters (`analysis/pipeline_tuning_test.py`).
  2026-10-15: state sizing / daily stops don't help (`analysis/combine_levers_test.py`); optional swap ONB ADX30 → ONB ML
  $1,100 = 52.0% (`analysis/combine_swap_test.py`). **Stagger new combines 5–10 trading days apart**: same-day combines on one
  copier share one outcome (correlation +1.0; 10 days apart +0.19). See FUNDED_PLAN.md 'Combine levers and staggering'.
- **Live tracking:** the user exports weekly MultiCharts reports into `live/`.
  - Run `python3 analysis/live_vs_backtest.py --all live/` (see `live/README.md`).
  - It now also prints a CUSUM **drift alarm** per strategy (OK / WATCH / ALARM = half size and review; `live/README.md`).
  - Count technical misses separately from the edge.
  - Scale beyond 3 slots only when the live edge is ≥ ~75% of backtest (×1.25 sizing only at ≥ 90%).

## Funded plan (when an account passes; `funded_strategies/FUNDED_PLAN.md`, roster in `funded_strategies/README.md`)

| Strategy | Chart | Inputs |
|---|---|---|
| Vault Break (`NQ_Vault_Break_SP.txt`) | 30 min MNQ | 3 MNQ, `FlaggedContracts` 1 |
| Overnight Bias ML v2 (`NQ_Overnight_Bias_ML.txt`) | 15 min MNQ | `RiskPerTrade` 400 |
| Monday Long | 5 min MNQ | 1 MNQ |
| Expiration Open Short | 5 min MNQ | `RiskPerTrade` 700 |
| Late-Day Flow | 5 min MNQ | 2 MNQ |
| NFP Fade | 5 min MNQ | `RiskPerTrade` 500 |
| Bridge Monday Long | as shipped | 1 MNQ |
| **CL Sunday Gap Fade** (new, `CL_Sunday_Gap_Fade.txt`) | 5 min **MCL**, Eastern exchange time | `NumContracts` 2, `ExitTime` 1000 (= 9:00 CT) |

- **Cushion sizing:** f = cushion / ref, kept in 0.5–1.
  - **Funded phase: full size from a $1,500 cushion (user's decision, 2026-10-14).** The $1,000 setting blows 17–18%
    of accounts in the bench vs 2–4% at $1,500; it only looked better counting blown accounts as cheap restarts.
  - The funded bench numbers below use ref $1,500.
- **Backtest per account** (bench, ref $1,500):
  - $9,818 in year 1, $12,595 in 2 years, blown 4% / 2%.
  - Median 239 trading days to all 6 payouts.
  - About $800 a month net per slot over the challenge → funded → next-challenge pipeline.
- **To do before the CL strategy goes live:** confirm Apex allows MCL on the account.

## Research state

- **Current goal (`S_RANK_PROGRAM.md`): one S-rank strategy per symbol.**

  | Symbol | Best | Tier |
  |---|---|---|
  | NQ | Overnight Bias ML v2 | S |
  | CL | Sunday up-gap fade, MultiCharts-confirmed (96/97 trades): $653 per CL, PF 3.02, t 3.2, 9/9 years | A, in the funded plan |
  | ES | MOC auction follow | B |
  | YM | MOC follow, post-settlement fade | C |
  | GC | Asian-range breakout; still hurts the funded bench | C, parked |
  | BTC | Nothing; CME bitcoin trades 24/7 since 2026-05-29, so the weekend gap is gone | D/F |

- **Done today:**
  - Covered-call ETF rolls: the only effect is EOS, which is already in the plan.
  - Forced-flow round 4: MOC auction follow C (watchlist #10); quarterly rebalance closes and Tokyo / London opens F.
  - S-rank rounds 1–2 on ES / YM / GC / CL / BTC.
  - The user's CL forced-flow chat: Platts window, EIA sweep fade and round numbers F; USO roll short D.
  - Gold / BTC FOMC: D.
- **Gold vs rates / dollar** (ZN + 6E now in `data/`, 2017-12 → 2026-10): F (`analysis/gold_rates_dollar_test.py`).
  - Treasury-auction price pressure paper (NY Fed SR 1188) on ZN / GC / 6E: D (pre-auction ZN fall real, +$15 gross t 2.3, vs $38.50 cost;
    `analysis/treasury_auction_test.py`).
  - Overnight-Intraday Reversal Everywhere (SSRN 2730304), cross-sectional on the 7 markets: F (gross negative on a
    synchronised clock; `analysis/co_oc_reversal_test.py`).
  - A Tale of One Day (SSRN 4192163), morning momentum / afternoon reversal on NQ / ES / YM: F
    (`analysis/morning_afternoon_test.py`).
  - Maroy 2025 exits (SSRN 5095349) on Vault Break: the VWAP exit looked better in Python but **MultiCharts did not
    confirm** (target on $4,947 / yr, Sharpe 1.29; off $5,849, 1.00; live VB $5,341, 1.35): D. Live VB unchanged.
  - Mesfin 2026 MNQ falsification study (SSRN 6709401): F; its London Signal B only works with a look-ahead entry
    (`analysis/london_signal_b_test.py`).
  - Mega-cap earnings on NQ (Alpha Vantage data in `data/ndx_megacap_earnings.csv`; the user's API key is NOT stored):
    pre-specified rules no edge; 'sell the news' short D (all from 2024–25); intraday shape F.
  - CL round 3 (Friday, Monday after the fade, overnight, London open): F. The Sunday up-gap fade stands alone.
  - Plan combination: Vault Break after an Overnight Bias ML long earns $214 vs $64 (t 2.55), but the funded bench says
    extra VB on those days lowers payouts and raises blow-ups at every size (+1 MNQ $9,519 vs $9,818; +2 blown 12%): D.
  - Quantpedia sentiment / overnight anomaly (SSRN 3829582): its filters backfire on OND (the overnight premium is larger
    after fear); neither version beats the funded plan: F.
  - ES mean reversion (six families + day-to-day fade): F on ES; ES reverts only slightly more than NQ and far below its
    $30 round trip; the day-to-day fade is stronger on NQ (t 2.2, 5/9 years: D).
  - The Bridge's exported indicators (order flow, gamma) scanned as filters on the plan: 1 pass in 63 (chance level), no bench
    gain: F (`analysis/bridge_filter_scan.py`; features cached in scratch `bridge_features.pkl`).
  - Gold Breakout 15M (user's TradingView strategy): real (t 3.1, beats a random side) but lowers the funded plan at 1 MGC: C.
  - Bridge indicators round 2 (user's code: depth, walls, other VWAP anchors, gamma fixed for the NDX → NQ basis): no filter
    beats the plan. GAMMA LEVELS ARE NDX POINTS: NQ level = level + basis. Earnings-day gamma rule on watchlist #15.
  - Single-print day filter (Red Ledger RL-FS-2026-01, `analysis/single_print_test.py`): replicates on our NQ 2018-26; VB earns
    $21 vs $123 a trade the session after an interior single print; funded VB 3 / 1 on flagged days $10,184 vs $9,818 (1 year),
    blown 3% vs 4%, beats all random-day placebos: B. MC-CONFIRMED (262 / 274 flagged days identical, no false skips);
    user to paste it over `NQ Vault Break` outside market hours. Combine: FlaggedContracts -1 (= old VB, no gain).
  - **USER PREFERENCE (2026-10-15): Twin Continuation is the profile the user wants -- a big edge that trades a lot. Keep it
    logged for future use (a personal / non-prop account, or a prop firm with a larger or static drawdown).** Look for more like it.
  - Twin-like search (2026-10-15): round 1 Twin is NQ-only (ES/GC/YM/CL fail); MO risk-sized doesn't fit. Round 2 MO with a
    tight 0.10-ATR stop: $374, PF 2.00, t 4.07, 9/9 yrs, but 29% win rate → losing streaks vs $2k trail: no Apex gain (B, not adopted).
    LESSON: for Apex look for HIGH win rate frequent edges (VB-like 66%), not trend-day capture.
    Round 3 high-win search: MO entry + T 0.10 / S 0.20 ATR = 75% win, t 4.13 (B) -- but adding ANY new risk to the funded plan
    raises blown (3% → 7%+): the plan's risk budget is full. Gains now need replacements, more accounts, or the combine.
  - Twin Continuation (user's MC code; `analysis/twin_continuation_*.py`, checker `checks/candidates/twin_continuation/verdict.md`):
    real edge (t 5.5, DSR 0.995, checker replica 99.8%, PASS WITH CONCERNS) but wrong shape for Apex (BO swing stops ~$6k/NQ,
    fat-tailed MO wins vs consistency): no gain in funded plan / own PA / combine. MC-CONFIRMED (v2 report: 1,069/1,074 entries identical, $296 t 5.3): A.
    Non-prop account idea; v2.1 in personal_strategies/ (holiday fix, SetExitOnClose removed).
  - Trials log + deflated Sharpe (`analysis/trials.py`, `TRIALS.csv`, `metrics.deflated_sharpe` / `t_threshold`): 193 items tested,
    bar |t| 3.47; plan DSR: ONB ML 0.99 passes, VB 0.92, Bridge Monday 0.91, LDF 0.79, Monday 0.73, EOS 0.42, NFP 0.16 (forced-flow
    items stand on the pre-registered rule; watch them live). New promotion rule in DEVELOPMENT_PROCESS.md.
  - The Bridge's 'Propfirms as a business' slides: 'bench strategies in drawdown' tested on our plan (`analysis/bench_in_dd_test.py`):
    no clustering, benching lowers the combine pass rate (50.1% → 41-48%): F. Don't bench on drawdown; the drift alarm covers a dead edge.
  - OU mean-reversion regime (user's post, `analysis/ou_regime_test.py`): theta doesn't persist day to day; VWAP fade loses, worse in
    the 'MR regime': F. Side find: Late-Day Flow $191 vs $19 in high-theta regime (t 3.1, 8/9 yrs) but funded no gain: watchlist #16.
  - NDX 0DTE open interest by strike (`data/GEXOI_*.csv`, `analysis/gex_oi_pin_test.py`): no pinning, no wall effect, put/call
    useless, 0 / 15 plan filters pass: F. Export has no Mondays; use only the 9:31 ET OI snapshot. Apex PA terms CONFIRMED from the user's dashboard 2026-10-15 ($2,000 drawdown, safety net
    $52,100, min balance to request $52,600, 5 days of $250+, 6 payouts then closed): the simulator already matches, no change.
  - YM's own events (Dow heavyweight earnings, ZN overnight / lead-lag / shocks): F (`analysis/ym_dow_events_test.py`).
  - BTC short-only euphoria fades (multi-day / overnight / intraday spike / heavy-volume / round numbers): F.
  - Funded bench rebuilt this session (numba, build_lab, s_rank_gap_round2 + gy / btc grids): reproduces the documented numbers.
- **Next research (needs data from the user):**
  - Closing-imbalance or options open-interest data for ES.
  - Without new data, the clock flows on GC / ES / YM / BTC are exhausted.
- **Watchlist (`WATCHLIST.md`), notable items:**
  - #1 Late-Day Flow sized by the gamma flip
  - #10 / #12 MOC follow
  - #13 ONB ML filter out of sample: fit on 2018–22 only, kept $469 vs skipped $212 on 2023–26, t 1.0. Live reports
    decide.
  - #14 EOS sized up in calm VIX
- **Data caveat:** continuous contracts are not back-adjusted.
  - Roll jumps happen at 03:32 or 17:01 CT (NQ +120..310 points per roll since 2023).
  - The plan's trades are clear of them; drop roll bars in new tests.

## Rebuilding the data (not in git)

- `pip install numba`, then `python3 analysis/build_lab.py scratch_data` builds g24 / ge / lab.
- The gc / cl pickles build on first `load("GC")` / `load("CL")`; btc via `cross_asset_overnight_test.btc()`.
- The CL fade's bench needs `scratch_data/s_rank_gap2.pkl`: run `analysis/s_rank_gap_round2_test.py` first.
- Raw 1-minute CSVs are in `data/` and the repo root.

## Open items for the user

1. Compile the fixed Overnight Bias code (combine chart now; funded ML version later) and re-enable auto trading.
2. Keep the PC / connection awake during trading hours (Monday's miss).
3. Optional: rerun the ONB ADX30 MultiCharts backtest once with the new code (should be nearly identical).
4. Check Apex allows MCL; send weekly live reports; no exports pending (ZN and 6E are complete).
