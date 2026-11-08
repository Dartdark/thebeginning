# Monday Long, Bridge Monday and ES MOC: WATCH — ingredient attribution completed

Summary:
Completed 15 frozen definitions on design history, then unchanged recent history.
Monday Long benefits from the later hold; Bridge's DI and target profit effects reverse between eras.
ES MOC's large-move gate excludes $39,298 of recent losses, but its recent original averages only $99 per ES.
Use these as component evidence for independent review; no new combination or allocation is established.

Plan: [`ingredients_monday_moc_20261108.md`](../plans/ingredients_monday_moc_20261108.md), committed **30b53e7** before returns.
Script: `analysis/codex_ingredients_monday_moc_20261108.py`; ledger aggregation: `analysis/codex_ingredients_monday_moc_report_20261108.py`.
Output: `analysis/outputs/codex_ingredients_monday_moc_20261108/`. Trials run: **15**, five per family.
Design checkpoint **756d29d** precedes recent replay. Evidence: [`ingredients_monday_moc_20261108.md`](../evidence/ingredients_monday_moc_20261108.md).

## Rule (as tested)

These are three additional existing strategies after DT/RS/LDF, FC2B/ONB/T_ONESIDE and EOS/NFP/CL.
The user permitted reuse, but none was needed. The two Monday rules distinguish weekday long exposure from
Sunday entry and price-state selection; MOC adds a different conditional late-day continuation question.

Weekday risk transfer, overnight drift and closing demand are proposed explanations from the evidence sheet.
These bars do not identify forced buyers or sellers. ADX/DI is a price-state filter, and the ES move is a price
signal, **not measured auction imbalance**. This experiment identifies dependence on the specified rules,
not the economic actors responsible for returns.

| Family | Original | Four other frozen definitions |
|---|---|---|
| MON, NQ Monday Long | Monday long at 08:31-labelled OPEN, stop 0.50×past-15-weekday ATR from slipped entry; exit 15:00 CLOSE | Same rule all weekdays; short original Mondays; no stop; exit 10:00 |
| BR, NQ Bridge Monday v2.1 | Sunday 19:00 CLOSE long; last completed RTH ADX7 ≥10 and <50 with DI+>DI−; 100-point target from raw close; no stop; Monday 15:55 CLOSE exit | Remove ADX band only; remove DI direction only; remove target; enter Monday 08:30 CLOSE |
| MOC, ES MOC Follow | Follow 14:00→14:50 move when magnitude ≥0.30×past-15-weekday ATR; enter 14:51-labelled OPEN; stop 0.25 ATR from slipped entry; exit 15:00 CLOSE | Remove move-magnitude gate; fade instead; no stop; exit 15:15 |

Times are Chicago. Close-stamped 08:31 OPEN means **08:30 civil CT**; 14:51 OPEN means **14:50 civil CT**.
Bridge's source Monday 08:30 **CLOSE** is preserved; it is not substituted with MON's next-minute OPEN.
The prior-15-weekday ATR uses the retained Grid24 full-calendar-day range convention. Bridge's ADX uses the
last completed regular session, normally Friday, and retains its holiday/no-trade policy.

Design: 2018-01-01–2022-12-30. Recent: 2023-01-01–2026-10-09. The 2017 files supply warm-up only.
Recent history and earlier source ablations were already seen; this is **historical replication**, not a fresh
holdout or a new discovery. All fifteen cases were replayed unchanged; no best version was selected.

One NQ uses $20/point, 0.25 tick and $7.25 round-trip commission. One ES uses $50/point, 0.25 tick and $5
commission. Market/stop fills incur one adverse tick per leg: normal total cost $17.25 per NQ / $30 per ES.
Bridge's source target uses a touch fill with favorable-gap improvement and no target-exit slippage, so its
target-trade cost is $12.25 per NQ. This inherited convention is exposed, not newly certified as executable.

