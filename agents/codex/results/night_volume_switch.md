# Overnight volume switch: WATCH; no current-plan change

Summary: This upload has positive standalone evidence: 866 eligible trades, $15.59/MNQ average, t 4.44.
Adding 1 MNQ improves expected first-year payouts $345, but two-year change is only +$25 [−$124,+$180].
Replacing ONB is worse; 2 MNQ increases recent risk, and evaluation shows no established gain.
DSR 0.94625 misses 0.95; the entry minute is unprotected, and original MultiCharts parity is unverified.
Keep the current plan; retain this as promising research rather than a promoted allocation.

Plan: [preregistration](../plans/night_volume_switch.md), **affb482**, committed before new returns.
Evidence: [TEST sheet](../evidence/night_volume_switch.md). Source: unchanged
`agents/codex/inputs/night_volume_switch/source.txt`, SHA256
`83b8e3bd67848a743e2df84fabe6a29b72cb8a1eb34d36d9afa0575eac1ec629`.
Latest context: Claude `febc65f1573040abf9a697d1d3468e1bce48c4c0`.
Scripts: `analysis/codex_night_volume_switch_{replay,diagnostics,portfolio,audit}.py`.
Output: `analysis/outputs/codex_night_volume_switch/`.
Independent implementation reviews: [diagnostics/accounts](REVIEW_night_volume_switch.md),
[account review](REVIEW_night_volume_switch_accounts.md), both PASS WITH CONCERNS.

## Rule and source-version differences

Heavy night: Ticks volume through the exact 08:29 bar exceeds 1.4 times the prior 20 valid-night
median, with at least 30 current bars. Fade its price move at the next observed open; stop distance
is 0.40 times prior 20 completed RTH high-low ranges, latest exit at the 08:45 bar open.
On nonheavy nights, a 09:59 one-sided upward morning range and close above session VWAP generates
a next-bar long, with 0.30-range stop. Exit at next open after a close below VWAP, else11:00 bar open.

Bars are close-stamped CT:08:30-bar open is08:29:00 wall time, and10:00-bar open is09:59:00.
The clock was not shifted to make the fade coincide with the cash bell. RTH and morning VWAP start
strictly after 08:30, normally the 08:31 bar. Histories use all observed bars, including warmup and
incomplete sessions, before any account coverage exclusion. No parameter optimization or side selection.

Two frozen models: primary `literal_delay` activates the explicit stop after the entry minute;
`immediate_stop` is an entry-protection counterfactual with identical signals. Executable benchmark
stops are rounded adversely to 0.25 points; actual stop gaps fill at the worse open. Market exits already
queued at a previous close fill at the next observed open before that bar's stop check. These are
declared execution assumptions, not proof of actual broker acceptance or tick-perfect MC parity.

The latest Claude branch already researched T_ONESIDE, but this upload changes total/up-tick volume,
night boundaries, the morning anchor, missing08:29 fallback, current-night validity and stop behavior.
Its867 raw trades share847 date/leg pairs with the prior874-trade ledger:20 are new,27 prior-only;
all shared pairs have the same side. Existing family returns cannot simply be assigned to this file.
Both new execution modes produce identical observed trade outcomes: no actual entry-minute stop hit
separates them in this sample. This does not establish that leaving the entry minute unprotected is safe.

## Code findings

