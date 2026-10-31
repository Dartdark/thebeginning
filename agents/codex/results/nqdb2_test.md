# NQDB2 / DriftBreak v2: REJECT for plan promotion
Summary: The fixed proxy earns money, but does not meet the validation requirements.
Apex-safe design: 813 trades, $123/NQ, t=4.05; recent: 721, $65/NQ, t=1.73.
The drift veto fails its required tests; full-sample DSR 0.855 is below 0.95.
Two original-data held-price gaps block the registered funded/evaluation/Monte Carlo stage; no account simulation ran.
Keep the current trading plan. This is a proxy result, not an exact MultiCharts validation.

Plan: `agents/codex/plans/nqdb2_test.md`, `eb7b8b07fd54e8083a13b04f25d1c5b59c68a00b`.
Script: `analysis/codex_nqdb2_run_profiles.py`, `_replay.py`, `_diagnostics.py`, `_test.py`, `_accounts.py`.
Output: `analysis/outputs/codex_nqdb2_test/`. Trials run: **one idea, five fixed return streams**, both registered periods; no retuning.

## Rule (as tested)

Long NQ above the calendar-open noise band (0.30 times the previous 15 positive Date high-low ranges) and 30-minute VWAP. Default veto rejects a four-valid-bar return <=-0.10%. Decisions 10:00-14:00 CT inclusive, next-bar market, maximum two submitted attempts/date. Prearmed 40-point target/75-point stop; exit after seven closes below VWAP or next bar after 15:30. Literal rollover/EOC behavior is preserved.

S0/S1 are the literal-source proxy with veto off/on. A0/A1 apply the same fixed existing VB early-close calendar: entries before 11:00, observed 11:30 close exit. A1 was the primary candidate before returns. E1 is A1 at three ticks slippage. No alternative modes, thresholds, bar sizes, timings or sizes were searched.

Assumptions: full-session, midnight-aligned close-stamped 30-minute bars, IOG off, total-volume-weighted typical price; MC `Volume` may be up-volume. Previous positive Date ranges include Sunday partials. Existing Grid24 and shared one-minute `grid._walk` are reused. $7.25/NQ commission plus one tick on market/stop fills; target requires 1 point trade-through. E1 uses three ticks. Account scaling would preserve the NQ 40/75-point geometry, dividing dollars by 10 per MNQ. No unmodified $800/$1500 brackets on an MNQ chart.

## Results

All dollars below are **per one NQ**, after stated research costs. 2026 ends 2026-10-09; 2023+ is seen historical replication.

| Rule | 2018-22 n | Net | $/trade | t | 2023+ n | Net | $/trade | t |
|---|---|---|---|---|---|---|---|---|
| S0 | 824 | $86,201 | $105 | 3.42 | 735 | $41,686 | $57 | 1.51 |
| S1 | 814 | $101,748 | $125 | 4.13 | 726 | $46,706 | $64 | 1.71 |
| A0 | 823 | $84,253 | $102 | 3.34 | 730 | $44,398 | $61 | 1.61 |
| A1 | 813 | $99,801 | $123 | 4.05 | 721 | $47,113 | $65 | 1.73 |
| E1 | 813 | $87,621 | $108 | 3.54 | 721 | $37,223 | $52 | 1.36 |

A1 whole-strategy metrics (identical for longs; **zero shorts**, all short metrics N/A):

| Period | n | Win | $/trade | t | Sharpe | Sortino | PF | Calmar | Ulcer% | Daily maxDD |
|---|---|---|---|---|---|---|---|---|---|---|
| design | 813 | 66.9% | $123 | 4.05 | 1.69 | 2.57 | 1.38 | 1.94 | 3.46 | $10,074 |
| recent | 721 | 67.0% | $65 | 1.73 | 0.85 | 1.23 | 1.15 | 0.51 | 11.34 | $23,708 |
| full | 1534 | 66.9% | $96 | 3.99 | 1.28 | 1.89 | 1.25 | 0.69 | 4.08 | $23,708 |

Daily mark-to-market includes actual fill costs and reconciles to trade net to the cent. All profiles' long/short and annual rows are in the CSVs. Ulcer uses the standard repository $50,000 reference equity; these statistics are not account payout results.

