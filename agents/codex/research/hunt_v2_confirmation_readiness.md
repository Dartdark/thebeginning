# Strategy hunt v2: B-item confirmation readiness

Decision: no listed item currently satisfies all of **unfinished confirmation + full specification + available
MultiCharts list + unexhausted book-improvement case**. Do not treat stale “pending” text as permission to
repeat an already confirmed/adopted item. If priorities1–3 produce no eligible test, FVB shorts is the most
interesting genuinely unfinished follow-up, but it is a result-informed nomination and lacks an MC list.
It is not ready for an immediate confirmation test under the requested prerequisites.

Scope: source/definition and already-published report review only. No raw price files, CSV trade ledgers,
MC workbook contents, new gross/return calculations or benchmark execution. New economic evaluations:0;
new tested hypotheses:0. These are readiness findings, not newly measured strategy statistics. The old t6
65-evaluation history remains separate from the new60-evaluation/10-hypothesis budget.

## Reference state and authority

Reviewed remote source: `origin/claude/nq-trading-strategy-params-5h9d20`, commit
`92b1d4cde768bcfce019cf9a95944158dd0ebba3`; local research reference at start:
`63f557da51f8348b1779f0dd44259aff8c2d01df` on codex/work. The new task is stored on the Claude branch,
but explicitly directs Codex to work on codex/work and never write claude/*. No shared/live files changed.

Read AGENTS.md, BUILDER_BRIEF.md, LESSONS.md, task text and relevant TIER_LIST rows before this review.
Latest explicit adoption notes and current personal/funded plans override older pending phrases in a row.
MINED_INDEX remains a discovery map: its BB_MRM B label is stale relative to the latest C/removal decision.

## Candidate-by-candidate map

| Item | Latest observed source status | Actual missing work / readiness decision |
|---|---|---|
| Swing Target v3 | TIER_LIST row61 and funded/personal plans record MC confirmation:595trades, zero overnight holds, t4.55 per NQ under the reported cost model. Adopted as personal1MNQ, 50K VB reduction+ST1, 150K DT replacement+ST2. MC list and v3 source exist. | **Already confirmed and adopted.** Older v2 holiday defect is not an unaddressed v3 defect. A new native-fee/current-book revalidation could be operationally useful, but it would not discover a new piece or justify repeating the old nomination as a fresh hypothesis. Second-MNQ personal sizing is explicitly parked because it lowers return/DD. |
| PAPERTREND v2 | TIER_LIST introductory MC update and current personal plan record Claude-code parity and adoption as the19thpersonal piece. Source and MC list exist; original upload535-trade discrepancy was different code, not an unresolved parity requirement for Claude's v2. | **Already MC-confirmed and adopted.** Retain known exit-time/selection/DSR concerns rather than trying a nearby exit to rescue them. The stale row phrase “not in any plan / MC needed” is superseded by the explicit later note and portfolio adoption. |
| BB_MRM | Latest TIER_LIST row63 records MC t2.5 and 2023+t1.2, extra profitable Python trades, C rank and user removal from personal plan. Real-fee/through stress had also weakened the rebuild. | **Known failed promotion; forward log only.** It has spec and MC list, but no unfinished positive confirmation case. Do not use the older Python B result or its personal gain as current evidence. |
| FVB shorts | Whole-rule fresh checker PASS WITH CONCERNS; source spec/Python independent rebuild exist. Whole-rule benches do not help. Personal shorts-only improvement is explicitly post-hoc, parked on the capital-expansion bench. | **Genuinely unfinished follow-up, not immediate confirmation-ready.** No FVB MC report/list is present in the reviewed tree. Short-side nomination needs its own mechanism/selection record and committed bounded design before any new returns. It must then clear native-micro promotion, both periods, random-time/side and current-book/empty-slot gates. Historical side selection is not a fresh holdout. |
| S03 v2 | Existing Codex report `agents/codex/results/s03_v2.md` already says REJECT current-plan promotion: funded placement disappoints, personal gains need more capital; current personal plan parks it on capital-expansion bench. Source and prior rebuild exist. | **No MC list/report found in reviewed tree; no qualifying placement already established.** Independent source rebuild is unfinished from Claude's perspective, but missing parity input and prior bench rejection make it lower priority than a new viable flow or filter. Do not claim the headline t alone is a plan gain. |
| T_ONESIDE | Full-switch checker exists; source `T_ONESIDE_v2.txt` and `mc_trades_T_ONESIDE_v2.csv` exist. Published MC parity report records358MC vs373Python trades,348same day/side/entry, all matched exits within1tick, MC t3.5. TIER_LIST describes this as the fade confirmation despite an older “MC pending” phrase. | **Fade parity already performed; full-switch confirmation not established by that small list.** The whole874-trade t4.3 headline includes OS, while the reported358-trade MC result is the fade-sized stream. Do not apply the full-switch t to the fade-only funded gain. Remaining native-fee/current-book/clock work is a limited revalidation, with MC t3.5 already below the task's approximate3.6bar and DSR below0.95 in prior checks. No ready new promotion claim. |

The numbers above are reported historical findings read from documents, not recalculated returns. They
must not be relabeled as current native-micro checks. A new criterion does not erase prior selection or
make these histories untouched.

## Most useful unfinished follow-up, conditional on earlier priorities failing

FVB shorts has the clearest new book question among these six: does a fixed, previously observed short
component improve the current book after real fees and valid paths? It also correlates with daytime DT/PT,
so a favorable old17-piece personal result is not enough. First acquire an independent MultiCharts list
from the frozen rule through Claude's normal workflow; no user/VPS/broker action was taken here.

No immediate DATA/TEST authorization follows from this review. Mechanism sheet must precede data,
followed by a committed<=5-configuration preregistration and the gross>=2x-roundtrip-cost gate. Any new
short-only nomination counts as result-informed, with all earlier full/side searches retained. Do not
generate a PowerLanguage “passing candidate” merely to fill the missing parity input before eligibility.

If a source-only existing-item revalidation is desired instead, T_ONESIDE has the files to audit exact
clock/cost semantics, but its already-below-bar fade result should be a cheap stop condition, not grounds
to adjust the entry, night threshold or exit after seeing the old outcome.

## Bench prerequisites and traps to carry forward

- Use the **current19-piece personal book**, with ST/PT included and BB_MRM excluded. The old FVB,
  PAPERTREND and Swing Target bench scripts describe17-piece baselines; their reported additions are not
  automatically gains versus today's book.
- Current funded source decisions include50K VB1/1+ST1 with Overnight Tick replacing Monday, and150K ST2
  replacing DT2 with its other current legs. Existing `t_oneside_bench.py` uses an older50K roster; FVB/ST
  bench builders also retain pre-ST150K DT settings. Snapshot adoption authority and source dependencies
  before computing BASE/ADD/REPLACE/EMPTY; do not silently use the older convenient baseline.
- `analysis/personal_portfolio.py` documents per-NQ/10 costs plus an approximate extra micro fee, with a
  known per-trade versus per-trading-day underestimate for some VB reentries. New native-fee work must
  count actual tickets/fills consistently for base and candidate, not just scale NQ returns.
- Reuse `funded_bootstrap.Boot` with paired histories and both50K/150K account engines where applicable;
  use `combine_levers_test.challenge` for evaluations, and the personal1-year block MC. Existing daily
  reports or scaled standalone streams are not a substitute for valid synchronized account paths.
- An EMPTY comparison must genuinely remove the proposed replacement leg/slot. Most old scripts list
  base/add/swap cases without an explicit empty-slot control; do not infer it from a small swap gain.
- T_ONESIDE's source spec and code comments disagree in plain-language clock descriptions: close-labelled
  native08:30bar open is08:29wall time in the spec/replica; code comments call it08:30cash open. Resolve raw
  bar-label/order semantics, receipt allowance and entry-bar protection before any operational claim.
  The earlier checker says each minute of delay materially reduces the fade; do not optimize that delay.
- Missing joint data is a reported limit, not permission to invent pass/payout changes. Half-day/holiday
  exits must be checked against actual native session chronology before an Apex claim.

## Reviewed source/report paths

Remote: TIER_LIST.md; MINED_INDEX.md; personal_strategies/PORTFOLIO.md;
funded_strategies/FUNDED_PLAN.md; analysis/personal_portfolio.py; analysis/{fvb,swing_target,t_oneside}_bench.py;
analysis/outputs/mc_parity_2026-10-25.txt (published report only);
checks/candidates/{fvb,papertrend,t_oneside}/{spec,verdict}.md where present;
checks/candidates/t_oneside/T_ONESIDE_v2.txt. Tree names verified the MC/spec availability described above;
no CSV/workbook bodies were opened.

Local: agents/codex/results/s03_v2.md and source/report/evidence path inventory only. No source was run,
no package installed, no network acquisition, no data/ledger alteration, no trial or plan change occurred.