Native-micro sensitivity uses one tenth of price/slippage dollars and **assumed $1.25 RT commission**:
normal $2.25 MNQ / $3.75 MES, or $1.75 MNQ for Bridge target trades. These are not verified broker fees.
An additional tick per market/stop fill is a fixed-order cost stress, not a latency or re-anchored-stop replay.
Results are fixed one standard contract with no compounding and are not equal-risk allocations across families.

## Results

All following dollar results are net per **one NQ for MON/BR or one ES for MOC**, after the stated costs.
DD is daily booked-P&L drawdown with the initial zero-P&L peak included; it is not account-floor survival.

### Monday Long: long direction and the later hold; weekday gate concentrates exposure

| Definition | 2018–22 net | 2023+ net | Recent daily DD |
|---|---:|---:|---:|
| Original | $34,009 | $152,532 | $15,742 |
| All weekdays | $90,944 | $197,274 | $68,238 |
| Short instead | −$48,709 | −$116,464 | $123,828 |
| Remove stop | $38,790 | $154,339 | $26,884 |
| Exit 10:00 | $3,874 | $78,976 | $11,896 |

The long-minus-short difference is positive in both eras; its design paired interval includes zero, while the
recent interval is positive. Holding to 15:00 rather than 10:00 adds **$30,135 design / $73,556 recent**, with
the same uncertainty pattern. These are complete trade-policy comparisons: changed stop exposure means the
difference is not simply an unconditionally tradable 10:00→15:00 return stream.

The Monday restriction **reduces total profit in both eras**, along with exposure and daily DD. Its excluded
non-Monday trades are profitable in aggregate, so this does not establish Monday as the only profitable day.
Recent Monday selection nevertheless beats most matched-count, within-year random subsets on both total profit
and DD; design does not. That supports recent concentration, not a universal isolated weekday premium.

Removing the stop adds only $4,781 / $1,807 while recent DD rises from $15,742 to $26,884. The recent worst
realized loss worsens from −$9,434 to −$11,672, and the no-stop observed adverse mark reaches −$14,807.
The stop shapes tails; no stop removal is recommended from these historical extra dollars.

### Bridge Monday: Sunday entry contributes; DI and target effects are conditional

| Definition | 2018–22 net | 2023+ net | Recent daily DD |
|---|---:|---:|---:|
| Original | $60,130 | $61,900 | $13,058 |
| Remove ADX band only | $60,458 | $66,197 | $13,058 |
| Remove DI direction only | $35,908 | $123,886 | $13,381 |
| Remove target | $58,735 | $111,195 | $15,841 |
| Enter Monday 08:30 CLOSE | $36,173 | $55,605 | $10,928 |

The original Sunday-entry policy earns **$23,957 design / $6,295 recent** more than the source RTH-entry policy.
Only the design paired annual interval excludes zero. The design timing comparison also has one additional
RTH-only trade, 2018-10-01, because the original lacks its Sunday entry close; recent dates match exactly.
Thus the design difference includes source eligibility as well as timing, and neither difference is an additive
overnight P&L attribution. In particular, the old source `ovn` mark is not realized overnight profit after an
already completed Sunday target exit.

The **DI direction result reverses**: its excluded trades lose $24,222 in design but earn $61,986 recently.
Recent omitted trades average $969, t 2.84. The original DI filter is not a persistent source of extra profit;
its design success cannot justify the claim that positive DI drives Bridge in all regimes. Removing the ADX
band adds $328 / $4,297 and leaves era DD unchanged, but affects only 10 / 8 trades and has wide uncertainty.
There is no earned optimal-filter or filter-removal recommendation here.

The 100-point target adds $1,395 in design but gives up $49,295 recently. It reduces DD in both eras:
$10,181 vs $18,195 design, $13,058 vs $15,841 recent. That is a changing profit/risk trade-off, not a stable
return engine. None of the target variants adds protection against a large losing overnight move.

