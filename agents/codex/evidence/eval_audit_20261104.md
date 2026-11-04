# Evaluation portfolio and sizing audit — evidence before outcomes

Summary: The user requests a broad audit after four failed evaluations, including sizing and replacement books.
Latest committed account records contradict treating chart-signal parity as broker-fill parity.
Some planned trade losses exceeded remaining floor/DLL room; inherited evaluation simulators also misstate rules.
Use a new bounded, counted portfolio comparison on existing frozen strategies; no new alpha optimization.
Research only: no trading, purchase, plan allocation, deployment, VPS, broker or key changes.

Sources: local codex/work0da4e8f and read-only Claude13e29ca7b45daabeb0ed2d8c286448610f594dab;
source/input hashes and required controls are bound in inputs/eval_audit_20261104/config.json. This direct new
user task is separate from paused t6/Huntv2 and the paper scout. Preserve all their trials/status/budgets.

## 1. What causes the financial opportunity or failure?

This is account-risk allocation research, not a newly discovered return signal. Existing strategy edges/selection
histories remain. The evaluation contract is a first-passage problem: positive expected strategy P&L does not
ensure reaching a target before an intraday floor or a calendar expiry. An oversized trade can be liquidated at
the account floor before its own stop; smaller size may improve survival but produce more expirations.
Alternative signal mixes can change the timing and joint shape of losses. None is presumed superior in advance.

The forensic note identifies #1 lostOctober26,#3October30,#2/#4November4. #3's roughly$1,823cushion was below
its$2,456planned ONB loss; November4cushions around$931/$1,940were below$1,062/$2,478planned ONB losses.
These are committed-source observations and arithmetic, not independently obtained broker statements. Late
chart trades after liquidation and daily-lock rejections cannot be called filled trades. Do not assume all
four failures were either software defects or independent bad-luck draws.

## 2. Information, sizing and execution clocks

Use source-recorded existing entry/exit signals, exact declared chart compression and source stop formulas known
before entry. Reconstructed initial risk must not come from a later stop exit. One price per asset values all
sleeves; opposing NQ sleeves must net. Native integer micro quantities apply separately to50K/150K accounts.
Allocation decisions may use current equity, already known EOD floor, daily opening equity and source stop risk.
They may not use the future worst path, subsequent signals or later account profitability.

Hard risk admission: any detected incomplete required observed risk input makes dependent sizing risk NaN;
its owned-feed estimate is diagnostic only. Wholly absent candles are not proof of complete risk history.
Known unresolved expected-open holes cannot grant integer size or a certified governor reserve. Missing
required source/settings evidence remains UNKNOWN; only explicit dated closures remove nontrading intervals.

Official EOD evaluation rules are pinned in primary_rule_receipts.json. Starting floors48,000/146,000;
targets53,000/159,000; daily limits1,000/2,000; max60/120micro equivalent aggregate net exposure. Floor is
touched intraday but ratchets on EOD balance. The PA starting+$100floor lock is not the evaluation lock.
Use an explicit30-calendar-day expiry convention rather than silently treating21trading sessions as identical.
Unknown actual purchased expiry/fee/installed guard inputs remain distinct from a model convention.

DLL/floor liquidations use prevailing modeled executable marks plus costs, not an invented perfect threshold
fill. Cancel later source orders after failure; pause entries after a DLL event until the next account session.
Current baseline does NOT assume a new account-level immediate target guard is installed. Guard-only variants
are explicitly prospective execution-policy counterfactuals. Source-close timing and within-minute order remain
conditional OHLC reconstruction, not recovered broker tick chronology.

## 3. Markets and source strategy universe

The full368-row latest registry was screened as metadata, not called368distinct strategies. Thirty-six curated
families retain eligibility/exclusion reasons. Eighteen existing-source candidates have primary/conditional
ledger adapters across NQ/MNQ,ES/MES andCL/MCL. Disallowed multi-day holds, failed designs, missing signals and
daily-only paths are not converted into usable evaluations by optimistic sizing. NBL's unresolved early-close
carry and Ricochet's failed design are retained as exclusions; no renamed rescue signal is created.

The frozen primary data window is2018-04-02through2026-07-07, common to the declared normalized source studies.
Last trade is not sampling end. Original MC settings/source-run declarations establish no-signal coverage;
no OT or other source is zero-extended past known coverage. Recent October/November losses are seen forensic
stress context, not an untouched selection period or an excuse to tune directly to four failures.

## 4. Inputs and feasibility

|Input|Evidence/availability|Limits|
|---|---|---|
|Owned one-minute NQ day/ON,ES,CL exports|Explicit registered file lists, hashes, timestamp inventory and Grid24|Continuous contract/quote identity and within-minute chronology unverified; no missing-price interpolation.|
|Fourteen primary normalized source ledgers|Prior portfolio audit source window and hashes|Inferred MC fill clocks, some held gaps and prior source model assumptions remain visible. VB_N/F are sizing partitions, not new independent alpha.|
|FC2B/ST/PT/VCS source adapters|Frozen CSV/workbook/PL hashes and causal clock/stop reconstruction|Known open/close clocks cannot move to an earlier favorable touch. Stop/target/source-feed uncertainty retained.|
|Account rules and exchange clock|Official primary receipts plus historical CME pause-removal filing|No unverified full historical holiday calendar or silently invented executable closed-market mark.|
|Recent failures|Pinned journals,raw ACCT,health/rejection records|Chart signals are not confirmed broker fills; missing official statements limit exact incident attribution.|