| Year | A1 trades | A1 net | $/trade | t | PF |
|---|---|---|---|---|---|
| 2018 | 138 | $6,754 | $49 | 0.74 | 1.16 |
| 2019 | 128 | $9,777 | $76 | 1.50 | 1.38 |
| 2020 | 185 | $37,104 | $201 | 3.10 | 1.66 |
| 2021 | 177 | $28,962 | $164 | 2.42 | 1.49 |
| 2022 | 185 | $17,204 | $93 | 1.23 | 1.21 |
| 2023 | 191 | $14,755 | $77 | 1.10 | 1.19 |
| 2024 | 179 | $-6,288 | $-35 | -0.45 | 0.93 |
| 2025 | 182 | $35,760 | $196 | 2.74 | 1.54 |
| 2026 | 169 | $2,885 | $17 | 0.21 | 1.03 |

Current VB comparator comes from its existing canonical MultiCharts report, with standardized research costs applied once. It uses different range, volume, cap and clock rules; this is not an isolated drift-veto test or account replacement result.

| Current VB period | n | Net | $/trade | t | PF | Daily maxDD |
|---|---|---|---|---|---|---|
| 2018_plus | 1743 | $159,813 | $92 | 4.25 | 1.26 | $13,618 |
| 2018_22 | 854 | $71,164 | $83 | 2.93 | 1.26 | $9,062 |
| 2023_plus | 889 | $88,650 | $100 | 3.09 | 1.25 | $13,618 |

## Placebos and account level

The design strategy gate passed, so the same five streams were opened once on 2023+. The independent compiled outcome/scheduler checks match all five full replays and 12 selected null reruns in each period. No source rule was changed after either period was opened.

**Default veto: fails.** Re-entry changes are counted, not treated as simple deletions.

| Period | Removed n | Removed mean | Removed t | New reentries | New net | A0 maxDD | A1 maxDD |
|---|---|---|---|---|---|---|---|
| design | 36 | $-291 | -1.74 | 26 | $5,082 | $11,429 | $10,074 |
| recent | 35 | $184 | 1.10 | 26 | $9,172 | $22,830 | $23,708 |

The removed trades must lose and t<=-2; neither period passes. Recent removed trades actually win. Each family/period has 1,000 matched-count trade-drop draws, a gross-removal sensitivity and 1,000 decision-mask reruns permitting re-entry. A1 must beat 95% on profit and drawdown, not merely raise its average trade.

| Period | Null | Profit p | Share null DD beaten |
|---|---|---|---|
| design | matched trade drops | 0.0010 | 82.3% |
| design | signal-mask reruns | 0.0040 | 55.6% |
| recent | matched trade drops | 0.1389 | 17.6% |
| recent | signal-mask reruns | 0.3916 | 25.8% |

Random-side controls have 100 draws per period. Count-preserving random-time controls also have 100; all exceed A1 profit in both periods. That time control conditions on A1's active dates/counts and **future occupancy feasibility** so schedules can actually submit the matched count. It is a conditional timing diagnostic, not an unconditional executable strategy or proof that the whole long-NQ edge is zero. The initial time sampler incorrectly matched proposed instead of actual submissions; those outputs are marked invalid and retained separately. The corrected sampler is checked against full replay; strategy ledgers never changed.

2023+ bootstrap: 3,000 20-day blocks, seed 20261024. 90% trade-PF interval 0.995-1.336; net-total interval $-1,851 to $97,179. Sharpe interval -0.03-1.78; maxDD interval $11,796-$37,707. These bounds do not demonstrate a reliably positive recent edge.

**Funded/evaluation/Monte Carlo: not run; registered path-quality gate blocked.** All 1,534 A1 rows were retained; no censored holdings or illegal carries, and full native/no-trade-date coverage passed. The held-path audit separately records 222 recurring legacy 15:16-15:30 gap-pattern trades and two unexplained held-day gaps:

| Date | Missing CT minutes | Original CSV |
|---|---|---|
| 2018-07-26 | 13:43-13:44 | data/NQ_1min_2018.csv |
| 2025-06-02 | 11:03 | data/NQ_1min_2025.csv |

The raw daytime files skip those rows; overnight files provide no replacements. The shared observed-bar replay skips missing OHLC, so it cannot observe an intervening stop/target/account breach. No bars were imputed, trades dropped or unofficial bounding variants run. The account gate is false, with zero account simulations. No payout, blow-up, pass-rate or replacement-gain claim is made. The one-addition/one-replacement/current/empty-slot adapter remains reproducible for a later authorized data-complete study.

