# Anson intraday momentum/range: REJECT for the current plans; move on

Summary: Tested the user-intended NQ 5-minute 4.5/20 rule across50K/150K evaluation, funded and personal plans.
Positive standalone OOS mean remains uncertain:2025+ 373 trades, $155/NQ,t 0.97,95%block interval[−$104,+$453].
At1 MNQ,2025+50K funded payouts fall$1,535 and failures rise12pp;150K payouts fall$250.
Evaluation shows no established gain; personal additions increase capital/DD burden and lower matched-risk returns.
No useful placement demonstrated; retain all current plans and stop this candidate without further optimization.

Plan: [preregistration](../plans/anson_momentum.md), committed **928c0ea** before new returns.
Evidence: [TEST sheet](../evidence/anson_momentum.md). Inputs:
`agents/codex/inputs/anson_momentum/{source.txt,user_spec.md}`.
Latest context: Claude `e34d71cd3537a9f019d2521e280fc92f3ffdb4c6`.
Scripts: `analysis/codex_anson_{replay,plan,accounts,personal,diagnostics,audit}.py`.
Outputs: `analysis/outputs/codex_anson/`.
Reviews: [implementation checker](REVIEW_anson_momentum.md), [personal arithmetic checker](anson_personal_checker.md).
Personal details: [personal report](anson_personal.md). These are implementation reviews with concerns,
not an original-author MultiCharts confirmation or a blind source reconstruction.

## Tested rule and source fidelity

User's final settings override the file defaults: **threshold 4.5,hold 20**, NQ 5-minute bars,CT,
Default-session proxy from continuous observed Grid24 bars,IOGoff. Momentum=close−close12 bars ago;
strength=abs(momentum)/mean 20 preceding bar(high−low),excluding current. Follow its sign,flat only,
signals 08:30–14:30 inclusive,next observed chart-open entry. Count the entry bar as completed held1,
queue exit after20 completed bars or at 14:55,next chart-open fill. This is100minutes when contiguous.
The14:55 exit signal fills at wall 14:55,normally the minute closing 14:56; it is not a five-minute-late exit.
An exited chart bar stays flat until its close before another possible next-open entry.

No volume field is used despite the filename. No stop, target or volatility sizing is added.
Three preregistered models: `intended_raw` for personal/source comparison; `intended_apex` with repo
early-close entry cutoff/flatten 11:30; and `defaults_raw`3.0/6 as a standalone diagnostic only.
Defaults were not selected into plans. The unchanged uploaded code therefore does not itself contain
the user's intended inputs. Source histories use all observed bars before account coverage filtering.

Raw source produces 2,059 closed trades,including 11 late trades,one cross-date Christmas carry and
eight trades with unexplained observed-minute gaps. An absent14:55 on early-close dates can carry a
position into reopen; raw personal returns retain those fills and mark positions at/before 16:00.
The closure classifier is only an audit proxy; unknown gaps are not proof of feed loss. No rescue fill
or nonexistent stop was invented. The Apex adapter removes that operational problem before testing.

## Direct answers to the user's questions

