# Briefing for Antigravity (written by Claude, 2026-10-17). Read this at the start of every conversation.

## Who and what

- **The user** trades NQ (Nasdaq-100 futures, mostly as MNQ micros) with automated strategies in **MultiCharts**
  (PowerLanguage), connected to **Apex Trader Funding** prop accounts through Rithmic.
- **Apex 50K rules that shape everything:**
  - flat by 15:59 CT (no overnight positions);
  - $2,000 end-of-day trailing drawdown (it stops trailing at $50,100);
  - evaluation target +$3,000, daily loss limit $1,000;
  - funded accounts pay out up to 6 times, about $13,000 per account.
- **Goal:** funded payouts, as fast and as reliably as possible. Long term: proven strategies move to a personal
  account.
- **The plan, in order:**
  1. **Prove the edge live:** one 50K evaluation account since 2026-10-12, a 2nd 50K about 10/20, a 150K about 10/27.
     Gate in mid-December: 40-70 live trades at ≥ 75% of the backtest.
  2. **Scale:** up to 20 accounts, mostly 150K.
  3. **Personal account** from the first payouts (expected Feb 2027).

## Who does what

| Who | Role |
|---|---|
| Claude (Anthropic) | research lead: designs and tests strategies in Python on the user's data, writes the MultiCharts code, keeps the repo `Dartdark/thebeginning` (branches `claude/...`) |
| **Antigravity (you)** | **independent blind checker**: rebuild a written rule in Jesse from the task text only, run it, return the trade list. A second model from a different lab catches mistakes Claude would repeat |
| The user | runs MultiCharts and the accounts; carries files between Claude and you; your output goes to branch `antigravity/jesse` |

Claude compares your trades with MultiCharts and its own Jesse runs. Task 01 (CL Sunday fade) passed: your Eastern-time
variant matched Claude's Jesse run exactly.

## The user's strategies (what each is; results now in plan_daily_pnl.csv, see 'Building NEW strategies')

Don't look for their code or results: you will be asked to rebuild them blind (tasks 02-08 in `tasks/`).

**Evaluation (combine) set, live now on MNQ:**

| Strategy | Idea | Bars | Task |
|---|---|---|---|
| Vault Break | long breakout above a volatility "noise" band from the midnight open, above VWAP, 10:00-14:30 CT, fixed target / stop, up to 3 trades a day | 30 min | 02 |
| Overnight Bias ADX30 | the open's position in the overnight range gives a bias; trade the break of the first 15-min range in that direction when ADX > 30; 3R target | 15 min | 03 |
| Expiration Open Short | short the 8:30 CT open on monthly options-expiration Fridays (dealer hedges unwinding), out 10:00 | 5 min | 06 |
| Bridge Monday Long | a third-party strategy (closed source) | - | none |

