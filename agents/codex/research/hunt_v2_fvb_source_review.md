# FVB source review before H02 data

Scope: source/document inspection only, 2026-10-26. No raw price files, CSV/workbook trade bodies, return calculations,
source imports, financial scripts, cache construction or git mutations. Two reviewers independently inspected the
source state/clock semantics. User templates remain reference-only and were not run or used to modify this rule.
V2 source-review running count remains **3/60 evaluations, 1/10 hypotheses, 1 gross screen**, H01 closed.
Archived t6 65 evaluations remain in selection history; this review does not restart that program.

## Pins and provenance

Remote source `origin/claude/nq-trading-strategy-params-5h9d20` resolves to
`92b1d4cde768bcfce019cf9a95944158dd0ebba3`. Work remains on codex/work. Source files were read through `git show`,
not copied into shared analysis paths or imported. Local HEAD at hash review was `a8839895736d6762b935c638230f42d518bf73e5`;
root owns the separate economic plan/commit and counters. The later research-controls supplement was read at
`7d1e6a295aca16c8204c45e9c5a7146b3e49c77e`; explicit information clocks/run identity/cost bridge are required.

| Source path at pin | SHA-256 |
|---|---|
| checks/candidates/fvb/spec.md | 66253ccf4e79b6d0c7230a724a1af5444b5b2dee8282c1f198ba95e87338a129 |
| analysis/fvb_test.py | 91710e836c9bed30f0b018acf542dd12b260224dfedf5b21b6851aeb53d8f130 |
| analysis/fvb_bench.py | 64229ad127b4b9bd2db16f9cc786751f7bcb3acaf8b9462a409d6748187a9577 |
| TIER_LIST.md | e3ea3a411f8682beb09af52802b1b0581e398865f0efadd035e0f710d4aa70a1 |
| MINED_INDEX.md | 17ab11a813c8774bcc07ad11b2458885f02d4e40975355b7a9b2ccd34c523cd8 |

Latest ranking records a B item with full-rule checker concerns, 27 reported source evaluations, older author search,
known full-history side splits and a post-hoc shorts-only personal result. These are historical source statements,
not recalculated outcomes and not current native-MNQ evidence. No FVB MC list for the proposed independent short
state was established. Existing readiness note remains correct that this is not an immediate MC-confirmed promotion.

## Why the old short result is not executable SHORT_EXEC parity

`analysis/fvb_bench.py:27–30` calls `FT.run(FT.Frame("NQ"), count=False)` for BOTH and only then filters `side<0`.
`analysis/fvb_test.py:90–116` maintains shared daily trade count, first-trigger side, open-position duration,
post-stop scan cursor and removed price levels. A long can occupy the morning, consume one or both slots,
or remove a same-price active level before any short can occur. Dropping the resulting long ledger rows does
not undo those state changes. It is a diagnostic short mask, not a separately executed short-only rule.

The proposed primary must ignore/remove long levels **before** scanning and state updates, with max two short
tickets, one retry only following a stop, later-bar rescan and removal by used price. Preserve remaining short
level order: PM low alone for the gap case; prior RTH low then distinct PM low otherwise. An unselectable BOTH
causal reference can expose implementation/selection differences. A post-hoc BOTH short mask may be shown as
a nonexecutable diagnostic, but cannot substitute for primary returns or add an undeclared selectable model.

## Causal/data/execution differences that the plan must bind

