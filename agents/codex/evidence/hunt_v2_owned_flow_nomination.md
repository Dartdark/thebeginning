# Published CL speculative-short state for Sunday fade: NEEDS DATA

Summary: investigate one independent positioning filter on the adopted CL Sunday short.
A net-short speculative cohort could face covering pressure after an up-gap; actual Sunday inventory and
forced orders are not observed. The owned COT publication/as-of/vintage bridge is unresolved.
Only a separately committed non-return source intake is appropriate now; no gross return test is authorized.

Sources: CFTC Legacy/TFF annual ZIP filenames; analysis/{cot_flows,cot_test,cot_reversal_index_test,bridge_cot_test}.py;
CL Sunday source/MC confirmation; TIER_LIST/MINED_INDEX at7f0800f; tools/exporters/OFB_COT_Exporter.txt at that pin.
Raw positions/prices/return ledgers were not read. Source detail: agents/codex/research/hunt_v2_owned_flow_nomination.md.
Return trials:0 for this proposal; prior NQ/ES COT families and CL Sunday selection remain in history.
Program at sheet preparation:3/60 counted evaluations,2/10 hypotheses,2 gross screens, plus archived65 t6 evaluations.

## 1. Participant and cause

Noncommercial CL traders can carry directional short futures risk. A Sunday price rise can increase
short-side losses and trigger risk-reduction/covering orders. This is a plausible contingent cause, not
an obligation established by COT. Legacy categories do not reveal individual stops, margin calls, hedge
offsets or which Tuesday positions still exist on Sunday. There is no claim that every reported short
must cover or that noncommercial net positions measure actual unhedged inventory.

The existing Sunday fade is a short liquidity-taking trade. The prediction is that its losses are
more likely when the latest available noncommercial cohort is net short. This directional prediction
is frozen as a source question; a failed sign/frequency must not be rescued with a rank/window search.

## 2. Direction, size and timing before entry

Prospective input: Legacy noncommercial long minus short positions from the last genuinely published
CL report. Possible predicate: skip existing short when net<0; otherwise keep, including unknown state.
One whole MCL would be the initial personal-book unit; no resizing or standalone long is proposed.
Exact active stop/entry/time exit remain the adopted CL source, to be independently frozen later.

Information clock has separate as-of Tuesday, original publication, chart-available and usable-at clocks.
Only a verified available-at plus a frozen allowance strictly preceding Sunday decision may be used.
NQ chart timestamps have not been admitted as CL batch receipt. No blanket Friday release or as-of+6day
mapping is authorized. Missing or ambiguous source state is retained explicitly, never treated as a
newly published net-short report or a convenient deletion.

Rough scale can later be expressed as reported short contracts ×1000barrels, but that is gross reported
exposure, not executable covering demand. No position counts, hedge fractions, dollar size or comparison
to Sunday liquidity were measured or invented here.

## 3. Transmission

The proposed inventory concerns CL, so direct CL risk reduction could affect the same underlying as MCL.
Actual contract-month coverage, swaps/options/cash offsets and liquidity can redirect it. Continuous CL
prices do not prove MCL fills or identify all COT contract-month exposures. No NQ causal link is required.

## 4. Inputs and independent information

|Input|Owned/source evidence|Unresolved before TEST|
|---|---|---|
|Legacy CL noncommercial long/short/OI|Annual deacot ZIP filenames exist; exact fields/codes to bind in a new intake|Raw coverage, revisions, correct contract identity and original release mapping|
|NQ TFF/Legacy nets for report mapping|Existing source loader and COT_NQ header; exporter emits changes only|Unique as-of matches, omitted/ambiguous weeks, actual common-batch/publication proof|
|Native CL/MC base|Adopted CL Sunday source and confirmation exist|Exact frozen protocol, calendar/roll/held-path/native-fee reconciliation later|
|Current book|Current personal/funded source definitions required|Joint same-date histories and plan-size controls only after a design pass|

COT varies independently of the current Sunday gap. Its available-at/vintage evidence is unresolved,
so a superficial net-value/date match cannot set a VERIFIED flag. No new provider/network request or
unchanged completed source audit was made for this sheet.

## 5. Costs and overlap

MCL point value100USD, .01tick=1USD. An illustrative1.24RT commission plus one adverse tick at entry
and exit is3.24USD; a future raw gross hurdle would be6.48USD/MCL, after the native fee basis is frozen.
This arithmetic is not measured gross edge or a verified broker quote. No CL/NQ cost rescaling qualifies.
The filter changes an existing leg rather than filling an empty hour. Sunday positions can overlap Bridge
and other book legs; no hedge, unused interval or pre-breach offset is inferred from average correlation.

## 6. Power before outcomes

There are at most about260 Sunday opportunities in2018–22 before gaps, warmup and exclusions; actual
base and net-short subset counts are unknown. The net-short state may be absent or too rare. Measure
only known-state coverage/frequency after a committed non-return intake, then reject an underpowered
proposal rather than choose a percentile. A later plan must state assumed SD/effective sample size and
the approximate net-mean requirement2×SD/sqrt(n_eff), plus costs; no numerical power claim now.

## 7. Prior work and falsifiers

NQ/ES TFF/Legacy rank and plan-agreement tests already exist. The exact CL noncommercial-state/Sunday-fade
filter was not found by this scoped source search. That is not a claim that all global COT filters are new.
The CL Sunday base is adopted, so its earlier parameter/side/MC selection is not independent confirmation.
Reject before returns if publication/vintage cannot be established or the state is too rare. Later reject
if removed trades do not lose money, kept total does not beat base, matched random subsets do as well,
same-exit placebos fail or no current plan improves versus BASE and EMPTY. Do not tune after2023+.

## 8. Failure and diversification

|Question|Prediction/limitation|Required evidence later|
|---|---|---|
|What ends the effect?|Tuesday positions changed or are hedged; shorts are informed; gap absorption dominates|Published-state stability and fixed-rule controls|
|Liquidity role?|Candidate base orders consume Sunday liquidity; filtering may avoid adverse selection|Native spread/fill and prespecified stress|
|Loss clusters?|Oil news, supply shocks, crowded covering, gaps and missing prices|Both sides/year and complete chronological paths|
|Shared book losses?|Macro risk may connect CL and equity positions despite different assets|Aligned conditional losses, not an assumed hedge|
|Offset before breach?|Unknown; removing a leg may reduce return without improving account utility|Valid joint whole-contract account paths|

**NEEDS DATA.** A bounded new publication/as-of intake is the next possible step, not a trading test.
Only later TEST+committed economic preregistration could allow2018–22 raw gross, frozen stopped designs,
1000matched subsets and immediate current BASE/ADD/REPLACE/EMPTY. No2023+, MC/account simulation or
PowerLanguage is authorized now. No budget counts, t6 resumption, user-action blocker or v2 pause follows.
