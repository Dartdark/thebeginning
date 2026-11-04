# Prior evaluation search audit — November 4, 2026

Summary: Existing work supports tradeoffs, not a proof that the present evaluation book is globally optimal.
Claude's latest bench tests 21 historical portfolio labels and eight recent-window presentations, mostly VB/ONB size changes.
Its strongest low-failure 50K alternative is ONB $550: reported pass49.4%,fail39.8%,timeout10.8%, versus50.0/48.1/1.9 baseline.
Many earlier "safer" rules reduce failures mainly by increasing timeouts; every new comparison must report all outcomes and time/cost.
This note reads saved work only: zero new return simulations, no plan/live changes, no independent economic reproduction.

## Scope and pinned sources

Local research snapshot: `codex/work` initially `0da4e8f1b7f42309ab3ad84635ad082b9ae895bf`.
Latest Claude source inspected read-only by `git show`:
`13e29ca7b45daabeb0ed2d8c286448610f594dab`, November4,2026 22:22:05UTC.
The source branch was never checked out, written or reset. All figures below are existing reported results, not newly run results.
Read AGENTS/builder/current context plus development/lesson/selection sources. Do not run paused t6/StrategyHuntv2.

The latest relevant Claude commits are:

- `75c1bd02689858f3f79d63d96e4b45cb3cb6899c`: #2/#4 failed November4; pre-screen softened and lessons corrected.
- `af1a271690ae9dad3c64bb035ebb14279cc07ccf`: live-vs-model replay through November4.
- `3a40d94db8de40745df2d17a6a44750610861404`: evaluation sizing script, stated run in progress with partial output.
- `13e29ca7b45daabeb0ed2d8c286448610f594dab`: final sizing output and brief update.

## Current evaluation reference

`analysis/eval_sizing_bench.py:1–8,67–81` at the pinned Claude head uses:

|Home|VB|ONB ADX30 dollar risk|Bridge Monday|EOS dollar risk|Historical rules used|
|---|---:|---:|---:|---:|---|
|50K|8MNQ|$1,100|2MNQ|$500|+$3,000target,$2,000EODtrail touched intraday,$1,000daily pause,21trading-day approximation|
|150K|20MNQ|$2,750|5MNQ|$1,250|+$9,000target,$4,000trail,$2,000daily pause,21trading-day approximation|

ONB/EOS quantities are floored separately from the dollar risk at each account size. The 150K book must not be created
by multiplying already-rounded 50K quantities by2.5. Exact deadline/product/fee and intraday fill assumptions still
require the account-engine audit; the historical documents are not current broker-rule certification.

## Latest Claude bench: useful facts and limits

Source: pinned `analysis/outputs/eval_sizing_bench_output.txt:4–27` and script `:67–81`.

|Home/policy|Reported pass|Reported fail|Timeout|Median pass days|
|---|---:|---:|---:|---:|
|50K current|50.0%|48.1%|1.9%|6|
|50K VB6|49.1%|47.5%|3.4%|7|
|50K ONB$800|49.2%|46.2%|4.6%|8|
|50K ONB$550|49.4%|39.8%|10.8%|9|
|50K VB4+ONB$550|37.6%|29.8%|32.5%|13|
|50K VB6+loss-cap+ONB$800|47.4%|43.5%|9.1%|9|
|150K current|41.0%|56.6%|2.4%|8|
|150K VB15|40.8%|54.1%|5.1%|8|
|150K ONB$2,000|39.1%|54.8%|6.1%|9|
|150K ONB$1,400|35.7%|53.1%|11.2%|10|
|150K VB10+ONB$1,400|28.6%|42.8%|28.7%|14|
|150K VB20+VB loss-cap|41.1%|56.5%|2.4%|8|

There are eleven historical 50K rows and ten historical 150K rows, including baselines. SectionC then shows four
pre-existing configurations on each of two recent windows. These are not an exhaustive strategy-universe or sizing search.

Important qualifications:

1. **"No sizing would have survived this stretch" is too broad.** SectionC script`:89–92` contains exactly four
   configurations per account. It does not establish that all position sizes or all different strategy books failed.
   A sufficiently small exposure could mechanically survive a loss sequence while failing to reach the target.
   Survival, pass probability and long-run economic value need separate objectives.