| Source semantics | Reference | Required frozen treatment / disclosure |
|---|---|---|
| Source `Frame` iterates `g.trading`, retains today only after seeing ≥10 whole-RTH closes | fvb_test.py:44–50; grid24 derives trading rows from observed day export | Use a preknown normal-session calendar, not current final membership or afternoon coverage. Current PM/past completed RTH may gate causally; later held data quality is audited without cherry-picking complete winners |
| Spec asks ≥10 premarket bars; code accepts any observed PM high | spec rules; fvb_test.py:47–50 | Explicitly freeze exact past/PM completeness and failure handling; do not claim original-code parity when stricter causal coverage changes the population |
| ATR14 is prior completed-row arithmetic mean, shifted; prior range/body use preceding retained row | fvb_test.py:51–54 | Exactly 14 previous normal cash-calendar slots, each 405 complete RTH minutes; no stretching over missing slots. Previous normal slot supplies levels, possibly older across excluded holidays/half-days. Full 330 PM minutes today. No invented 2017 warmup/current data |
| Data-derived roll detection and interval through today's RTH close | fvb_test.py:40,55–58 | Root's preknown conservative guard is quarterly second Thursday+calendar offsets 0,1,4,5, excluding today/priorreference; **not official vendor-switch provenance**. ATR may use guarddate intraday ranges, never crossdate TR. Native splice uncertainty remains; no return-informed guard tuning |
| Signal closes 511..630; author's ET open-stamped mapping is `m-59` | spec; fvb_test.py:32–34,77,95 | Native CT labels; exact j+1 entry. Prefix observed through first signal or all 120 if none; first missing=>unresolved/veto. Later gap after first signal uses held-path audit. Audit DST, no clock tuning |
| `js` contains all observed current RTH closes, so next item may jump a missing minute | fvb_test.py:89,93,103 | Exact next-minute O[j+1], with causal signal/entry observations. No next-observed entry substitution |
| `np.round(x/tick)*tick` uses ties-to-even | fvb_test.py:79,85,103 | Name exact tie policy before returns; preserve tick-rounded entry and .18ATR stop distance |
| Stops tested before time exit and active on entry bar | fvb_test.py:104–109 | Keep entry-bar protection, worse open for every stop-gap held bar, adverse slippage. No target, so target-through is N/A |
| `gap_fill` only worsens openings after the entry bar, default fills at stop | fvb_test.py:107 | Apply conservative gap rule consistently; do not inherit old claim of no gap-through or old fast-bar stress as new evidence |
| Time exit first observed k≥911, else defaults to last RTH close | fvb_test.py:103,109 | Exact column911 close, no earlier last-bar or later-observed fallback; missing held path vetoes pass. Skip known half-day/holiday sessions before entry; no candidate exit after15:59CT |
| Two trades shared across sides; second only after stop, later bar; remove by PRICE | fvb_test.py:90–116 | SHORT_EXEC runs its own short-only state, not masked BOTH. Freeze price-duplicate handling and all stop/reentry tickets |
| Source costs are NQ $7.25+two $5ticks | spec; fvb_test.py:76,110 | Candidate MNQ native $1.24+two $0.50ticks=$2.24RT; frozen fourticks/fill stress=$5.24RT reprices same two executable configs, retained/unselectable. NQ price as MNQ fill proxy and nextopen zero-delay receipt idealization remain limits |
| Old personal17 and stale funded/evaluation rosters; NQ/10 cost conversion | fvb_bench.py:38–50,81–93 | Current personal19 with ST/PT in, BB_MRM out; current adopted funded/evaluation sources. Whole-contract BASE/ADD/REPLACE/EMPTY, paired paths, identical dates/costs/coverage |

No source executable was imported. `fvb_test.py` modifies argv/imports `s_rank_gap_round2_test` at module load;
its main block runs many full-history parameter/side/market variants and writes shared candidate outputs.
Reusing it unmodified would violate both the committed bounded design and allowed-path constraints.

## Next gate, not a new result

The eight-question sheet at `agents/codex/evidence/hunt_v2_fvb_short_execution.md` permits a preregistration for a
bounded result-informed confirmation test. Root must commit the exact causal policies and at-most-five designs
before raw prices/new returns. Proposed gross gate: first short signal/day, exact next open→15:11 close,
RAW_NO_STOP, no reentry, ≥100 events, mean≥$4.48/MNQ, years/side/count/dispersion, all paths retained and complete.
A failed gross screen costs zero counted economic evaluations but remains in hypothesis/screen selection history.

Only after gross passes run the frozen stopped SHORT_EXEC and unselectable BOTH causal reference; any actually
examined additional return/stress variant must remain in selection history. The fourticks/fill stress changes costs
only, not entry/exit/state. Design gate requires ≥100 trades, net>0, trade t≥2, dailyNW5>0, ≥4/5positiveyears and no
unresolved scan/held paths. Design pass triggers immediate current personal19 BASE/ADD/REPLACE-DualThrust1MNQ/EMPTY
benches at one MNQ before robustness; no improvement versus BASE and EMPTY stops this hypothesis. Later selection
commit precedes selected rule+matched control's single previously seen2023+ historical validation. Native costs,
both-period positivity, current promotion bar/DSR, both identical-exit placebos p≤.05, dependence/selection checks,
complete calendar/fill/source audits and a fresh independent raw-spec check remain necessary. Missing MC list and
joint account paths are limitations; no favorable old mask/book headline can satisfy them. No PL draft yet.
