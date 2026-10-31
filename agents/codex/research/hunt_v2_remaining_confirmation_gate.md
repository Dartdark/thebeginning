# Hunt v2: remaining named B-item confirmation gate

Decision: **DON'T TEST a repeat T_ONESIDE fade confirmation as a new v2 hypothesis.** Its independent rebuild,
stop-gap counterfactual and MultiCharts fade-list parity already exist. Remaining receipt/volume/clock and
current-book questions are real limits, but do not make that completed confirmation new. The related Codex
total-volume source variant has also already been preregistered, replayed and benched. Do not rename or
retune it to fill the hunt budget.

This source-only review adds **0 hypotheses, 0 gross screens and 0 counted economic evaluations**. Root owns
the counters and H02 closure update. The progress file read during this review showed3/60 evaluations and
2/10 hypotheses, with H02 still marked pending; root separately reported the completed H02 gross-data veto.
H01 and H02 remain closed. No raw price rows, CSV/trade-list bodies, workbook contents, saved return arrays
or new economic results were read or calculated here. Existing published report statistics below are source
context, not newly verified native-cost results.

## Authority and source scope

Read AGENTS.md, BUILDER_BRIEF.md, LESSONS.md, RESEARCH_CONTROLS.md, TASK_strategy_hunt_v2.md,
strategy_hunt_v2_progress.json and the existing confirmation-readiness map. Work remains on codex/work.
Current adopted-source pin inspected read-only:
`92b1d4cde768bcfce019cf9a95944158dd0ebba3`, Claude's source branch. No Claude-branch writes occurred.

Targeted sources at that pin:

- TIER_LIST.md, especially the explicit2026-10-25 MultiCharts update and the six named confirmation rows;
  MINED_INDEX.md is a discovery map, not adoption authority.
- `checks/candidates/t_oneside/{spec,verdict,REVIEW,checker_report}.md`, `meta.json`, `T_ONESIDE_v2.txt`;
  `analysis/t_oneside_test.py`, `analysis/t_oneside_bench.py` and the published
  `analysis/outputs/mc_parity_2026-10-25.txt`.
- Adopted `personal_strategies/PORTFOLIO.md` and `funded_strategies/FUNDED_PLAN.md` source definitions.
- Local prior source reports/plans: `agents/codex/results/{night_volume_switch,overnight_volume_switch_context,s03_v2}.md`,
  `agents/codex/evidence/night_volume_switch.md`, `agents/codex/plans/night_volume_switch.md`.

No strategy module was imported or run. No CSV header/body was needed, no web/source acquisition was attempted,
and no completed data or return audit was rerun. Only this report was written; no commits or counter changes.

## What is already completed for T_ONESIDE

| Question | Source evidence | Consequence for v2 |
|---|---|---|
| Independent raw-spec rebuild | `verdict.md` states the maker's874 full-switch tickets were reproduced exactly, with14 additional January2018 tickets from the specified December2017 warm-up. | A basic independent rebuild is already completed. Do not advertise another matching replay as a newly discovered piece. |
| Fade MC list | The explicit latest TIER update and published parity report describe358MC vs373Python fade-sized trades,348 same day/side/entry and matched exits within1tick. | The earlier row's “MC pending” phrase is superseded for the fade. This is not a list for the874-ticket full switch. |
| Stops active on entry | Spec says active from entry; Python `hold` checks from `j_in`; v2 PowerLanguage adds built-in `SetStopLoss`. | Entry-bar protection was already part of this source version. It must still be verified for any operational implementation; it is not an untested new alpha input. |
| Worse gap fills | The independent verdict reran worse-open stop handling and reports0such cases among60stopped trades. | The optimistic source assumption was already challenged on that history. No favorable new result can be inferred from repeating the same counterfactual. |
| Half-day/holiday clocks | The source exits T around08:44 and OS by10:59wall time; the checker documents21holiday/half-day trades, not an overnight-hold defect. | There is no source-backed reason to invent a later exit or a blanket “missing holiday fix” discovery. Complete actual paths still matter. |
| Existing promotion evidence | Published fade MC t≈3.5; older raw-spec T-only t≈3.58/DSR≈.76. Full-switch t≈4.28/DSR≈.926 belongs to T+OS, not T. | No current native-cost promotion is established. Do not lend full-switch t to fade-only book results, or round an approximately3.5 fade into a pass. |
| Existing book case | The original bench used an older funded roster and reports only a small selected fade addition effect. It does not certify the current personal19/50K/150K books. | A stale bench is not a current improvement, but rebenching it is revalidation of an already selected family, not a new forced-flow lead. |

