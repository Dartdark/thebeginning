# Video Drift VWAP Pullback: REJECT for current-plan advancement

Summary: The reconstructed video rule is profitable, but earns no portfolio test under the frozen gates.
2018–22, 1 MNQ: 2,808 trades, $12,219.68 net, $4.35/trade, PF 1.10.
Daily t 2.31 misses 2.5; the prespecified conditional timing null also fails (p=1.00).
Keep all five current portfolios unchanged; 2023+ and new account simulations were not earned or run.

Plan: [frozen rules](../plans/drift_video_20261030.md), `ae629418567183d7b21c21c0c803027d801cd09e`.
Correction: [documented implementation repair](../plans/drift_video_20261030_implementation_correction.md), `3f20093`.
Scripts: [test](../../../analysis/codex_drift_video_20261030.py), [report](../../../analysis/codex_drift_video_report_20261030.py),
[second-agent audit](../../../analysis/codex_drift_video_audit_20261030.py).
Output: [result](../../../analysis/outputs/codex_drift_video_20261030/design_result.json),
[run receipt](../../../analysis/outputs/codex_drift_video_20261030/run_receipt.json),
[trade ledger](../../../analysis/outputs/codex_drift_video_20261030/design_trades.csv).
Trials: 5 definitions, including 2 controls with 100 draws each; 2 implementation runs of the same frozen definitions.
Earlier family trials remain counted; no new scout discovery, reservation, history reset or automation.

## Rule (as tested)

The strategy from 5:34 onward is the existing **DriftPullback/VWAP momentum** family, already in TIER_LIST and the
personal capital-expansion bench. This is a video reconstruction, not an exact replication of hidden code.

- NQ, completed 15-minute trend state and 5-minute triggers. VWAP uses completed 15-minute HLC3×volume bars from 08:30 CT.
- Long: 15m close above VWAP, VWAP rising, previous-hour return≥0.1%; shorts mirror the conditions.
- First opposing-color 5m bar means a color transition: red after non-red for longs; green after non-green for shorts.
  No VWAP touch or distance threshold. This definition is an explicit assumption.
- Entry next bar open, 09:30–14:30 CT decisions, flat 14:55 CT; known half-days 11:30 last decision / 11:55 flat.
- 80-point stop, 40-point long target / 50-point short target; entry-bar protection, 1-point target trade-through.
- One position, max 4 trades/day; primary stops after 2 consecutive net losses. Total-loss interpretation is diagnostic only.

Source timestamps: 14:24–16:40 trend, 16:46 first-hour wait, 17:18–18:37 trigger/next-open,
21:32–23:20 brackets and guards. Transcript's early “50 minute” is corrected to 15 minute later.
The trading-flow explanation and employment/performance statements are source claims, not independently verified facts.

## Results

**Design only: 2018-01-02–2022-12-30.** 1,247 complete cash sessions of 1,259 (99.05%); no unknown session is zero-filled.
All dollars below are for 1 MNQ except the separately labeled NQ fee bridge; that bridge applies NQ fees to the same
accepted micro-strategy ledger, not a separately executed NQ strategy. t is also shown by day to avoid treating
several entries on one day as independent sessions. Max DD includes the initial zero equity peak.

| Side | Trades | Win | Avg 1 MNQ | Avg NQ fee bridge | Trade t | Daily t | PF | Sharpe | Sortino | Max DD 1 MNQ | Calmar | Ulcer |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| all | 2808 | 61.0% | $4.35 | $46.67 | 2.27 | 2.31 | 1.10 | 1.04 | 1.54 | $2,285.50 | 1.08 | 1.39 |
| long | 1487 | 63.3% | $3.65 | $39.60 | 1.49 | 1.46 | 1.09 | 0.66 | 1.00 | $2,050.40 | 0.53 | 1.02 |
| short | 1321 | 58.5% | $5.15 | $54.62 | 1.71 | 1.68 | 1.11 | 0.76 | 1.30 | $1,798.04 | 0.76 | 1.28 |

| Year | Trades | Net all 1 MNQ | Long net | Short net | Daily t |
|---|---|---|---|---|---|
| 2018 | 427 | $2,438.42 | $48.62 | $2,389.80 | 1.25 |
| 2019 | 335 | $750.10 | $624.80 | $125.30 | 0.59 |
| 2020 | 623 | $3,251.08 | $3,303.96 | $-52.88 | 1.33 |
| 2021 | 600 | $2,000.50 | $655.54 | $1,344.96 | 0.79 |
| 2022 | 823 | $3,779.58 | $787.60 | $2,991.98 | 1.18 |

