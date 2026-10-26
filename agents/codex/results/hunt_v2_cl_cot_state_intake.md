# I02 CL speculative-short state: stopped at the frozen identity gate

Summary: the committed non-return intake verified all six owned ZIPs, then stopped because the
2022 target's market name changed. The declared code/name pair matches five 2022 rows; the other
47 use `WTI-PHYSICAL - NEW YORK MERCANTILE EXCHANGE` with the same code `067651`. No position
count was converted, so the proposed net-short state's frequency remains **unmeasured**. This
does not establish that the contracts differ, nor that the state is absent.

**Running budget: 3/60 counted economic evaluations, 3/10 registered hypotheses, 2 gross screens.**
This source intake adds zero to each. Prior t6's 65 evaluations remain archived. The proposed filter
was not registered as H04, and no strategy or book improvement is claimed.

Plan: `agents/codex/plans/hunt_v2_cl_cot_state_intake.md`, committed **b1b50c6** before rows.
Mechanism: `agents/codex/evidence/hunt_v2_owned_flow_nomination.md` (NEEDS DATA).
Script: `analysis/codex_hunt_v2_cl_cot_state_intake.py`, SHA256
`d20c86df31927e2d6dd7442008d026c7c3a546026f324bc5c1fba27a3d8e4bb3`.
Source/synthetic review: `agents/codex/reviews/hunt_v2_cl_cot_state_preexecution.md`.
Artifacts: `analysis/outputs/codex_hunt_v2_cl_cot_state_intake/`.

## Question and permitted scope

The possible later filter would skip an existing CL Sunday up-gap short when the last genuinely
published Legacy noncommercial position is net short. Covering pressure is an unmeasured contingent
mechanism, not observed compulsory orders or Sunday inventory. The parent rule, size and exits were
not changed or replayed. A source-only prerequisite was frozen: at least 20 distinct negative as-of
ISO weeks in 2018–22. Passing that prerequisite would still require original publication, receipt,
batch and vintage evidence; an as-of date is never a release timestamp.

The six exact `data/cot/deacot2017.zip` through `deacot2022.zip` files and their `annual.txt` members
were bound by ZIP SHA256/size, member CRC/size/SHA256, and the exact 129-column header. Metadata
for all six years had to pass before any selected count conversion. Only CL OI/noncommercial long/
short counts in 2018–22 could then be converted; 2017 was metadata only. No NQ chart, TFF,
publication mapping, other-market numeric fields, prices, trades or 2023+ data were admitted.

## Actual source result

| ZIP year | Target metadata rows | Exact declared name/code matches | Identity gate |
|---|---:|---:|---|
| 2017 | 52 | 52 | Pass |
| 2018 | 53 | 53 | Pass |
| 2019 | 52 | 52 | Pass |
| 2020 | 52 | 52 | Pass |
| 2021 | 52 | 52 | Pass |
| 2022 | 52 | 5 | Fail: 47 different market-name strings |

The accepted 2022 metadata spans January 4 through February 1. The mismatching raw name/code
strings and original record IDs are retained. A common code suggests a possible naming transition;
the frozen plan required the exact declared pair and explicitly forbade silently accepting an alias.
The intake therefore returned **NOT_TESTABLE_IDENTITY** at 18:23:22 UTC on 2026-10-26. All years'
position-count conversions were blocked, including those whose metadata passed. The selected-count
ledger contains its header only. The 20-week support condition was not measured or failed on frequency.

The verified marker binds the code, pre-row input manifest, identity audit and all retained artifacts.
Root verified the saved output hashes. The immutable original attempt remains saved; there was no
retry, alternate output directory, relabelled identity, shortened date range or threshold change.
Twelve author and six independent synthetic groups passed before the actual intake; those checks
established parser/control behavior, not data or economic performance.

## Gates not reached and limitations

No gross mean/t, cost hurdle, stopped design, long/short/year performance, five metrics, net trade t,
DSR, placebo, matched subsets, Monte Carlo, BASE/ADD/REPLACE/EMPTY bench or historical validation was
calculated. No half-day/execution path was tested and no PowerLanguage draft was produced. Native MCL
fees/fills and joint book paths remain unverified; no funded/evaluation claim follows from metadata.

The source question is closed under this intake. A separately evidenced naming-history study could
clarify identity, but it would not alter this result or supply the unresolved publication/vintage
clock. No such reinterpretation or follow-on numeric parse is authorized by this report. Continue
the bounded hunt with a distinct eligible question; this is not a user-action blocker or a reason
to pause the program.

**Verdict: source identity gate stopped I02 before position statistics or financial returns; no alpha verdict.**