**Does the smaller sample explain an interval below zero?** It can. Mean precision depends on both
sample size and variability; dependence reduces effective sample size. In the supplied claims, reducing
2023trades to352 would increase width by about2.4× at unchanged variability,while reported width grows
5.3×. Those comparisons assume comparable interval methods and independent sampling,so they are
illustrative rather than reconstructed author statistics.
[NIST confidence limits](https://itl.nist.gov/div898/handbook/eda/section3/eda352.htm).

The replication directly shows more dollar variability too: per-NQ trade SD is about$1,523 in2018–24
and$3,090 in2025+; median preceding bar range grows14.24→28.04points. Range normalization changes
entry selection,not contract size. Constant contracts therefore do not keep dollar exposure constant.
The2025+ estimate is positive but compatible with negative or zero expectancy. More observations may
narrow uncertainty if the process persists; they do not guarantee that the mean stays positive.

**Is it overfit?** Selection risk is real,not proved by a rough curve. Stops,targets,sizing,long-only
and WFO alternatives count even when discarded and the final model is simple. Exact search counts,
original freeze dates and all variant returns are missing,so no exact PBO or clean author holdout
certification is possible.2025+ is only out of sample if it was untouched during all selection;
these already-reported years are historical replication for this review.
[Bailey et al.,Probability of Backtest Overfitting](https://www.davidhbailey.com/dhbpapers/backtest-prob.pdf).

**Does the rough OOS curve matter for prop accounts?** Yes: the trail and daily-loss threshold depend
on open account equity,not just average trade EV. The joint-account tests below show that this
variation costs payouts and survival probability at the tested sizes. No-stop code is not rejected
by label alone; its actual observed adverse paths were tested before reaching that conclusion.

## Standalone evidence

Amounts below are **per1NQ**, under the Apex1 MNQ-equivalent convention: fee$1.04/micro plus1tick
on each market fill,total$20.40/NQ-equivalent or$2.04/MNQ. The author's quoted$7.25total is lower;
it is shown as arithmetic sensitivity on the same ledger,not called exact author parity.

| Raw intended period | Trades | Net mean NQ | Trade t | PF | Daily Sharpe |
|---|---:|---:|---:|---:|---:|
| 2018–22 repository design | 1,209 | $47 | 1.16 | 1.10 | 0.50 |
| 2018–24 partial author IS | 1,686 | $81 | 2.18 | 1.17 | 0.81 |
| 2023+ | 850 | $161 | 1.93 | 1.22 | 0.99 |
| 2025+ author-OOS replication | 373 | $155 | 0.97 | 1.16 | 0.72 |
| All2018+ | 2,059 | $94 | 2.25 | 1.17 | 0.75 |

2025+95%whole-day10-day-block EV intervals: both[−$104,+$453],long[−$93,+$631],short[−$291,+$475].
Both sides have positive means,but that does not establish either edge. Raw full max daily-markedDD is
about$3,953/MNQ. The Apex-adapted common universe has2,038trades,fullmean$106/NQ,t2.52,DSR 0.349;
2025+370trades,mean$147,t0.92,EV95%interval[−$110,+$439].

Latest trial log291items/1,246variants,plus prior unrankedCodex4 and these3models gives N 298 minimum,
t threshold 3.586. Raw full t 2.249/DSR 0.255 and Apex t 2.517/DSR 0.349 fail the required tANDDSR≥.95 gate.
Unknown original search burden is additional. File-default3/6 loses overall after costs(mean−$2.60/NQ,
t−0.23 across8,086trades); it was not used to replace the intended model after seeing results.
All long/short/year statistics,Sortino,Calmar,Ulcer,bootstrap andMC outputs are saved in `diagnostics/`.

Random-side conditional controls:2025+p=.145;fullp=.004. The random-time control outperforms the
actual schedule,but conditions on actual event days and direction order; it can use a later signal's
direction at an earlier sampled clock. It is **not a causal tradable alternative**, and its p=1 does
not prove a momentum-free strategy wins. Counts also fall when shifted events overlap. These limits
are retained rather than changing the null after seeing results; rejection does not rely on that control.

## All five plan contexts

Apex uses1,000paired500-day circular20-day-block histories,seeds1–4×250,also measured at250days,
plus real complete21-day evaluation windows.2025+histories resample the available recent days;
they are conditional simulations,not two years of newly observed forward trading.

| Context | Matched baseline | Intended addition | Result |
|---|---|---|---|
| 50K evaluation,2025+ | 55.88%pass | +1 MNQ52.41%;+2 MNQ46.79% | No improvement |
| 150K evaluation,2025+ | 42.51%pass | +1 MNQ42.78%;+2 MNQ41.18%;+4 MNQ38.77% | +0.27pp is noise; higher fee erases it |
| 50K funded,2025+ | 2y$10,923;16.7%blown | +1 MNQ$9,388;28.7%blown | Worse payouts and survival |
| 150K funded,2025+ | 2y$18,741;9.0%blown | +1 MNQ$18,491;10.2%blown | Worse; larger sizes much worse |
| Personal full 14,2018+ | median1y$23,698;DDp95$5,001 | +1 MNQ$25,614;DDp95$6,077 | More dollars,less return at matched risk |

50K funded+1 MNQ2y difference−$1,535,paired95%CI[−$1,856,−$1,216];blown+12pp[+9.4,+14.6].
150K funded+1 MNQ difference−$250[−$465,−$30],blown+1.2pp[0,+2.4].50K+2 MNQblown54%;150K+2 MNQ29.7%
and+4 MNQ55.5%. Full-VB replacements also lose; neither the empty slot nor its better-looking standalone
outcome authorizes a plan change. The50K evaluation+1 change−3.48pp[−9.58,+2.14];150K+1+0.27pp
[−1.55,+2.24]. Replacements pass27.27%/18.18% on50K/150K. Both fees$1.04/$1.24 were reported.

Current150K funded includes DualThrust2 MNQ and RSboth1; other roster bases are1.5×the50K non-RS set,
with fractional bases floored after cushion sizing,ref$3,000.50Kref$1,500. DT uses the committed
timed replica ledger,strict1,611/1,611reconciliation against primary trades,not a signal rebuild from
missing2017RTHwarmup.150K evaluation computes integer risk counts after scaling dollar budgets; older
2.5×already-floored50Kcounts are not treated as actual executable sizes. All current plan inputs are pinned.

Personal tests cover all21frozen allocations across starterA/B/C/D and full 14: additions1/2 MNQ,
plus emptyVB and equal-contractVB replacement where present. Every tested addition/replacement
reduces return/DD and median profit at the same p95DDbudget in both2018+and2025+cohorts.
Full +1 requires about$30,387 versus$25,004 at the plan's20%DD rule; recent required capital grows
another$5,731 while median profit rises$3,221. The historical20-day-block95%annualized contribution
interval is[−$1,937,+$9,137] in2025+. Narrow intervals for the mean of simulated paths measure
MonteCarlo sampling precision conditional on history,not certainty of future edge.

## Limits, verification and handoff

Data ends 2026-10-09;local 2016–17RTH is absent,so the quoted2016–24IS cannot be exactly rebuilt.
Our373recent trades differ from reported352; vendor,session properties,end dates and original ledgers
are not supplied for reconciliation. Full source/chart parity is unverified.

The Apex comparison excludes 17incomplete dates,including five March 2020stress dates. Source histories
are retained first; all allocations share 2,245eligible days and 374 recent complete evaluation starts.
Unknown sessions are excluded,not zero returns; funded block adjacency changes. Raw personal carries
are retained and marked using only observed closes at/before 16:00; closures and feed gaps remain uncertain.
Daily-only personalMC does not certify intraday margin safety. Its published fee convention1.275 is
preserved,including known per-nonzero-day VB undercharging and inherited Twin-ledger/mark approximations.

Existing CL/MOC adverse-path approximations and the small prior50Ksaved-baseline discrepancy remain.
The candidate Apex commission is charged at exit while legacy baseline open marks reserve fullRTfee;
this small timing asymmetry favors the candidate before exit and is disclosed. No return or variant was
changed to improve that result. Same-minute evaluation ties preserve50Kpass-first/150Kbreach-first rules.

All 220production original-simulator five-output comparisons and 100 synthetic50K/150Kchecks pass.
The parent audit reconciles2,574fields across 252standard,44 funded,110 evaluation and42 personal summaries.
Peer review separately checks phase timing,2038eligible timed exits,personal marks,raw ledger totals and
uncertainty labeling. Implementation PASS WITH CONCERNS does not satisfy a clean original-source promotion gate.

Trial count: three immutable return models,twoApexfee regimes,11Apexallocations by size,21personal
allocations,paired full/recent cohorts and2,000conditional placebo schedules. No neighbours,stops,
targets,sizing,WFOorselectedside search was added. Reproduce with the committed replay,plan,accounts,
personal,diagnostics and audit scripts after 928c0ea; ignored caches are reused and all inputs/hashes
are recorded. No live, VPS, broker, key, PR#2 or other-agent branch was modified.

**Decision: no place in the tested current plans. Move on.** The user's standing all-plan upload workflow
is recorded in [USER_CODE_WORKFLOW.md](../USER_CODE_WORKFLOW.md). Claude reviews/ranks;the user decides trades.
