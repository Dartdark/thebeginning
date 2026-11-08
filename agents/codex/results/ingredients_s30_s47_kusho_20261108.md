# S30, S47 v2 and Kusho v9: WATCH — ingredient attribution completed

Summary:
Completed twenty frozen market/rule combinations across the three requested families, with S30 on NQ and ES.
S30's entry advantage changes by era; S47's direction is consistent; Kusho's wick is not a persistent profit contributor.
S30 NQ's marked DD is $59,548 versus $37,656 booked at exits; removing Kusho BE roughly doubles recent DD.
Use the component evidence for independent review; no changed strategy, combination or allocation is selected.

Plan: [`ingredients_s30_s47_kusho_20261108.md`](../plans/ingredients_s30_s47_kusho_20261108.md), **f43c459**, before returns.
Script: `analysis/codex_ingredients_s30_s47_kusho_20261108.py`; aggregation: `analysis/codex_ingredients_s30_s47_kusho_report_20261108.py`.
Output: `analysis/outputs/codex_ingredients_s30_s47_kusho_20261108/`. Trials run: **20 market/rule combinations**,
five definitions per family, with the same five S30 definitions applied to each of NQ and ES.
Design checkpoint **324f5c1** precedes recent replay. Evidence: [`ingredients_s30_s47_kusho_20261108.md`](../evidence/ingredients_s30_s47_kusho_20261108.md).

## Rule (as tested)

The user named S30, S47 and Kusho for the next ingredient round. S47 uses v2; Kusho uses the roll-adjusted v9
source, rather than FAR or C03. S30 uses both existing instrument legs. Prior author optimizations, source
rebuilds, controls and ingredient rounds remain known selection history. These are historical component
comparisons, not new strategy discovery or clean out-of-sample evidence.

Proposed mechanisms are low-close liquidity normalization, cross-session momentum and trend pullbacks.
Long-index drift and weekend risk-bearing are competing explanations. The bars identify neither forced
participants nor actual institutional orders; the results do not establish those causal stories.

| Family | Original | Four other frozen definitions |
|---|---|---|
| S30, NQ and ES | Long when completed cash-session IBS<0.20; exit when IBS>0.80; next-bar market orders; no stop/target; multiday/weekend holds | Enter any valid session while flat; replace exit with five source weekday rows; short the original entry/exit schedule; long high IBS and exit low IBS |
| S47 v2, NQ | London impulse magnitude>0.0625 of past overnight range, matching cash-first-hour direction; follow at 09:31 OPEN; 0.50×overnight-range stop; 15:00 CLOSE exit | Remove NY agreement; NY direction alone; opposite direction on original dates; no stop |
| Kusho v9, NQ | 15-minute pullback limit, EMA50, wick≤70ticks; mirrored shorts in DOWN regime; source swing/fallback bracket and BE; scheduled 21:00 exit | Remove wick; remove EMA; disable BE explicitly; flatten 15:45 using existing source option |

All clock times except the stated London window are **Chicago**. S30 uses source 08:31–15:00-labelled bars,
at least380 observed closes, the15:00 close, positive range and a valid15:01 OPEN. Its15:01 OPEN is15:00 civil CT.
S47's London07:45→08:30 uses Europe/London→America/Chicago timezone conversion, including mismatch weeks.
Its cash-first-hour comparison is08:30→09:30 CT;09:31 OPEN is09:30 civil CT, after that first hour.
Both next-open models assume immediate processing at a bar boundary; this is not measured order latency.

S47 retains source overnight coverage, past20/at-least15 usable range history, tick-rounded stop, holiday and
roll-day exclusions. Its stop starts **after the entry minute**. The separate fixed MultiCharts file adds an
entry-bar backstop; this source replay does not silently claim that additional protection.

Kusho retains adjusted indicators/regime/swings, one-bar limit life, one-tick entry trade-through, one-point
target trade-through, source swing/fallback sizing and BE. Stops/targets work only after the fill's15-minute
bar. Source BE can use that fill bar's full high/low, whose favorable excursion may precede the limit fill.
Nonpositive swing risks are accepted as coded. These limitations are retained, not fixed or certified here.

Data: pinned raw snapshot`fe35af99aa90d7f31b91f8693859251bb44dd9ab`,2017 feature warm-up only.
Design2018-01-01–2022-12-30; recent2023-01-01–2026-10-09. Each era starts flat; all cases are unchanged between
eras. Boundary-only liquidation is explicit and pays market friction; **no original baseline requires one in either era**.
Some alternatives do, as recorded in the phase summaries. No future-period return is used to complete design.

