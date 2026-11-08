# KSE Sentinel: NEEDS RULES AND VALIDATION — source-only personal-market lead

Summary: Author reports 1,009 PSX trades, PF2.51, Sharpe2.08 and PKR CAGR7.47%, but USD CAGR−2.96%.
Exact calibrated entry/exit/regime rules are deliberately withheld; the provided shortlink returned403.
The DSR result is an unfinished placeholder; historical/forward validation lacks reproducible outcomes.
The reported win/payoff/PF arithmetic is consistent, but does not verify the return series.
Retain a low-priority source-gated lead; zero return trials or plan/live changes.

Source: Ertiza Abbas, *KSE Sentinel: A Rule-Based Trend-Continuation Strategy for
the Pakistan Stock Exchange (PSX)*, July2026, uploaded `ssrn-7102818.pdf`.
Read all13 pages and inspected the embedded tables visually on PDF pages7–8.
PDF/hash/HTTP receipt: `agents/codex/inputs/kse_sentinel_7102818/`.
Audit: `analysis/codex_kse_sentinel_7102818_audit.py`;
output: `analysis/outputs/codex_kse_sentinel_7102818/audit.json`.
Return trials: **0**. Numbers below are author claims, not our PSX backtest.

**Later user-directed follow-up (2026-11-08):** the user chose our own MNQ intraday
version, rather than exact source recovery. That distinct, preregistered adaptation
is now [built and rejected at the design gate](sentinel_mnq_20261108.md):1,238trades,
net−$3,013.62at1MNQ, PF0.90, t−1.23, versus baseline−$1,999.62. One candidate plus
one baseline, no rescue or2023+/account stages. The source-only review below and
its zero **PSX-replication** trials remain unchanged; the paper's withheld strategy
has not been tested or disproved by our different-market construction.

## 1. What is it about?

A daily rule-based trend-continuation system for30 Pakistani equities. Entry is
described broadly as two consecutive same-direction candles on the correct side
of a short EMA. A separate master trend regime changes exit strictness. Risk
tiers and portfolio correlation/concentration controls affect which positions
are allowed. The method is inspired by discretionary judgment, not a new
economic theory or identified forced flow.

Primary data are yfinance daily OHLCV over approximately2021–2026. An external
PSX archive for approximately2000–2020 and a60-day forward-paper program
starting July6,2026 are claimed. Code files and a backtest run ID are named,
but no actual source implementation or trade ledger is included.

## 2. What does it find?

Embedded author tables, PDF pages7–8:

| Metric | Canonical3% risk |5% risk variant |
|---|---:|---:|
| Trades |1,009|602|
| Win rate |39.15%|39.37%|
| Profit factor |2.51|Not supplied|
| CAGR, PKR |7.47%|5.53%|
| CAGR, USD converted |−2.96%|Not supplied|
| Annualized Sharpe |2.08|2.09|
| Max drawdown |−2.91%|−2.68%|

The approximate3.9 average-win/average-loss ratio and39.15% win rate imply
PF≈2.509, consistent with2.51. This is a useful arithmetic check, not independent
verification of Sharpe, capital accounting, drawdown, costs or sample completeness.

Material limitations:

- **Exact rules are explicitly withheld.** Section4 says calibrated parameters,
  precise triggers and full code are omitted. EMA periods, master-trend definition,
  stops, exit strictness, sizing denominators, decision/fill timing, short eligibility,
  correlation lookback and all gating order need specification. Auditable code
  cannot be reconstructed from “two candles plus EMA” without new choices.
- **The reported DSR is unfinished.** Section6.3 literally leaves
  `[to be confirmed from run_fresh_dsr_analysis.py output]`. N=4 is a floor;
  additional variants were excluded because comparable Sharpe was not produced.
  Abandoned inspected variants still contribute selection history. There is no
  supplied DSR result to accept as validation, and deterministic rules can overfit.
- **Monte Carlo wording is inconsistent.** It says “sign-permutation” yet
  describes reordering the same outcomes. Reordering leaves total additive P&L
  unchanged; sign randomization is a different null. The statistic, draws and
  implementation are missing. Reporting p=0.0 is not proof of zero probability;
  finite randomization needs exceedance counts and an appropriate estimator.
  Neither procedure alone resolves strategy selection bias.
