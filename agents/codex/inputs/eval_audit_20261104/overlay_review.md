# DT factual exit-clock overlay: independent code-only review

Summary: The source uses a next-observed-bar OPEN, while the original DT adapter demanded CLOSE for kind2 exits.
Source date/kind metadata independently confirms401flat exits and zero fallback-close exits in the study window.
The overlay preserves original prices/times and changes only selected DT exit row/raw-fill fields plus segment indexes.
Its fabricated selftest and compilation pass; the reported equal-time entry-priority edge is now conservatively guarded.
No actual overlay, corrected path, return, selection or account result was computed by this reviewer.

Reviewer: `eval_path_builder/path_code_review`. This separate review does not alter the original frozen
path/engine/config review, artifacts or results.

## Source justification and narrow scope

`analysis/dual_thrust_test.py:58` exits at the current observed minute's `o[j]` after the prior observed
bar reaches14:55. `analysis/codex_portfolio_audit_prepare.py` retained that close-labelled minute and
raw price, but mapped both `flat` and fallback `close` into numeric kind2 without preserving the
open flag. The new transform therefore addresses a factual normalization error rather than a new signal.

Because generic kind2 can include true fallback closes, the reviewer read only `date` and `kind` from
`checks/candidates/dual_thrust/trades.csv`. In2018-04-02 through2026-07-07 it has1,521rows:
712stops,408targets and401`flat`, with zero`close`. These match the prepared source metadata counts.
This source classification is now pinned as the third amendment provenance source. The public repair
also requires the exact original normalized DT ledger hash and the401-exit clock cohort:400at14:56
and1at14:57. It does not treat future DT kind2 datasets as necessarily open exits.

No author-profitability or independent economic-verification claim follows from this source check.
The reported390wrong-phase mismatches and11equal-open/close cases come from the existing source
diagnosis; this reviewer did not rerun that historical quote analysis.

## Engineering findings

The reviewed implementation copies events, changes only columns0(event row) and6(raw fill) for
selected DT own exits, checks unique own entry/exit and expected NQ/DT/market-exit classification,
and asserts other fields are unchanged before sorting. It leaves `prices` and `times` as the original
objects and recomputes segment bounds with the moved source-event nodes included. Additional old
nodes are harmless subdivisions. Callers must regenerate window node indexes against the corrected
tape rather than reuse original `node_a`/`node_b` slices.

The known clock is exactly `exit_at` minus60seconds in Chicago. There is no favorable-touch search,
nearest-time search or changed source price. A missing/mismatched known-open quote produces an
unknown own raw fill. Earlier-than-entry and cross-session clocks also fail admission.

**Equal-time priority issue fixed with a conservative admission guard.** Choosing the rightmost equal-time row normally
selects current-minute phase0 instead of the previous minute's close. However, if that open has a
duplicated own-roundtrip node, rightmost can be the duplicate AFTER other source entries on the first
phase0 node. Moving an already-active DT exit there can violate the frozen exit-before-new-entry
priority and change contract/risk admission. The final implementation checks for any earlier source
entry at that same epoch. A collision moves the DT unknown raw fill to the first equal-time point,
before such entries can influence the account. It does not select a favorable ordering. The added
collision fixture passes; an executable repair still requires exact price at the known current open.

## Guard and provenance

The new guard requires a distinct40-character amendment commit containing identical bytes for the
overlay and source-justification scripts. The transform keeps the original preregistration reference,
records amendment/source hashes and original/corrected event hashes, and creates overlay-only files.
Existing output artifacts and the original prepared directory are protected from overwrite.

The documented precondition is important: the supplied `Tape` must come directly from the original
hash-verified loader. Checking source-directory artifact hashes and matching metadata alone does not
prove that an arbitrary caller-supplied in-memory array has never been modified. The authorized runner
must preserve that verified-loader chain. The review does not authorize editing frozen source code,
weakening risk/through gates, new portfolio definitions or inspecting2023+ outcomes for selection.

## Checks and snapshot

- `python analysis/codex_eval_source_overlay_20261104.py selftest`: PASS; fabricated prices/events only.
- `python -m py_compile analysis/codex_eval_source_overlay_20261104.py`: PASS.
- Read-only code/source inspection and date/kind metadata counts; no source price/PnL columns loaded.
- Final reviewed overlay SHA256: `f9f23256911f1659770e398917d1c7117c8afd0db8180a746158212fb05f6b8f`.

No unresolved engineering defect was found in this bounded review of the final hash under its verified-loader
precondition. The post-fix script and distinct amendment must be committed before actual overlay or account
calculations. This engineering review does not establish a profitable strategy or authorize allocation changes.