Costs: fixed one NQ ($20/point,0.25tick,$7.25RTcommission) or ES ($50/point,0.25tick,$5RTcommission).
S30/S47 pay one adverse market tick each leg, total$17.25/NQ or$30/ES. Kusho entry/target are limits without
an extra slippage tick; a market/stop exit pays one tick, total$12.25/NQ, or$7.25 on target exits.
Native micro sensitivity uses one tenth price/slippage dollars and **assumed$1.25RTcommission**: normal
$2.25MNQ/$3.75MES for S30/S47; Kusho$1.75MNQ market exit/$1.25 target exit. These are not broker quotes.
An additional tick per market/stop leg is subtracted on fixed orders as cost stress, without changing fill paths.

## Results

Dollar results are **net per one standard NQ or ES as labeled**, not equal-risk positions or account payouts.
Daily risk uses marked P&L at weekday23:59CT cuts with past-only last observed closes; weekend changes/exits
accrue to the next weekday. This research clock differs from the earlier S30 cash-close marks, MultiCharts
and a prop firm's floor clock. Consequently these marked DD numbers are not a new estimate of current-book
breach risk or capital requirements. Entry/exit fees, slippage and crossed roll jumps reconcile to trade totals.

### S30: long exposure matters; entry and holding advantages are regime dependent

| NQ definition | 2018–22 net | 2023+ net | Recent marked DD |
|---|---:|---:|---:|
| Original | $200,734 | $141,312 | $59,548 |
| Enter any valid session | $109,514 | $240,108 | $94,251 |
| Fixed five-session exit | $189,639 | $194,203 | $88,923 |
| Short original schedule | −$206,047 | −$144,728 | $146,421 |
| Buy high IBS, exit low IBS | −$112,619 | $212,937 | $109,497 |

| ES definition | 2018–22 net | 2023+ net | Recent marked DD |
|---|---:|---:|---:|
| Original | $113,080 | $83,208 | $50,003 |
| Enter any valid session | $43,525 | $101,410 | $63,485 |
| Fixed five-session exit | $73,330 | $80,118 | $38,420 |
| Short original schedule | −$121,720 | −$88,968 | $102,848 |
| Buy high IBS, exit low IBS | −$55,950 | $72,990 | $41,138 |

Longing the original schedule beats shorting it in both markets and eras. Both ES paired annual-effect intervals
exclude zero, while recent NQ's lower bound is slightly negative. This establishes historical directional
dependence; it does not separate bullish index beta from all possible timing alpha.

The low-IBS entry helps **design total profit** by$91,220 NQ/$69,555 ES, but **reduces recent total profit**
by$98,796/$18,203 relative to entering any valid session. It reduces marked DD relative to that broader rule
in both eras and markets. Thus the entry has a concentration/risk role; its isolated profit advantage is not
stable. These are different stateful position schedules, not pure deletions of identical trades.

The source exit beats the fixed five-session exit in both ES eras, though the recent gap is only$3,090 and both
intervals include zero. NQ's exit effect reverses. Buying strong closes instead of weak closes loses in design
but earns substantial recent profit, especially NQ. The original timing story does not win every regime.

**Open risk is material.** Whole-history marked DD is$59,548/NQ and$50,003/ES, versus exit-booked DD$37,656 and
$24,040. An NQ trade from2024-07-23 to2024-08-08 shows an observed adverse mark−$51,492 before exiting−$28,137.
An ES trade from2025-04-03 to2025-04-09 shows−$30,243 before closing+$2,633. The latter is a profitable final
trade with large intervening risk. These are observed source paths with closures/gaps, not certified native extrema.
S30 remains a personal-account/multiday family, not an Apex-legal standalone rule. No stop or sizing is added here.

### S47: direction is persistent; confirmations concentrate risk rather than universally adding dollars

| Definition | 2018–22 net | 2023+ net | Recent marked DD |
|---|---:|---:|---:|
| Original v2 | $143,095 | $103,633 | $15,325 |
| Remove NY agreement | $218,817 | $105,836 | $36,528 |
| NY direction alone | $158,246 | $73,148 | $64,436 |
| Opposite direction | −$82,990 | −$109,207 | $127,601 |
| Remove stop | $121,480 | $175,838 | $22,074 |

Following the selected direction beats reversing it in both eras, with both paired intervals above zero.
It is the clearest S47 return ingredient in this experiment.

The NY agreement filter removes profitable trades in both eras:$75,722 design and$2,203 recent. It substantially
reduces DD, but does not improve total profit over plain London-direction S47. The London gate versus NY-only
gives up$15,151 design and adds$30,485 recent; both intervals span zero. London-agree dates concentrate recent
profit and reduce DD, yet the earlier average-trade argument alone is insufficient to call it a persistent total-dollar
improvement. The full removed-trade/random-drop controls are below.

