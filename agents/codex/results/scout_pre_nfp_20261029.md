# ES pre-payroll reopen premium: REJECT

Summary: The frozen pre-payroll adaptation fails its 2018–22 design screen; continue discovery in other families.
55 longs average −$87.29 gross per ES and −$12.47 net per MES; net t −0.89, PF 0.71.
Only 2/5 years profit; matched-calendar p 0.819; 90% year-bootstrap mean interval −$35.81 to +$11.97/MES.
No 2023+ or portfolio outcomes were opened. This rejects our adaptation, not every result in the source paper.

Plan: `agents/codex/plans/scout_pre_nfp_20261029.md`, preregistration/reservation commit `a63d7bc11720b99eb67c69c36812a61216361058`.
Frozen script: `analysis/codex_scout_pre_nfp_20261029.py`; receipt recovery: `analysis/codex_scout_pre_nfp_20261029_audit.py`.
Outputs: `analysis/outputs/codex_scout_pre_nfp_20261029/`. Trials: 1 candidate + 2 controls, all executed and retained.

## Rule as tested

Buy ES at the prior date's 17:06-labelled minute open (17:05 CT wall clock), exit at the payroll
date's 07:25 minute close; protective 1 ATR15 stop, using the already-lagged ATR known at the prior
date's start. No targets, shorts, reentry or sizing selection. Actual upcoming BLS dates were confirmed
in 60 preceding-month official release notices before outcomes. Preset minute-coverage and roll exclusions
leave 55/60 events. Unlike the source, this starts after the maintenance break and adds a stop.

## Results

| 2018–22, all trades = longs | 1 ES gross | 1 ES net | 1 MES net |
|---|---:|---:|---:|
| Trades | 55 | 55 | 55 |
| Win rate | 56.4% | 56.4% | 56.4% |
| Average/trade | −$87.29 | −$117.29 | −$12.47 |
| Total | −$4,800.83 | −$6,450.83 | −$685.78 |
| Event t | −0.62 | −0.83 | −0.89 |
| Daily Sharpe | −0.27 | −0.37 | −0.39 |
| Sortino | −0.32 | −0.42 | −0.44 |
| Profit factor | 0.79 | 0.72 | 0.71 |
| Close-to-close max drawdown | $7,596.67 | $8,770.83 | $913.34 |
| Calmar | −0.12 | −0.14 | −0.15 |
| Ulcer index | 7.06 | 8.37 | 0.88 |

Ulcer uses the shared $50,000 reference capital; daily drawdown is not an account-breach simulation.
Native fees/slippage: $30 round trip per ES; $3.74 per MES. MES stress at $6.24 yields −$14.97/trade.
No short rule registered/run. Recent history not opened.

| Year | Trades | Net, 1 MES |
|---|---:|---:|
|2018|9|−$226.58|
|2019|11|+$157.61|
|2020|12|−$565.80|
|2021|11|+$406.36|
|2022|12|−$457.38|

## Placebos and account level

1,000 same-year/month/weekday calendar-null samples average −$2.00/MES/trade versus −$12.47 for
the actual event rule; one-sided p 0.819. The 2,000 year-cluster bootstrap 90% mean interval crosses zero.
The event-count gate passes; all six economic gates fail. Stop this candidate's later stages.
BASE/ADD/REPLACE/EMPTY for evaluation, funded and personal accounts were not run because design failed.
No current allocations change. Move to a different source-supported hypothesis; no event/window/side rescue.

## What could make this wrong

This is a narrow and underpowered adaptation, not an exact source replication. Continuous contracts lack
contract-identifying quote data; missing-minute/roll exclusions are explicit. Stops derived from ATR are not
rounded to an exchange tick in the frozen replay, and time exits approximate a completed-bar close; those
execution limitations would require resolution before promotion. Negative gross dollars already defeat this
registered protocol without a claim that the paper's original cash-close premium is absent everywhere.
Costs do not include an extra invented benefit from bid/ask timing. Prior repository multiple-testing history
is retained; no significance claim, ranking or independent verification follows.

The run completed trade, daily, year and placebo CSVs, then JSON serialization failed on numpy.bool_.
The audit script reconstructs the receipt from those saved CSVs, with the same bootstrap seed and gates;
it opens no prices, creates no new trades and changes no rule. Native cost identities and trade/daily totals
reconcile. This engineering recovery is not an independent economic checker.

## Paper questions

About: Hu/Pan/Wang/Zhu study compensation for uncertainty before scheduled macro announcements.
Findings: their pre-payroll futures window averages 10.10bp gross, t 3.63 in their older sample.
Why: their proposed impact-uncertainty premium can resolve before the news; it is not a proven forced buyer.
Build on it: this particular implementable reopen/stop adaptation fails. Archive it and continue other families.
[Primary author paper](https://www.mit.edu/~zhuh/HuPanWangZhu_preannouncement.pdf).

## MultiCharts

No code written because the screen fails. No live, VPS, broker or plan files changed.