- **Entry protection:** source 179-194 generates explicit stops only after position recognition at bar close;
  it also has no market fallback for a stop already crossed before placement. This is acknowledged in its
  comments. Built-in SetStopLoss has special same-entry-bar behavior; explicit next-bar orders differ.
  [MultiCharts SetStopLoss documentation](https://www.multicharts.com/trading-software/index.php?title=SetStopLoss).
- **Volume is a version change:** Ticks is total bar volume under Trade Volume; intraday Volume is the
  up-tick field. The exporter writes Ticks, matching this upload. It does not prove equivalence to the
  original strategy's Volume threshold or settings.
  [Ticks](https://www.multicharts.com/trading-software/index.php?title=Ticks),
  [Volume](https://www.multicharts.com/trading-software/index.php?title=Volume).
- **Thin-night OS guard:** lines 97-98 validate prior histories; lines 151-156 do not require30 current-night
  bars. A thin night may enter the nonheavy long branch. Preserved in the primary replay; no such actual
  entry occurred. There is no fallback classification when08:29 is missing.
- **Order-residency claim is unverified:** explicit stop syntax alone does not establish survival of a
  platform/disconnection failure. MultiCharts supports native and locally emulated price orders.
  [Auto Trading / Price Order Emulation](https://www.multicharts.com/trading-software/index.php?title=Auto_Trading).
- Normal exits precede ordinary early closes, so absence of a holiday list is not itself a default
  early-close violation. There is no final flatten fallback if those exits are missed; time-exit
  generation stops at15:00. No cross-date or late trade occurred in this replay. Orders omit Qty, so
  actual chart quantity is a strategy-property dependency; account tests explicitly use1/2 MNQ.

Prior-only median/range histories and array indexing are coherent. `pendStop` intentionally survives
the flat signal bar until fill; no ordinary stale-stop inheritance or future-information leak was found.
No PowerLanguage repair, compile, live setting or deployment was performed.

## Coverage, costs and baseline

Cache ends 2026-10-09. There are 2,254 shared complete mornings out of 2,262 trading dates:
1,282 design and972 recent. Eight excluded dates:2019-12-05;2020-03-09/12/13/16/18;
2021-09-17;2025-11-14. Missing stress sessions remain a material uncertainty, even though source
features are built before filtering. Funded blocks join eligible days; this changes adjacency.
Evaluation keeps real calendar order and excludes any21-day window touching an unknown morning.

Raw source replay has867 trades;866 are on the shared account universe. The excluded2025-11-14
fade earned$177.96/MNQ under the model; it was removed by the frozen coverage rule, not by its return.
No raw held gaps, missing-volume bars, late/cross-date trades or invented rescue fills occurred.
The eight-date exclusion differs from the earlier ORPullback test; compare candidates only with
the baseline included in this test, not its differently filtered baseline.

Use real $1.04/micro round-trip fees plus0.25-point slippage on both market/stop fills, totaling
$2.04/MNQ per ordinary trade. Sensitivity$1.24 fees applies to baseline and candidate together.
Signals and bracket geometry are unshifted by costs. The prepared baseline was reused: all 27
dependency blobs, real_fee_bench and RS source/reference are unchanged at the latest context pin.
No price or shared research cache was rebuilt.

The earlier full-calendar rebuilt funded baseline remains$9,193.50/$11,976 at1y/2y versus saved
$9,180/$11,982: close, not identical. This unresolved small input/context difference remains disclosed.
Inherited CL whole-Monday adverse marks and ES MOC close-based paths are preserved. Full21-day
evaluation BASE gives50.00% over2,242 starts; the older49.8449% reference also counted truncated-tail
starts that had already passed/failed. The main paired comparison below uses2,151 complete starts.

## Standalone results

All means below are net per1 MNQ at $1.04 fees, on the frozen eligible universe. Full standard
metrics, years, sides, legs and both fees are in `diagnostics/standard_stats.csv`.

| Period/group | Trades | Win | Mean MNQ | Trade t | Daily Sharpe | PF |
|---|---:|---:|---:|---:|---:|---:|
| 2018-22 all | 516 | 55.6% | $13.49 | 3.63 | 1.60 | 1.58 |
| 2023+ all | 350 | 50.3% | $18.69 | 2.77 | 1.40 | 1.49 |
| 2018+ all | 866 | 53.5% | $15.59 | 4.44 | 1.47 | 1.53 |
| 2018+ longs | 717 | 52.4% | $13.54 | 3.65 | 1.21 | 1.47 |
| 2018+ shorts | 149 | 58.4% | $25.46 | 2.57 | 0.84 | 1.77 |
| 2018+ fade | 362 | 58.8% | $23.08 | 3.46 | 1.14 | 1.63 |
| 2018+ OS | 504 | 49.6% | $10.21 | 2.79 | 0.93 | 1.43 |

The whole book is positive in every year 2018-26, with2026 partial through10/09. Annual net1 MNQ:
$643,$666,$2,333,$2,032,$1,286,$1,259,$1,983,$399,$2,900. Both sides have positive design
and recent means; no side/leg was promoted or given a selected portfolio allocation.
Whole max closed-equity DD is$1,204/MNQ. Recent daily Sharpe90% bootstrap interval[0.63,2.19];
DD95th percentile about$1,979/MNQ. Standalone252-day EOD-only trailing-breach estimates in 2023+
are0.64% at1 MNQ and15.46% at2 MNQ. These omit intraday breaches and do not replace the joint test.

Latest trials log:290 ranked items/1,245 variants. Add prior unranked ORPullback2 and the two new
execution models: N 294, t threshold3.58264. Full t 4.43775 passes; **DSR 0.946250 fails 0.95**.
The required tANDDSR gate therefore fails. Do not round this to a pass. Author selection burden
remains incompletely known;2023+ is historical replication, not fresh sealed evidence.

Controls reexecute stops and VWAP/time exits. Primary recent random-side p=.002997 and random-time
p=.000999. Null timing occurs only after the source information is known. An independent event walker
matches all 866 actual exit minutes, kinds, phases, gross returns and rounded stops per mode before controls.
Heavy-night fade selection also beats matched-count random masks on recent total profit(p=.004995).
Quiet removed fades have mean −$1.77/MNQ,t−0.43 over844 trades: their loss estimate is weak.
The recent drawdown-control p≈.25 is not strong evidence of improved drawdown. No heavy-OS or symmetry
optimization was added; prior-family tests of those cells remain context rather than new selections.

## Funded plan comparison

Apex 50K funded plan unchanged: VB 2/1,ONBMLrisk400,MON1,EOSrisk700,LDF2,NPFrisk500,Bridge1,
CLS2MCL,MOC2MES,RS_L1. One thousand paired 500-day histories,20-day circular blocks,seeds1-4×250,
also measured at250days. Integer cushion scaling[.5,1], reference $1,500. Days6 includes infinity
for noncompletion. Primary and immediate-protection results are identical; both are saved.

| Eligible2018+ configuration | Expected 1y | Expected 2y | Blown 2y | All six 2y | Median days 6 |
|---|---:|---:|---:|---:|---:|
| Current plan | $8,939 | $11,790 | 9.4% | 89.2% | 269.5 |
| ONB slot empty | $6,752 | $11,086 | 11.7% | 78.4% | 333.5 |
| Add1 MNQ | $9,284 | $11,815 | 9.0% | 89.8% | 256 |
| Add2 MNQ | $9,666 | $11,638 | 10.9% | 88.6% | 243.5 |
| Replace ONB with2 MNQ | $7,979 | $11,039 | 15.2% | 81.1% | 296 |

Add1 produces a real first-year acceleration signal: **+$345 [+$222,+$472]**, median days 6
13.5days faster. Its two-year effect **+$25 [−$124,+$180]** and blown−0.4pp[−1.7,+0.8]
are uncertain. Add2 increases expected1y$727 but changes2y−$152.50[−$405,+$87]. These are
different objectives; do not describe faster early payouts as no benefit or as a proved lasting gain.
Two-year payout5th–95th percentiles are $0–$13,000 for all configurations, distinct from paired mean CIs.

| Frozen2023+ histories | Expected 1y | Expected 2y | Blown 2y | Median days 6 |
|---|---:|---:|---:|---:|
| Current plan | $10,453 | $12,043 | 7.5% | 227 |
| Add1 MNQ | $10,593 | $11,990 | 7.9% | 219 |
| Add2 MNQ | $10,736 | $11,749 | 9.9% | 214 |
| Replace ONB2 MNQ | $9,562 | $11,319 | 13.7% | 241.5 |

Recent add1:1y+$140[+$4,+$280],2y−$53[−$195,+$85],blown+0.4pp[−0.7,+1.6].
Add2:2y−$294[−$546,−$62],blown+2.4pp[+0.6,+4.4]. Replacement:2y−$724[−$1,013,−$461],
blown+6.2pp[+4.0,+8.6]; it also loses to the empty slot recently. At$1.24 fees, recent add1
2y effect−$92.50[−$251,+$56],add2−$320[−$578,−$77],replacement−$780.50[−$1,071,−$512].
No promotion is established by these sensitivities.

## Evaluation and exposure

Current evaluation set: VB 8,ONB ADX30risk $1,100,Bridge2,EOSrisk $500; same eight frozen allocation
configurations, with replacement removing ONB30. Real21-day windows,integer sizes,joint minute paths.

| Configuration | Pass 2018+ | Pass 2018-22 | Pass 2023+ | Median passing days |
|---|---:|---:|---:|---:|
| Current plan | 49.74% | 46.10% | 54.51% | 6 |
| ONB slot empty | 38.77% | 29.53% | 50.86% | 11 |
| Add1 MNQ | 49.28% | 46.10% | 53.43% | 6 |
| Add2 MNQ | 50.02% | 46.84% | 54.18% | 6 |
| Replace ONB2 MNQ | 39.52% | 31.34% | 50.21% | 11 |

Recent pass changes: add1−1.07pp[−4.33,+1.72],add2−0.32pp[−4.08,+3.20],replacement−4.29pp
[−12.65,+4.40]. The small overall add2 gain+0.28pp does not persist in recent starts and is within
uncertainty. Intervals resample20 chronological starts before omitting invalid windows; starts overlap
and are not independent accounts. Inherited same-minute target/breach ties are pass-first, disclosed
for consistency with the existing challenge routine. Higher fees do not create an evaluation advantage.

Recent full-size daily correlation with the plan is 0.094; candidate1 MNQ net on 357 plan-loss days is
+$1,063.70. Yet 73.33% of held minutes overlap existing NQ exposure, 71.04% same-side and 2.30%
opposite-side; RS_L44.41%,VB_N29.47%,ONB14.12%. These descriptive MNQ figures exclude MES/MCL
and cushion scaling. They do not establish that hedging gains arrive before a breach; the joint
account simulation, not correlation alone, determines the reported account effect.

## Review, trial count and decision

Parent audit independently reconciles2,112 arithmetic fields across240 diagnostic rows,32funded
rows and48evaluation rows; all 160 original-simulator five-output checks match exactly. Peer reviews
also check null draws, heavy/quiet controls and independent phase fixtures. Implementation status is
PASS WITH CONCERNS, not a blind source reconstruction or a clean promotion PASS. Original MC export,
broker-event/stop acceptance parity and disconnect residency remain unresolved. Tick rounding is an
explicit executable benchmark adapter; no compiled source or deployment is delivered.

Trial record: two source execution models, two fee regimes, two all-night-fade falsification models,
4,000 side/time schedules and2,000 full-calendar random masks, eight account allocations per fee,
two funded cohorts and three evaluation period cuts. All are reported; no leg or mode was selected.
No more than four strategy return models were examined. Missing stress sessions and inherited
CL/MOC/adverse-minute baseline approximations remain in every interpretation. Separate per-leg
adverse extremes are conservative and cannot recover tick-order netting of simultaneous positions.

Reproduction: use existing caches and prepared baseline; run
`codex_night_volume_switch_replay.run_cached()` after affb482, then the diagnostics CLI, portfolio CLI
and audit CLI. The replay retains warmup without rebuilding caches. Manifests record source, script,
data, prior-reference and unchanged baseline hashes. Bundled Python 3.12 with existing ignored
task-local scientific packages was used; the configured Linux venv is not available on this PC.

**Decision: WATCH, retain current plan.** The standalone edge and earlier payout signal merit further
research, but the declared DSR/MC gates and a clear sustained portfolio advantage are not met.
Claude reviews/ranks these results; the user decides trades. No live, VPS, broker, key, PR#2 or
other-agent branch was changed.