**The original already has material intratrade risk.** The trade attributed to Monday **2025-01-27** has an
observed adverse mark of **−$16,427 per NQ**, then exits at **−$5,757**. No held bars are missing on this particular
source path. The mark is about −$1,643 per MNQ under the stated fee sensitivity. Other paths do contain gaps;
this is neither a complete native-tape worst loss nor an account breach probability. Different Monday entry
times do not make two NQ long strategies independent hedges.

### ES MOC: large-move conditioning and cash-close exit are more persistent than recent profitability

| Definition | 2018–22 net | 2023+ net | Recent daily DD |
|---|---:|---:|---:|
| Original | $24,795 | $7,026 | $6,904 |
| Remove large-move gate | $3,746 | −$32,272 | $35,772 |
| Fade instead | −$25,469 | −$4,839 | $11,549 |
| Remove stop | $24,633 | $4,033 | $9,510 |
| Hold to 15:15 | $17,850 | $343 | $10,500 |

The move-magnitude gate excludes losses in both eras: **−$21,048 design / −$39,298 recent**, and lowers daily DD
relative to trading all nonzero-move sessions. Both paired annual-effect intervals are above zero, although
the design lower bound is only about $18/year. It also beats most matched-count subsets on profit in each era.
Recent random subsets often have lower DD than the actual selected trades, so it does not dominate random
selection on both measures. The filter is more credible as a conditional profit ingredient than as a claim of
unusually low risk at a fixed trade count.

Following beats fading in both eras, but the recent directional-effect interval spans zero. Exiting at 15:00
rather than 15:15 adds $6,944 / $6,683, with both annual-effect intervals above zero. The stop adds $162 / $2,994
and lowers DD in both eras; only its recent profit-effect interval excludes zero.

These relative results do not make the original strong recently: average trade falls **$189→$99 per ES**,
Sharpe **1.53→0.59**, and 2025 loses **$4,776**. The recent baseline Sharpe 5/95% interval is **−0.40 to 1.56**.
This replay neither reverses earlier account sizing decisions nor establishes an upgrade from actual auction data.

### Baseline metrics: whole history and eras

| Original, whole history | Trades | Win | Net | Avg | t | Sharpe | Sortino | PF | Calmar | Ulcer | Daily DD |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| MON / NQ |452|55%|$186,540|$413|3.25|1.07|1.90|1.52|1.00|10.66|$20,847|
| BR / NQ |218|70%|$122,030|$560|4.44|1.43|2.17|2.03|1.04|3.37|$13,058|
| MOC / ES |202|58%|$31,821|$158|3.47|1.13|2.24|2.11|0.51|2.77|$6,904|

| Original / era | Trades | Net | Avg | t | Sharpe | Sortino | PF | Calmar | Ulcer | Daily DD |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| MON 2018–22 |258|$34,009|$132|1.01|0.45|0.70|1.18|0.32|13.47|$20,847|
| MON 2023+ |194|$152,532|$786|3.31|1.65|3.14|1.92|2.51|3.69|$15,742|
| BR 2018–22 |120|$60,130|$501|3.44|1.46|2.30|2.11|1.15|2.57|$10,181|
| BR 2023+ |98|$61,900|$632|2.91|1.43|2.12|1.97|1.23|5.92|$13,058|
| MOC 2018–22 |131|$24,795|$189|3.60|1.53|4.31|2.71|2.54|0.91|$1,898|
| MOC 2023+ |71|$7,026|$99|1.16|0.59|0.90|1.50|0.26|5.71|$6,904|

MON and BR originals have only long trades; their short-side samples are empty. MOC's 83 longs earn $18,333
(average $221, t 3.17, PF 3.08); its 119 shorts earn $13,487 (average $113, t 1.90, PF 1.68). No side was selected.
Every case's complete long/short metrics, including wins, Sharpe, Sortino, Calmar, Ulcer and DD, are retained in
`whole_metrics.csv`, `year_side_metrics.csv` and phase `metrics.csv` rather than duplicating all 45 rows here.
Ulcer uses a $50K metric reference, not a sufficient-capital recommendation.

