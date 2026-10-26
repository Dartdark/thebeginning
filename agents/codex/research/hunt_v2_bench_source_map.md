# Strategy hunt v2: current bench source map

Source/interface review only, 2026-10-26. No raw price rows, trade ledgers, P&L CSV contents, pickles,
financial outputs or new returns were opened/computed. File existence/size checks and source-code,
documentation and provenance-manifest reads only. New hypotheses/evaluations from this review: 0/0.

Working branch remains codex/work. The task is stored on Claude's branch but explicitly requires Codex
to work here. Reviewed local head63f557da51f8348b1779f0dd44259aff8c2d01df and remote source pin
92b1d4cde768bcfce019cf9a95944158dd0ebba3. Do not merge the whole Claude branch merely to run a bench.

## Recommended first route: current personal19, with explicit limits

Use the already retained current19 baseline at the native-fee research convention, rather than the
old funded_bootstrap.PLAN constant or an old17-leg personal snapshot. The source definition and roster
at92b1d4c are byte-identical to afde088 for analysis/personal_portfolio.py, analysis/personal_variants.py,
personal_strategies/PORTFOLIO.md and funded_strategies/FUNDED_PLAN.md (git diff returned no changes).

Current personal book: every adopted piece at1micro; Swing Target v3 and PAPERTREND v2 are IN, BB_MRM
is OUT. The planned future aggressive allocation is not the adopted current comparison. The source
variant uses2micros on TwinContinuation, OvernightTick, Kusho, OvernightBiasML and DualThrust; do not
silently use it as current. Personal still includes both Monday Long and Dual Thrust.

Ready local paths, checked for existence only:

| Item | Local path | Status and use |
|---|---|---|
| Current19 fixed-fee daily baseline | analysis/outputs/codex_rebound/personal19/UNIFORM/fee_1.24/baseline_daily19.csv | Present,267640bytes; existing committed result, not opened here |
| Independent saved-case baseline copy | analysis/outputs/codex_rebound/personal19/SUNDAY2/fee_1.24/baseline_daily19.csv | Present,267640bytes; equality/hash must be verified after an eligible mechanism sheet, not assumed from equal size |
| Source bindings | agents/codex/inputs/rebound/plan_update_afde088/manifest.json and frozen_binding.json | Present; source reference afde088b8b64cf939ff1b325a27eea041cf62c70 |
| Current source context | agents/codex/inputs/rebound/plan_update_afde088/analysis/personal_portfolio.py and personal_variants.py | Present; preserve snapshot and original booking definitions |
| Added MC ledgers | agents/codex/inputs/rebound/plan_update_afde088/checks/candidates/swing_target/mc_trades_v3.csv and checks/candidates/papertrend/mc_trades_claude.csv | Present nested copies; contents were not read |
| Original core export | agents/tasks/plan_daily_pnl.csv | Present; no trade-count/native-fee or chronology certification follows from existence |

The local root-level analysis/personal_portfolio.py, analysis/overnight_tick_bench.py and root-level
checks/candidates/swing_target/mc_trades_v3.csv / papertrend/mc_trades_claude.csv are absent. Import the
minimum SOURCE snapshot into an allowed agents/codex/ subtree if needed; do not overwrite shared files.
Existing nested copies and baseline artifacts can avoid a new shared-code import entirely.

Existing adapters to inspect/reuse after authorization:

- analysis/codex_rebound_personal_update.py fixes the19-leg source composition and native fee repricing;
  its added_daily() converts MC net/NQ ledgers with commission correction only, because the retained
  ST/PAPERTREND ledgers already include17.25/NQ total cost. Do not charge the slippage twice.
- analysis/codex_rebound_accounts.py: personal_benchmark() produces historical/by-year cohorts and
  paired1-year daily paths; personal_configurations() supplies BASE/ADD/EMPTY/REPLACE. Its frozen
  replacement leg is OvernightTick or OvernightBiasML for the OLD overnight candidate. A new hunt
  candidate must preregister its actual overlapping slot instead of inheriting that unrelated choice.
- analysis/codex_anson_personal.py supplies reusable histories()/simulate_daily()/interval helpers.
  The old rebound bench uses252-day horizons and10-day blocks. The current repo personal publication
  uses analysis/montecarlo.py daily_mc(horizon=252,n=5000,block=20,seed=1). Freeze one declared primary
  convention before returns and keep paired histories across all compared plans; do not choose whichever
  block convention gives a favorable result. The user/task's one-year MC is a252-day horizon, not proof
  that a252-day block is intended.

At the cheap design pass, compare design2018-22 BASE, ADD, EMPTY and REPLACE on the same dates and
resampling indices before expensive robustness. Do not inspect future candidate2023+ through a full-book
bench before design selection is committed. Later historical validation/full-book rows use the frozen
selection once. Keep actual whole-contract candidate weights, native commission/slippage, cash-day zeros,
the same candidate coverage and a fixed source baseline. Calculate correlation with VB/DT/RS and the
remaining book on aligned daily series; annual correlation cannot establish an offset before breach.

### Personal baseline limits that do not disappear on reuse

