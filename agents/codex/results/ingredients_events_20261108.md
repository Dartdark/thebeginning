# EOS, NFP Fade and crude Sunday Fade: WATCH — ingredient attribution completed

Summary:
Dissected three new existing strategies with 15 frozen definitions, first2018–22 then unchanged2023–2026-10-09.
Direction is the clearest common contribution; calendar/spike selection has conditional effects on profit and risk.
CL's later morning hold adds profit in both eras; removing its stop hides a roughly$16,007 observed intratrade loss.
No combined strategy, promotion, account simulation or trading-plan change; independent review pending.

Plan: [`ingredients_events_20261108.md`](../plans/ingredients_events_20261108.md), commit **fa2be26**, before returns.
Evidence: [`ingredients_events_20261108.md`](../evidence/ingredients_events_20261108.md).
Harness: `analysis/codex_ingredients_events_20261108.py`; aggregation: `analysis/codex_ingredients_events_report_20261108.py`.
Outputs: `analysis/outputs/codex_ingredients_events_20261108/`; design checkpoint **08a2ead** before recent replay.
Cases: **15**, five per family, replayed unchanged in two eras. All previous source/ingredient/combination looks remain relevant.

## Why these three

Expiration Open Short (EOS), NFP Fade and CL Sunday up-gap fade cover different scheduled/event exposures and include
our non-NQ oil leg. They are distinct from the earlier DT/RS/LDF and FC2B/ONB/T_ONESIDE rounds and Claude's
Twin/OvernightTick/noise-area study. Selection uses their existing records, not a clean independent strategy discovery.

The proposed mechanisms are expiry/hedge-reset pressure, post-payroll repricing/liquidity normalization, and reversal
of crude's thin Sunday opening repricing. Our bars do not observe forced dealers, actual news surprises or inventories.
The experiment tests dependence on specified rule ingredients; it does not identify those causal actors.

## Rules and interventions

| Family | Baseline | Other four frozen cases |
|---|---|---|
| EOS, NQ | Short08:30civilCT, source monthly expiry/holiday-shifted dates; stop0.30ATR; exit10:00CLOSE | All Fridays plus shifted-expiry Thursdays; opposite long; no stop; exit09:00 |
| NFP, NQ | Friday day<=10 and07:30–07:35 spike >3×past20weekday median; fade07:30→07:45; enter07:45civilCT; stop0.50ATR; exit09:00 | Remove spike gate; all spike weekdays; follow reaction; no stop |
| CL Sunday | Up-gap>=0.10ATR versus last prior close; short17:05civilCT; stop0.75ATR; Monday09:00CLOSE | Short all valid nonzero-gap Sundays; long original up-gaps; no stop; Monday03:00exit |

ATR uses the existing past15weekday full-calendar-day Grid24 convention. EOS has no reaction condition. NFP retains
the existing price-detected early-Friday proxy, not a complete authenticated payroll calendar; all Good Fridays are
skipped per current code. CL uses the MC-confirmed source timing (17:06labelledOPEN and09:00exit), not the older
17:05labelledOPEN/10:00exit experiment. Its first observed opening must occur within the first five minutes.

Costs are explicit: one NQ$20/point, tick0.25, $7.25commission +$10slippage; one CL$1,000/point, tick0.01,
$7.25commission +$20slippage per round trip. Micro sensitivity uses one-tenth price/slippage dollars and
**assumed$1.25RTcommission**: normal$2.25MNQ /$3.25MCL, not a verified broker quote. No compounding or sizing search.
NQ source stops anchor to raw entry; CL source stops anchor to slipped entry. Stops are active on the entry bar.
An extra-tick-per-leg cost view holds orders fixed and subtracts another$10NQ /$20CL; it is not a new path/latency replay.

## Main results and attribution

**All amounts below are net per one standard contract, NQ or CL as labelled.** They are not comparable risk allocations,
payouts or recommended sizes. The 2023+ period is already-seen historical replication, not an untouched holdout.

### EOS: short direction is persistent; calendar benefit depends on era

| Version | 2018–22net | 2023+net | Recent daily DD |
|---|---:|---:|---:|
| Original | $18,731 | $31,083 | $7,429 |
| Remove expiry gate | $32,824 | −$3,417 | $38,669 |
| Long instead | −$20,598 | −$31,805 | $32,503 |
| Remove stop | $21,865 | $31,034 | $9,579 |
| Exit09:00 | $8,725 | $26,605 | $4,870 |

Short versus long is the clearest EOS ingredient: baseline-minus-long is positive in both eras and both paired
annual-effect90% intervals exclude zero. This is a conditional directional comparison, not proof of dealer causality.

The expiry gate lowers historical drawdown in both eras but reduces total design profit; it is **not a persistent
profit improvement across both samples**. It excludes195design trades earning+$14,093 (mean+$72,t0.64) and150recent
trades losing−$34,500 (mean−$230,t−1.22). Recent selection beats most matched-count random Friday subsets: only1.3%
earn as much and3.7%have equal/lower DD; design corresponding shares15.1%/6.9%. Recent paired profit uncertainty
still spans zero, so do not turn the random-subset result into a certain isolated calendar premium.