Removing the stop costs$21,615 design but adds$72,205 recently. Recent DD rises$15,325→$22,074, the worst realized
loss worsens−$4,612→−$20,902, and the observed adverse mark reaches−$26,227 perNQ. The stop is protection with a
changing profit effect. This is not evidence to remove it or an account-level test of a new unprotected rule.

### Kusho: wick is risk shaping; EMA and BE have different roles

| Definition | 2018–22 net | 2023+ net | Recent marked DD |
|---|---:|---:|---:|
| Original roll-adjusted v9 | $199,570 | $138,473 | $17,080 |
| Remove wick filter | $203,326 | $153,589 | $26,627 |
| Remove EMA filter | $217,027 | $82,851 | $39,557 |
| Disable break-even | $230,386 | $167,591 | $34,799 |
| Flatten 15:45 | $165,130 | $121,818 | $22,642 |

The wick filter **reduces total profit in both eras**, as well as DD. Its absence adds$3,756/$15,116 while recent
DD rises$17,080→$26,627. Neither paired profit interval excludes zero. The liberal70-tick wick is not established
as the persistent source of extra profit; that is not the same as proving the filter useless for risk.

EMA selection gives up$17,457 design but adds$55,623 recently, with only the recent interval above zero. This
supports a recent trend-state contribution, not a stable profit improvement in both eras. Position occupancy and
later entry opportunities change when the gate is removed, so no exact nested-trade filter claim is made.

Disabling BE adds$30,817 design and$29,117 recent. Both uncertainty intervals include zero. The recent marked DD
roughly doubles to$34,799; the worst design trade worsens−$3,837→−$7,002. The existing BE is a protection/profit
trade-off, not the positive-dollar engine of the source return. The off case uses an explicit Boolean guard and
passes an actual simulator fixture; it does not repeat the earlier zero-threshold-'off' bug.

The extended-hold policy adds$34,440 design/$16,655 recent relative to15:45 flattening. Both effects are positive,
but the recent paired lower bound crosses zero. Weekend-held original trades earn$106,927/$37,488, about43% of
whole-history net combined. **That grouped trade profit is not the causal return from weekends.** The full-policy
difference against15:45 is$51,095 across both eras and also changes weekday holding paths and later occupancy.
No exact weekend-only contribution was measured.

Original v9's2026-06-17 entry shows an observed−$6,482 source mark before a−$2,782 stop exit; its fill bar has no
missing observed closes. The stop works only after that15-minute fill bar. There are also50/27 original trades
with nonpositive source swing risk in design/recent. These inherited mechanics keep native executable parity
and entry-bar protection unresolved despite favorable aggregate statistics.

### Baseline whole/era/year metrics

| Original, whole history | Trades | Win | Net | Avg | t | Sharpe | Sortino | PF | Calmar | Ulcer | Marked DD |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| S30 NQ |253|70%|$342,046|$1,352|3.52|0.82|1.24|1.82|0.63|5.74|$59,548|
| S30 ES |240|67%|$196,288|$818|3.58|0.82|1.24|1.85|0.43|16.08|$50,003|
| S47 NQ |714|51%|$246,729|$346|4.09|1.35|2.69|1.51|1.73|2.85|$15,725|
| Kusho NQ |3,152|57%|$338,043|$107|5.24|1.75|3.22|1.37|2.18|3.73|$17,080|

| Original / era | Trades | Net | Avg | t | Sharpe | Sortino | PF | Calmar | Ulcer | Marked DD |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| S30 NQ design |154|$200,734|$1,303|3.07|1.10|1.64|1.95|1.54|6.27|$25,151|
| S30 NQ recent |99|$141,312|$1,427|1.96|0.63|0.97|1.69|0.61|12.06|$59,548|
| S30 ES design |144|$113,080|$785|2.67|0.97|1.44|1.82|0.71|20.99|$30,675|
| S30 ES recent |96|$83,208|$867|2.39|0.70|1.07|1.88|0.43|10.07|$50,003|
| S47 design |391|$143,095|$366|3.56|1.55|3.40|1.68|1.76|3.19|$15,725|
| S47 recent |323|$103,633|$321|2.30|1.16|2.17|1.38|1.73|6.28|$15,325|
| Kusho design |1,829|$199,570|$109|4.48|2.01|3.69|1.42|2.78|4.69|$13,869|
| Kusho recent |1,323|$138,473|$105|2.96|1.49|2.75|1.31|2.07|4.65|$17,080|