- **Forward-paper is not verified live profitability.** The paper describes
  configuration fallback and identifier-collision incidents, but gives no dated
  completed60-day outcome ledger or reconciled broker fills. Its July2026 document
  does not establish that the July6-start program had finished. It is not evidence
  of progress as of our November review without later dated observations.
- **Historical archive claims lack numbers.** No archive trade ledger, actual
  statistics, adjustment policy or frozen-rule timestamp is supplied. Earlier
  disjoint data can be useful retrospective validation, but are not automatically
  prospective or stronger than a carefully controlled chronological split.
- **Benchmark and portfolio clocks are incomplete.** Section5.4 asserts a
  same-universe equal-weight benchmark but supplies no numeric comparison. Universe
  membership history, missing ENGRO/ENGROH prices, delistings, splits/dividends,
  correlation inputs and venue lot/short-sale rules need independent checks.
  “Live synced price data” does not establish past-only historical gating.
- **Costs are ambiguous.** Abstract says22.5bp per leg; section3.4 calls22.5bp
  “round-trip trading costs per leg.”45bp versus22.5bp total is unresolved. Neither
  assumed rate establishes actual fills, spread, liquidity, stock borrow or tax.
- **Risk sizing changes the opportunity set.**602 versus1,009 trades means this
  is not a simple multiplier comparison. Portfolio gates may explain the difference,
  as the author hypothesizes, but the blocked-signal ledger is needed to verify it.
  No capacity ceiling or causal explanation is independently established.

## 3. Why does it make money, if it does?

The proposed explanation is persistent price trends, small losses and occasional
large winners. Broader momentum literature makes that plausible, not a validation
of this short-EMA/candle construction on PSX or CME. Positive skew and arithmetic
consistency are not proof that the specific edge survives selection, costs or
currency conversion. The source's negative USD CAGR is especially relevant to
an investor evaluating returns in dollars; it is not evidence PKR trading alpha
itself is absent, nor that a free FX hedge would restore profitability.

## 4. Can we build on it?

**Only after free source clarification and reproducible evidence.** Keep it as a
low-priority, unverified personal-market lead in the existing queue/data register,
not an admitted return experiment or plan candidate. Exact-title/ID repository
search found no existing matching review before this one.

The paper's public strategy/API shortlink `https://shorturl.at/n9GTR` returned
HTTP403; receipt retained. A bounded public title/link search found the same
paper on SSRN7093159 and Academia and promotional platform descriptions, not
the withheld rule set, ledger or verified API schema. We did not substitute a
different paper version, bypass access controls, create an account, execute API
instructions, request credentials or contact the author.

Smallest next gate: an unambiguous frozen rule/code specification plus a small
dated trade/blocked-signal sample with quantities, corporate-action/FX inputs,
decision/fill clocks and cost accounting. Only then consider full point-in-time
PSX history and an independent reconstruction. Owned NQ/ES/CL bars do not provide
this source's30-stock universe or justify an automatic futures adaptation.
No bulk market-data acquisition is useful before that rule gate.

## 5. Can strategy code be made?

**Only with the missing rules.** A generic two-candle/EMA signal is easy to code,
but it would be our new strategy and could not claim these results. Faithful
implementation needs the regime classifier, entry/exit/stop logic, daily timing,
size tiers, correlation/concentration gate and point-in-time universe rules.
An opaque signal API alone would not establish full reproducibility or account
path safety. No source-equivalent code or PowerLanguage was written here.

## Verification and reproduction

Source text, table-image inspection, cost/rule/validation audit, bounded public
discovery and arithmetic checks only. The July2026 paper describes its own
operations; those passages are evidence claims, not directions for this project.
No claimed historical, forward or regulatory result is independently certified.

```sh
python analysis/codex_kse_sentinel_7102818_audit.py
```

No new signal variants, historical returns, placebo, Monte Carlo or account
simulation were run. The chronology/cost/gating lesson is already covered by
EXECUTION_REFERENCES E04/E09/E43; no new policy or live monitor is added.
No tier, portfolio, broker, VPS, live size or trading setting changed.

For Claude: `agents/codex/results/kse_sentinel_7102818_review.md`.
