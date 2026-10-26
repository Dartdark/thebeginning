# H03 saved-entry codec diagnostic: source PASS

2026-10-26. Independent source and synthetic review only of
`analysis/codex_hunt_v2_swing_mc_codec_diagnostic.py` against
`agents/codex/plans/hunt_v2_swing_mc_codec_diagnostic.md` and the research controls.
Reviewed SHA256: `de436b84914b446f66e83538c468f88756f949b5e932072f48430a6b2ad771ee`.
Root must commit this code and narrow diagnostic plan before execution. The original16ed951 maker,
pre-gross marker and artifacts remain unchanged. No codec match result was read/calculated by this review.

The earlier saved-reference/clock source review is
`agents/codex/reviews/hunt_v2_swing_opening_codec_review.md`; its separately authorized saved-quality audit
does not constitute execution of this new diagnostic. No additional saved financial body, MC body, raw price,
endpoint, return, stopped engine or grid was read during this preexecution review. Only this review file changed.

## Scope and gate checks

- The code is standalone. It imports only the pure shared `grid24.jof` codec, never Grid24 construction,
  the old gross maker, entry reconstruction, protective execution, raw-window attachment or MC P&L engines.
- Exact allowed CSV projections are saved parent date/side/entry/entry_j; saved calendar date/comparison_eligible;
  retained MC date/side/entry/t_in. No feature/flow/source-price recalculation, raw exit open, MC exit/kind/
  gross/net field or2023+ entry/time/price conversion is present. Dates are interpreted before MC financial
  entry fields. Ineligible design dates retain date-only exclusion IDs rather than silently shrinking the
  published comparison universe. Parent rows outside that universe fail metadata instead of being selected away.
- Clock syntax is fixed3/4ASCII-digit HHMM, valid0..23hours and0..59minutes, converted by jof. It admits
  848→528,1145→705,900→540. It rejects decimal/colon clocks, whitespace, Unicode digits, impossible times
  and other encodings. No offset/format optimisation or chart-timezone inference occurs.
- Side canonicalization is the original frozen integer-valued±1 serialization, including trailing-zero
  decimal strings. Invalid/nonfinite/nonpositive entry metadata is rejected. Duplicate dates are fatal
  under the one-entry/day parent, regardless of favorable match fractions.
- The original one-to-one matching rule remains date+side, price<=.25point and minute<=1, with both reciprocal
  fractions>=90% AND valid metadata. Every saved parent row stays in the denominator. MC recall uses all
  eligible design MC entries, not only observed parent-entry dates. Original tolerances/epsilon are unchanged.
  Matching source IDs, unmatched parent/MC flags and calendar exclusions are retained.

## Binding and immutable output checks

Before interpreting saved metadata, the runner verifies codex/work; current HEAD and authorization-commit
code equality; and diagnostic plan equality to the authorization commit. It requires an original failed
pre_gross marker with raw_returns_calculated=false and gross_screen_runs0. The original maker hash must
still equal its marker's hash. Consumed saved parent/calendar/original-binding artifacts must equal the
original marker inventory. MC bytes must match the original input binding, and shared jof source must
match its original bound hash. The new binding retains all consumed source/artifact hashes, the original
marker hash and source-producer proof. These hashes are checked again after comparison before output.

The independent generic producer at pinned7f0800f writes integer HHMM with `%H%M`→int; dedicated STv3
converter provenance and chart timezone remain explicitly unverified. Source evidence is recorded, not
inferred by maximizing the match statistic.

Output is fixed under the allowed H03 `codec_diagnostic/` directory, protected by a nonblocking local lock,
completed-marker refusal and write-once files. It creates a separate hash-bound diagnostic marker and
does not overwrite/reinterpret the original run. No arbitrary output directory is exposed by CLI.

## Synthetic verification and decision

Using `/workspace/venvs/thebeginning/bin/python -B`, the reviewer called ONLY `fixtures()` in memory.
All8 grouped synthetic checks passed on the exact hash above: strict HHMM/bounds, parent metadata,
future-poison/date filtering, unchanged price/minute/reciprocal thresholds, duplicate rejection, exclusion
IDs and the inability of parity repair to clear original faults. No actual diagnostic or artifact write ran.

**SOURCE PASS for the separately committed saved-entry metadata diagnostic only.** No fatal mismatch found
in that scope. A different hash requires review reconciliation before execution. All results/markers state
zero raw returns, zero gross screens, zero economic evaluations and no authority to run gross, stopped,
validation or book tests. Even a codec parity PASS leaves H03 CLOSED because its frozen reference/prefix
gate remains failed. This is a reporting correction, not an alpha result, promotion or research restart.