The mechanism remains the author's **unmeasured inventory-unwind hypothesis**: unusually heavy overnight
volume could represent inventory that is unwound near the cash open. The inspected sources do not identify
the participant, mandate or inventory amount. Many heavy nights include07:30data releases; heavy volume is
not itself proof of involuntary selling or buying. The OS explanation is weaker: the independent review
finds the quiet-night switch does not add to OS and the long branch is concentrated in a few winners.
No new independent forced-flow input was established by this source review.

## Important unresolved issues, without turning them into a new parameter search

1. **Clock and receipt.** Spec/native replica: close-labelled08:30bar opens at08:29wall time. The code's prose
   calls its next-bar order the08:30cash-open fill. These descriptions must be reconciled against actual chart
   semantics and receipt/execution evidence before an operational claim. The prior checker already tested
   delayed entries and found material decay. Moving the clock now would be a changed, previously examined
   protocol, not an untouched confirmation or permission to choose the favorable minute.
2. **Volume meaning.** Original PowerLanguage uses intraday `Volume`; source notes distinguish up-tick Volume
   from total Ticks. The native exporter and Python research use a different field convention. Multiplying
   volume by a presumed constant does not prove identical heavy-night flags. New field/availability choices
   require their own source specification and selection history; no favorable definition may be chosen here.
3. **Full-switch confirmation.** The small fade-sized MC list does not establish the OS/full-switch trade
   stream. A properly identified full-switch MC export and its exact code/settings would be new evidence.
   This is **NEEDS DATA for that specific parity question**, not a reason to rerun the old fade and borrow
   its full-rule headline. No user/VPS/broker action or data acquisition is requested by this review.
4. **Current joint book paths.** Any future eligible revalidation must use current personal19/ST/PT adoption
   and funded allocations, actual tickets/native fees and valid joint chronology. Daily-only comparisons
   cannot establish funded pass/payout improvements or an offset arriving before a breach. Missing paths
   remain limits; changing a portfolio baseline must be separated from candidate alpha.

## The nearby total-volume/stop-repair variant is also prior research

`agents/codex/results/night_volume_switch.md` records preregistration **affb482**, result commit **8eadab6**.
It explicitly distinguishes a later uploaded total-Ticks source from original T_ONESIDE: changed night/morning
anchors, missing08:29behavior, current-night validity and explicit-stop timing. The two frozen modes were
literal delayed protection and immediate entry protection. It already used worse gap fills, native micro
fees, paired funded BASE/ADD/REPLACE/EMPTY rows, joint evaluation paths and random-time/random-side controls.
Its verdict is WATCH/no current-plan change, with unresolved original MC/receipt/entry-protection issues.

That report is not a passing current-v2 result. It used earlier book definitions/coverage and its own gate;
v2's t-OR-DSR criterion must not be retroactively substituted for its original t-AND-DSR decision to declare
success. More importantly for selection, another “use total volume, repair the stop or move the cash-open
anchor” hypothesis would revisit already researched protocol changes. Retain their history rather than
counting a renamed variant as a new mechanism.

## Other user-named B items

| Item | Current source-backed decision |
|---|---|
| Swing Target v3 | Already MC-confirmed and adopted. The old v2 holiday defect does not justify a new confirmation of fixed v3. Second personal MNQ is explicitly parked because return/DD worsens. |
| PAPERTREND v2 | Already MC-confirmed and adopted in personal19. Earlier “not in plans/MC needed” wording is superseded. |
| BB_MRM | MC weakened the result; demotedC and removed by user. No unfinished positive confirmation case. |
| S03v2 | Independent/MC provenance remains incomplete, but its existing result already rejects current-plan promotion and parks personal expansion. Missing parity does not erase the prior placement failure. |
| FVBshorts | H02 is the authorized independently executable follow-up; root reports its frozen raw gross-data veto. Do not rerun, use the old masked-short stream or relax clock/coverage policy to rescue it. |

## Next action

No new TEST is established among the six named B-item confirmations. Preserve T_ONESIDE as selected prior
research with specific receipt/volume/full-switch parity limits. Continue the v2 priority search only when
a distinct credible mechanism or genuinely new admissible input supports a mechanism sheet and preregistration.
This review does not claim the public research universe is exhausted, does not create a new user-action
blocker, and does not authorize pausing the hunt before its actual budget/termination condition.