S30 originals are long only. S47 longs380 trades/$103,610/average$273/t2.49/PF1.41; shorts334/$143,119/$429/t3.28/PF1.61.
Kusho longs2,690/$266,643/$99/t4.62/PF1.35; shorts462/$71,401/$155/t2.47/PF1.45. No side was selected from these results.
Full all/long/short metrics for every case and era/year are retained in phase`metrics.csv`, `whole_metrics.csv`
and`year_side_metrics.csv`. Ulcer uses a$50K metric reference, not a sufficient-capital recommendation.

| Year, marked net | S30 NQ | S30 ES | S47 NQ | Kusho NQ |
|---|---:|---:|---:|---:|
|2018|−$1,614|−$24,040|$18,985|$24,718|
|2019|$19,676|$13,320|$8,638|$2,648|
|2020|$91,449|$51,320|$29,289|$47,107|
|2021|$55,821|$26,010|$26,630|$21,406|
|2022|$35,401|$46,470|$59,555|$103,691|
|2023|$67,722|$15,465|$19,581|$35,395|
|2024|−$5,360|$5,395|$4,811|$38,774|
|2025|$49,483|$32,575|$58,217|$51,795|
|2026 through10/09|$29,468|$29,773|$21,025|$12,509|

Yearly net marks holdings through the cutoff; trade count/average/t are by exit-booking year and can include a
different part of a cross-year trade. The CSV retains both marked net and exit-trade net; whole-era and whole-history
totals reconcile. The different marking clock explains differences from earlier15:00 S30 daily-risk reports.

Recent original Sharpe5/95% block bounds: S30 NQ **−0.01–1.27**, S30 ES **0.01–1.40**, S47 **0.50–1.89**,
Kusho **0.71–2.22**. Full-history one-micro fee sensitivities net$34,072 MNQ/S30, $19,449 MES/S30,
$24,298 MNQ/S47 and$32,150 MNQ/Kusho. All originals remain positive in both eras under the fixed extra-tick stress.
These bounds/frictions are conditional on this selected history and source repair, not future regime guarantees.

## Placebos and account level

S47's two pure gates pass identical retained-date/side/entry/exit/net checks. One thousand within-year random
subsets match original counts per year. The final columns are fractions of subsets with profit at least as high,
or DD at most as large, as the actual filter. Smaller favors the filter on that objective; these are not independent
or multiplicity-adjusted discovery p-values.

| S47 gate / era | Removed n | Removed total | Removed avg | Removed t | Random profit ≥ actual | Random DD ≤ actual |
|---|---:|---:|---:|---:|---:|---:|
| NY agreement, design |426|$75,722|$178|1.88|9.4%|19.9%|
| NY agreement, recent |281|$2,203|$8|0.05|5.5%|1.1%|
| London vs NY-only, design |824|$15,151|$18|0.31|0.1%|13.8%|
| London vs NY-only, recent |600|−$30,485|−$51|−0.50|2.1%|0.1%|

Recent London-conditioned selection beats most matched subsets on both objectives, but the full-sample profit
advantage is conditional, removed mean is uncertain and design excludes profitable trades. NY agreement also
concentrates returns/risk but fails the requirement that omitted trades lose. No gate passes a claim of adding
total profit robustly across eras merely because average trade profit or a random-subset statistic looks better.

S30 entry/exit rules and Kusho filters change later positions. Those are paired whole-policy comparisons,
not the deletion of a common realized-trade set. We do not fabricate removed-trade or nested random-drop results
for them. Direction and exit cases likewise preserve their actual changed paths rather than fixed exit labels.

Paired original-minus-intervention annual-dollar5/95% intervals,1,000 moving20-weekday blocks, seed80314:

| Comparison | Design annual interval | Recent annual interval |
|---|---:|---:|
| S30 NQ unrestricted entry |[−$4,386,$41,023]|[−$64,793,$13,569]|
| S30 NQ five-session exit |[−$16,957,$22,500]|[−$42,437,$16,578]|
| S30 NQ short original schedule |[$43,093,$121,634]|[−$609,$134,694]|
| S30 NQ close-strength |[$23,855,$100,943]|[−$83,205,$39,316]|
| S30 ES unrestricted entry |[−$3,621,$30,539]|[−$19,864,$11,491]|
| S30 ES five-session exit |[−$3,474,$18,053]|[−$16,893,$19,378]|
| S30 ES short original schedule |[$20,868,$71,300]|[$1,970,$77,011]|
| S30 ES close-strength |[$7,812,$59,141]|[−$30,334,$30,124]|
| S47 no NY agreement |[−$28,162,−$4,097]|[−$19,171,$16,204]|
| S47 NY only |[−$17,201,$10,633]|[−$19,597,$32,623]|
| S47 opposite |[$25,796,$62,279]|[$25,602,$89,700]|
| S47 no stop |[−$4,424,$12,783]|[−$34,003,−$2,643]|
| Kusho no wick |[−$8,867,$6,131]|[−$16,229,$9,225]|
| Kusho no EMA |[−$12,183,$5,683]|[$2,668,$28,634]|
| Kusho no BE |[−$14,445,$1,014]|[−$23,632,$6,557]|
| Kusho15:45 exit |[$2,076,$10,764]|[−$2,066,$10,432]|