The retained baseline preserves published daily booking, not intraday margin/liquidation paths. Core
commission correction is per nonzero P&L day and undercounts some reentries; MOC/S30 retain inherited
fee approximations. Twin is the marked v1 checker ledger rather than an exact v2.1 ledger; Kusho is
booked at exit. The adopted OvernightTick input ends2026-07-07 in the retained source; later zero P&L
is missing baseline evidence, not verified no-trade activity. A calendar/coverage policy must be frozen
before comparison, not chosen after returns. Native candidate fees can be exact while the inherited
book remains a conditional publication-method comparison; report that distinction and audit any material
improvement against fee/mark/coverage uncertainties. Daily drawdown or a daily MC is not Apex clearance.

## Current funded/evaluation definitions

Authoritative source context: funded_strategies/FUNDED_PLAN.md at92b1d4c, especially sections headed
Overnight Tick/VIX, Swing Target v3 and current funded roster. Do not take its older historical tables as
the current plan. Relevant overlays on the shared funded_bootstrap.PLAN base are:

| Plan | Adopted changes that the old constant omits |
|---|---|
|50K funded| VB normal/flagged1/1; SwingTarget1MNQ; MondayLong removed in favor of OvernightTick1; RS longs1; MOC2MES; existing core retained |
|150K funded| Source scaling/cushion context retained, RS both1; SwingTarget2 replaces DualThrust2; OvernightTick2; MondayLong stays; do not add DT back |
|50K evaluation| Existing VB8, ONB_ADX30 risk1100, BridgeMonday2, EOS risk500; ST/DT/RS/OT not adopted there |
|150K evaluation| Existing evaluation stack at its own whole-contract/risk sizing; do not multiply an already floored50K risk quantity by2.5 |

Shared engines/interfaces:

- funded_bootstrap.Boot(lab).run/compare uses paired circular whole-day blocks, normally20-day blocks,
  H500 for the two-year funded horizon, and preserves all strategies' same-day paths together. The
  file's PLAN constant still starts VB_N3 and old core positions; it is a constructor base, not current
  adopted authority. `Boot.compare` defaults the first plan as reference, so name BASE explicitly and
  also report comparisons to EMPTY.
- funded_lab.Lab needs W[leg] adverse paths shaped(days,minutes), C[leg] closing net, and stop distances
  for risk sizing; funded_sim/funded_sim150 perform account checks. Actual q is floored after cushion
  scaling; document the current integer full-size ladder and risk sizing so fractional inherited bases
  cannot be mistaken for executable fixed contracts.
- Source92b1d4c funded_lab.py adds N/J0 trade counts/first-entry clocks and real_fees(); the local shared
  file lacks those24lines. real_fees still estimates one round trip per active day for manually assembled
  CLS/MOC and VB split legs, so it is not an exact trade-count repair for every leg.
- combine_levers_test.challenge(W,R,days,scale_fn,...) uses chronological adverse/closed paths with the
 50K finish/trailing/daily-pause rules. It requires valid joint intraday paths, not a daily return proxy.
- analysis/montecarlo.py at92b1d4c adds ret_dd=median annual profit/median max drawdown. Local source lacks
  that result key, although dd_p50 exists; an allowed Codex wrapper can report the same ratio explicitly
  without modifying shared code. Keep its EOD-only trailing estimate separate from account-engine checks.

### Known chronology problems: do not claim funded/pass improvements from them

Existing codex_swing_accounts.py and codex_rebound_accounts.py document these source limits: OT/CLS
whole-day constant adverse proxies can invent simultaneous exposure; BridgeMonday prepared paths omit
Sunday19:00-to-midnight adverse exposure; inherited MOC paths are close-based; OT history has a cutoff.
The afde088 manifest explicitly labels funded/evaluation status LIMITED_BASELINE_CHRONOLOGY and asserts
no joint account simulation/pass-payout claim. A new candidate's valid path does not repair the baseline.
Use personal daily-book comparisons first where permitted, or rebuild the missing joint paths before
any claimed50K/150K improvement. Do not call an approximation an executable account result.

## Current workspace cache and multi-instrument readiness

Metadata checks found these usual caches ABSENT: scratch_data/g24.pkl, ge.pkl, lab.pkl, rs_trades.csv,
single_print_sessions.pkl, s_rank_gap2.pkl; agents/codex/runtime/anson_plan.pkl and
anson_personal_baseline.pkl are also absent. Root-level current ST/PAPERTREND XLSX reports are absent.
This is a cache/input-path readiness result, not evidence that raw data or research execution is blocked.
Build/retrieve only what the eventual mechanism and committed plan require, into allowed Codex paths.

grid.execute, portfolio.paths and Lab.add assume NQ point value20, NQ costs and then divide by10 for
MNQ-equivalent paths. They are not generic native ZN/6E/YM/GC/CL/MES account adapters. grid._walk is a
reusable price-path exit kernel, but new instruments need native tick/point value/fee/target-through
and session handling in an allowed Codex extension. MES/MCL paths in old constructors are manually
inserted; copying the NQ assumption would be wrong. Native micro costs and executable prices must be
audited separately rather than inferred by return rescaling.

No baseline financial table, candidate trial, hypothesis, promotion verdict or new blocker is generated
by this source map. It identifies an available conditional personal19 route and the repairs required
before stronger account claims; the mechanism sheet and preregistration still precede new data/tests.
