# Weekly NQ/VIX adaptation: TEST — cheap design screen only

Summary: User explicitly authorizes filling the original paper's missing formulas with reasoned assumptions.
This is a new personal-account adaptation, not recovery or validation of its claimed metrics.
Owned NQ RTH minutes2017–26and cash VIX daily permit a bounded weekly signal/daily-mark design screen.
One full rule plus one EMA-only comparator; no tuning or forced positive outcome.

## Evidence questions

1. Mechanism: equity drift/trend persistence, with equity-vs-fear relative strength as a proposed regime filter.
   No forced counterparty or verified institutional flow. This is weaker prior evidence than scheduled flows.
2. Direction/clock: long only. Completed Friday RTH weekly prices and Friday final VIX known by next Monday;
   decision Monday07:59CT, entry/exit first08:00CTbar OPEN. The08:00bar closes08:00and opens07:59;
   to avoid using its open before the decision, **execute08:01close-labelled bar OPEN at08:00CT** instead.
   No same-Fridayclose fill, unfinished VIX or revised intraday reconstruction. Final weekly RSI etc descriptive.
3. Transmission: trade NQ/MNQ directly; VIXcash is a feature, not a VXfuture or an actual hedge.
4. Data: read existing local raw exports without altering their checkout; verify Git blob identity against
   current codex/work before use, retain hashes and aggregate daily/task inputs. No new external data needed.
   Weekly Monday–Friday RTH aggregation, last available session; missing Monday delays to first actual
   weekday session. Final VIX from last observed date <=Friday, max7calendar days; no indefinite fill.
5. Costs/gaps: source weekly holds have no Apex fit. Test oneMNQ($2/point) with$1.25round-tripcommission
   and0.25pointslippage per market leg, so$2.25total; NQreference$7.25+$10slippage=$17.25.
   No implied margin sufficiency or exchange/broker guarantee. RTHdaily marks cover gross overnight gaps
   in close-to-close P&L, but not every overnight intraperiod adverse excursion. Fullrisk needs later replay.
6. Power: at most~261design weeks; original frequency suggests only~20independent holds. Minimum20closed
   trades and t>=2for cheap advancement, plus baseline/Sharpe/profit rules in preregistration. No claim of
   confirmed power; full-time series dependence and multiple-testing remain later hurdles.
7. Dedup/falsifiers: original source5630830was rejected for unverifiable metrics/formulas, not a run of this
   definition. Preserve that history. Reject on failed fixed design gates; no alteredRSI/EMAorstop after outcomes.
8. Failure/diversification: whipsaw and gaps can coincide with equity-book losses; no hedge promised. Market
   orders have slippage. Weekly close5%losscondition becomes next-sessionmarketexit, not loss cap. Only one
   open position. Missing NQ execution aborts rather than impute fills; missing VIX forbids newcandidateentries
   and exits an existing candidate. Quarterlyroll quarantine is defined before outcomes in the plan.

Decision: TEST a single explicitly assumed full rule and its simplebaseline on2018–22only, with2017warm-up.
Native dated-roll ledger/full collateral not established by this screen. No funded/evaluationbench; personal
comparison only after earned validation and fullrisk/native cost gates. No live/plan/rank/scoutchanges.
