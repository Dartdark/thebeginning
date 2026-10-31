# Bilateral equity-hedge demand before month-end London fix: NEEDS DATA

Summary: a DISTINCT pairwise US-minus-Eurozone equity-return proxy could predict pre-fix EURUSD hedge pressure.
The documented portfolio-hedging actor and benchmark clock justify source intake, not a return test yet.
Equal hedge sensitivity/notional, actual flow size and the pairwise translation are assumptions, not a paper replication.
New public index metadata has been located; actual identity, history, publication/adjustment provenance and calendar are unadmitted.
This sheet precedes any data intake; no strategy returns or new signal values have been read/calculated.

Sources: Melvin–Prins2013 paper as cited in saved `month_end_fx_hedging_feasibility.md`; source-resolution
limits in `agents/codex/research/hunt_v2_prefix_equity_source.md`; current ranking/source pin615485f;
existing `fx_fix_reversal.md` plan/source; newly located public README metadata described below.
Prior returns/selection: old post-fix reversal and other FX/calendar work are already known. This pairwise
pre-fix rule is not a new result. Root owns counts; checkpoint3/60evaluations,2/10hypotheses,2gross screens,
plus archived65t6evaluations. This NEEDS DATA sheet itself adds0/0/0 and does not become H03 automatically.

## 1. Who trades, and what forces or causes the trade?

International equity investors with benchmark currency-hedge mandates adjust their hedges when foreign
equity portfolio values change. An investor keeping a fixed hedge ratio must sell additional foreign
currency after the value of those foreign equities rises, all else equal. The saved primary-paper review
documents month-end hedge adjustment near the London16:00benchmark, with orders submitted at least an
hour earlier. This supplies a credible participant and reason to accept benchmark execution rather than
optimise the minute's price. It does not identify actual current investors, their holdings or their orders.

Hypothesis for a bilateral proxy: stronger US than Eurozone equity performance requires relatively more
USD selling/EUR buying by currency hedgers, so EURUSD appreciates before the fix; reverse when Eurozone
outperforms. Equal aggregate hedge sensitivity/notional across the two exposures is an explicit simplifying
assumption. Flows may net across global portfolios, be prehedged earlier, or be absorbed by dealer liquidity.
This is an independently stated price-to-demand proxy, **not a faithful Melvin–Prins statistical replication**.

## 2. Direction, size and timing known before entry

Proposed specification for source feasibility only, NOT a committed return-test plan:

- Input direction: `sign(R_US_MTD - R_Eurozone_MTD)` using independently identified broad equity indices,
  price-return conventions and only completed/publicly available prior-day values. Positive means long
  EURUSD/M6E; negative short; zero skip. No price threshold, favorable-month subset or timing search.
- A common-slope cross-sectional model would cancel the shared cross-country mean in a bilateral
  difference. That is an algebraic justification for this proxy under stated assumptions, not a verified
  equation/country-index list from the original paper. US-only returns are not substituted.
- Event calendar proposal: the FINAL WEEKDAY of each month only when UK AND US financial centres are
  independently known open; otherwise skip the whole month, never move it earlier after outcomes.
- Tentative mechanism clock: decision15:00Europe/London, exact next native-minute open, fixed15:55London
  liquidation before the fixing window. Root must freeze receipt delay, signal-close/bar-open labels and
  any stop before an economic preregistration. This clock is a new explicit translation of the documented
  pre-fix demand, not evidence that actual orders occur uniformly over that hour.
- Equity event_time=the relevant completed index close; available_at=verified source publication/receipt
  time, not the current download timestamp. Prior-day close must satisfy available_at≤decision_time.
  Exact month base/as-of/holiday alignment and revisions must be frozen after schema/source admission,
  before derived equity returns/signals or futures returns. A late or unknown input means no signal.
- Proposed executable size1wholeM6E, maximum1position/1ticket on an eligible month-end. No stacking or
  pyramiding. Dollar demand and fraction of6E/M6E volume are **unknown**: equal sensitivity is not a measured
  hedge notional. Do not derive a fictional required flow amount from an index percentage change.

## 3. Does the flow reach the traded contract or its direct hedge?

EURUSD spot/forward hedge orders directly change relative euro/dollar exposure.6E/M6E futures reference
the same EURUSD risk and are linked by arbitrage, so transmission is plausible. Spot or forward demand
does not guarantee a futures fill at the same quote, nor compel hedgers to use M6E. Banks can net orders,
warehouse inventory or hedge through forwards/swaps. No automatic NQ/ES transmission or portfolio hedge
is claimed. Adding a different instrument can diversify the book only if aligned results/path timing
later demonstrate it; the instrument name alone is not an offset before a drawdown breach.

