# NQ Overnight Rebound: WATCH — profitable replication, no allocation recommendation

Summary: 1,004 source tickets; full PF 1.27 UNIFORM / 1.33 SUNDAY2, materially weaker than supplied claims.
Full t 2.59/2.90 fails the 3.61 ranked-item bar and 3.79 sensitivity for 336 author versions; direction is stronger than random, filter benefit unproven.
Current 17-leg personal ADD raises 2023+ mean annual profit by $2,402/$3,847, but DD95 by $842/$861; portfolio return/DD does not improve.
All 50K/150K evaluation/funded comparisons are LIMITED by missing causal joint overnight baseline paths, not by legal calendar-date crossings.
821 unobserved held minutes, cache timing differences and absent original MC trades prevent exact parity. No live/ranking/allocation change.

Plan: [`overnight_rebound.md`](../plans/overnight_rebound.md), **d94d815** committed before new returns.
Models: UNIFORM down-day Qty1, source-default SUNDAY2, ALLNIGHTS unfiltered control (not selectable).
Prior search: author336 versions plus unknown filters. No new parameter grid or rescue optimization.
Scripts: `analysis/codex_rebound_run.py`, `codex_rebound_engine.py`, `codex_rebound_diagnostics.py`, `codex_rebound_accounts.py`, `codex_rebound_report.py`.
Source/snapshots: `agents/codex/inputs/rebound/`; outputs: `analysis/outputs/codex_rebound/`. Current17-leg baseline pinned toe1a94f7.

## Rule and clock as replayed

Cash08:31-labeled open through15:00 close CT; arm if close<open, stop .5×cash high-low. First available close>=17:01 submits next-native-bar buy.
Normally17:02-labeled entry open and03:01-labeled next-bar exit open after03:00 decision. Friday down-day arming can enter Sunday; sourceSundayQty2
is determined by the raw ET chart date at submission. ET-display/-60 is normalized into CT; the CT cache is not shifted by another hour.
Uniform and Sunday2 have identical ticket/price paths; quantities and per-contract fees multiply exactly once. Long only; shorts0, metricsN/A.
Source08:31–15:00 safety exit retained. No new16:45ET or weekend cutoff was inserted, despite the prose's stronger guarantee.

Actual cache entry labels:543 at17:03,460 at17:02,1 at17:32. Those correspond to next-bar opens approximately one minute earlier.
Earlier history frequently has no17:01 native bar, causing the source to submit at17:02 and fill17:03. No missing bar/earlier price was fabricated.
Timing differences can affect the early/late-period comparison and claimed MC match. Known CT schedule is a declared proxy, not verified author-feed parity.
All three design2018–22 runs precede validation2023–October9,2026; previously inspected history is not fresh holdout.

## Results and costs

Per-unit NQ pays$7.25 RT plus1tick each entry/exit ($17.25 total), multiplied by actualqty. Native baseMNQ pays$1.24 RT plus$.50 eachfill;
$1.04 and author's$1 zero-slippage conventions remain separate. Source SUNDAY2 means1baseMNQ ordinary nights and2MNQ Sundays.
Tickets are distinct nights; summed contracts are not independent samples. Equity is booked to the actual17→16 account session.
Initial zero counts in drawdown, all/long are identical, and all dollar figures below use the stated NQ-cost model unless labeled otherwise.

