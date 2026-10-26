# IFT_NQ5_Flow_Signal: WATCH / NEEDS DATA — worth a careful replication, not cleared

Summary: Author's walk-forward claims are more informative than the headline screenshot, but remain unverified.
Structure was selected using2020–26, so annual parameter refits do not make that structure out of sample.
Source has an unprotected entry bar and a live-only position gate, materially affecting execution and portfolio comparisons.
Owned directional-volume exports lack Globex, so an honest full-strategy backtest is currently blocked.
Do not deploy; obtain native full-session fields and detailed report before preregistered return testing.

Evidence: agents/codex/evidence/ift_nq5_flow.md. Script/output: analysis/codex_ift_nq5_data_audit.py; analysis/outputs/codex_ift_nq5_flow/data_audit.json.
Return trials:0. Claimed performance below is from supplied text/screenshot, not independent reproduction.
Source/note hashes and data inventory retained in data_audit.json.

## What the submitted evidence does and does not establish

The note reports final full-sample~407 positions, PF1.66,~$177k net and~$22.7k DD at2NQ; yearly walk-forward PF1.31/~$21.6k DD.
The screenshot reads approximately$178,115 net, PF1.62 and$23,565 DD. Those are related but not identical headlines; settings/date span/costs and trade grouping must reconcile.
Partial scale-outs can cause trade-row counts to differ from flat-to-flat positions. The screenshot cannot establish a770-row/407-position reconciliation; never treat exit legs as independent trades for a t-test.
No t-statistic, DSR or independent trade-level audit is available from these aggregates alone.

The author deserves credit for disclosing structural hindsight, search size, adverse years and unprotected risk. Those admissions make the claims easier to assess, not automatically verified.
Percent profitable across a parameter grid is supportive but does not itself measure selection-adjusted significance or incremental alpha.
Full-sample and walk-forward outputs require identical contract counts, cost conventions and portfolio-entry rules before comparing PFs.

## Answers to the five questions

### 1. How to test structure out of sample?
Annual retuning is parameter-out-of-sample conditional on a chosen structure. Since sessions/ribbon/delta were designed after seeing2020–26, that period cannot independently validate those design choices.
A genuinely never-consulted2018–19 period and a genuinely prespecified ES transfer are useful structural checks, if provenance supports that claim. ES is correlated equity exposure, has only86 reported positions and uses a short recent span; it is not conclusive independent replication.
Freeze the whole structure, data semantics, selection rule and executable order protocol now. Use subsequent observations as confirmatory evidence.
Any new session/delta/exit changes after viewing results start a new trial. Do not repeatedly mine the2018–19 test or claim a new random partition restores independence.
First require trade-list parity and compare a simple same-session continuation baseline; rerun controls and ablations only under a registered finite budget.
A forward log is meaningful only with sample-size/decision rules chosen before observing it; rare overnight shorts may require substantial calendar time.

### 2. Why might up-volume outperform total volume?
Possible hypotheses: a large up-volume reading jointly encodes activity and upward price pressure; for bearish bars, requiring high up-volume plus even higher down-volume identifies unusually active two-sided trade with negative imbalance.
Normalizing against the last100minutes also mixes time-of-day transitions with activity. The author's worse same-time normalization supports this distinction but does not identify a causal institution.
It could reflect vendor classification, bar aggregation, volatility scaling or selection noise. No mechanism is established by naming it institutional.
Compare up-volume, down-volume and total-volume specifications with matched session/trend/volatility exposure and a frozen price-only baseline; test incremental net value rather than only PF.
Important algebra: (Up-Down)/Up<=−0.35 is Down>=1.35Up. With only these two components, that is conventional (Up-Down)/(Up+Down)<=−0.14894, approximately−14.9%, not−35%. These two delta definitions cannot share the same numerical cutoff.
Verify whether the chart fields use uptick/downtick or aggressor classification; neither the name nor an earlier different strategy's parity proves equivalence.

### 3. Run the entry bar unprotected?
For this proposed Apex use, I would require an initial protective stop from the fill before considering deployment.
The note claims protection changes PF1.66→1.63 and worst position loss$3,110→$2,420; if reproduced, that is a modest average-performance tradeoff for less unbounded first-bar exposure.
Those reported maxima are historical outcomes, not guaranteed limits. Stops can gap.
The provided code does not implement immediate protection. A protected version would be a separately documented change, tested with the same signals and without adjusting thresholds to recover profit.

### 4. What overnight slippage do we see?
We have no verified live fill/quote sample for this strategy's23:00–08:30 window. I cannot honestly supply an empirical average.
One NQ tick is0.25point/$5 per contract; MNQ tick value is$0.50. A per-side tick budget must be charged by each actual fill type/quantity, accounting for passive targets separately.
Observed spread is not total slippage. Order size, stop gaps, queue, release times, latency and quote depth matter.
The author's0–4tick sensitivity is useful conditional evidence, but not measured live slippage or a tail-risk bound. Use synchronized quote/fill diagnostics before accepting that budget.