| Year | MON net / NQ | BR net / NQ | MOC net / ES |
|---|---:|---:|---:|
|2018|−$11,465|$1,472|$1,259|
|2019|$4,124|$7,390|$301|
|2020|$41,146|$27,882|$11,561|
|2021|$5,994|$22,189|$4,449|
|2022|−$5,790|$1,197|$7,224|
|2023|$43,044|$14,290|$2,000|
|2024|$16,479|$5,133|$8,289|
|2025|$47,469|$24,797|−$4,776|
|2026 through 10/09|$45,540|$17,681|$1,514|

Original-rule recent Sharpe 5/95% moving-block bounds: MON **0.95–2.32**, BR **0.62–2.31**, MOC **−0.40–1.56**.
Whole-history native-micro sensitivities net $18,417 MON / $12,089 BR per MNQ and $3,031 MOC per MES.
All originals remain profitable in both eras under the additional-tick cost stress. This holds orders fixed,
does not add new contract/receipt evidence, and does not overcome historical selection or omitted regime risk.

## Placebos and account level

The four pure filter comparisons verify identical retained dates, sides, entries, exits and net. The table shows
excluded-trade outcomes and 1,000 within-year random subsets with exactly the original retained count per year.
The last two columns are the fractions of random subsets earning at least the original's profit, or having at
most its DD. Smaller fractions favor the actual filter on that objective; these are conditional diagnostics,
not independent significance levels or multiplicity-adjusted discovery tests.

| Filter / era | Removed n | Removed total | Removed avg | Removed t | Random profit ≥ actual | Random DD ≤ actual |
|---|---:|---:|---:|---:|---:|---:|
| MON weekday, design |1,031|$56,935|$55|0.76|30.3%|16.4%|
| MON weekday, recent |779|$44,742|$57|0.45|1.0%|0.6%|
| BR ADX band, design |10|$328|$33|0.08|16.1%|100.0%|
| BR ADX band, recent |8|$4,297|$537|0.54|29.8%|87.1%|
| BR DI direction, design |92|−$24,222|−$263|−0.85|1.1%|1.3%|
| BR DI direction, recent |64|$61,986|$969|2.84|73.3%|49.0%|
| MOC magnitude, design |1,102|−$21,048|−$19|−1.72|0.0%|1.1%|
| MOC magnitude, recent |852|−$39,298|−$46|−3.51|0.4%|80.2%|

Paired effects use baseline minus intervention, 1,000 moving 20-session block draws, seed 80313. Intervals below
are **annual dollars, 5th–95th percentiles**, not whole-period dollars or account payouts. All fixed definitions,
failures and mixed findings are included; intervals are not adjusted for the earlier strategy searches.

| Baseline minus intervention | Design annual interval | Recent annual interval |
|---|---:|---:|
| MON all weekdays |[−$34,572, $11,155]|[−$55,048, $25,189]|
| MON short |[−$5,241, $37,193]|[$34,667, $102,776]|
| MON no stop |[−$8,402, $5,756]|[−$7,284, $7,863]|
| MON exit 10:00 |[−$1,706, $13,300]|[$8,308, $31,121]|
| BR no ADX band |[−$1,038, $1,103]|[−$4,523, $2,025]|
| BR no DI direction |[−$4,477, $13,774]|[−$25,204, −$7,095]|
| BR no target |[−$6,064, $6,868]|[−$22,875, −$1,545]|
| BR RTH entry |[$96, $10,192]|[−$7,407, $11,370]|
| MOC no move gate |[$18, $7,852]|[$5,979, $15,154]|
| MOC fade |[$4,461, $16,587]|[−$3,887, $8,523]|
| MOC no stop |[−$658, $692]|[$54, $1,722]|
| MOC exit 15:15 |[$229, $2,896]|[$538, $2,986]|

Under the frozen rule, the MOC magnitude gate and 15:00 exit have the stronger historical profit-contribution
label: positive effects and paired lower bounds in both eras. MON direction/later hold and BR Sunday entry
are positive in both eras but not above zero on both lower bounds. Bridge DI/target are conditional; its ADX
band and MON weekday restriction are not persistent total-profit improvements. Protection still needs separate
tail and account interpretation. No ingredient is labeled new alpha or an earned S-rank combination.

