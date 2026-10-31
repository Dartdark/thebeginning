# Resume section + research summary (draft 2026-10-31)

Everything below is true and checkable in the repo or the Apex accounts. Keep it that way: no titles, years or results
that aren't here. Update the numbers when funded payouts arrive.

## Resume section

**Independent Systematic Futures Research** · self-directed · Oct 2026 – present
- Design and run a systematic research program for intraday equity-index and commodity futures (NQ, ES, CL, GC, NG, ZN, 6E),
  working with AI coding agents (Claude, Codex) as the implementation team and directing the research, review and
  live-trading decisions.
- Built a Python research pipeline with cost-aware backtests ($ commissions + 1-tick slippage per fill), pre-registered
  hypotheses, design / holdout splits, placebo and random-entry controls, Bonferroni-style multiple-testing bars across
  350+ ranked trials, and an independent re-implementation check before any strategy is promoted.
- Evaluated 370+ strategy ideas from academic papers, practitioners and internal research; rejected the large majority
  on out-of-sample or cost grounds, with every verdict and failure lesson recorded.
- Run strategies live on prop-firm evaluation accounts (Apex Trader Funding) via MultiCharts / Rithmic on a VPS, with
  automated monitoring: account-floor alarm, code-version stamps, pre-market readiness checks, missed-trade and
  live-vs-backtest drift alarms.
- Model account-level risk with Monte Carlo / block bootstrap simulations of trailing-drawdown rules and payout ladders;
  used them to set position sizing and the account-buying plan.
- Run a weekly cross-review between two independent AI agents plus a dedicated code-review process; found and fixed
  defects such as timezone errors, fractional contract sizing and look-ahead in test harnesses before they affected decisions.

**Skills:** research design and validation (bias, leakage, multiple testing, walk-forward), futures market structure and
execution, backtest review, risk / Monte Carlo, Python (pandas, NumPy) at reading-and-review level, AI-agent workflows.
(Adjust the Python line to what you can do alone.)

## One-page summary: how the research process works

**Goal.** Find intraday futures strategies with a real economic reason to exist, prove them out of sample, and run them
on prop-firm accounts under strict drawdown rules.

**1. Ideas need a mechanism.** Each idea states who is forced to trade at a bad price and why (scheduled releases,
auctions, fixing flows, hedging). Sources: papers, practitioners, our own failed-model lessons.

**2. Written down before testing.** Rule, at most 3 variants, costs and pass bars are committed before any return is seen.

**3. Staged gates.** Design period 2018–22 (t, profit factor, trade count) → placebo / random-entry and year-by-year
checks → one counted look at the 2023+ holdout → account-level simulation under the prop firm's rules → independent
rebuild by a checker that only gets the written spec. Each idea stops at the first gate it fails.

**4. Honest accounting.** Realistic costs and slippage, every trial counted, so the bar rises as more ideas are tested
(currently t ≥ 3.63). Results are ranked S–F and kept, failures included.

**5. Risk at the account level.** Strategies are judged by what they do to pass rates, blow-up rates and payout timing
under trailing drawdowns, not by standalone returns.

**6. Live monitoring.** Live trades are compared with the backtest range; alarms catch frozen charts, wrong code versions,
accounts near their floor and drift from the backtest.

**7. Review.** Weekly two-agent cross-review and code review. Example: a review found 150K-account simulations using
fractional contracts; fixing it confirmed one decision and reverted another (a strategy swap that turned out to be a tie).
