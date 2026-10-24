# Overnight-volume switch: source-version and current-plan test

Summary: Test the new upload's exact default rules against the current funded and evaluation plans.
Reuse prior T_ONESIDE work as version context, not as results for this changed source.
Freeze two protection timings, real fees and allocations before new source returns; no optimization.
This is already-seen historical replication, with independent review before any recommendation.

Evidence: `agents/codex/evidence/night_volume_switch.md` (TEST).
Source: unchanged `agents/codex/inputs/night_volume_switch/source.txt`.
Context pin: Claude `febc65f1573040abf9a697d1d3468e1bce48c4c0`.
Current-plan cache from the ORPullback task is reusable: its pinned27 dependencies and roster are
unchanged between a67035b and febc65f. Verify that fact and hash, do not rebuild market caches.
This plan must be committed before actual-price execution of the new source.

## Frozen rule and time clock

Replay observed finite close-stamped1-minute bars in CT over the existing Grid24 cache, including
2017-12 warmup. Night = Time>16:00 orTime<=08:29; reset only on an observed nonnight→night transition,
carry across calendar midnight. Sum Ticks and bar count; night open is the first observed night bar open.
At an exact08:29 close, ATRd is the mean prior20 stored completed RTH high-low ranges (not true range),
night median is the prior20 nights with count>=30, and classified requires both histories ready.
Heavy requires count>=30 and current volume>1.4*prior median. Append the current valid night after
classification. Heavy/flat/nonzero night move/ATRd>0 generates a next-observed-bar market fade.

RTH = Time>08:30 and<=15:00. At the first observed RTH bar, set morning open/high/low and reset
VWAP sums. Extend morning extremes through09:59; VWAP uses(H+L+C)/3*Ticks through the current bar.
At exactly09:59, classified/nonheavy/flat/RTH-on/ATRd>0 and(H-open)>2*(open-L), close>VWAP generates
a next-bar long. Preserve the missing current-night MinNightBars OS guard; no invented validity filter.
No fallback classification if08:29 is absent. Store the day's RTH range only at an observed exact15:00.

Fade stop distance=.40*ATRd; OS=.30*ATRd; anchor to actual next-bar open entry. Fade time exit is
next-bar market after a bar>=08:44 and<15:00. OS long exits next-bar market after close<VWAP or
bar>=10:59, while bar>09:59 and<15:00. A queued market exit fills at the next observed open before
stop checking on that bar. Ordinary labels: fade entry08:30bar=open08:29:00wallCT, exit08:45bar=
08:44:00wall; OS entry10:00bar=open09:59:00wall, latest exit11:00bar=open10:59:00wall.
Do not silently move execution one minute to match the comments' bell language.

Two immutable source execution variants, no other selectable versions:

1. `literal_delay` PRIMARY: explicit stop first active entry_j+1; entry minute unprotected.
2. `immediate_stop` diagnostic: same signals/brackets but protection active on the entry minute.

One position and at most one ordinary entry per classified day from the mutually exclusive regimes.
Preserve pendStop until fill and reset stop level when flat. No targets. Stops gap at worse opens;
an accepted stop behind the activation open executes at that adverse open, a model assumption rather
than proof that this source's broker order would be accepted. No price filling across missing held
minutes and no favorable backdated stop fills. Unknown held spans/late exits must be audited.

Eligibility for shared account comparisons: finite OHLC for08:29..11:00 on that date, with source
state/features built from ALL observed bars first. Exclude incomplete return days for every plan;
do not remove those observations from the past-volume/range histories. Preserve volume/calendar
gaps rather than requiring929 night minutes. Audit missing08:29, missing15:00, thin nights and any
late/overnight positions. If the source cannot exit because of missing data, mark that account day
unknown; do not pretend an unverified rescue order executed. The complete morning interval ensures
normal default exits before11:00 and early closes; no new holiday adapter is needed.

Costs: fee$1.04/micro round trip plus.25point entry and exit slippage for every trade; fee$1.24
sensitivity on both plan and candidate. Bracket and signal geometry is raw price, never cost-shifted.
Stop price need not be a valid tick multiple: use adverse tick rounding (sell stop down, buy stop up)
for executable benchmark and disclose its difference from raw source levels. Use same rounding in
both models. No assumption that stop syntax proves broker/exchange residency or disconnect safety.