| Model | Period | Tickets | Contracts | Win | Net/ticket NQ | t | Sharpe | Sortino | PF | Calmar | Ulcer | Closed EOD DD/NQ |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| UNIFORM | 2018-22 | 576 | 576 | 51.7% | $82.09 | 1.42 | 0.63 | 0.96 | 1.19 | 0.45 | 8.69 | $20,373.25 |
| UNIFORM | 2023+ | 428 | 428 | 58.2% | $231.48 | 2.17 | 1.10 | 1.74 | 1.34 | 1.10 | 5.98 | $23,296.75 |
| UNIFORM | all | 1004 | 1004 | 54.5% | $145.77 | 2.59 | 0.86 | 1.35 | 1.27 | 0.70 | 7.45 | $23,296.75 |
| SUNDAY2 | 2018-22 | 576 | 692 | 51.7% | $105.04 | 1.42 | 0.63 | 0.98 | 1.20 | 0.47 | 9.80 | $25,229.75 |
| SUNDAY2 | 2023+ | 428 | 510 | 58.2% | $360.55 | 2.54 | 1.29 | 2.23 | 1.44 | 1.44 | 5.62 | $27,647.00 |
| SUNDAY2 | all | 1004 | 1202 | 54.5% | $213.96 | 2.90 | 0.96 | 1.61 | 1.33 | 0.86 | 8.23 | $27,647.00 |
| ALLNIGHTS | 2018-22 | 1245 | 1245 | 52.2% | $49.34 | 1.31 | 0.58 | 0.86 | 1.12 | 0.53 | 6.02 | $22,739.50 |
| ALLNIGHTS | 2023+ | 938 | 938 | 55.2% | $147.24 | 2.33 | 1.19 | 1.82 | 1.24 | 1.30 | 9.31 | $27,312.50 |
| ALLNIGHTS | all | 2183 | 2183 | 53.5% | $91.41 | 2.64 | 0.88 | 1.34 | 1.18 | 0.74 | 8.44 | $29,837.00 |

| Model | Year | Tickets | Native net/baseMNQ | PF/NQ costs |
| --- | --- | --- | --- | --- |
| UNIFORM | 2018 | 121 | -$677.29 | 0.83 |
| UNIFORM | 2019 | 110 | $988.60 | 1.43 |
| UNIFORM | 2020 | 107 | $2,573.07 | 1.42 |
| UNIFORM | 2021 | 108 | $2,096.08 | 1.50 |
| UNIFORM | 2022 | 130 | -$548.95 | 0.94 |
| UNIFORM | 2023 | 99 | $974.74 | 1.27 |
| UNIFORM | 2024 | 119 | $895.44 | 1.15 |
| UNIFORM | 2025 | 112 | $4,523.87 | 1.59 |
| UNIFORM | 2026 | 98 | $3,292.73 | 1.29 |
| SUNDAY2 | 2018 | 121 | -$582.80 | 0.88 |
| SUNDAY2 | 2019 | 110 | $1,141.55 | 1.40 |
| SUNDAY2 | 2020 | 107 | $3,346.82 | 1.45 |
| SUNDAY2 | 2021 | 108 | $2,731.26 | 1.54 |
| SUNDAY2 | 2022 | 130 | -$942.91 | 0.92 |
| SUNDAY2 | 2023 | 99 | $1,548.91 | 1.36 |
| SUNDAY2 | 2024 | 119 | $2,138.65 | 1.30 |
| SUNDAY2 | 2025 | 112 | $6,930.36 | 1.77 |
| SUNDAY2 | 2026 | 98 | $4,551.18 | 1.33 |
| ALLNIGHTS | 2018 | 245 | $638.95 | 1.14 |
| ALLNIGHTS | 2019 | 249 | $1,203.74 | 1.26 |
| ALLNIGHTS | 2020 | 250 | $4,176.00 | 1.31 |
| ALLNIGHTS | 2021 | 251 | $817.51 | 1.08 |
| ALLNIGHTS | 2022 | 250 | -$1,334.50 | 0.93 |
| ALLNIGHTS | 2023 | 248 | -$590.77 | 0.95 |
| ALLNIGHTS | 2024 | 249 | $4,278.49 | 1.41 |
| ALLNIGHTS | 2025 | 247 | $6,752.47 | 1.42 |
| ALLNIGHTS | 2026 | 194 | $2,887.94 | 1.14 |

## Comparison with the supplied January2018–July2026 claims

Claimed uniform966tickets,55%wins,PF1.38,$2,240/year,DD$2,290 perMNQ; Sunday2PF1.44,$3,100/year,DD$3,020.
The separate mixed-size MC report claims966tickets,PF1.47,$275,430 net and$33,880 strategy DD per1NQ/Sunday2.
No report/trade export was supplied to verify its costs, intrabar assumptions or923shared-day/corr.97 claim.
Our same-calendar-window comparison below uses **the author's $1/baseMNQ RT and zero extra slippage**:

| Model | Tickets | Contracts | Win | PF | Net/year/baseMNQ | Closed EOD DD | Avg win | Avg loss | Worst ticket | Time exits | Stops | Sunday tickets |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| UNIFORM | 977 | 977 | 54.7% | 1.29 | $1,739.85 | $2,291.25 | $124.93 | $118.22 | -$898.25 | 819 | 158 | 191 |
| SUNDAY2 | 977 | 1168 | 54.7% | 1.37 | $2,610.79 | $2,729.75 | $156.91 | $140.14 | -$898.25 | 819 | 158 | 191 |

This does not reproduce966tickets or the claimed return strength. Closed equity DD and MC's open-position strategy DD are different quantities.
No return-selected time/price adjustment or deleted mismatch was used to force a match. Source entry/stop/time gap handling and unknown feed differences remain.

## Does the down-day filter add value?

ALLNIGHTS uses the same source stop/entry/exit but permits every valid cash session. Every down entry matches its all-night counterpart exactly.
Compare **total dollars**, not only per-trade PF:

| Period | Down nights | All nights | Down net/NQ | All-night net/NQ | Removed net/NQ | Removed avg | Removed t | Random keep >=down net | Down beats random on net+DD |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 2018-22 | 576 | 1245 | $47,281.50 | $61,428.75 | $14,147.25 | $21.15 | 0.43 | 20.7% | 55.8% |
| 2023+ | 428 | 938 | $99,072.00 | $138,112.00 | $39,040.00 | $76.55 | 1.04 | 11.6% | 52.6% |
| all | 1004 | 2183 | $146,353.50 | $199,540.75 | $53,187.25 | $45.11 | 1.06 | 7.0% | 80.2% |

The excluded up/flat nights are profitable overall (+$53,187/NQ, mean+$45,t1.06), so the required removed-trades-lose condition fails.
The down filter improves PF/average and lowers drawdown, but gives up profitable trades; net/DD advantage over random removal is not stable in both eras.
This is not proof that up nights have an independent edge, nor permission to adopt the all-night control. It weakens the filter's incremental claim.

| Model | Fixed null | Actual NQ/ticket | Null mean | Null >=actual |
| --- | --- | --- | --- | --- |
| UNIFORM | random_time | $145.77 | $133.33 | 25.7% |
| UNIFORM | random_side | $145.77 | -$20.16 | 0.4% |
| SUNDAY2 | random_time | $213.96 | $172.53 | 4.4% |
| SUNDAY2 | random_side | $213.96 | -$10.99 | 0.6% |

500runs/family/model,502,000 closed signals each, no omitted nulls. Random-time evening entries use the cash signal already known before entry;
there is no future direction label. UNIFORM timing is not distinct from random evening times (p.257); SUNDAY2 timing p.044 is weak after prior search.
Long direction beats random side, consistent with overnight long beta/reversal rather than proof of these exact entry settings.

## Uncertainty and risk

| Model | Metric | Actual | 2023+90% block-bootstrap interval |
| --- | --- | --- | --- |
| UNIFORM | sharpe | 1.10 | 0.27 to 1.83 |
| UNIFORM | max_dd | 23296.75 | 15,167.85 to 43,930.89 |
| UNIFORM | annual | 25632.59 | 6,254.13 to 43,204.22 |
| SUNDAY2 | sharpe | 1.29 | 0.53 to 1.99 |
| SUNDAY2 | max_dd | 27647.00 | 17,356.62 to 48,995.05 |
| SUNDAY2 | annual | 39926.09 | 15,931.96 to 64,142.92 |
| ALLNIGHTS | sharpe | 1.19 | 0.49 to 1.89 |
| ALLNIGHTS | max_dd | 27312.50 | 19,150.16 to 49,371.61 |
| ALLNIGHTS | annual | 35623.57 | 14,786.46 to 56,131.95 |

5,000 ten-session paths with initial-zero accounting; permutations/trade Monte Carlo saved separately.

| Model | Trial scope | N | t | Required t | DSR |
| --- | --- | --- | --- | --- | --- |
| UNIFORM | ranked_plus_three | 328 | 2.59 | 3.61 | 0.37 |
| UNIFORM | ranked_plus_three_plus_336 | 664 | 2.59 | 3.79 | 0.29 |
| SUNDAY2 | ranked_plus_three | 328 | 2.90 | 3.61 | 0.49 |
| SUNDAY2 | ranked_plus_three_plus_336 | 664 | 2.90 | 3.79 | 0.40 |
| ALLNIGHTS | ranked_plus_three | 328 | 2.64 | 3.61 | 0.39 |
| ALLNIGHTS | ranked_plus_three_plus_336 | 664 | 2.64 | 3.79 | 0.31 |