Account-scope refresh: while this task ran, `USER_CODE_WORKFLOW.md` was published at concurrent Codex commit `fe84522` (blob `11d532bd92264f6ecb00774ffc34e5ac2ab995e7`). Its broader scope is recorded below. These are limiting conditions, not simulated findings or inferred results at another account size.

| Destination | Result / limiting condition |
|---|---|
| 50K evaluation | Not scored: two unexplained held-price gaps fail the registered account-path gate. |
| 150K evaluation | Not scored: the same candidate path is incomplete; no 50K-to-150K performance inference. |
| 50K funded | Not scored: complete intraday paths and canonical baseline parity are prerequisites. |
| 150K funded | Not scored: incomplete candidate paths; no distinct 150K bootstrap was run. |
| Personal ladder/full portfolio | Not scored: no registered personal comparison opened; source-volume/path uncertainty and failed validation remain. Portfolio contribution is unknown. |

None earns a placement from this evidence. The data gate and failed validation end this trial; no size search or open-ended rescue test follows.

## What could make this wrong

- **Source parity:** chart session/IOG and native up-volume history are unverified. Total volume and midnight chart/session choices are declared proxy assumptions. Literal S1 has three cross-date trades across both periods; A1 has none. The original code has no verified holiday liquidation policy.
- **Data/fills:** unexplained intratrade gaps limit even the standalone proxy. One-point limit trade-through and shared OHLC ordering are fixed assumptions; no exact-version MC export was supplied.
- **Multiple testing:** 291 existing ranked items plus this idea gives t bar 3.581. A1 full t 3.994 clears that bar, but DSR 0.855 fails. Recent t 1.727 misses 2; both t and DSR are required, plus clean checks and plan gain. +5-profile sensitivity is in all_period_metrics.csv.
- **Selection/history:** the upload's original development/selection record is unknown and 2023+ is already seen. No parameters were chosen on those returns here. Positive pooled profit does not validate the added drift filter, diversification or account risk.
- **Account baseline:** the independent review notes an unresolved small prior prepared-cache versus published canonical-funded discrepancy. No new account comparison was reached, so it is neither explained away as rounding nor used to support a candidate.

## Differences between the MultiCharts code and the test

No new MC code or live file was written. Differences: total-volume surrogate; declared full-session/midnight grid and IOG off; one-minute path/one-point target fill convention; A-profile early-close safeguard; research costs; explicit endpoint/data-gap auditing. The independent review is `agents/codex/results/nqdb2_independent_review.md`: implementation arithmetic passes inspection, source/data validation remains WITH CONCERNS.

## Reproduce

Use the configured Python environment; existing caches are inputs, never rebuilt. From the repository root:

```bash
export PYTHONPATH=analysis
PY=/workspace/venvs/thebeginning/bin/python
$PY analysis/codex_nqdb2_run_profiles.py --design --prereg-sha eb7b8b07fd54e8083a13b04f25d1c5b59c68a00b
$PY analysis/codex_nqdb2_test.py --period design
$PY analysis/codex_nqdb2_diagnostics.py --design --prereg-sha eb7b8b07fd54e8083a13b04f25d1c5b59c68a00b
$PY analysis/codex_nqdb2_test.py --certify-design
$PY analysis/codex_nqdb2_run_profiles.py --recent --prereg-sha eb7b8b07fd54e8083a13b04f25d1c5b59c68a00b --gate-file analysis/outputs/codex_nqdb2_test/design_gate.json
$PY analysis/codex_nqdb2_test.py --period recent
$PY analysis/codex_nqdb2_diagnostics.py --recent --prereg-sha eb7b8b07fd54e8083a13b04f25d1c5b59c68a00b --gate-file analysis/outputs/codex_nqdb2_test/design_gate.json
$PY analysis/codex_nqdb2_accounts.py --audit-only --root-authorized --preregistration-commit eb7b8b07fd54e8083a13b04f25d1c5b59c68a00b
$PY analysis/codex_nqdb2_accounts.py --baseline-all-existing --preregistration-commit eb7b8b07fd54e8083a13b04f25d1c5b59c68a00b --out analysis/outputs/codex_nqdb2_test
$PY analysis/codex_nqdb2_test.py --finalize
$PY analysis/codex_nqdb2_test.py --report
```

Do not use --run or --mc against a false account gate. Full generated feature pickles and redundant null samples can be regenerated; published ledgers, metrics, audits and source/cache hashes identify this run. No plan, ranking, live, VPS or broker setting changed.
