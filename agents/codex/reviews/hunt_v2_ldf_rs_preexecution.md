# H07 owned RS position input: SOURCE/SYNTHETIC PASS only

Independent preexecution review, 2026-10-27. This approval covers the implemented **SOURCE-only** metadata/coverage stage. It does not cover a feature/support, gross, stopped, null, bench, validation or promotion phase: this wrapper deliberately implements none of them. No actual workbook/native values, feature counts, price marks, economic ledgers or returns were read by this reviewer; no actual phase ran. No files were written by fixtures. This review adds0 gross screens/economic evaluations.

| Reviewed object | SHA256 |
|---|---|
| `analysis/codex_hunt_v2_ldf_rs_open_loss.py` | `ccd3e4e2e92c8a6f12138192a518178924e16e708857759722a60809803f8d77` |
| `analysis/codex_hunt_v2_ldf_rs_metadata.py` | `1b85ccfcbccb62ece192fb8c7d04049440b1242f0e09ae7c4c23edf4c3e7815f` |
| `agents/codex/research/hunt_v2_ldf_rs_predata_adjudication.md` | `245dcdfc18ed6bd9878379a6e30a80c511f5687df106a2e532e40a733d61102d` |

Original economic preregistration is `4c3612104c10f5e5eeb96e53d8cde6bc2a3f2b3d`; current HEAD at review was that commit on `codex/work`. Its ancestry was checked read-only. The exact reviewed implementation/addendum must be committed before ROOT runs SOURCE.

## Source protocol

The wrapper binds the original plan/evidence, committed implementation/addendum and authoritative workbook SHA before interpreting selected metadata. It verifies committed H01 gross/protected markers and their referenced artifact hashes as opaque bytes. It does not execute the H01 maker or interpret its economic columns. Only immutable parent decision dates are interpreted for coverage. Imports open no workbook/native input; there is no native-reader, mark, feature-mask or outcome callable in this version.

The helper requires the fixed sheet names/members, headerrow3, Excel1900 system and Date E/style7/format14 plus Time F/style8/format21. Selected Date DAY is interpreted before the design-year gate; outside2018–22, Time/Type/Signal/IDs/entryPrice/Contracts are not decoded. Exit G Price and outcome cells are never decoded. Required Settings B values are allowlisted; unrelated Settings values remain opaque. Symbol, one-minute compression, both-side/current fixed parameters and full source coverage must pass; the filename alone cannot establish the FLAT assumption.

Trade# inheritance is restricted to declared unique two-row columnA merge coordinates, with entry on top and exit below. Both event quantities must close the same one-contract ticket. Order# is required-present opaque provenance, with no invented equality, consecutive-number or uniqueness rule. Otherwise valid pairs can be physically presented in descending order: raw row IDs/order are retained, then events sort deterministically by their recorded timestamps. Contradictory pair times, sides, quantities, IDs, multiple daily entries or overlapping positions fail the whole selected stream.

## Clock, coverage and causality

The Date/Time codec uses numeric Excel semantics, not arbitrary integer truncation or a fitted offset. Date supplies its integer day; Time supplies its fraction. A nonzero Time day must equal the Date day. A nonzero Date fractional clock must agree with Time; a date-only zero fraction is not a conflicting midnight observation. Minute resolution uses the frozen1e-4second representation tolerance. Both raw serials and exact components are retained. Valid noncanonical entry clocks remain diagnostics for later prefix-state handling, not offset-corrected.

Settings coverage now accepts the predata-frozen finite ISO/US optional-clock grammar, including24-hour/AM-PM, and numeric full Excel serials. Exact rational bounds and raw representations are retained. Every admitted event and every parent14:00 decision must lie inside those full bounds; a timestamp is not reduced to its date. ROOT explicitly froze date-only End Date conservatively at midnight, not an invented full day. Both `1 Minute` and `1 Minutes` describe the same required compression; no other bar size is accepted.

The initial plan ambiguity about future malformed exits was resolved before values: global selected-stream structural failures stop the entire source, never selectively turn an earlier omitted ticket into UNKNOWN KEEP. Once the source passes, the future feature implementation must consume only the as-of prefix. Events afterC840 cannot affect earlier state through future exit/entry existence, signal, price, eventual pairing or the helper's full-stream `noncanonical_entry_dates` diagnostic. Events exactly840 are UNKNOWN KEEP. Earlier valid noncanonical entries or uncertain price basis remain UNKNOWN KEEP under the frozen policy. There is no feature implementation here to certify beyond that contract.

The ordinary native/account-state information convention is appropriate to the contemplated owned-position input; original private receipt logs are not categorically required. Nevertheless this historical MC stream is a reported baseline, not verified live positions or a corrected raw-spec replay. Exact native O541/MC-entry basis and C840 marks, known-state/kept/removed/year/side support and both null-mask combinatorial supports remain unmeasured and unapproved until the separately committed feature stage. SOURCE PASS cannot waive any of them or clear H04's failures.

## Synthetic evidence and runtime boundary

Re-ran13 author helper groups and3 wrapper coverage tests directly with Python `-B`, without fixture CLIs/output writers. Three fresh wrapper/coverage groups passed: exact inclusive endpoints and±1ns coverage failures; fixed ISO/US/AM-PM grammar with impossible/unregistered clocks rejected; and fully mocked SOURCE PASS/FAIL workflows that always retain0 features,0 returns,0 screens/evaluations and no alternate-source path.

Two additional final-helper groups passed. An instrumented selected-cell getter raises on future-year A/B/C/D/F/G/H, exit G and outcome cells; the artificial workbook still admits its permitted metadata and only future Date is decoded. A legal later-exit time/signal mutation leaves the pre840 prefix identical, while malformed later-exit metadata vetoes the whole source before feature authorization. A focused independent reviewer also passed6 earlier event-parser groups covering the same exclusions, fullserial/fraction consistency, merge/quantity/side conflicts and1904 rejection; the final revision's changed coverage handling was rerun above.

The source wrapper uses a nonblocking exclusive lock, committed byte checks, a retained write-once attempt and output-family no-retry guard. It rechecks implementation, workbook and parent artifact hashes and binds the saved source artifacts in its completion marker. A source failure directs closure before features; success directs only a new committed feature/support implementation. The actual marker records0 gross screens/evaluations and explicitly states that SOURCE PASS is not feature/economic admission.

## Verdict

**No blocker remains for the exact reviewed SOURCE-only stage after commit.** ROOT owns its one actual execution and accounting. Source metadata may still fail; that is not permission to substitute another report, reinterpret a clock from prices or retry H04. The four definitions, unknown KEEP rule, native costs, support thresholds, exact add-one null formula and implementation-matched book controls remain frozen. No gross result, book improvement, MC/raw-spec parity, trading approval or PowerLanguage follows from this review.