Both versions fail the promotion bar, including the optimistic ranked-items-only comparison.336is a disclosed search count, not a clean preregistered
few-variant exception; additive sensitivity may double-count related work but still omits unknown rejected filters. No side or Sunday-only version was selected.
Validation remains profitable under4ticks perfill, but profitability under costs alone does not establish a new portfolio edge.

Standalone one-year EOD-trail illustrations at1baseMNQ (Sunday2 doubles Sunday quantity):

| Model | P(losing year) | DD95 | P(hit$2k EODtrail) |
| --- | --- | --- | --- |
| UNIFORM | 12.6% | $3,031.22 | 20.0% |
| SUNDAY2 | 8.1% | $3,514.18 | 23.9% |
| ALLNIGHTS | 8.7% | $3,628.77 | 29.5% |

These are not account pass/payout forecasts: no intraday breaches, DLL, joint positions or baseline chronology is modeled by this standalone illustration.
The20.0%/23.9%2023+trail-hit estimates are substantial at one base micro and do not support assuming high win rate means safe sizing.

## Data coverage and source verification

143 actual positions contain821 unobserved held minutes. None are in the audit's nominal16–17maintenance/weekend-closure windows;
the cause is unverified (no prints, omissions, restrictions/halts or feed gaps cannot be distinguished). Do not call them verified feed failures.
Largest ticket count289minutes is March16–17,2020; the observed exit is delayed to03:12 label. Longest contiguous gap is54minutes.
We retain all events, count gaps and fill stops at the next observed worse open when applicable; unobserved stop paths remain a limitation.
No actual closed trade crosses the15:59 daily deadline in this cache, and no terminal open position is fabricated closed.
Synthetic tests and independent code review pass, including Sunday quantity/ET calendar, entrybar stop, short-null gaps and explicit unclosed-nullIDs.
This is not an independent end-to-end raw-data replica or exact MC confirmation.

## Current personal portfolio and Apex placement

Current17-leg book andA–D starters pinned toe1a94f7; no BB_MRM. Model/base fees consistent at$1.24, with$1.04 sensitivity.
20fixed configurations: BASE/ADD/EMPTY/REPLACE for eachstarter andFULL. FULL replaces currentOvernightTick; starters replaceONBML.
All1004source nights are retained. Sundayqty multiplies raw unit-price P&L and contract fees exactly once.
1,000 paired252-session10-day bootstrap paths; historical annual-mean95%intervals below are different from90%standalone intervals.

| Model | Addition | Mean annual increment | 95%historical mean CI | Change in DD95 |
| --- | --- | --- | --- | --- |
| UNIFORM | A__ADD | $2,401.93 | [$269.49, $4,614.54] | $369.89 |
| UNIFORM | B__ADD | $2,401.93 | [$269.49, $4,614.54] | $328.77 |
| UNIFORM | C__ADD | $2,401.93 | [$269.49, $4,614.54] | $250.27 |
| UNIFORM | D__ADD | $2,401.93 | [$269.49, $4,614.54] | $96.94 |
| UNIFORM | FULL__ADD | $2,401.93 | [$269.49, $4,614.54] | $842.07 |
| SUNDAY2 | A__ADD | $3,846.68 | [$1,128.26, $6,842.76] | $655.26 |
| SUNDAY2 | B__ADD | $3,846.68 | [$1,128.26, $6,842.76] | $636.38 |
| SUNDAY2 | C__ADD | $3,846.68 | [$1,128.26, $6,842.76] | $554.51 |
| SUNDAY2 | D__ADD | $3,846.68 | [$1,128.26, $6,842.76] | $216.70 |
| SUNDAY2 | FULL__ADD | $3,846.68 | [$1,128.26, $6,842.76] | $860.96 |

For2023+FULL, baseline median-profit/DD95 is5.620; ADD gives5.370 UNIFORM /5.553 SUNDAY2. Thus higher modeled income buys more drawdown,
with no clear risk-efficiency improvement. FULL OvernightTick replacement is-$450/+$994 mean annually, with historical intervals including0;
DD95 increases$783/$765. Empty-slot controls are retained; no reliable replacement superiority is established.

