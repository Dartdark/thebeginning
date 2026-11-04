# Independent fixed-quantity amendment review — 2026-11-04

Summary: **PASS for bounded conditional amendment execution after committing these exact artifacts.**
The original 2,485 definitions and 606,340 completed design cases remain retained; this is an explicit post-design amendment.
460 new fixed-lot definitions plus the shared 30-case reservation give a maximum 2,975, below 3,000.
The DT correction is confined to its documented existing open-time exits; original results are not replaced.
No amended or 2023+ account outcomes were calculated by this reviewer; no further code fixes are requested.

Reviewer: `eval_loss_forensics`, independent of the new generator, source-overlay and wrapper implementers. The original design outcome/admission summaries were already known and are explicitly disclosed in the amendment evidence. This is an engineering/admission review, not independent economic verification.

## Reviewed scope and tests

Reviewed `analysis/codex_eval_fixed_arm_20261104.py`, `analysis/codex_eval_source_overlay_20261104.py`, `analysis/codex_eval_amended_run_20261104.py`, the fixed registry and the amendment plan/evidence. Inspected the underlying DT exit and normalization source. Executed only pure/synthetic selftests and the original hash/committed-file guard. No new market preparation, amended account case, selection, historical validation or source return calculation was run.

The original guard against commit `a087708b13697df4c3dd0b0814f98cb53a2b254a` passed on current bytes, including all 118 registered input hashes and original implementation/configuration. The proposed new files must match their separate committed amendment before the wrapper permits its work. The original guard and original definitions/results are not rewritten by this wrapper.

## Findings

1. **Finite additional menu and shared budget: PASS.** The generator requests all 18 standalone keys at 1/2/4/8/12/20 fixed micros and the 65 allowed two-key combinations at equal 2/4 micros, separately for each account size. It requests 476 definitions, identifies 16 canonical aliases to originals and adds exactly **460**: 229 for 50K, 231 for 150K. Fresh deterministic generation equals `fixed_policies.json`. All quantities are integers; ordinary governor and target guard are disabled. Plain ONB30+ONBML is excluded as the same signal family. No original registry object is mutated.

2. **Multiplicity and amendment disclosure: PASS.** Original 2,485 plus new 460 equals **2,945**. Only the original shared **30** derived slots remain, giving **2,975** maximum against the 3,000 cap. There is no second derivative reservation. The plan expressly supersedes the earlier no-additional-grid clause for this input-compatible arm, retains prior results and discloses the observed missing-risk admission and original FC2B summaries. This is a post-design extension, not a claim that the fixed menu was part of the original untouched experiment.

3. **Fixed size does not validate missing ATR: PASS with stated limits.** Fixed quantity avoids using an unavailable ATR/range to choose size. It retains original entries/exits, source protective orders, held-price/target/clock gates and source coverage. It does not certify original risk inputs or reproduce source-feed indicators. Earned governors still use the original declared stop-input admission/rejection semantics. Results remain conditional source-ledger allocation research.

4. **Original plus new commit guard: PASS.** Every amended command first invokes the original committed-code/config/input guard. The new wrapper then compares its generator, overlay, registry, plan and evidence with an exact separate ancestor commit. Overlay execution also freezes all three source-justification files, including the source-kind provenance CSV. Candidate fingerprints include amendment context, overlay receipt and original tape identity. New runtime/selection paths preserve originals. The first market work requires the new full SHA; an uncommitted amendment cannot run.

5. **DT factual correction: PASS for the demonstrated scope.** `dual_thrust_test.py:trade` returns `o[j]` for `kind='flat'` after the prior observed bar reaches the flat clock. `lab_trades` maps that exit to numeric kind2. It also maps fallback `kind='close'` to2, so that distinction was checked: metadata-only inspection of the saved source date/kind columns in the common window gives **401 flat**, 712 stop and 408 target, with no fallback-close row. This corroborates applying the correction to all 401 current-window kind2 exits rather than only the 390 mismatches. The final overlay also freezes the source-kind provenance CSV and asserts the exact selected cohort of 400 exits at14:56 and one at14:57; the execution source/normalization files remain original-hash verified.