## 4. New information and data feasibility

|Input|Source/product/fields|Coverage/warm-up|Point-in-time/revisions|Ownership/cost/status|
|---|---|---|---|---|
|US broad equity index|Public metadata: `MohammadrezaAmani/Global-Stock-Market-Indices-Historical-Dataset`; advertised `global-stocks/bourse_sp-500.json` OHLC/Gregorian/Jalali|Actual span/duplicates/holes not read; preceding month-end and prior-day history required|Instrument/provider, close timezone, price vs adjusted/total-return, correction/version history unverified|README metadata newly found by root; raw JSON NOT admitted/read; no purchase|
|Eurozone equity index|Same repository advertises a EuroStoxx50JSON; exact tree path remains to verify|Actual span/coverage not read; EuroStoxx50 would be an explicitly chosen large-cap proxy, not the paper's certified universe|Currency/close/adjustment/source provenance unverified; filename does not prove index identity|Public discovery only; no raw prices or signals read|
|Month-end fix service|Saved primary institutional clock plus WMR methodology/service documents referenced in prior feasibility note|2018–26 ordinary both-open-date policy and exceptional closure evidence unresolved|Current policy is not itself a historical service/receipt log|No new blocked-host request; no complete-calendar claim|
|Financial-centre calendars|Authorities for UK and US ordinary holidays, observed days and exceptional closures must be pinned|Entire design/validation period|Bank-centre holidays, exchange holidays and benchmark service are distinct|Source definition still to verify; final-weekday both-open restriction is prospective only|
|6E minute observations|Existing owned native futures file inventory; no price rows opened here|Full2018–26 and native clock/gap/roll audit later|Native close labels/DST and actual contract transitions need audit|Owned observations; does not prove M6E quote/fill history|
|M6E native costs/ticks|Contract size12,500EUR; tick.0001=$1.25 as cited in prior CME spec review|Historical contract-era/fee assumptions must be explicit|M6E fills, spread and actual commission basis are not verified by6E prices|Proposed fee assumption below, not a new observed brokerage rate|

New README metadata pin supplied by root: blob`9fcd21a4c56d86f4f1c521de2ed11041978315be`.
The exact two data paths must be checked from repository tree metadata; a misspelled/absent advertised path
is unresolved, not permission to substitute a different series. Root may admit at most the two named
equity JSONs for a separately scoped NON-RETURN coverage/provenance audit after this mechanism is saved/
committed. That intake must not compute candidate MTD signs, price correlations, futures P&L, grids of
alternative series or any2023+economic validation. A successful parse is not a TEST decision.

There is incremental cross-country equity exposure information relative to6E's own price momentum/reversal;
the proposed pairwise notional mapping remains a model assumption. If identity/publication or historical
coverage cannot be established, stop at NEEDS DATA. Do not silently use SPY_daily.csv, whose instrument
identity the prior feasibility note already questions, or invent missing Eurozone/global exposures.

## 5. Costs and actual intraday gaps

Proposed research cost assumption for1M6E: **$1.24round-trip commission plus one adverse native M6E tick
on EACH fill**=$1.24+$1.25+$1.25=**$3.74RT**. Gross2xcost hurdle would be**$7.48/event**, approximately5.984
EURUSD pips at$1.25/pip/M6E. The commission amount is a prospective assumption requiring a credible fee
basis before TEST, not a verified broker quote, and is not inferred from MNQ's tick value. Actual spread/
latency/liquidity stress must be frozen; full6E costs cannot simply be divided by ten.

No new gross effect has been measured. A bid/ask or adverse-tick allowance must be charged once, not twice;
missing quotes/fast fills cannot be described as established native micro execution. Calendar-specific
UK/US DST conversion is mandatory. This window falls during US RTH and can overlap VB/DT/RS and other
current pieces. Current OvernightTick also invalidates the task's stale claim that all01:00–03:00hours
are always empty, but this candidate does not use that interval. Do not select month-end events based
on later book P&L or whether the book happens to be flat.

## 6. Power before a return test

Calendar ceiling is60month-ends for2018–22 before both-open restrictions, warm-up and data loss; actual
eligible count is unmeasured. The user prefers≥100trades, so this small sample needs unusually clear
effect/cost evidence and honest uncertainty; do not add days or count minute bars as independent events.

