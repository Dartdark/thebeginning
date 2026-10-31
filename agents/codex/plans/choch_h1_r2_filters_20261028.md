# Hourly R2 CHoCH: five frozen filter configurations

User approved this follow-up with “run it”. This is a bounded follow-up to the failed 2018–22 hourly two-candle-confirmed CHoCH 1:2 design, not a restart of Hunt v2 or t6. Freeze this document in Git before new filter returns. No additional window/threshold/side search.

## Evidence sheet and mechanism

1. **Participant/cause:** this is a price-structure hypothesis, with no identified forced participant or independently measured flow. A trend reversal may continue after breaking a confirmed opposing swing; the previous test does not establish an edge. The filters test execution geometry and broader price structure, not a new claim of scheduled flow.
2. **Why these features:** 293/408 resolved baseline trades exited by time, only 32 reached 2R. A distant target may be impractical within the remaining session. A completed four-hour structure in the new direction might distinguish reversals with wider support from hourly countertrend breaks. These are prior-result-informed hypotheses; preserve that selection history.
3. **Who pays/how big:** unknown. Historical range is a scale yardstick, not an estimated probability of reaching the target. A four-hour alignment is not independent information or proof of an economic mechanism.
4. **Liquidity/common losses:** directional NQ exposure; overlaps SwingTarget/PAPERTREND and can share trend/chop losses with VB/DT/RS. Removal of trades can lower drawdown mechanically. Random subsets must distinguish that effect.
5. **Executable risk:** confirmed prior swing stop, active from entry, no cap/sizing search, one MNQ. Wide stops can exceed account tolerances. No presumed hedge before an account breach.
6. **Evidence decision:** TEST as the exact small falsification requested by the user. A failure ends this experiment; it does not authorize another filter search.
7. **Plan fit if it survives:** personal19 ADD and SwingTarget EMPTY/REPLACE at one micro first. Review current funded/evaluation definitions separately; no daily proxy claims about account pass/payouts. Current 50K funded uses T_ONESIDE fade replacing RS longs; personal/150K retain RS.

## Unchanged foundation and frozen execution correction

Hourly bars, strict R=2 pivots, persistent HH/HL versus LH/LL/CHoCH state, normal signal closes 09:00–14:00 CT; early close 09:00/10:00 only. Same missing-bar resets and reconciled source hashes as `codex_choch_rr2.py`. Full 2017 warm-up / 2018–22 design; no 2023+ feature/price/return reads until selection.

Primary market entry at OPEN(signal+2), one-minute delay after the known hourly close. Stop is the confirmed opposite swing. Target = entry + side*2*positive(entry−stop). Normal flatten OPEN of minute labelled15:58 CT; early flatten OPEN11:30 CT. Shared grid `_walk`, worse stop gaps, one-point target-through; one position at a time. One MNQ $2/point, $1.24 commission + $1.00 slippage round trip, total $2.24. Costs shown separately; extra $2.24/trade stress is diagnostic only.

**Correction frozen before new outcomes:** a submitted market entry which fills at/beyond its stop is filled and immediately closed at that open, gross zero, net −$2.24; it must not silently disappear. Preserve/reproduce the old full baseline first and show corrected full baseline separately. No quote-cancellation rule is assumed. Primary shared intraminute nearest-extreme ordering is retained; count bars hitting both stop and target-through and retain a prespecified stop-first stress for every configuration. An unknown entry blocks through flatten; unresolved path is not zero P&L and is never filtered using future completeness.

## Information clocks and features

Both features are fixed at completed hourly decision close; actual future entry open never sets filter acceptance. Signal decision j; completed 4h data have end<=j; first primary executable fill j+2.

**Feasibility:** decision target distance `2*side*(signal_close−stop)`, required positive. Denominator = median historical high-minus-low over [j_clock+1, flatten_clock−1], additionally including the flatten OPEN as one price but not its later H/L/C. Use the **20 immediately preceding normal cash-calendar sessions**, excluding today, evaluated at this same clock and today's normal/early flatten. All 20 windows must contain every expected open minute and the liquidation open. Missing history => unavailable, never silently skip to older complete days. No current-session future range/coverage is consulted. 2017 source lacks RTH: resulting initial warm-up loss is recorded, not alpha. Thresholds are <=1.0 and <=1.5 times this median. Zero median => unavailable. Prior-day windows are closed/mature before decision.