Under the frozen interpretation, S47 direction and S30 ES's long-versus-short comparison have stronger
historical contribution support. S30 ES source exit/close-reversal and Kusho extended holding are positive in
both eras but uncertain. Other profit effects are mixed or negative for the original component; risk protection
can still be useful. None earns a new S-rank recipe, a position-size change or an account admission.

No sixth economic definition, additional random-time/side rule, optimized horizon, account simulation,
portfolio combination, addition/replacement/empty-slot run or new MC code was attempted. Existing account
results are not rerun or inferred from standalone net. Any changed/combined candidate needs a separate frozen
protocol, native implementation checks and actual current-book comparisons before an allocation claim.

## What could make this wrong

- **Roll repair is conditional.** Source`roll_minutes` chooses a monthly maximum price jump within preset windows
  and a full-history threshold. Kusho removes these jumps from indicator inputs; both multiday ledgers remove
  them from held returns. This is retrospective continuous-series repair, not authenticated contract identities,
  live-known roll metadata or paid executable rolling. Real market jumps can be removed. The exact jumps are saved
  in admission receipts; no new point-in-time/native alpha claim is made from these estimates.
- **Held paths have closed/missing minutes.** The raw absent-calendar-minute counts include scheduled maintenance,
  weekends and holidays as well as any missing data. They are not counts of proven bad feed bars. Last observed
  daily marks and their ages are retained; some are over a day old around closures. There is no invented quote,
  continuous native path, queue record or intraday-floor guarantee. Source S47 has0/1 absent held closes by era.
- **Inherited execution defects remain.** S47's entry minute and Kusho's full fill bar lack source protection;
  Kusho accepts nonpositive swing risk and can arm BE from a full bar's excursion before the fill. Tick bars,
  native stops/receipts and the current fixed MC code have not been independently paired in this task.
- **State and sample boundaries matter.** All eras start flat, and alternatives with open end positions are explicitly
  liquidated. Original terminal counts are zero; alternative terminal counts are saved. Exposure-changing filters
  cannot be assessed as if only losing original trades disappeared.
- **Selection and dependence remain.** S47's author searched about3,700 settings and added NY agreement after
  seeing2023+. Kusho's settings were also optimized. Previously seen source controls and every prior ingredient
  round remain multiplicity. Twenty-session blocks may not preserve every long S30 hold/regime; bounds are
  conditional diagnostics, not a robust new-strategy significance certificate.

Ten synthetic fixture groups passed before returns and inside each era, covering S30 entry/exit/opposite behavior,
five-session timing, actual guarded BE-off behavior, S47 infinite-stop behavior/DST, Sunday bookkeeping, roll
removal, daily totals and micro fees. Closed original-source parity passes154/99 S30 NQ,144/96 S30 ES and1,829/1,323
Kusho trades by era; S47 uses the unchanged source function on391/323 trades. S47 source reuse is not an independent
fill test. All gross/cost/net, daily, long/short and marked yearly totals reconcile. Code/plan/source/input hashes,
dependency versions and exclusions/mark receipts are retained. Independent review remains pending.

## Differences between MultiCharts code and the test

No new PowerLanguage was written and no fresh MC trade-list pairing was performed. The above source protection,
trade-through, roll, accounting-clock and state-boundary limitations remain explicit. This does not certify the
current fixed MC implementation or authorize a source defect to be deployed. Useful execution findings are
retained in[`EXECUTION_REFERENCES.md`](../EXECUTION_REFERENCES.md).

Reproduction: configured Python runs`analysis/codex_ingredients_s30_s47_kusho_20261108.py fixtures`, then`design`,
then`recent`. Market phases require committed exact inputs and refuse to overwrite saved directories; rerun in
a scratch checkout with saved outputs moved aside intact. The report script regenerates tables/audits from
committed ledgers alone. Source copies preserve original CRLF/whitespace bytes for hash verification.

No TIER_LIST, trading plan, live/VPS/broker/key, scout history or automation change. No changed version selected.
