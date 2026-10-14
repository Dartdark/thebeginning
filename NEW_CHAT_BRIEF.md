# New-chat brief (2026-10-14): read this first

Paste this into a new chat: *"Read `NEW_CHAT_BRIEF.md`, then `CLAUDE.md`, in github.com/Dartdark/thebeginning (branch
`claude/nq-trading-strategy-params-5h9d20`) and continue from there."*

## Who / what

- Algo trader running MultiCharts (PowerLanguage) on **Apex 50K** accounts via **Rithmic** (data dxFeed). Apex only
  (ignore Topstep). Flat by 15:59 CT; $2,000 end-of-day trailing drawdown (locks at $50,100); combine: $3,000 target,
  $1,000 daily loss limit.
- Goal: **funded payouts** (6 payouts = $13,000 per account), reached as fast as possible.
- Preferences: forced / scheduled flows (they work here; price patterns fail), low correlation, longs and shorts
  analysed separately. Always give **direct GitHub links + raw links** for code to paste into MultiCharts.
- Working rules, testing standard and branch rules are in `CLAUDE.md` (push every commit to
  `claude/nq-trading-strategy-params-5h9d20`, `claude/quirky-noether-4dla64` and the session's own branch).

## Live status (2026-10-14)

- **3 combine accounts started together** (trade copier allowed by Apex: one master per phase). First live days:
  - **Monday 10/12:** a winning trade was missed because the connection dropped.
  - **Tuesday 10/14:** the Overnight Bias short (5 MNQ) was rejected by Rithmic: *"Invalid StopMarket order
    parameters"*, a sell stop placed above the market.
    - **Fixed:** all Overnight Bias versions now enter at market when price is already at / through the
      opening-range level (`EntryBufTicks` 2). The new order names are "ON Bias LM / SM".
    - **User must paste and compile the new code before the next open.**
  - Accounts still flat at $50,000; pass odds unchanged (~50%).
- **All strategy files were audited:** every other entry is a market order; order names are unique per file.
- **Combine set** (`apex_strategies/`, MNQ, 24-hour session, Exchange time CT):

  | Strategy | File | Chart | Live inputs |
  |---|---|---|---|
  | Vault Break | `NQ_Vault_Break.txt` | 30 min | `NumContracts` 8 |
  | Overnight Bias ADX30 | `NQ_Overnight_Bias_ADX30.txt` | 15 min | `RiskPerTrade` 1100, `NumContracts` 1, `ADXMin` 30, `StopAtrPct` 0.25, `ExitTime` 1430, `EarlyExitTime` 1130 |
  | Bridge Monday Long (ships with The Bridge, not in repo) | — | as shipped | 2 MNQ; enters Sunday 19:00 CT |
  | Expiration Open Short | `funded_strategies/NQ_Expiration_Open_Short.txt` | 5 min | `RiskPerTrade` 500; next trade **Fri 2026-10-16** (3rd Friday) |

  Backtest: pass 50.1% per try, median 6 trading days; combine sizing barely matters (`analysis/pipeline_tuning_test.py`).
- **Live tracking:** the user exports weekly MultiCharts reports into `live/`.
  - Run `python3 analysis/live_vs_backtest.py --all live/` (see `live/README.md`).
  - Count technical misses separately from the edge.
  - Scale beyond 3 slots only when the live edge is ≥ ~75% of backtest (×1.25 sizing only at ≥ 90%).

## Funded plan (when an account passes; `funded_strategies/FUNDED_PLAN.md`, roster in `funded_strategies/README.md`)

| Strategy | Chart | Inputs |
|---|---|---|
| Vault Break | 30 min MNQ | 3 MNQ |
| Overnight Bias ML v2 (`NQ_Overnight_Bias_ML.txt`) | 15 min MNQ | `RiskPerTrade` 400 |
| Monday Long | 5 min MNQ | 1 MNQ |
| Expiration Open Short | 5 min MNQ | `RiskPerTrade` 700 |
| Late-Day Flow | 5 min MNQ | 2 MNQ |
| NFP Fade | 5 min MNQ | `RiskPerTrade` 500 |
| Bridge Monday Long | as shipped | 1 MNQ |
| **CL Sunday Gap Fade** (new, `CL_Sunday_Gap_Fade.txt`) | 5 min **MCL**, Eastern exchange time | `NumContracts` 2, `ExitTime` 1000 (= 9:00 CT) |

- **Cushion sizing:** f = cushion / ref, kept in 0.5–1.
  - The live recommendation is full size from a **$1,000** cushion (pipeline tuning: +7% net per slot).
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
- **Next research (needs data from the user):**
  - **ZN (10-year) and DX / 6E 1-minute exports** for gold (rates / dollar divergence).
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
4. Check Apex allows MCL; send weekly live reports; export ZN + DX for gold research.