The verified preJune28,2021index pause may be omitted only when every potentially held asset is closed and no
source order occurs. This is absence of a trading event, not filled missing returns. Reopened observed quotes
carry gap risk. Unexplained missing held quotes remain UNKNOWN. Cross-asset mixed open/closed valuation and
material source/target/clock ambiguities remain flagged; they cannot become a certified native pass by omission.

## 5. Costs and actual account fit

Primary model:1.24RTcommission per native micro, one adverse tick per market/stop fill, no market-exit slippage
on a source limit target. Trade-through qualification is frozen at NQ 1.00 point, ES 1.00 point and CL 0.01,
in addition to causal source-fill/phase checks; a failing material qualification becomes an UNKNOWN reached
fill rather than a free target. Native point valuesMNQ2,MES5,MCL100. Low-fee1.04and stress2.48RT/two-tick scenarios are
unselectable diagnostics on frozen nominees only. These are model assumptions, not a newly verified broker fee
schedule. Source reports and account MTM costs are reconciled rather than dividing mini net by10.

Fixed current book:50K VB8,ONB30risk1100,EOSrisk500,Bridge2;150K VB20,ONB30risk2750,EOSrisk1250,Bridge5.
VB stop is75points, not its0.30ATRentry-noise setting: nominal8/20MNQ losses1,200/3,000already exceed the
1,000/2,000daily pause before costs. Portfolio/account risk is therefore not protected by every strategy stop.
New entry governors reserve open-position stop exposure and both floor/DLL room; they do not guarantee fills
through a gap. No-stop Bridge/OT risk is not invented as a finite source stop under such governors.

## 6. Power, selection and comparisons before returns

Roughly250weekly design purchase starts have heavily overlapping30-day histories, not250independent accounts.
Effective information is smaller; a few tenths of a percentage point is unlikely to prove an improvement.
Primary ranking uses2018–22only and counts every registered allocation, including failures, duplicates aliases,
controls and unused reserved definitions. Source2023+has been repeatedly seen; later checks are historical
validation, never a fresh holdout. No new strategy entry/indicator tuning is authorized by this experiment.

Use paired4/8-week-block,5,000-replicate uncertainty for pass/fail/expiry differences; unknown outcomes retain
identification bounds. A successful historical portfolio could still fail in a new regime. Lower failures alone
do not establish lower cost if expirations increase. Fee multiples1/Ppass are separate from the conditional
150K$249purchase-price example; no unsupported$24950Kfee or funded-income extrapolation.

Full potential 30-day source coverage is checked before replay, a conservative rule that may retain an UNKNOWN
even when an early outcome might otherwise be known. Sparse safe-segment acceleration does not establish exact
joint account max drawdown; preserve visited minima and separately labeled conservative bounds.

## 7. Falsifiers and prior work

Read loss_forensics.md,prior_search.md,engine_audit.md and registry inventory. Old72grid/21latest sizing labels,
ONBML swaps, cushion gates, risk caps and strategy-addition studies remain prior selection. Do not count an
old policy as new independent support or assert that four recent sizing examples exhaust all possible policies.
Reject a superiority claim if it disappears under correct floors, market liquidation costs, source coverage,
integer sizing, held-path uncertainty, chronological validation or paired uncertainty. No winner is an allowed
result. A benchmark with unresolved source inputs cannot certify a globally optimal allocation.

## 8. Failure/diversification predictions

|Question|Prediction and required check|
|---|---|
|Mechanism failure|Existing source edge weakens; fitted book selects historical luck. Check held-out chronology and regime/cost stress.|
|Liquidity role|Marketable entries/stops/forced exits; source target limits. Missing quotes and same-minute timing can change barriers.|
|Loss clustering|Shared NQ beta, overlapping long positions, same starts, DLL loss locks and gap exits. Preserve joint source dates.|
|Common losses|Current VB/ONB dominate account risk; morestrategylabels need not reduce net exposure or simultaneous losses.|
|Offset before breach|Only synchronized intraday account replay can establish this; later chart winners after broker death do not offset failure.|

## Decision

**TEST: bounded portfolio/sizing comparison on explicitly conditional source paths.** Publish the frozen plan,
code,input hashes,calendar/rule receipts and counted registry before any new account outcome. This does not
admit every source as native execution truth. Data/model gates may yield only a provisional frontier or no
eligible winner. Do not stop at the forensic findings; carry eligible comparisons through earned validation,
uncertainty and independent review, while retaining material limits and every live-system boundary.