| View | Trades | Net 1 MNQ | Avg | Daily t | Max DD |
|---|---|---|---|---|---|
| Primary: two consecutive losses | 2808 | $12,219.68 | $4.35 | 2.31 | $2,285.50 |
| Robustness: two total losses | 2789 | $12,888.94 | $4.62 | 2.47 | $2,221.92 |
| Replayed higher-cost primary | 2808 | $9,554.58 | $3.40 | 1.81 | $2,418.14 |

The alternative was not selected after results. Both daily t values are below 2.5; no long-only/short-only rescue was run.
The full per-side/per-year standard metrics are in [CSV](../../../analysis/outputs/codex_drift_video_20261030/design_metrics.csv).
2023+ metrics, bootstrap and account effects are **not available** because the design failed; do not substitute
the video's own results or old family results for this rule's validation.

Cost bridge, primary 1 MNQ: gross **$17,243.50** − fees **$2,920.32** −
slippage **$2,103.50** = net **$12,219.68**.
Fee $1.04 RT, one tick ($0.50) per market/stop fill; limit target has no separately added market slippage.
Higher-cost replay: fees $3,481.92, slippage $4,207.00, net $9,554.58.
Its daily loss cap uses stressed net outcomes. Primary daily.csv's stress column is only the fixed-primary-ledger
accounting bridge; stress_trades.csv is the separately cap-replayed stress result.
Current net permits about $4.35 extra average cost per trade before arithmetic break-even,
not a guarantee of executable spread/latency capacity.

| 10-day block bootstrap, 5,000 draws | Actual | 5% | 95% |
|---|---|---|---|
| sharpe | 1.04 | 0.35 | 1.71 |
| max_dd | 2,285.50 | 1,787.22 | 4,900.53 |
| annual | 2,469.41 | 815.04 | 4,060.95 |

## Placebos and account level

| Conditional null | Draws | Median total | 95th percentile | Actual total | Empirical p |
|---|---|---|---|---|---|
| side | 100 | $-7,684.91 | $540.43 | $12,219.68 | 0.0099 |
| time | 100 | $25,559.44 | $31,384.33 | $12,219.68 | 1.0000 |

Random-side draw directions are independent of source bias; the prospective signal calendar is retained and daily
caps/occupancy replayed. The rule beats this control, which supports directional information in the combined setup.
The random-time control retains each date's **complete-day signal count and side order** while randomizing allowed
slots. This is a **retrospective conditional timing null**; those future daily labels are unavailable for deployment
at earlier randomized times. Its profits must not be advertised as an executable alternative, a causal timing edge,
or proof that random orders outperform a live strategy. The source's first-counterbar timing does not beat this
frozen null, and the independently failed daily-t gate already stops advancement. No replacement control was selected.

Frozen gates: ≥500 trades PASS; positive native net PASS; daily t≥2.5 **FAIL**; ≥4 positive years PASS;
positive cost stress PASS; side placebo p≤.05 PASS; conditional-time placebo p≤.05 **FAIL**.

| Current home | Explicit placement verdict | What was actually tested |
|---|---|---|
|50K evaluation|No eligible addition/replacement|Design failed; current account BASE/ADD/REPLACE/EMPTY not run|
|150K evaluation|No eligible addition/replacement|Same design stop; no 150K pass-rate claim|
|50K funded|No eligible addition/replacement|No new payout/blow-up/timing simulation|
|150K funded|No eligible addition/replacement|No new 150K payout/blow-up/timing simulation|
|Personal A–D/core/full|No eligible addition/replacement|No current 19-piece return/DD/capital comparison|

Current roster was checked from the [six-plan snapshot](../inputs/greenorb/plan_snapshot/manifest.json),
Claude7a42ea76c62838109d45d168887f57a922933ef2:50Kfunded uses Tfade instead ofRS_L;150KkeepsRSboth,OT2/ST2;
evaluationVB8/20+ONBADX30+Bridge+EOS; personal19pieces. The conditional replacement was Vault Break, chosen
before outcomes from related-family overlap, not a sweep over convenient replacement slots. Some account-source
ledgers were acquired while design ran, but no candidate account input was loaded or account outcome computed.