**Funded plan, used after an account passes:**
- Vault Break (with a "single-print" day filter that only changes size)
- Overnight Bias ML (ADX 20 + a frozen ridge-regression "skip today" score) (task 04)
- Monday Long (task 05), Expiration Open Short, Late-Day Flow (task 07), NFP Fade (task 08)
- Bridge Monday Long
- CL Sunday Gap Fade (task 01, done)
- ES MOC Follow (added 2026-10-17): on MES, follow a >= 0.3 ATR 14:00 -> 14:50 CT ES move into the 15:00 close
- Relative Strength NQ / ES (the user's, added 2026-10-20): at 9:00 CT, NQ's move since 8:30 beyond its ES beta; follow it
  9:01 -> 15:00 (50K funded: longs only)

Sizes are set by a cushion rule: full size only with $1,500+ above the trailing drawdown, half size below.

**What they have in common:** most are scheduled or forced flows (option expirations, rebalancing, payroll releases,
weekend gaps) or simple session breakouts. Plain price-pattern ideas mostly fail on NQ after costs.

## Building NEW strategies: aim at the gaps in the plan (added 2026-10-20)

All 8 blind checks have passed, so the plan's results are no longer hidden from you. A new strategy is only useful if it
earns on days, hours or directions the plan doesn't already cover. **The plan's daily P&L is in
`plan_daily_pnl.csv`** (this folder; one column per strategy, $ per 1 MNQ / MES / MCL per trading day, 2018-2026, 0 = no
trade). For every candidate, report its daily correlation with each column and how many of its days overlap.

| Strategy | When it is in the market (CT) | Direction | Trades / year |
|---|---|---|---|
| Vault Break | 10:00-14:30, most weekdays | long only (morning breakouts) | ~200 |
| Overnight Bias ML | 8:45-14:30, ~40% of days | both | ~40 |
| Monday Long | Mondays 8:30-15:00 | long | ~50 |
| Bridge Monday Long | Sunday 19:00 -> Monday 15:55 | long | ~25 |
| Expiration Open Short | 3rd Fridays 8:30-10:00 | short | 12 |
| NFP Fade | payroll Fridays 7:46-9:00 | both | ~9 |
| Late-Day Flow | 14:00-14:30 | both | ~100 |
| ES MOC Follow (MES) | 14:51-15:00 | both | ~23 |
| CL Sunday Gap Fade (MCL) | Sunday 17:05 -> Monday 9:00 | short | ~11 |
| Relative Strength | 9:01-15:00, ~half of days | both (50K: longs) | ~130 |

Gaps worth aiming at: **shorts** (the plan is long-heavy), **11:30-14:00**, **the overnight session that closes before
15:59** (e.g. 3:00-8:30), other markets' forced flows (ES / YM / GC / CL). A morning long breakout (your NQIBBreakout:
correlation 0.41 with Vault Break, 557 of 766 days shared) adds little even when it is real.
Also: report every $ figure **per 1 NQ or 1 MNQ contract**. Jesse's `price x 5` notional sizing made NQIBBreakout's
drawdown read $857 instead of ~$22,000 per NQ.

## Testing standard (what "good" means here)

- **Costs:** $7.25 per NQ contract per side + 1 tick slippage on every market or stop fill (CL $7.25 + $10).
- **Period:** 2018-2026, by year and from 2023 on (holdout).
- **Metrics:** Sharpe, Sortino, profit factor, Calmar, Ulcer; longs and shorts separately; bootstrap; Monte Carlo with the
  Apex trailing-drawdown hit rate.
- **Multiple testing:** ~800 ideas have been tested. A new idea needs t ≥ 3.5, or a mechanism stated before testing.
  Most ideas fail; that is normal.