2. **SectionC printed P&L is not a dead-account realized ledger.** Script`:97–101` computes account failure, then
   separately sums full-window `Rs[s0:De,-1]` and worst daily P&L through November4, including dates after a modeled
   account failure. This is a potential strategy-stream diagnostic, not the balance trajectory of an account after failure.
3. **Fee labels need correction/qualification.** Script`:8,21,55` defines$249 as the150KNo-Activation evaluation fee
   but applies it to both account sizes and prints "fee per funded" as fee/pass. This is evaluation-acquisition cost
   under that scalar assumption, excluding any activation/other fees, correlated retry dynamics or a verified50Kprice.
4. **Loss cap means gross price loss here.** Script`:24–32` marks a loss by exit-vs-entry price, rather than full net
   after commission/slippage. A small price gain with negative net would not activate it. The sequence also needs
   confirmation that a later admission occurs after the prior exit; one-position VB trades may ensure this, but it is
   not proven for arbitrary alternative ledgers by the helper alone.
5. **Recent outcomes are already seen.** The output provenance says `af1a2716 dirty`; the script/partial output commit
   precedes the final output commit, but a clean committed preregistration before the first outcomes was not established.
   Preserve this as prior selection history; do not call a renewed November4 comparison a fresh holdout.
6. **Current head is newer than the local brief.** Latest `NEW_CHAT_BRIEF.md` now identifies #2/#4failedNovember4,
   #1failedOctober26 and #3failedOctober30, with no open accounts. The older #2~46%pass-odds statement is stale context.

## Earlier search history that must not be erased

|Source|Declared search/count|Reported result or implication|
|---|---|---|
|`analysis/pipeline_tuning_test.py:1–10`, saved output|72combine grids: VB4/6/8/10×ONB$700/$1,100/$1,500×Bridge1/2/3×EOSoff/$500; twelve funded sizing grids afterward|Four-strategy sizing grid, not all-strategy optimality. Current50Kpasses50.1%, but ranked46.5on its old three-year pipeline objective. Different objective selects different policies.|
|`analysis/combine_levers_test.py:1–15,65–73`, saved output|Twelve prespecified nonbaseline levers plus a post-hoc pair|Current50.1/48.1/1.9; whole scale0.75pass47.6; finish-halfafter+$2,000pass51.2; daily−$750pass50.9. Post-hoc pair52.4needs inherited multiplicity, not renewed promotion. Source explicitly scales quantities continuously.|
|`analysis/combine_swap_test.py`, saved output|ONBML risks$800/$1,100/$1,400; simultaneousADX+ML; scaled funded books; several composite levers|ONBML$1,100instead ofADX:52.0%pass,39.1%fail,8.9%timeout,9medianpassdays; baseline50.1/48.1/1.9,6days. A modest existing Pareto candidate, not a verified universal improvement.|
|`analysis/vb_cushion_sizing_test.py`, saved output|Five nonbaseline VB/whole-set cushion policies|VB4below$1,500:48.4%pass; VBoffbelow$1,200:47.8%; wholehalfbelow$1,000:46.3%. Lower fail count does not automatically lower cost/time per pass.|
|`analysis/onb_cushion_test.py:1–6,17–40`, saved output|Four nonbaseline ONB/VB gates for each size, native integer ONB risk|50K bothONB+VBoffbelow$1,200:36.2%pass,11.3%fail,52.5%timeout.150K bothoffbelow$3,000:24.7/10.7/64.6, versus41.0/56.6/2.3baseline. Daily-start gates do not equal per-entry remaining-cushion protection.|
|`analysis/combine_vb_size_test.py`, saved output|VB4–10,other book unchanged|50K pass48.2–50.4%; VB8nominalstop$1,200already exceeds$1,000daily pause; old engine clipping/fill realism needs independent checking.|
|`analysis/single_print_combine.py`, saved output|Several flagged-day sizes plus ten random-day controls|VB8/4reported50.5vs50.1baseline; best placebo50.5. Small difference not a proven new edge.|
|`analysis/dual_thrust_combine.py`, saved output|14add/replacement mixes plus baseline in saved50Ktable|DTadd/replacement generally worse; VB4+DT2reported49.6%pass/46.5%fail. A new ticker/title is not new information.|
|`analysis/swing_target_bench.py`, saved eval output|12fifty-Krows and9one-fifty-Krows including baselines|50KST1add50.0vs50.1;150KST1–3add41.2vs41.0. Later exit-kind/source-account reviews are material; never re-adopt old saved swaps without matching corrected ledger/current roster.|
|`analysis/combine_days_test.py`, saved output|S47/FC2B1–3MNQadditions|Pass probabilities around47–50%; some more passes byday10 but not an overall pass gain. Speed and ultimate pass are different.|
|`analysis/combine_gold_test.py`, saved output|14gold-add rows and6gold-alone rows|Adds generally reduce passes; gold-alone smaller risk often survives by timing out. Mixed-symbol uncorrelation alone does not establish account benefit.|
|`analysis/codex_overlap_risk_cap.py`, report|Five fixed funded variants|NQcap2lowered rawDDbut reduced profit, slowed payouts;2023+fundedblown6.7→9.9%. A funded result is not an evaluation rejection proof, but prevents assuming an exposure cap must help.|