**4h alignment:** full 17:00 CT anchored 4h bars closing21:00/01:00/05:00/09:00/13:00, unused13–16 stub, strict R=2 pivots confirmed only after two later completed bars. Use the complete persistent state of the existing core signal algorithm: confirmed HH/HL sets +1, LH/LL sets −1; an eligible CHoCH flips it; mixed pivots retain previous state; invalid bar resets to0. A state is unavailable until two confirmed highs AND lows since reset; neutral0 with adequate context is known but cannot align. As-of join latest completed bar end<=decision, including a simultaneous09:00/13:00 close. No future state/backfill.

## Exactly five primary configurations / coverage control

1. BASE: unchanged entry/swing/2R rules on common feature-known eligible signals.
2. F1: target distance <=1.0*median historical remaining range.
3. F1_5: <=1.5*median historical remaining range.
4. A4: hourly side equals known 4h state.
5. F1_A4: strict feasibility AND alignment.

Both features must be available for the common primary universe, including BASE. State0 is known. This makes feature-warm-up coverage identical. Also retain full original and corrected full baseline references, and the unknown-feature exclusions with their fixed-baseline P&L; those are coverage controls, not extra selected alpha configurations. There are four new active filter definitions, five inspected primary definitions including reused BASE, plus full-baseline/execution stresses. Preserve six prior structural variants/twelve prior economic definitions, all data reruns, failures and controls; do not reset multiplicity. This phase is outside closed Hunt/t6 counters.

Apply each filter to raw eligible signals then rerun one-position execution. Removing a baseline trade can free a later signal; an executable filtered ledger need not be a subset. Separately apply masks to common BASE trade IDs for fixed-trade kept/removed attribution. Publish IDs, feature availability, entry/exit clocks and exclusions. No favorable subset may stand in for executable returns.

## Design checks, random subsets and gates

Before market outcomes: synthetic prefix/future-mutation invariance for both features, pivot-state parity with the core, reset/as-of confirmation, decision-close versus future fill invariance, exact median/history clocks, entry gap-through, collision stress and exact time-open exit. Bind prior data hashes, code/prereg commits, versions and fixed seeds. Reproduce old baseline to floating tolerance. Use shared metrics/daily marks/resampling; retain both sides, every year, five metrics, net trade t and daily NW5 t, risk/exits/unresolved and gross-to-net bridge.

For each of four filters, **1,000 matched random subsets** of resolved common BASE trades, matched exactly on year × side × signal hour with identical stratum kept counts. Seed20261028, RNG sequence in listed filter order. Keep full membership IDs and daily paths. Same original exits/costs. Use plus-one `(1+#random>=observed)/1001` profit p; DD p uses randomDD<=observedDD; joint uses both conditions. Report effective random variation and ties. Removed total/average/t required; unknown BASE paths excluded from numeric diagnostics but retained and disclosed. These are selection diagnostics, not executable/account simulations or final random-time/side placebos.

Cheap gross gate: mean resolved gross >$4.48. Candidate needs >=30 resolved executable trades, netpositive, trade t>=2, >=3/5 positive design years; **no unresolved entry/path** for a complete design pass. In addition, fixed-trade kept total net must exceed same-window BASE, removed total must be negative, and profit AND DD subset p<=.05 (therefore report joint too). Executable filtered total must exceed common BASE total, with no larger maxDD. Extra-cost and stop-first stresses must remain netpositive; surviving stress is not a second tuned version. Report lower-DD results even if rejected, without calling them proven alpha.

If no configuration passes all gates, save failures and stop this approved experiment; no 2023+, benches, placebos or PL. If any pass, immediately run current personal paired BASE/ADD/EMPTY/REPLACE design benches and252-day block MC before robustness. Require improvement over both BASE and EMPTY under current definitions; missing funded/evaluation joint paths remain limits. Freeze one survivor by highest design NW5 (ties F1, F1_5, A4, F1_A4 order), commit selection, then only it and matched BASE on previously seen2023+ historical validation once. Promotion still requires full-history multiplicity bar or DSR, matched random-time/side placebos, dependence/selection checks and fresh independent raw-spec checker. No trading approval or PL before full gates.

Code `analysis/codex_choch_filters*.py`; outputs `analysis/outputs/codex_choch_filters_20261028/`; report `agents/codex/results/choch_h1_r2_filters_20261028.md`. Raw uploaded/source CSVs and caches stay local. Publish only authorized derived files to codex/work using fresh expected-head checks, preserving all other work.