No additional random-time or random-side definitions were priced outside the frozen fifteen. Direction cases
and matched-count subsets are the bounded diagnostic controls, not a complete new-strategy admission suite.
No account simulations, sizing search, addition/replacement/empty-slot tests or live changes were performed:
this task decomposes existing rules. Any changed or combined candidate must get its own protocol, execution
checks, current-book tests and independent review. Historical daily net cannot establish a funded payout gain.

## What could make this wrong

Raw annual files are Git-blob/SHA256 checked against snapshot `fe35af99aa90d7f31b91f8693859251bb44dd9ab`.
Exact source copies and dependencies are committed before returns. Five synthetic fixture groups cover separate
ADX/DI intervention, unchanged source pricing, Sunday target chronology, target/micro costs and ES multiplier/gap
isolation. Original-source price parity passes **258/194 MON, 120/98 BR, 131/71 MOC** trades by era; MOC also agrees
with the retained independent vectorized price simulator. MON/BR source-wrapper identity is not an independent
native fill check. Gross/commission/slippage, daily, side and yearly totals reconcile for all fifteen cases.

Coverage and execution limitations remain explicit:

- Source Bridge requires Monday 14:55 data before replaying the prior Sunday entry; MOC checks full-session
  availability. These are retrospective coverage policies, not authenticated live-known data gates.
- MON original has **29/1 missing held bars** and **22/18 last-close fallback exits** in design/recent. Source
  walks skip absent bars and use the last available close rather than invent a scheduled fill. Holidays and
  incomplete sessions can therefore differ from another export/native implementation.
- BR original has **1,046/39 missing held bars** across **68/16 trades**, with no final-close fallback. Original
  Sunday target fills are **4/7**, kept at their actual Sunday times and attributed to Monday. The full observed
  Sunday-to-exit path is inspected, rather than starting risk measurement after midnight. Source target-bar
  range order is ambiguous; all target trades flag it. A target touch is not verified trade-through or queue fill.
- ES original has no missing held bars or fallback exits. Its feature audit records **49/43 sessions** with missing
  reference/decision/entry bars, outside the tradable full-session baseline. The source's predecision close
  forward-fill is preserved and flagged, not presented as an authenticated receipt feed.
- Dated-contract roll metadata, historical bid/ask, tick paths and actual order receipts are absent. Fixed-tick
  friction and source parity do not certify executable stop levels, latency, roll handling or intraday floors.
- Existing source optimizations, prior ablations and all earlier ingredient rounds remain selection history.
  Resampling these returns cannot undo it; the eras are not independent repetitions of a newly discovered rule.

The saved `path_ledger_audit.json` retains worst-event dates, observed marks, realized net, missing-path counts,
Sunday exits, ambiguous targets and the timing comparison's eligibility differences. This is supporting execution
evidence, also retained in `EXECUTION_REFERENCES.md`, not authorization to deploy or alter protection.

## Differences between MultiCharts code and this test

No new MultiCharts code was written and no new MultiCharts report was paired. The retained source is replayed;
its touch-target convention and fallback/coverage policies are reported rather than silently changed. Source
instrumentation only separates the two registered Bridge gates and preserves actual entry/exit/kind metadata.
Any future candidate needs explicit native fill parity and a separate account-level gate before consideration.

Reproduction uses the configured Python environment. `analysis/codex_ingredients_monday_moc_20261108.py fixtures`
runs synthetic checks without pricing market returns. The `design` and `recent` commands reprice the frozen
cases in order and refuse to overwrite existing phase directories; use a scratch checkout with saved outputs
moved aside intact. The report script regenerates summary tables and ledger checks from committed CSVs alone.

No TIER_LIST, trading-plan, live/VPS/broker/key, scout-history or scheduling changes. Independent review pending.