| Model | All-history full-book daily corr | Joint losing days | Candidate net on book-loss days |
| --- | --- | --- | --- |
| UNIFORM | 0.28 | 265 | -$13,129.89 |
| SUNDAY2 | 0.27 | 265 | -$14,345.80 |

This is another NQ overnight long exposure, not a hedge. Its rebound arrives after the signal cash loss; it cannot rescue an account already breached
before entry. Existing personal booking/fee/day/Twin/MOC/S30 approximations remain, and OT data endsJuly7,2026. Source zeros afterward are not verified
no-trade activity. One legal Dec4→Dec5,2018night lacks a published personal-calendar row and is booked to the next published Dec6session by the inherited
helper; all money is retained and this mapping is logged. Daily portfolio risk/correlation is conditional on that published calendar.
After metadata/calendar review, all four fixed model/fee cases were repeated under the frozen final adapter:28 financial CSVs hash-match
the preserved primary results. Earlier first-run full-file hashes were unavailable; contemporaneous rerun hashes and equality proofs are saved.

| Requested context | Result |
| --- | --- |
| 50K evaluation | LIMITED: existingBridge Sunday-night exposure is collapsed/omitted beforeMonday00:00; no valid joint overnight comparison |
| 150K evaluation | Same concrete chronology limit; no pass-rate claim inferred from50K |
| 50K funded | LIMITED: OT/CLS whole-day adverse proxies and omittedBridge night path cannot identify simultaneous overnight risk |
| 150K funded | Same joint-path limit; no payout/blown claim inferred from50K |
| PersonalA–D/FULL17 | Positive added dollars, higher DD; no allocation recommendation under significance/risk-efficiency/parity limits |

Normal17→03 crosses calendar midnight inside one CME trading day under the current adopted OT-plan convention. It is **not** rejected merely for
crossing a date. Current-plan accounting is a simulation assumption, not new verification of broker rules. All eight model/Apex-context limits are saved;
we did not run an invalid account benchmark. Candidate821missing-price minutes independently limit intraday-risk precision.

## Research interpretation and decision

The literature is related, not exact validation. Liu's currently indexed result reverses **overnight** losers into the **intraday** window; Abdi studies
common stocks with additional conditioning. Bondarenko/Muravyev and Cliff/Cooper/Gulen support historical overnight timing/premium, not this NQ stop/filter.
Boyarchenko/Larsen/Whelan supplies the relevant inventory-pressure hypothesis. Their [July2026follow-up](https://libertystreeteconomics.newyorkfed.org/2026/07/the-disappearing-overnight-drift/)
reports that the narrow02–03ETdrift flattened after2020, includingNQ/YM. A broader conditional18–04rule can still be positive, but the older paper cannot
be used as current proof. Primarylinks and retrieval limits: [`overnight_rebound_source_review.md`](overnight_rebound_source_review.md).

**Keep out of the active allocations on this evidence.** The source has positive historical returns, but weaker replication, no multiple-testing pass,
unproven down-filter benefit and no clear personal return/DD improvement. The matching MC trade export/session settings would be the cheapest way
to investigate the price/timing gap; no new optimization grid or portfolio addition is justified now.
No live trading, VPS, broker/API settings, shared research caches, rankings or allocations changed.

Reproduce from repo root using the installed interpreter:

```powershell
$reboundPython = 'C:\Users\dmoto\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe'
& $reboundPython -B analysis/codex_rebound_run.py --phase design
& $reboundPython -B analysis/codex_rebound_run.py --phase validation
& $reboundPython -B analysis/codex_rebound_diagnostics.py
foreach ($reboundModel in 'UNIFORM','SUNDAY2') {
  foreach ($reboundFee in '1.24','1.04') {
    & $reboundPython -B analysis/codex_rebound_accounts.py --personal --ledger "analysis/outputs/codex_rebound/${reboundModel}_trades.csv" --model $reboundModel --prereg d94d815 --fee $reboundFee
  }
}
& $reboundPython -B analysis/codex_rebound_report.py
```

Claude review path: `agents/codex/results/overnight_rebound.md`.
