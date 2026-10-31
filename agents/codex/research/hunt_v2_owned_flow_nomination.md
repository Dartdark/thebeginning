# Owned-input nomination: CL Sunday fade conditioned on published speculative shorts

Decision: **NEEDS DATA on the publication bridge; no TEST yet.** This is a distinct, source-grounded
filter question worth a bounded new non-return intake. It is not a reason to run CL returns now.
No raw price, position-data rows, trade ledgers, new strategy returns or financial code were opened/run.
Only the COT_NQ CSV header was read, alongside source/docs and Git object/source definitions.
New hypotheses/gross screens/economic evaluations: **0/0/0**. Root owns the counters.

Read AGENTS.md, BUILDER_BRIEF.md, LESSONS.md, RESEARCH_CONTROLS.md, TASK_strategy_hunt_v2.md and progress.
Current read-only Claude source was updated from615485f to **7f0800f** after root's fetch. Its tree delta
changes lessons/TODO and operations/exporter documentation; no Claude-branch write or live access occurred.
TIER_LIST/MINED_INDEX were consulted at the fetched source. The program checkpoint is3/60 counted evaluations,
2/10 registered hypotheses,2 gross screens; H01/H02 and I01 remain closed.

## One concrete mechanism

The adopted CL Sunday up-gap trade is short. A report showing noncommercial traders already net short
could indicate a different risk state: an opening up-gap may create contingent covering demand and impair
the fade. The possible filter is to skip the otherwise unchanged short only when the LAST demonstrably
published CFTC Legacy CL report has noncommercial net positions below zero; retain the base when unknown.
This is a hypothesis about crowding/squeeze risk, not identified stop orders, margin calls, actual Sunday
inventory or a measured compulsory dollar flow. The old CL price gap provides the existing trigger; COT
would be independent positioning information. No rank threshold, lookback or size search is proposed here.

It may have no usable events: CL speculators might seldom be net short. That must be measured during an
approved non-return source intake, before any candidate trade P&L. No observed category frequencies or
power claims were obtained here. Lack of events would stop this proposal, not justify choosing a percentile.

## Exact prior-family distinction

| Source | Already tested definition | Why this question differs, without erasing history |
|---|---|---|
| analysis/cot_test.py; analysis/cot_flows.py | NQ/ES TFF dealer, asset-manager, leveraged/nonreportable features; weekly returns and NQ-plan filters | This is Legacy noncommercial CL state conditional on the existing CL Sunday short, not another NQ dealer-rank threshold |
| analysis/cot_reversal_index_test.py | NQ/ES commercial26-week min/max plus10-week trend and plan agreement | No commercial reversal index or moving-average confirmation is proposed |
| analysis/bridge_cot_test.py | NQ TFF/Legacy ranks and weekly/day holds, actual chart release timestamps | Its timing input could help identify reports; it does not supply CL's historical release/version proof |
| analysis/cl_sunday_fade_confirm.py; adopted CL Sunday gap code | Existing gap/stop/exit and MC comparison | The base is already adopted; do not retune its gap, stop, time or continuous-roll handling |

Scoped searches of CL forced-flow sources and the latest COT ranked rows found no exact Legacy CL
noncommercial-state/Sunday-fade counterpart. This is a bounded novelty result, not a universal originality claim.

## The unresolved clock is material

Owned Legacy annual CFTC ZIPs2017–26 contain financial/commodity reports. COT_NQ.csv's header is
`date,time,tff_net,tff_rank13,tff_rank26,tff_ok,leg_net,leg_rank13,leg_rank26,leg_ok`.
There is **no report-as-of date in that export**. The source exporter at
`7f0800f:tools/exporters/OFB_COT_Exporter.txt` emits a row only when either NQ net value changes.
It labels the first chart bar after availability, not an authenticated original receipt. Unchanged nets
can omit a report, and shutdown/catch-up releases cannot be assigned by a blanket Friday convention.

Matching exported NQ TFF dealer/Legacy commercial net values to current CFTC NQ reports could establish
candidate as-of mappings. Exact unique matches would not by themselves prove the CL batch's original
publication time or original CL vintage. Repeated tuples, revisions, missing exports and report-specific
exceptions must remain unresolved. Do not assume report date+3/+6days, forward-fill an unavailable report,
or choose a match according to later CL performance. An NQ chart timestamp cannot be called verified CL
receipt without a supported common-batch/publication bridge.

## Smallest new intake, before economic registration

Use the eight-question NEEDS DATA sheet at `agents/codex/evidence/hunt_v2_owned_flow_nomination.md`.
If root pursues it, first commit a **separate bounded non-return plan** that fixes:

- Only2017–22 NQ TFF dealer, NQ Legacy commercial and CL Legacy noncommercial/OI source fields, with
  exact contract codes/schema and ZIP/input hashes bound before positions are read; no prices/trades.
- The unique-tuple matching policy, literal chart timestamp convention plus a frozen allowance, and
  retention of every unmatched/multiple/revised report. No rank-based tie-break without a source spec.
- Independent primary evidence for common CFTC Legacy publication batches, exact exceptions and vintage
  treatment. No automatic VERIFIED flag merely because dates/net values match.
- Only source coverage, release mapping, eligible known-state frequencies and planning power; never
  CL return, held-window outcome, trading metric, signal-P&L correlation or a future-year outcome.

Only a successful clock/input admission and a subsequent TEST sheet could justify a new <=5-configuration
economic preregistration. A future gross test would use the unchanged CL Sunday base raw window first,
native MCL costs, kept/base/removed totals and all retained failures; the stopped filter would need1000
matched subsets and immediate current-book BASE/ADD/REPLACE/EMPTY after design pass. A cap-dependent or
overlapping diagnostic is not an executable portfolio. Unknown input states must not delete bad base paths.
No current promotion, account utility or source admission is claimed. This note does not pause v2.