### 5. ATR or dollar-risk sizing?
The stop already varies with recent extrema and ATR; fixed2-contract quantity therefore leaves variable dollar risk.
Test a dollar-at-stop budget using actual fill-to-stop distance × contract point value plus cost/gap allowance. ATR helps define a scale, but ATR quantity scaling does not cap actual dollar risk by itself.
Do not silently size off the signal-close risk: next-open gaps can change it after the<=2.5ATR check.
The submitted scale-out needs **at least2contracts**. At1MNQ the first1-contract target closes everything; there is no runner. At Qty4 the first exit is still1contract, not half.
For a small account, preserve2MNQ and skip setups above the frozen risk budget; a variable half/half allocation is another protocol requiring separate validation.
Simple scaling of the supplied$22.7k DD from2NQ to2MNQ is about$2,270, already comparable to/exceeding the50K account's$2,000 trail. That does not calculate an account blow-up rate, but defeats automatic claims of prop suitability.

## Material code differences and risks

- **Entry-bar protection:** exits are ordinary next-bar orders inside MarketPosition blocks; no built-in initial stop is present. With bar-close recalculation, the first5-minute position bar is unprotected.
- **Staged exits:** TP2 is not submitted until tp1Done is observed; breakeven also updates at recalculation, not necessarily the instant TP1 fills. A1-minute port that instantly activates both targets/BE can improve fills relative to this source. Bar Magnifier alone is not proof of identical strategy recalculation.
- **OnePos:** enabled only when GetAppInfo(aiRealTimeCalc)=1. Historical entry lists do not enforce the live gate. Broker net position is not a full gross per-strategy inventory ledger; flat net exposure or simultaneous charts can defeat the comment's intended global lock.
- **Direction lock:** first filled side locks the session, so simply adding independently backtested longs and shorts is invalid.
- **Price anchors:** initial stop/TP levels use signal Close, not actual EntryPrice. The alleged1.5R/3R and2.5ATR cap are signal-based; gaps/slippage can change actual risk/reward.
- **Input comments drift:** header mentions other short-window/delta settings; active defaults are23:00–08:30 and0.35. The inputs/code are the replication source, not older headline comments.
- **Short clock boundary:** an08:30 signal submits its order for the next5-minute bar, whose open is at the08:30 cash-open boundary. This is not uniformly an overnight-liquidity sample; separate the final-window entries when measuring execution costs, without selecting a profitable subset afterward.
- **Early closes:** flat decision14:55 cannot execute during a midday holiday halt. There is no early-close calendar guard. An overnight short can persist into the halt/reopen if still active; this needs explicit audit before Apex eligibility.
- **Parent-bar roll/warm-up:** all indicators/rank use the continuous5-minute stream. RTH-only data, zero-filled nights or a different contract-roll construction change the strategy.

## Audited input blocker and exact next files

Owned35OF CSVs:876,077 rows, earliest clock09:30ET, latest16:15ET, zero rows outside that span.
All19native NQ CSVs have only date,time,OHLC,volume. NQ_Bar_Exporter.txt writes Ticks into that volume column.
OFB_OrderFlow_Exporter.txt documents Eastern timestamps and its default RTH window; Volume equals upvol in the audited OF files. It is not the native full-night input required here.
Even long-only source replication needs those missing nights for ratio/rank/EMA/ATR history.

To unblock:
1. Native same-feed full-Globex5-minute export with date,time,OHLC,Volume,UpTicks,DownTicks; include500+prior bars and exact history start. Record chart timezone, session template, volume mode, MaxBarsBack, IOG/recalculation and target-fill assumptions.
2. Detailed MultiCharts report/trade list for these exact inputs, grouping entry, partial exits and flat-to-flat positions. Include commission/slippage settings.
3. Matching1-minute magnifier prices (existing prices may help after feed/parity checks).
4. Claimed Python port plus yearly selected774-grid settings/fold schedule if the walk-forward claim is to be reproduced.
Do not export from or modify the live VPS as part of this task; research-chart/export proposals only.

## Requested account placement status

| Destination | Status |
|---|---|
| 50K evaluation | Blocked: exact full-session directional-volume data absent |
| 150K evaluation | Independently blocked before replay; no inference from50K |
| 50K funded | Blocked before paired addition/replacement/empty-slot bench |
| 150K funded | Blocked before independent sizing/payout replay |
| Personal portfolio | Blocked before integer-size, overlap and equal-capital comparison |

This is incomplete performance validation due to a concrete data blocker, not a negative backtest result.
Verdict: **worth a bounded replication, not ready for live and not rankable from these claims alone**.
No proxy returns, optimization, portfolio change or new performance claim made.

