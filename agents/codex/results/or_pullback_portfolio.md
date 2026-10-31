# ORPullback versus the current plan: REJECT as an addition or VB replacement

Summary: The earlier source review missed the user's requested portfolio backtest; this completes it.
Adding 1 MNQ reduces simulated two-year payouts $337 and increases blown accounts 8.3% to 10.7%.
Adding 2 MNQ or replacing VB is substantially worse; evaluation pass rates also fall.
Standalone recent returns are positive, but t1.96, DSR and random-time controls fail promotion gates.
Keep the current plan; missing stress sessions and execution concerns remain material limitations.

Plan: [preregistration](../plans/or_pullback_portfolio.md), committed **1ad4306** before actual-price replay.
Evidence: [TEST sheet](../evidence/or_pullback_portfolio.md). Current-plan pin: Claude
`a67035be4189b493098c80f1def979348520fd5d`. Independent checker:
[PASS WITH CONCERNS](REVIEW_or_pullback_portfolio.md).
Additional [diagnostics/exposure review](or_pullback_replay_checker.md) reconciles 200 arithmetic checks.
Scripts: `analysis/codex_or_pullback_{replay,plan,portfolio,diagnostics,supplement,exposure}.py`.
Output: `analysis/outputs/codex_or_pullback_portfolio/`; baseline audit:
`analysis/outputs/codex_or_pullback/baseline/`.

## Rule and account comparison

The funded roster is VB 2/1, ONB ML risk $400, MON 1, EOS risk $700, LDF 2, NFP risk $500,
Bridge 1, CL Sunday2 MCL, ES MOC2 MES and RS longs1 MNQ. Evaluation is VB 8, ONB ADX30
risk $1,100, Bridge 2 and EOS risk $500. This is an overall-plan comparison.

The source's fixed 15-minute opening range, subsequent counter-colour close outside the range,
50/100-point brackets, maximum two entries and one consumed trigger per side are unchanged.
Entries close through 14:30 CT; flatten 14:55 CT. Arming persists across a range recross and blocked
triggers consume their side. No optimization, side selection or author's rolling six-month switch.

Primary `reported_rule` protects from the first minute after the close entry. `literal_mc_delay`
models ordinary IOG-off source timing: five full post-entry minutes without brackets.
Both use a disclosed early-close adapter: flatten 11:30 CT, no entry at/after that time.
Entry-minute OHLC precedes the close fill and is excluded from held risk. Stops win minute
collisions and gap at adverse opens; targets need1-point trade-through and get favorable gap opens.
This is explicit Python modeling, not verified author or MultiCharts parity.

Costs are $1.04/micro round trip plus0.25-point slippage per market/stop fill; target exits have
no exit slippage. Trigger/bracket geometry is raw price. Entry slip and fees are included during
open exposure. The frozen$1.24 fee sensitivity applies to baseline and candidate together.

## Coverage and baseline verification

Existing caches were reused. Data ends **2026-10-09**. Of 2,262 trading sessions from 2018,
2,246 have complete minute OHLC 08:31 through applicable flatten. **Sixteen are excluded**,
including 2020-03-09,03-12,03-16 and03-18. Those omissions may reflect halts/stress and make
the risk estimates conditional on coverage; they do not establish survival on the missing days.

Funded histories use the same complete sessions for every configuration; removing sessions changes
block adjacency. Evaluation keeps real trading-day order and omits any 21-day window touching an
unknown session:1,972 starts, including 858 in 2023+. Unknown candidate returns are not zero returns.

The missing RS baseline ledger was rebuilt with its pinned unchanged functions: **1,161/1,161
trades reconcile exactly** on date,side,kind,entry,exit and net. Per-trade fee counts were recovered
from the same MC lists. No RS parameter search or price-cache rebuild was performed.

| Full-calendar baseline audit | Rebuilt | Latest saved |
|---|---:|---:|
| Funded expected1y | $9,193.50 | $9,180 |
| Funded expected2y | $11,976 | $11,982 |
| Funded blown2y | 7.7% | 7.6% |
| All six 2y | 91.0% | 90.8% |
| Median days 6 | 263 | 263 |
| Evaluation pass | 49.8449% | 49.8% rounded |

The small funded saved-reference discrepancy remains unresolved without its original serialized
lab. Do not claim exact saved-benchmark parity. Decisions below use internally paired rebuilt
baselines. All 160 production five-output checks match the current pinned funded_sim exactly;
the full-calendar reference has ten additional checks. This is simulator, not strategy/MC, parity.

## Funded results

These are Apex 50K funded-account simulations, not forecasts for every account size.

One thousand paired circular 20-day-block histories, seeds 1-4 ×250,500-day horizon and 250-day
payouts. Whole days keep strategies together. Unchanged funded cushion multiplier[.5,1],
reference$1,500, integer flooring. Noncompletion counts as infinite days to six. The following
table uses eligible2018+ sessions and$1.04 fees.