**Prior evidence, different definition/book:** the existing v2.1 test reported 5,733 trades, $56/NQ, t 4.0;
its 1-point-through view had t 3.0. On its old funded roster, ADD 1 MNQ raised one-year blow-ups 3%→13% and cut two-year
payouts $12,436→$11,182. Simplified v3 later added personal dollars but reduced return/DD 8.3→8.0 on an older 17-piece
book. These help identify the repeated family; they are not measurements against today's portfolios or today's rule.
Sources: [old test](../../../analysis/drift_pullback_test.py),
[old output](../../../analysis/outputs/drift_pullback_test_output.txt),
[personal snapshot](../inputs/greenorb/plan_snapshot/personal_strategies/PORTFOLIO.md).

## What could make this wrong

**Implementation and audit:** a second-agent review caught that the first code allowed half-day decisions through 11:50,
contrary to the committed 11:30 rule. The correction was committed before rerunning and preserves every original artifact
under [pre_correction_halfday](../../../analysis/outputs/codex_drift_video_20261030/pre_correction_halfday).
Primary accepted trades and P&L are unchanged; prospective/null schedules can change. Stress fee/slippage display was
also corrected; its economic net calculation was already correct. This is a repair, not a new sample or threshold change.

[Audit receipt](../../../analysis/outputs/codex_drift_video_20261030/audit.json): **1,339 checks PASS**,
40 sampled days/2,080 independently trailing feature decisions;
all 2,808 unique saved trade paths checked against raw entries/brackets/earlier hits,
plus cost/cap/daily/side/year reconciliation. This is second-agent implementation/accounting review, not a blind full-universe
economic rebuild, independent MC approval, native MNQ fill verification or forward record.

**Coverage:** unknown dates: 2018-04-30, 2018-07-26, 2018-08-28, 2019-12-05, 2020-03-09, 2020-03-12, 2020-03-13, 2020-03-16, 2020-03-18, 2020-11-30, 2021-09-17, 2022-03-08. Several are March 2020 halt/limit sessions. Excluding them can flatter risk;
the observed DD is not a full-market tail-risk bound. No claim about their unobserved strategy P&L is made.
Continuous NQ history, bar-volume and one-minute path assumptions remain; native MNQ contract IDs/quotes/fills are absent.
No change from 1-point research trade-through to 0.25was tried to improve results. Calendar helper conservatively treats July 3 as
early in some years, an existing disclosed limitation. Freeze source/chart/session settings for any future parity request.

**Mechanism:** a VWAP-weighted average is not the price of maximum traded volume. A large proportion of VWAP
algorithms does not demonstrate signed forced flow or future continuation. This is a price/volume pattern test.
Prior family selection and the speaker's 2020–24 optimization contaminate any claim that our design is pristine discovery.
No new historical validation or future forward return is represented here.

**Prop-firm claim:** 49.8% per attempt gives 1−(1−0.498)^4=93.65% only for independent equal-probability attempts.
Four copied simultaneous accounts can have essentially the same outcome. One NQ's 80-point stop is $1,600 against
a 50K $2,000 trail; a quoted 64% hit rate alone cannot establish profitability (40/80 long gross breakeven 66.67%,
50/80 short 61.54%). Claimed 3.44 days must identify whether conditioned on successful attempts. Passing is not a payout.

## Differences between MultiCharts code and this test

No new MultiCharts code written: source code was not supplied and the advancement gate failed.
The archived v3 is a related version with extra distance/timing logic; do not paste it as an exact implementation
of this video. 15m-held bias, HLC3 VWAP, color-transition trigger, holiday timing, first-minute eligibility, net loss
counter and immediate protection are disclosed reconstruction choices, not validated matches to the author's engine.
Useful execution lessons merged into [EXECUTION_REFERENCES.md,E09/E18](../EXECUTION_REFERENCES.md).

Reproduce:
```bash
# Use the configured Python and an isolated directory containing only the five hashed2018–22day files.
/workspace/venvs/thebeginning/bin/python analysis/codex_drift_video_20261030.py inventory --data /workspace/drift_video_inputs/design
/workspace/venvs/thebeginning/bin/python analysis/codex_drift_video_20261030.py design --data /workspace/drift_video_inputs/design
/workspace/venvs/thebeginning/bin/python analysis/codex_drift_video_audit_20261030.py
/workspace/venvs/thebeginning/bin/python analysis/codex_drift_video_report_20261030.py
```

For Claude: review `agents/codex/results/drift_video_20261030.md`; no plan allocation/ranking/live change proposed.