## Design, diagnostics and controls

Run design2018-22 first, then2023+ once. Both modes remain fixed, literal_delay stays primary even
if immediate protection performs better. No settings selected on either period. Whole, long, short,
fade and OS results by year/design/2023+, standard metrics, DSR, t, bootstrap90% intervals with
5,00010-day-block samples and trade/daily Monte Carlo at1/2MNQ. Design negativity blocks promotion;
the user's requested frozen portfolio comparison can still document failure without tuning.

Prior family ledgers and reported claims are context only; compare source signal dates/leg/side with
the pinned committed stopped ledger, mapping by date (never trust its old grid-row indices). Record
differences due to morning anchors, histories and timing instead of forcing matches.

Falsification:1000 random-side schedules per mode using observed event day/time and fixed stops/time
exits; OS direction/VWAP crossing is mirrored as a null, not interpreted as a new source short rule.
1000 random-time schedules per mode: preserve actual day, leg and direction, choose fade entry from
08:30..08:40 with08:45open time exit; OS10:00..10:20 with11:00open time exit and the same VWAP
cross rule. All choices occur after the observed classifier/morning signal. Seeds848/849, no selection.
Also replay the source fade on all otherwise eligible nonzero-night-move days; quiet-night removed
trades must lose net. Compare heavy-night selection against1000 jointly drawn masks per execution
mode, retaining its number of days separately within design and2023+ (2000 full-calendar mask draws
in total), using total net and drawdown (seed850). These are nulls
and a falsification control, not selectable strategies; count all examined return series explicitly.
No additional heavy-OS or symmetry tuning is authorized; prior family already examined those cells.

## Portfolio and account test

Use current real-fee funded roster unchanged: VB2/1,ONBMLrisk400,MON1,EOSrisk700,LDF2,NPFrisk500,
Bridge1,CLS2MCL,MOC2MES,RS_L1. Frozen allocations: BASE; EMPTY_ONB; each of two execution modes
added1/2MNQ; each replacing full ONBML slot at2MNQ. No selection of slot by measured correlation.
Common intraday paths, integer cushion multiplier[.5,1],reference1500; reuse funded_sim/Boot and
already reviewed codex_ob_v2_accounts exact quantity-state acceleration with five fixed histories
and both horizons checked against original simulator per configuration. Use1000paired500-day
histories,20-day circular blocks,seeds1..4each250; also measure250-day payouts. Full2018+ and2023+
cohorts; identical eligible days across configurations. Save payout5/95ranges, all6, blown, median
days6including noncompletion, paired95% effect intervals (5000paired resamples), both fees.

Evaluation: VB8,ONB ADX30risk1100,Bridge2,EOSrisk500; same eight allocations, replacement removes
ONB30. Reuse latest challenge routine, actual integer sizes, full real-day chronological21-day
windows; exclude any window touching unknown candidate sessions rather than compress time. Save
full-calendar BASE reference separately, pass/fail/time/median days and paired outcome changes by
design/2023+, with20-day block intervals. Preserve/disclose inherited same-minute pass-first tie.
No live account settings or plans change.

Cheap screen is prior-family reported stopped mean~$15/MNQ against~$2.04 cost; the new source still
requires measurement. Do not substitute standalone P&L sums for joint adverse-minute account paths.
Show daily correlation, joint loss-day contributions and held-minute NQ overlap; offsets count only
if they exist before the account breach. Reuse baseline CL/MOC approximations and state their limits.

## Trial accounting and decision

Two new source execution models, two fee regimes, one all-night fade falsification control per mode,
4000randomside/time schedules plus2000random-mask runs across design/recent. No more than five
strategy variants; diagnostics by leg are not adopted portfolios. Include prior family's unknown
selection burden and prior CodexORPullback2variants in significance counts. Use latest trial-log
N_items+4 at minimum. Every tested model/allocation must be reported, including failures.

Keep the current plan unless all latest gates pass: MC confirmation, multiple-test tANDDSR>=.95,
positive design/recent with2023+t>=2, clean placebos, independent clean PASS and paired plan benefit
over baseline AND empty slot without materially worse risk. A small noisy payout gain near the cap
does not establish a useful change. Claude reviews/ranks; user decides trades. Reports start with
Summary<=5lines. Commit/push results on codex/work, no other branches or live infrastructure.