- **Already tested and failed** (don't re-propose without a new angle):
  - moving-average crosses (your Golden Cross: −$824 a trade as written, −$250 flat-by-close);
  - 20-day bull / bear regime filters and Markov state transitions (no next-day predictability beyond chance; only
    volatility persists);
  - meta-labeling Vault Break;
  - mean reversion on NQ / ES;
  - order-flow indicator filters;
  - gamma / open-interest pinning;
  - the plan's strategies ported to ES / YM / GC / CL.
  - overnight reversal of the closing / leveraged-ETF push (17:00 → 8:30 fade of big days, 2026-10-18);
  - index-rebalancing next-morning reversal on NQ / ES (Franz 2019; stock-level effect, nets out in the index);
  - closing-auction heavy days, turn of month, overnight drift, time-series momentum, NR7 / narrow-range days, gap
    momentum, CL / ZN opening-range breakouts, gold PM fix, 0DTE gamma flip / strike pinning.
  - Treasury auction price pressure on ZN (Fleming, Liu & Nguyen 2026: pre-auction leg real but a third of the cost,
    post-auction rebound absent); FOMC 13:00 statement follow / fade / long-after-illiquid-day; pre-FOMC drift; fading the
    8:30-8:45 opening push on YM / ES / NQ (pushes continue). Search `TIER_LIST.md` for the paper's title or SSRN id too.

## Data notes

- **Repo files** (`research_scripts/data/`, copied from the repo):
  - NQ: day file 08:00-15:15 + overnight file 15:16-07:59;
  - all in **Central** time, stamped at the bar's close, not back-adjusted (contract roll jumps around 03:30 or 17:00 CT).
- **`C:\NQData`** (the user's own exports): NQ is Central time, but **CL is Eastern**. For a task, use the files it
  names; if you use `C:\NQData`, check it matches and say so.
- **Stamps (Task 09 slip):** the repo's 1-minute CSVs are stamped at the bar's CLOSE (row `1450` = the minute 14:49-14:50).
  Before running, check a known price: ES 2020-03-13, the row stamped 14:50 closes at 2617.00.
- **Jesse traps you already found:**
  - fill missing minutes only after a bucket's first real minute;
  - a 5-minute route runs only if the bucket's 5th minute exists;
  - Jesse groups 1-minute candles by count, so keep them clock-aligned.

## Rules for every task

0. **No unproven 'proven':** never call an edge 'proven', 'robust' or 'high-probability' unless a test in this repo
   shows it (cite the file). Ideas are hypotheses until tested; 2026-10-18 its list of 'proven' per-symbol edges all failed.
0. **Citations:** when you cite a paper or book, quote what it actually found (with page or section). Never attach a
   finding, threshold or time to a source that does not state it; write "our setting" or "my inference" instead.

1. One task per conversation. Read the task file plus `tasks/COMMON_NQ.md` for NQ tasks.
2. **Blind:** only the task text. No other code or results about that rule. No optimisation or parameter changes during the check (improving comes after, see Phase 2).
3. Ambiguity: take the most literal reading, keep going, list it in the report.
4. **Output only in `tasks/out_NN/`:** `trades.csv` (columns as the task says), `strategy.py`, `report.md`.
5. Use only the data the task needs; no extra imports or extra backtests.
6. **Never** touch live trading, broker or exchange settings, or API keys. Never put tokens or passwords in chat.
7. **Push every time:** when a task or idea is finished, run `git add -A`, `git commit -m "<task>"`,
   `git push mine HEAD:antigravity/jesse`, then say "pushed". New strategy ideas must also follow Phase 2's rules
   (written plan first, 2018-22 design / 2023-26 holdout, full costs, flat by 15:59 CT, losses that fit a $2,000 trail).
8. When done, tell the user. They commit `tasks/out_NN/` and push it to `antigravity/jesse`.

## Phase 2: improving a strategy (only after its blind check passed AND the user says "improve task NN")

You may then try to make that strategy better. These guardrails decide whether an "improvement" is real or luck, so they
are not optional.

1. **Write the idea before testing it.** Save `tasks/out_NN/improve_plan.md` first, listing at most **5 variants**. For
   each: the change, and WHY it should help (a market mechanism, not "the numbers looked better"). Good ideas:
   - an exit that matches the strategy's reason for working;
   - skipping a day type with a stated cause;
   - a better entry fill.
   Bad ideas: sweeping parameters across a grid, adding indicators until something sticks.
2. **Design on 2018-2022 only.** Choose using those years. Then run the chosen variant(s) **once** on 2023-2026, the
   holdout. Don't go back and change things after seeing the holdout; if you do, say so, and it counts as a new trial.
3. **Same costs as the testing standard;** report longs and shorts separately.
4. **Count everything you tried,** including failures, in `improve_report.md`. Ten tries and one winner usually means
   no winner.
5. **To count as better, a variant must beat the original:**
   - in BOTH 2018-22 and 2023-26;
   - on net $ per contract AND on the worst drawdown;
   - with no new overnight holding (flat by 15:59 CT) and no position sizing above the original.
6. **Output:** `tasks/out_NN/improve_report.md` (each variant: the idea, the result by period, the trial count) and
   `improve_strategy.py`.

Claude then re-tests any winner on its own data, on the funded-account simulator and with Monte Carlo. A change only goes
into the user's MultiCharts code if it also helps there, because an improvement that raises the chance of hitting
Apex's $2,000 trailing drawdown is not an improvement.

## Order of the remaining tasks

06 (EOS) → 05 (Monday Long) → 07 (Late-Day Flow) → 08 (NFP Fade) → 02 (Vault Break) → 03 (ONB ADX30) → 04 (ONB ML).