6. **Exact clock and immutability: PASS.** The overlay changes only each selected DT exit's event-row pointer and raw-fill qualification. A close-labelled minute's known open is exactly60 seconds earlier. It requires an existing equal-time row, the original account session, causal entry-before-exit order and an exact common-price match. It does not search for a favorable touch or insert a quote. Absence/mismatch keeps the own event NaN/UNKNOWN. An earlier new entry at the same epoch creates an explicit priority ambiguity, placing the UNKNOWN exit at the first equal-time row before that entry. Input prices/times are retained by identity, original events are unchanged, non-DT/non-kind2 event fields are asserted unchanged, and nodes/bounds are recomputed. Before/after hashes and source/repair receipts are saved separately; existing overlay files cannot be overwritten.

7. **Aliases and source scope: PASS.** The 16 exact fixed-lot aliases reuse their original observations; they are not replayed on a repaired source under the same ID. Original DT design results remain as observed, while the new fixed arm and earned derivatives use the disclosed clock overlay. CURRENT contains no DT, so its unresolved ATR quantities are not repaired or silently changed. Comparisons across the retained old and amended source scopes must remain labeled.

8. **Joint nomination and earned stages: PASS.** The wrapper reads/revalidates the preserved original case receipts and new arm cases, requires identical design-start calendars and invokes the unchanged five-year 2018–22 selector. At most three roles per account nominate one joint set. Derived definitions are reconstructed exactly from registered joint nominees and linked to the committed initial selection SHA; the count/registry chain is checked again. Final nominees must exactly equal registered policies. Committed final nomination and overlay identity precede previously seen 2023+ account validation. No extra selector, weakened UNKNOWN gate or 2023 nomination is added.

9. **Baseline uncertainty and scenario interpretation: PASS with limits.** Original CURRENT50K is 0 confirmed passes, 4 failures and 240 unknown starts, not a verified zero pass probability. The same unconditional denominators and identification bounds remain in summaries/paired contrasts; a broadly unidentified baseline can prevent a superiority recommendation. Frozen nominees and references use three cost scenarios by four cushion states (**12** prespecified sensitivities), not 12 opportunities to choose a new rule. Unknown/fill/coverage gaps are not inferred as expired accounts, zero returns or funded payouts.

## Synthetic and metadata evidence

- Fixed-arm generator selftest: PASS; canonical identity, aliases, original immutability, integer lots, disabled governors, pair exclusions and determinism.
- Source-overlay selftest: PASS; exact known-open clock, immutable original, unrelated events, no favorable touch fallback and early/late mismatch handling.
- Amendment wrapper selftest: PASS; 460 new, 2,945 unique joint definitions, 2,975 maximum and explicit 22-component nomination metadata.
- Original committed-code/config/input guard: PASS; no new market calculation.
- Deterministic generated registry equality and count checks: PASS.

## Remaining interpretation limits

The original plan's conditional OHLC chronology, source-signal reuse after resizing/skipping, complete-window coverage, target trade-through, costs, UNKNOWN bounds, overlapping-start uncertainty, sparse minima and native broker/source verification limits remain unchanged. A factual clock correction is not a profitable-strategy finding. The baseline's unresolved quantities do not acquire a narrow pass-rate estimate. No global-optimality, funded/personal-income or allocation/deployment claim follows. No live system, broker, VPS or external message was used.

## Frozen review pins

|Artifact|SHA256|
|---|---|
|`analysis/codex_eval_fixed_arm_20261104.py`|`33a5903a393d44059caf18eeebc91d155df887692ae1257d56080031086a53a0`|
|`analysis/codex_eval_source_overlay_20261104.py`|`f9f23256911f1659770e398917d1c7117c8afd0db8180a746158212fb05f6b8f`|
|`analysis/codex_eval_amended_run_20261104.py`|`e011074a80334a92d90ca6d37712df73bffbc4b2f65dcce4486278c9aacb9564`|
|`fixed_policies.json`|`1449fbf76897c5f8073a9c778419ab6f1d3b4c4e50cab10f894ded99d8d2c899`|
|Amendment plan|`104b2108fc5be1a7ee582f53c91178f92c43ee117c7802ea2a457eb10aeb3381`|
|Amendment evidence|`38b47b5b98e156ed482f0798e0a5514eecf3e9d3a0b75678266c92dfc932e1cd`|

These exact bytes are approved for bounded conditional research execution once committed. The wrapper enforces the actual new amendment SHA and later nomination-commit boundaries. No remaining blocker or optional refactor is requested by this review.
