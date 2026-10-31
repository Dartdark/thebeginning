# H05 High-win MO: SOURCE/SYNTHETIC PASS for the frozen gross screen

Independent preexecution review, 2026-10-26. Scope is code, frozen definitions and artificial inputs only. No actual native, OF, daily-index, MC, cache, trade or economic-output rows were read. No old financial maker was imported or executed. This review produces no hypothesis, gross-screen or economic-evaluation count and makes no strategy, book-placement or MC-parity claim.

Reviewed on `codex/work`, HEAD `92ca1fa99dd3b5c9480321a7eb200fff1c14532a`, before the registration commit and before actual execution:

| File | SHA256 |
|---|---|
| `analysis/codex_hunt_v2_highwin_gross.py` | `c1358e141d549be37839c7b22b0b305c3f283b3597bc297ed3cbd59b9083c659` |
| `analysis/codex_hunt_v2_highwin_signal.py` | `1e94260caf7d9420653de57a1fc565e3ad8fe72460f33a735a0d9f3ddf2c8ff3` |
| `agents/codex/plans/hunt_v2_highwin_confirmation.md` | `e09611907c55f96669647e5559ec38f0d4650f7de2b291e5c1c9cbe5e5f94a9e` |
| `agents/codex/research/hunt_v2_next_executable_nomination.md` | `bdecd4b608b85dc2b889e42a185d1183fd335e2dc130142b76111004ea7f2097` |

## Definition and stage checks

- The exact three source archives byte-match full source pin `d14dc9a153df128aafd3f48d4fea2aa78b88bb28`, their manifest SHA256 values and the plan's Git blobs. The archives remain source references; importing the old maker would calculate outcomes and is avoided.
- The independent helper reproduces contiguous occurrences of `row*1000+((j-1)%1440)//10`, including the separate current-row midnight fragment. Every observed partial bucket updates EMA21, RMA14 true range and EMA3. Initial true range/pivot, first finite oscillator, strict crossings, current-bucket-inclusive minimum60, exact10 unique minutes, 08:40–09:30 window and first qualifying signal/date match the registered definition. No BO position or old stop outcome selects entries.
- The source July3/December24/Friday-after-Thanksgiving predicate is retained. Shared known holiday/early-close exclusions apply only to entries; indicator history is retained. Actual helper coordinates come from the sorted shared native grid and state starts at fixed2017-09-01.
- The adapter enumerates exactly12 owned DAY/ON annual inputs:2017 warmup and2018–22 design. It validates calendar/HHMM/year metadata before native numeric loading. No2023+, OF, broad pickle/cache or MC input is admitted. Audited source rows retain conflicting/identical duplicate IDs; only identical coordinate values merge. Invalid observed OHLCV and conflicting coordinates fail admission.
- The first fill is the exact next native minute OPEN; a missing entry is not moved forward. Every held minute through the minute preceding OPEN891 and the exact positive OPEN891 endpoint must exist and be valid. Otherwise the event is retained unresolved and the entire raw screen is blocked. No earlier-close fallback or favorable jump deletion exists.
- Raw admission requires at least100 events before endpoint arithmetic. Whole missing normal RTH sessions are reported as `NO_OBSERVATIONS` diagnostics under the frozen observed-data definition, not repaired or converted to an infinite ideal-minute EMA veto. The raw phase computes no ATR and imposes no ATR veto.
- Only after admission does the raw screen calculate signed `(OPEN891-entry)*2USD/MNQ`, with no bracket, fees or reentry. The frozen market RT assumption is2.24USD and the mean-gross hurdle is4.48USD. Both sides and each design year retain count, mean, SD, SE, t and total, including empty groups. No protected-design, bench, validation or account outcome is produced by this script.

## Reproducibility and failure boundary

Source inspection verifies branch restriction, preregistration ancestry, equality of required working/HEAD/preregistration bytes, archived-source binding, exact input inventory/header/byte/hash records, isolated shared-grid inputs, nonblocking exclusive lock and exclusive artifact creation. A retained attempt/completion in the candidate output family forbids an automatic retry or alternate-directory rerun. Bound input/code hashes are checked again after execution.

The attempt and pre-row binding precede metadata/body interpretation. Source/implementation exceptions are caught only before `after_admission`/raw attachment and retain their stage, type, message and traceback with0 raw screens/evaluations. Errors after the raw boundary cannot be mislabeled as0-return source failures. Actual successful and failed stage markers bind saved artifact hashes. Importing the reviewed modules does not load actual market data.

The plan/source/code are still awaiting the parent's registration commit at this review snapshot. That commit and unchanged bytes are required by the actual command; this review is not a substitute for the runtime guards. Parent owns the one actual run and progress accounting.

## Synthetic evidence

Re-ran5 author main groups and9 author helper groups through their pure functions using Python `-B`; actual `pandas.read_csv` was explicitly forbidden during these runs. No fixture CLI or output writer was called.

Four additional independent main groups passed:

1. Opaque raw-grid poison proves count99, conflicting-source, invalid-source and unresolved-held gates do not touch any raw endpoint. A whole missing normal-day diagnostic alone does not block100 otherwise valid events.
2. One hundred artificial entries verify the direct MNQ point-value bridge, values below/above4.48, exactly1 gross screen,0 economic evaluations, no fee subtraction and all18 period/side summary rows.
3. Patched memory-only native frames verify identical duplicate merging with both row IDs retained, conflicting duplicate rejection and invalid OHLC observation retention.
4. Date-only calendar tests cover mourning, Good Friday, Thanksgiving Friday, observed Juneteenth and the normal2021-12-31 exception.

A focused independent signal reviewer additionally passed5 groups: closed-form recursive values through partial/full/partial buckets;60 zero-range buckets followed by a first finite oscillator above100 correctly emitting no crossing; midnight1/10/9/1 occurrences; backward-coordinate/date-conflict rejection; and Friday-after-Thanksgiving versus Thursday across2018–22. No actual input or output rows were read and no files were written by those checks.

## Limits and verdict

**No preexecution blocker found for this exact frozen gross screen.** Actual event coverage, invalid/conflicting observations and complete held paths remain unmeasured until the committed run. The selected E1 family, initialization/calendar changes, prior nine/twelve looks and old book failures remain selection history; this is confirmation of a selected existing rule, not new signal alpha.

Ordinary bar availability uses the disclosed close-to-next-open model assumption; historical local receipt and identical MNQ liquidity are not verified. Continuous-contract mapping, missing ideal observations and external chart/MC parity are not certified by this review. These uncertainties must remain visible and cannot be reinterpreted as favorable execution evidence. Before any stopped outcomes, the frozen ATR reference admission requires its own concrete review. Promotion and book claims still require the later protected execution, immediate paired personal19 benches, selection/placebo/dependence checks and a fresh independent raw-spec checker specified in the plan. No PowerLanguage or trading approval follows from this source pass.