Planning assumptions only: at n60, per-event SD$10 implies net mean≈$2.58 for t≈2, so gross≈$6.32 after
adding$3.74cost; the separate$7.48gross gate is stricter. At n40 and SD$20, net mean≈$6.32, gross≈$10.06.
Formula `2*assumed_SD/sqrt(n)` is not a promotion test or an observed SD. Monthly clustering, differing
hedge notionals and prior family selection can reduce effective information. No checked primary magnitude
currently establishes that this proxy can clear the hurdle. Intake should stop rather than proceed if
the expected required move is unsupported or the resulting sample is inadequate under the frozen gate.

## 7. Already tested and falsifiers

Source/ranking inspection at615485f plus targeted code reads:

- `analysis/codex_fx_fix_reversal.py` / prior plan: trades AFTER the fix, fading6E's own15:30→16:03move,
  two holding horizons. That failed family shares the benchmark clock but not this lagged relative-equity
  predictor/pre-fix direction. Do not rerun it as a control without its own retained prior history.
- `analysis/anti_forced_flow_ideas_test.py`: NQ post-Treasury-auction reaction and trapped overnight inventory,
  not a US-minus-Eurozone month-end currency-hedge input.
- `analysis/forced_flows_round5_test.py`: US stocks-versus-bonds pension rebalancing over the last3days,
  not bilateral foreign equity currency-hedge adjustment at London fix.
- `calendar_flows2_test.py`, `forced_flows3_test.py`, latest TIER_LIST/MINED_INDEX and the saved FX feasibility
  note establish calendar/European-close/FX prior history; the scoped search found no exact pairwise
  US-minus-Eurozone PRE-fix rule. This is a bounded novelty statement, not proof no related study exists.

Falsifiers BEFORE prices: cannot verify the two instruments/point-in-time closes/calendar/cost assumptions;
unable to justify direction without choosing a favorable proxy after returns; gross below2xcost; source or
holding gaps incompatible with frozen execution. Later: negative design/validation, failed identical-exit
random-time/random-side placebos, selection/dependence failure or no plan improvement versus BASE AND EMPTY.
Failure never authorizes changing countries, weights, timing, thresholds or bar availability after results.

## 8. Failure and diversification

|Question|Prediction before results|Evidence needed / refutation|
|---|---|---|
|What stops the mechanism?|Hedge ratios/holdings differ, fund flows net, execution occurs earlier, arbitrage absorbs demand|No gross differential versus calendar/price-only/random-direction controls; known participation/timing change|
|Liquidity role?|Marketable next-minute order and liquidation consume liquidity near a benchmark|Native spread/receipt/fill evidence or frozen conservative stress, not a spot-mid backtest|
|Loss clustering?|Month-end macro/news or dollar risk-on moves overwhelm weak proxy; rate/FX regime shifts|Both sides/by-year/common-loss analysis and dependence-resampling with monthly event clustering|
|Shared book losses?|USD/equity risk can link it to NQ momentum despite a different ticker; exact signs unknown|Aligned VB/DT/RS/current19 P&L and conditional losses; no correlation claim now|
|Offset before breach?|Unknown; a later FX gain cannot repair an earlier account breach|Valid joint intraday paths/account replay; daily personal MC alone cannot certify funded/evaluation benefits|

Prospective exposure cap1M6E/1ticket/month-end, fixed pre-fix time liquidation; exact stop and active-entry/
worse-gap rules require later preregistration before returns. No target optimisation or overnight hold.
Known holidays/early closes must prevent holds beyond the appropriate session or15:59CT for Apex.
Data failures mean no signal or unresolved-path veto under a frozen policy, never favorable deletion.
No sizing from a smooth short record. If later eligible, current whole-contract BASE/ADD/REPLACE/EMPTY
book comparison must follow design pass immediately, with paired one-year personal MC or valid current
funded/evaluation joint paths. Missing account paths are limits, not invented payout/pass improvements.

## Decision and next gate

**NEEDS DATA — permit only a newly scoped non-return intake/provenance review after committing this sheet.**
It is NOT permission to calculate strategy signals/returns, register H03, select an exit or backtest the
public repository's implementations. Exact primary formula remains unverified; this bilateral proxy must
stay explicitly separate. Only after source identity, history, information clocks, restricted fix service,
native costs and power support TEST may root update the evidence and COMMIT≤5frozen economic configurations.
Then2018–22gross first, stopped design only if it passes, immediate book bench, committed selection, and
previously seen2023+validation once. Full promotion/placebo/independent-checker gates remain unchanged.
No PL draft, trading or deployment follows from intake. No external messages/purchases/accounts/settings.
