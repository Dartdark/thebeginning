# I03 native/OF OHLC: diagnostic complete, provenance still needed

Summary: the new non-return intake found402normal-RTH OF timestamps absent from the native NQ
files, including the2018-04-30minute that first affected H04's recursive state. All402observations
are internally valid, but source identity/build/roll/receipt remains unverified. Across486,004common
timestamps,96.582%have identical OHLC and96.513%have equal native versus auxiliary total quantity.
No replacement bars, strategy returns, old-study reruns or book improvements were produced.

**Running budget:3/60economic evaluations,4/10registered hypotheses,2gross screens; archived t6=65.**
I03 adds0to each. This is input-quality research, not H05, a strategy TEST or statistical promotion.

Source note: `agents/codex/research/hunt_v2_native_OF_gap_source.md`.
Plan: `agents/codex/plans/hunt_v2_native_OF_gap_intake.md`, initial **41ef515**, effective reviewed
code/plan **386b812**, committed/pushed before new data joins.
Main: `analysis/codex_hunt_v2_native_OF_gap_intake.py`, SHA256
`7006e9634004f95da3b9ad602592df001a41513a70411c6c719246c8a886e334`.
Numeric helper SHA256: `b08e43b4d61bd1b38a2691bb145794f9f5cb4c1ca41e991695243ada3339b220`.
Review: `agents/codex/reviews/hunt_v2_native_OF_gap_preexecution.md`.
Artifacts: `analysis/outputs/codex_hunt_v2_native_OF_gap_intake/`.

## Scope and ordering actually executed

The exact five native NQ2018–22files and20OF annual parts were reused from the immutable H04 input
inventory, with byte/size/header hashes verified. No2017,ES,MC,2023+ or new provider input was opened.
The native export writes chart OHLC and Ticks as volume; OF writes its ASCII chart OHLC plus buy/up
and down quantities. OF volume equals upvol, so native total was compared with upvol+downvol.
Neither exporter document authenticates the original upstream producer or contract/roll map.

The once-only run began19:11:28UTC and completed19:14:20UTC on2026-10-26. Stage A read timestamp
strings and source IDs, using the fixed ET-minus60minute mapping and shared calendar. All normal
weekday close labels511..900were enumerated, independently of H03/H04tickets or outcomes. The common
and OF-only sets were saved and hashed before numbers. Stage B inspected every common key and saved
those results before inspecting exactly the402prebound OF-only keys. There was no offset/level search,
calendar retuning, favorable deletion, interpolation or temporal-price arithmetic.

## Stage A: complete fixed timestamp universe

| Presence at expected normal-RTH key | Keys |
|---|---:|
| Both sources | 486,004 |
| Native only | 650 |
| OF only | 402 |
| Neither | 54 |
| Total expected | 487,110 |

Metadata validation passed with0invalid records. All original IDs and outside-primary-calendar
metadata counts are retained. Source absence is not a verified no-trade minute, halt or export error.

## Stage B: all common keys, without selecting a matching subset

All486,004common pairs have internally valid OHLC/quantities and no unresolved duplicates. Every
common key remains in each percentage denominator.

| Same-key diagnostic | Count | Share of all common keys |
|---|---:|---:|
| Exact O/H/L/C tuple equality | 469,394 | 96.582% |
| Entire OHLC tuple within1native tick | 469,478 | 96.600% |
| Close alone within1tick | 469,710 | 96.647% |
| Native total equals OFup+down | 469,058 | 96.513% |
| OFvolume equals upvol | 486,004 | 100.000% |

There are16,610nonidentical OHLC tuples. A close-only one-tick check would accept232more keys than
the complete OHLC one-tick comparison. All mismatching fields, raw formats and original IDs remain
in the compressed ledgers, with fixed year/calendar/source strata. Differences could involve contract,
roll, feed or construction rules; this intake does not identify their cause or certify a splice.
One-tick agreement was diagnostic, never a replacement-bar acceptance threshold.

## Exactly the prebound OF-only observations

| Date | Additional OF keys absent from native |
|---|---:|
| 2018-04-30 | 1 |
| 2018-07-26 | 2 |
| 2018-08-28 | 4 |
| 2019-12-05 | 2 |
| 2020-11-30 | 390 |
| 2021-09-17 | 1 |
| 2022-03-08 | 2 |
| Total | 402 |

All402are internally valid, with positive OHLC/quantities, no duplicate conflicts and the expected
volume alias. The April30observation is close label882(14:42CT), with its original source ID retained.
These are second-stream observations. Positive quantities and common-key agreement cannot prove
that a missing native bar should have existed or establish its true contract, price path or receipt.
No row was added to a native grid and no inferred fill or missing-period profit was calculated.

## Retention and interpretation

All large key, source-ID, common/mismatch and OF-only ledgers use deterministic gzip, retaining every
record. A standard gzip decoder reproduces them. Root verified all20marker artifact hashes, Stage-A
frozen-set hashes and the common-results checkpoint preceding probes. Input/code bindings were
rechecked by the executed program. The nine main and ten numeric synthetic groups plus independent
scope/integration checks passed before actual rows; the earlier artificial integration failure remains
retained. These implementation checks are not market-performance trials.

Final status: **DIAGNOSTIC_ONLY_NEEDS_PROVENANCE**. Original contract/roll/session/adjustment,
upstream bar construction, correction/version and historical receipt remain unresolved. This does
not certify2017warmup,2023+history,ES,MNQquotes or account paths. H03/H04remain CLOSED under their
original source definitions; neither the unsupported MC time codec nor their financial testing was
rerun. A future distinct rule still requires a credible mechanism, admitted inputs and its own
committed economic preregistration and all promotion/bench/independent-checker gates.

No t/DSR, five trading metrics, native-cost edge, placebo, Monte Carlo, funded/evaluation outcome or
PowerLanguage draft follows from this source intake. It is not trading approval, a user-action
blocker or a reason to pause the bounded hunt. **No new qualifying book candidate.**