Holding09:00→10:00 adds net profit in both eras but recent DD rises. Both timing-effect intervals include zero.
The stop is risk shaping: removing it barely changes recent net but worsens the largest realized loss from
−$3,645 to−$8,087 perNQ. This is not a reason to remove it based on earlier extra profit.

### NFP: reversal is more consistent than the spike/calendar gates

| Version | 2018–22net | 2023+net | Recent daily DD |
|---|---:|---:|---:|
| Original | $8,950 | $18,196 | $4,784 |
| Remove spike gate | $5,825 | $29,911 | $4,986 |
| Allow all spike weekdays | $9,875 | $36,580 | $15,581 |
| Follow reaction instead | −$14,767 | −$18,972 | $20,570 |
| Remove stop | $14,001 | $18,196 | $4,784 |

Fading beats following in both eras. Its recent paired directional interval excludes zero, but the design interval
does not. Thus the observed direction is consistent, while the independent statistical support remains limited by
the small selected sample and earlier research.

The spike filter **helps design and hurts recent total profit**. The39removed design trades lose−$3,125
(mean−$80,t−0.49); the31removed recent trades earn+$11,715 (mean+$378,t0.96). Neither era passes a strong joint
random-drop profit/DD claim: shares beating the filter's profit are19.3%/26.9%, and lower-DD shares56.9%/50.4%.
The source spike threshold is not established as the engine of returns or an optimal filter.

Restricting to the early-Friday proxy cuts total profit in both eras, along with DD: its removed non-payroll-proxy
spike trades have means+$13(t0.07) and+$172(t0.73). That is a historical concentration/risk trade-off, not proof that
all other release fades lose. No extra calendars, revised actuals or time windows were tried to rescue the story.

Removing the stop adds design profit and changes nothing in recent history. This does not earn a no-stop policy;
the small historical sample cannot price protection through a new news regime. No best exit/filter is selected here.

### CL: fade direction and the later morning hold carry the clearer return contribution

| Version | 2018–22net | 2023+net | Recent daily DD |
|---|---:|---:|---:|
| Original | $22,130 | $40,530 | $5,156 |
| Short all valid Sundays | $26,957 | $29,137 | $12,773 |
| Long the original up-gaps | −$20,898 | −$42,804 | $45,831 |
| Remove stop | $21,953 | $47,621 | $5,156 |
| Exit03:00 | $10,713 | $14,540 | $4,858 |

Fading these up-gaps beats following in both eras, with both paired directional intervals above zero. Extending the
same trade03:00→09:00 adds+$11,418design and+$25,991recent. The later-hold effect is positive historically, but the
recent annual-effect90% lower bound is approximately−$30, so it does **not** clear the frozen stronger-evidence label.

The up-gap filter lowers DD in both eras; total profit is lower in design and higher recently, so its isolated profit
effect is conditional. Removed trades average+$24(t0.24) /−$86(t−0.89). Only1.7%/1.3%of random matched-year subsets
earn as much as the actual up-gap filter, but6.4%/10.2%have lower DD; do not claim it dominates random selection on
both objectives in either era.

**The stop's role cannot be judged from daily net DD alone.** Without it, recent net is+$7,091 higher and daily DD
is unchanged, yet the Monday2026-03-09 trade shows an **observed adverse source mark−$16,007 perCL**, before closing
at+$3,813. Its source path has a missing bar, so the true worst path is not certified. Even this observed mark is
about−$1,601 perMCL under the stated micro-fee assumption. A profitable closing trade need not survive an account
floor intraday. We did not simulate account offsets or breach probability; no stop removal is recommended.

## Baseline metrics and yearly record

Whole history2018–2026-10-09, fixed one standard contract:

| Baseline | Trades | Win | Net | Avg | t | Sharpe | Sortino | PF | Calmar | Ulcer | DailyDD |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| EOS |105|59%|$49,815|$474|2.58|0.84|1.61|1.93|0.75|2.54|$7,429|
| NFP |77|53%|$27,146|$353|1.91|0.63|1.28|1.83|0.40|5.29|$7,562|
| CL |96|66%|$62,661|$653|3.18|1.01|2.94|3.01|1.35|1.42|$5,156|

| Baseline/era | Trades | Net | Avg | t | Sharpe | Sortino | PF | Calmar | Ulcer | DailyDD |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
|EOS2018–22|60|$18,731|$312|1.60|0.70|1.31|1.74|0.81|2.84|$4,520|
|EOS2023+|45|$31,083|$691|2.02|1.00|1.94|2.11|1.08|2.61|$7,429|
|NFP2018–22|44|$8,950|$203|0.85|0.38|0.70|1.47|0.23|6.60|$7,562|
|NFP2023+|33|$18,196|$551|1.90|0.93|2.17|2.32|0.99|2.98|$4,784|
|CL2018–22|41|$22,130|$540|2.02|0.86|2.87|3.40|1.37|1.48|$3,154|
|CL2023+|55|$40,530|$737|2.46|1.19|3.30|2.85|2.02|1.68|$5,156|