Counts above are source-declared grids/printed rows and can contain repeated baselines, overlapping economic
definitions and implementation reruns. They are not summed into an invented unique global count. Preserve original
trial registers and add each new portfolio definition before returns. Existing2023+has been viewed repeatedly.

## Sources that must not become the new account optimizer

- `analysis/account_tools.py:4–18,87–104`: dashboard `pass_odds` uses daily-P&L5-day bootstrap, explicitly omits the
  daily loss limit and uses60days if deadline missing. It misses intraday breaches and cannot validate a thin-cushion
  size recommendation. The ~46%older brief number must not be imported as native account evidence.
- `analysis/combine_levers_test.py:13` explicitly says continuous scaling; not executable native integer sizing.
- `analysis/pipeline_tuning_test.py:24–27` applies an ex-post average-profit haircut as a stress. This is not an
  estimated point-in-time trading signal. A renewed chronological selection should freeze its stress definition
  from design data and keep it distinct from operational slippage/fee stress.
- Old small decimal differences41.6vs41.0for150Kare not economic progress without matching input coverage,
  native risk flooring, fee conventions and end-window handling. The October30integer correction is already known.
- Rolling21-day-start outcomes overlap heavily. Do not use the number of starts as independent Bernoulli sample
  size for narrow confidence intervals. Preserve whole-day, all-strategy pairing and block dependence.
- "Near ceiling for this edge" in the old plan is a heuristic description of its finite search, not a mathematical
  proof that no replacement portfolio or correctly modeled policy can improve it.

## Useful next research menu for root preregistration

These are source-informed policy families, not a new recommendation or executed search:

1. Correct reference with native per-trade integer sizing, actual account rule/deadline and fees, intraday marks,
   realistic stop/daily-liquidation fills and current costs. Recover why the latest replay can report a modeled
   failure earlier than the actual account's later failure before calling it calibrated.
2. Fixed per-strategy sizing and existing ONBML substitution: explicitly include the already observed ONB$550
   50Ktradeoff and ML$1,100swap as inherited candidates; compare pass/fail/timeout/time/fee with paired uncertainty.
3. A bounded admission-risk policy based on **current** remaining cushion and known stop/cost budgets at each entry,
   rather than only morning cushion or an oracle future worst path. Include existing open-position commitments.
   Stops can gap; a risk budget is not a guarantee. Exact prospective metadata is necessary.
4. Distinct verified-strategy-book replacements from the separately audited universe, using design-only selection
   and stable clusters rather than the best of a huge full-history weight grid. Retain every explored definition.
5. Broader account-acquisition/dependence analysis only if the root scope includes it: same-day or close-start
   accounts share outcomes. Old stagger-table (FUNDED_PLAN736–766) has same-day outcome correlation1.00,
   five-day0.39,ten-day0.19. It changes batch risk, not the intrinsic expected pass probability of each identical book.

Before any new outcomes, root must fix which objective matters: fewer failures, more funded conversions per fee,
time to pass, and worst-case drawdown are not equivalent. An honest Pareto frontier may be the result. Four losses
do not justify tuning directly to October20–November4 or promising loss-free evaluations. No change to any live
account, allocation, purchase, deployment, VPS or broker is authorized by this note.