| Configuration | Expected 1y | Expected 2y | Blown 2y | All six 2y | Median days 6 |
|---|---:|---:|---:|---:|---:|
| Current plan | $9,021 | $11,948 | 8.3% | 90.4% | 270 |
| VB slot empty | $7,963 | $12,143 | 5.4% | 89.8% | 306 |
| Primary: add1 MNQ | $9,070 | $11,611 | 10.7% | 87.7% | 260.5 |
| Primary: add2 MNQ | $7,817 | $9,023 | 32.4% | 67.2% | 273.5 |
| Primary: replace VB with2 MNQ | $7,638 | $9,341 | 29.3% | 69.3% | 283.5 |
| Delayed: add1 MNQ | $9,038 | $11,634 | 10.4% | 87.5% | 263.5 |
| Delayed: add2 MNQ | $7,608 | $8,743 | 34.8% | 64.8% | 278 |
| Delayed: replace VB with2 MNQ | $7,479 | $9,191 | 30.2% | 67.8% | 288 |

Primary add1 MNQ first-year change is+$49, paired95% interval[−$119,+$217]. Its two-year
change is **−$336.50 [−$525,−$147]**, blown **+2.4pp [+0.8,+4.0]**. Add2 MNQ two-year
change is−$2,925 [−$3,280,−$2,584], blown+24.1pp [+21.3,+27.0]. Replacement also loses
to both current plan and empty VB. Payout5th–95th percentiles are $0–$13,000 for the baseline
and all candidate configurations; empty VB$3,000–$13,000. These path ranges differ from
uncertainty intervals for paired mean effects.

One nominal MNQ is floored to zero below full cushion; two nominal MNQ remains one at the half
multiplier. That discontinuity helps explain the larger risk increase at2 MNQ. Faster median
payout timing does not compensate for more failed accounts and lower expected total payouts.

| Frozen2023+ histories | Expected 2y | Blown 2y | Median days 6 |
|---|---:|---:|---:|
| Current plan | $11,959 | 8.4% | 229 |
| Primary add1 MNQ | $11,613 | 11.2% | 229.5 |
| Primary add2 MNQ | $9,172 | 31.0% | 246 |
| Primary replace VB2 MNQ | $9,251 | 30.5% | 262.5 |

At $1.24 fees, eligible2018+ baseline is $11,887/8.7%blown, add1$11,513/11.3%,
add2$8,895/33.7%, replacement$9,160/30.6%. No fee/timing sensitivity rescues the conclusion.
All paired intervals and individual outcomes are saved in CSV/NPZ.

## Evaluation results

Joint minute paths, actual current-plan integer sizes,$3,000 target,$2,000 EOD trail,
$1,000 daily limit and21-day horizon. Overlapping chronological starts are dependent.

| Configuration | Pass 2018+ | Pass 2018-22 | Pass 2023+ | Failed 2018+ | Median passing days |
|---|---:|---:|---:|---:|---:|
| Current plan | 50.61% | 47.04% | 55.24% | 47.62% | 6 |
| VB slot empty | 42.70% | 39.59% | 46.74% | 39.71% | 10 |
| Primary add1 MNQ | 48.73% | 45.78% | 52.56% | 50.41% | 6 |
| Primary add2 MNQ | 48.02% | 46.14% | 50.47% | 51.52% | 5 |
| Primary replace VB2 MNQ | 45.94% | 43.54% | 49.07% | 45.99% | 8 |
| Delayed add1 MNQ | 48.73% | 45.78% | 52.56% | 50.41% | 6 |
| Delayed add2 MNQ | 47.62% | 46.05% | 49.53% | 51.93% | 5 |
| Delayed replace VB2 MNQ | 46.20% | 43.72% | 49.42% | 46.50% | 8 |

Add1 primary pass change−1.88pp, paired 20-day-block95% interval[−4.16,+0.25]pp: no
demonstrated improvement. The inherited challenge routine awards pass on an exact minute tie
between target and breach, unlike stricter portfolio.py prose. Preserved for baseline consistency;
minute OHLC cannot establish the true intraminute sequence.

## Standalone diagnostics and controls

Dollar means below are net per1 MNQ; Sharpe uses eligible daily returns. Full side/year statistics,
both fees, Sortino/Calmar/Ulcer/maxDD and bootstrap intervals are saved in `diagnostics/`.

| Primary period/side | Trades | Win | Mean MNQ | Trade t | Daily Sharpe | PF |
|---|---:|---:|---:|---:|---:|---:|
| 2018-22 all | 1,502 | 44.0% | $6.98 | 2.34 | 1.06 | 1.15 |
| 2018-22 long | 806 | 45.8% | $4.91 | 1.27 | 0.57 | 1.11 |
| 2018-22 short | 696 | 42.0% | $9.36 | 2.02 | 0.89 | 1.19 |
| 2023+ all | 1,174 | 40.5% | $7.65 | 1.96 | 1.00 | 1.13 |
| 2023+ long | 623 | 42.4% | $10.41 | 1.95 | 0.99 | 1.19 |
| 2023+ short | 551 | 38.3% | $4.53 | 0.79 | 0.40 | 1.08 |
| 2018+ all | 2,676 | 42.5% | $7.27 | 3.03 | 1.03 | 1.14 |
| 2018+ long | 1,429 | 44.3% | $7.31 | 2.29 | 0.77 | 1.15 |
| 2018+ short | 1,247 | 40.3% | $7.23 | 1.99 | 0.67 | 1.14 |