EOS/CL baseline trades are all short; there is no baseline long-side estimate. NFP's35longs earn+$11,261
(avg$322,t1.48,PF1.95), while42shorts earn+$15,885(avg$378,t1.31,PF1.76). No side was selected after inspection.
Full metrics for every case/side/year are in `whole_metrics.csv`, `year_side_metrics.csv` and the phase metrics files.
Ulcer uses a$50Kmetric reference and initial zero-P&L peak; it is not an adequate-capital recommendation.

| Year | EOSnet/NQ | NFPnet/NQ | Sundayfadenet/CL |
|---|---:|---:|---:|
|2018|$239|$870|$1,009|
|2019|−$172|−$1,383|$3,258|
|2020|$5,478|−$2,700|$3,312|
|2021|$2,114|$5,935|$712|
|2022|$11,073|$6,228|$13,839|
|2023|$8,515|$6,908|$2,658|
|2024|$5,758|$3,973|$5,143|
|2025|$15,623|$3,537|$7,562|
|2026to10/09|$1,188|$3,779|$25,167|

About62%of recent CL net comes from2026; rare-event selection and regime concentration remain material limitations.
Recent original-rule Sharpe5/95%moving-block bounds: EOS0.22–1.68, NFP0.22–1.58, CL0.48–1.74. These are conditional
resamples of already selected history, not protection against source selection, an unseen regime or execution gaps.
All three original rules stay profitable under the fixed extra-tick-per-leg cost stress in both eras.

## Implementation checks, placebos and limits

All raw annual files are Git-blob/SHA256 verified against snapshot`fe35af99aa90d7f31b91f8693859251bb44dd9ab`;
2017warm-up only. No persistent research cache, external data request, source overwrite or top-level strategy script
execution occurred. Exact dependencies/source copies, feature/admission receipts, exclusions and trade/daily ledgers
are retained. Five synthetic fixture groups cover long/short gap stops, no-stop behavior, missing-exit fallback and
standard/micro costs. The ledger-to-daily totals and gross/commission/slippage identities pass for all cases.

Baseline source-replay parity passes on60/45EOS,44/33NFP and41/55CL trades in the two eras. NFP is checked against
the retained independent reaction-price simulator; CL against its vectorized confirmation function. EOS wrapper
identity shares the source walker and is not an independent fill test. **No fresh MultiCharts report pairing** was
performed. Current holiday guards and source-calendar eligibility mean older published trade counts can differ;
this diagnostic is not a new source-parity promotion or a native dated-contract validation.

Source missing-path policy remains a limit: baseline EOS has one missing held bar in design, none recently; NFP has
none; CL has69design and276recent missing held bars and one recent last-close fallback. The broader CL Sunday
control has638/2,052missing bars and one fallback in each era. The source walker skips absent held bars and may use
the earlier last close if the scheduled exit is missing; these are exposed, not represented as observed live fills.
No missing entry or actual execution price was invented. Continuous-roll metadata, broker spreads, latency,
publication/receipt differences and native contract identity remain unverified. NFP source stops anchor to raw,
CL stops to slipped entry; silently unifying them would change the source comparison.

The four selection comparisons are verified nested filters on common dates/side/entry/exit/net; all removed-trade
and1,000within-year random-subset results are in each phase's `summary.json`. Direction/exit/stop interventions are
paired strategy comparisons, not nested trade removal. Every paired annual effect uses1,000twenty-session block
draws, seed20261109. Full results retain negative and uncertain cases. No new calendar/threshold/time was chosen.

Account level: not run, because this task diagnoses existing rules rather than proposing an addition/replacement.
There is no claim of improved funded payouts, evaluation speed, personal capital needs or a new rank. A proposed
changed/combined rule would require a separate protocol and current-book BASE/ADD/REPLACE/EMPTY comparisons.

## Reusable conclusions and code differences

- EOS: conditional short direction and the expiry morning window are more defensible ingredients than a generic
  every-Friday short. Its calendar concentrates risk/return differently across eras.
- NFP: the fade direction is more consistent than insisting the existing spike threshold/calendar proxy is the
  unique source of alpha. The latter are conditional selection/risk rules, with weak or mixed incremental evidence.
- CL: fading a qualifying weekend up-gap and allowing the later morning reversal are the clearer historical pieces.
  Keep modeled intratrade risk separate from booked net; an apparently helpful no-stop variant is not risk-free.

These pieces do not automatically form one coherent new strategy: EOS's directional calendar exposure is distinct
from the two reaction fades. No indicator stacking or automatic combination follows this round.
Useful clock/cost/risk lessons are retained in `EXECUTION_REFERENCES.md`.
No MultiCharts code was written or modified. No live/VPS/broker/API-key, trading plan/TIER, scout history or schedule
change, external message or paid access. Tell Claude to review this result, frozen plan and exact trade ledgers.
