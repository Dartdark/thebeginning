# FC 2B v2 bench and forward protocol: WATCH — keep outside the Apex plans; finish the forward specification

Summary: The reported benches show no material gain from FC 2B in the tested 50K configurations; keeping it out is reasonable.
The v2 MultiCharts rerun addresses the entry-minute stop and holiday carry defects in the historical export.
A fits the repository's historical numerical tier, with full-sample selection and forward validation still disclosed.
The bench uses scaled NQ commissions, not verified MNQ fees; the forward acceptance bands are not yet fully specified.
Before tracking starts, freeze the band calculation, exhaustive checkpoint decisions and prospective records; do not change the strategy.

Plan: not applicable — source/report review, no new strategy test or parameter choice.
Sources: Claude branch pinned at `28cdaa2`; scripts `analysis/fc_2b_bench.py`, `analysis/funded_lab.py`,
`analysis/portfolio.py`, `analysis/funded_bootstrap.py`; existing output `analysis/outputs/fc_2b_bench_output.txt`.
New strategy trials: **0**. No bench, strategy backtest, new bootstrap, account simulation or live action was run.
The separate existing-export audit was rerun only to correct its trading-clock description.

## Decision supported by the supplied benches

The funded output uses paired histories across plans. The one-MNQ addition has almost unchanged two-year payouts;
larger size raises blown rate. Replacing RS longs also shows no material improvement. The combine output does not
show a pass-rate improvement overall, and recent-period results deteriorate at each tested size.

Keep the wording **no demonstrated material improvement in the tested configurations**. The output does not give
paired confidence intervals for payout differences or an equivalence margin. It therefore does not establish
statistical equivalence or that every possible account, size or portfolio would behave the same way.
The combine starts overlap in time, so their outcomes are not independent Bernoulli trials.

The payout-cap explanation is plausible within this simulator; it does not rule out useful future additions.
`beats_base` in `analysis/funded_bootstrap.py:77` counts half of tied payouts, so it is a tie-adjusted score rather
than the probability of strictly earning more. One MNQ also denotes the full-size maximum: cushion sizing can
round that position to zero below the full-size cushion. No current-roster mismatch was found in the bench script.

## Cost convention needs an explicit qualification

`analysis/funded_lab.py:47-52` builds per-NQ paths and divides both equity paths and terminal results by ten.
`analysis/portfolio.py:96` deducts the NQ commission; `funded_lab.with_slippage` adds adverse ticks.
For FC 2B's entry and non-target exit this implies:

- $7.25 commission per NQ round trip becomes **$0.725 commission per MNQ**.
- Two adverse ticks become **$1 per MNQ**.
- Total modeled debit is **$1.725 per MNQ round trip**, rather than a verified actual micro fee schedule.

The combine section uses the same path-scaling convention. This contradicts the review's statement that the
funded bench already uses MNQ commissions. It does not create a reason to add FC 2B: the conservative keep-out
decision remains supported. Before using these results to justify adoption, implement actual contract-specific
fees consistently for the candidate and baseline. Keep per-NQ analytical reporting separate from that accounting.
No claim is made here about the user's actual broker fees.

## What v2 resolves, and what remains open

`checks/candidates/fc_2b/REVIEW.md` documents the v2 MultiCharts report, code commit `848923d` and report commit
`aa41668`: same 826 signal days, 31 changed trades, three entry-bar backstop exits, no exits after 15:00 and
29 holiday flattenings at 11:31. Those are historical confirmation of the intended execution changes, not live
protective-order validation. No live chart, order tracker or VPS was accessed for this review.

The independent replica matches all trade fields on 725 shared days but still has unmatched signal days.
Up-tick `Volume` versus exported total `Ticks` is a plausible, disclosed cause; it is not measured proof of the
remaining differences without paired observations. Keep the v2 MultiCharts ledger as the explicitly identified
reference. Do not describe the original 856-trade PDF ledger as reconciled.

My earlier v1 audit said all positions were intraday after checking that exit and entry dates matched. That
check was insufficient: 26 exits occur after 15:00, including the holiday halt-to-evening-reopen holds Claude
identified. `analysis/codex_fc2b_report_audit.py` and its report now state that distinction and retain the v1
results separately. The correction changes no trade prices or P&L.

## Historical A tier is distinct from prospective readiness

FC 2B meets the numerical A rubric in `TIER_LIST.md` and its t-stat clears the repository's multiple-testing bar.
The process permits t or DSR, so the failed DSR leg does not by itself invalidate that historical tier.
The formal checker nevertheless prints FAIL while the independent verdict records PASS WITH CONCERNS;
preserve both facts instead of calling it an unconditional checker pass.

The exits were selected on the full sample; 2023+ is historical replication, not a clean holdout for v2.
Profit concentration, weak recent incremental value of the z filter, and fixed-point risk as NQ prices change
remain concerns. **Historical A; outside the plans; forward evidence pending** is a fair description.
This review does not change the tier list or a trading plan.

## Finish the forward rule before the first observation

The frozen code identity is recorded correctly. `agents/codex/FORWARD_LOG.md:24-31` needs these operational
details before its stated 2026-10-26 start:

1. Freeze the exact v2 reference ledger and cost convention, the resampling unit/block length, number of runs
   and seed, and the numeric lower/upper predictive bands for 40 and 80 signals. Distinguish a predictive band
   for future outcomes from a confidence interval for the historical mean. Do not recompute the acceptance
   baseline from a changing backtest after forward observations arrive.
2. Make the decisions exhaustive at both checkpoints. The current text does not define outcomes above the
   upper band or what "in between" means, and its explicit negative-mean/t condition names only 40 signals.
   Specify what finishes the 80-signal checkpoint and whether any extension is permitted. An unusually good
   result should trigger a data/fill check, not an undefined state or automatic promotion.
3. State that two lower-decile checkpoint rules do not imply a calibrated 10% overall false-rejection rate.
   Either accept the joint stopping convention openly or calibrate it before tracking; do not tune it later.
4. Archive each export, chart inputs/session/volume settings, history start/warm-up and source version.
   Append new signals without rewriting old observations when historical data are revised. Track missing
   data separately from an observed no-signal day. A monthly rerun of a frozen rule can provide paper results,
   but cannot establish actual spreads, fills or protective-order timing.
5. Clarify that 80 paper signals can qualify the idea for another review or a new account-level test, subject
   to the user's decision; they do not demonstrate the lifecycle's live-incubation requirements or authorize
   personal-account deployment. A 150K plan test is a separate question with separate account rules.

These are protocol clarifications before tracking, not new entry/exit variants. No change was made to the
forward log, candidate code, tier list, plan or live files.

## Source inspection

All source claims above were checked using `git show origin/claude/nq-trading-strategy-params-5h9d20:<path>`
at `28cdaa2`. Relevant existing documents are `checks/candidates/fc_2b/REVIEW.md`, `verdict.md`, `checker_report.md`,
`agents/codex/FORWARD_LOG.md`, `DEVELOPMENT_PROCESS.md` and `TIER_LIST.md`.
`codex/work` did not yet contain those Claude commits when pulled; they were inspected without merging another
branch or changing its files. This review is committed only to `codex/work`.

Tell Claude: review `agents/codex/results/fc2b_bench_forward_review.md`; keep FC 2B outside both Apex plans,
qualify the scaled commission convention, and finish the forward bands/checkpoint rules before tracking starts.