| Year | Trades | Net1 MNQ | Trade t |
|---|---:|---:|---:|
| 2018 | 293 | −$317 | −0.19 |
| 2019 | 268 | $954 | 0.73 |
| 2020 | 321 | $100 | 0.05 |
| 2021 | 295 | $5,172 | 2.42 |
| 2022 | 325 | $4,569 | 1.84 |
| 2023 | 319 | $1,572 | 0.69 |
| 2024 | 314 | $3,270 | 1.37 |
| 2025 | 310 | $4,016 | 1.68 |
| 2026 through10/09 | 231 | $118 | 0.06 |

Primary closed-trade maxDD$1,939/MNQ overall; delayed$2,144. The2023+ daily Sharpe 90%
bootstrap interval is[0.21,1.77], maxDD95th percentile about $4,956/MNQ. Standalone252-day
EOD-only trail-breach estimates are 25.6% at1 MNQ and 56.6% at2 MNQ in 2023+; these omit
intraday breaches and cannot replace the joint bench.

Pinned trial log: 288 ranked items/1,241 variants; two new execution variants give N 290 and
t threshold 3.579. Primary full t 3.031/DSR 0.559 fail;2023+t 1.955 also fails. Delayed full
t 2.955/DSR 0.528 and recent t 1.852 fail. Unknown author search counts remain unaccounted for.

Each timing mode has1,000 random-side and1,000 random-time schedules with replayed exits.
Primary2023+ random-side p=.013, but **random-time p=.342** (full p=.461): the particular
pullback timing does not beat its same-day/side timing control. Controls can have fewer entries
when the first shifted/reversed trade blocks the second; counts are saved. No future-exit-based
resampling forces a constant count. The independent event walker exactly reproduces all 2,676
original exits per mode before controls.

At full integer plan size on common eligible sessions, primary daily correlation with the plan
is 0.276. On 829 plan-loss days,1 MNQ candidate net totals **−$13,339**, with 495 joint loss days.
This descriptive fixed-size diagnostic differs from actual cushion-sized account results.
In 2023+, 57.21% of candidate held minutes overlap another current NQ slot; 23.07% overlap VB.
Same-direction exposure overlaps 48.20%, opposite direction 11.26% (both can coexist).
At descriptive full size, adding 2 MNQ raises maximum concurrent NQ gross exposure while held
from 8 to 10 MNQ; replacing VB with 2 has maximum 8. These figures exclude MES/MCL and cushion
scaling. All nine NQ-leg trade counts reconcile with cached metadata; details are in `exposure/`.

## Limitations, review and reproduction

Original author ledger, search register and exact current-code MC parity remain missing. Feed/roll
differences, target trade-through, same-close execution, holiday adapter and incomplete sessions
prevent equating this with PDF returns. No PowerLanguage source was changed or compiled.
The baseline preserves legacy CL whole-Monday adverse marks and ES MOC close-based paths.
Summed adverse minute marks cannot recover every offset/fill sequence within a minute.
Bootstrap uncertainty conditions on the observed sample; it cannot restore omitted stress days
or establish future persistence. 2023+ was already seen, not a fresh sealed holdout.

Independent review checked all 32 funded summary rows against NPZ outcomes, all 160 production
simulator checks and ledger invariants. Status is PASS WITH CONCERNS for coverage, author parity
and the small saved-baseline discrepancy; it is not a clean promotion PASS.

Trial accounting: two price-return models, two fee regimes, eight allocations per fee, two funded
cohorts ×1,000 paired histories ×two horizons, three descriptive evaluation period cuts and
4,000 placebo schedules. No settings selected or changed after2023+ results. Daily statistics
were corrected to use the declared eligible calendar without changing any trade return.

Reproduce in order: `codex_or_pullback_plan.prepare_sources()` and `build_current_plan(...,
preregistration_commit='1ad4306', authorized_returns=True, plan_cache=...)`; then
`codex_or_pullback_replay.run_cached()`, diagnostics script, portfolio script, exposure script,
supplement script. Existing market caches are required; all input/cache and script hashes are
recorded in manifests. Windows bundled Python 3.12 plus ignored task-local packages was used;
the configured Linux venv is unavailable locally.

**Decision: keep the current plan.** Positive standalone returns do not compensate for worse joint
account results and failed statistical/timing gates. Claude reviews/ranks evidence; the user decides
trading. No live system, VPS, broker, keys, PR#2 or other agents' branches were modified.
