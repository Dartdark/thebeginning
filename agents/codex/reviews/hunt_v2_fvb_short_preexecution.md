# H02 FVB gross implementation: source PASS before data

Scope: independent source and synthetic preexecution review, 2026-10-26. This is **not** a promotion/raw-spec
financial review. No native price file, financial ledger or financial output was opened, and no gross/stopped
return calculation ran. Only this review file was written by the reviewer. Work remains on codex/work.

Reviewed AGENTS.md, BUILDER_BRIEF.md, RESEARCH_CONTROLS.md, the H02 eight-question evidence sheet,
`agents/codex/plans/hunt_v2_fvb_short_execution.md`, the source review, and gross implementation plus its
pure imported helpers, shared Grid24 and calendar sources. Initial preregistration is2421d7e; root must bind
the final implementation and pre-data evidence clarification in the effective registration/implementation
commit before authorizing a gross run.

Final reviewed code: `analysis/codex_hunt_v2_fvb_short_gross.py`.
SHA-256: `221efb8959d12b7522009325a9bb22e846a4dc4ebc55853494304676d1f4fb38`.

## Checked semantics

- Shared Grid24 is storage only. No `trading`/`last_j` or current final-session coverage determines entries.
  Exactly14 preceding normal cash-calendar slots provide RTH ranges, each requiring405 minutes08:31–15:15.
  Missing slots are not replaced by older observed rows. Only dates strictly before the decision date supply
  references; future/current RTH perturbations do not change those references.
- PM uses330 completed minutes03:01–08:30. Known missing prior/PM inputs cause retained pre-entry skips,
  consistent with the root plan. Otherwise-eligible scan prefix holes or held-path holes veto gross admission.
  The earlier evidence sentence implying a global veto for all prior/PM skips was clarified before any data.
- First SHORT signal/day only, inclusive08:31–10:30 close labels, strict close below ordered known low.
  Gap case/duplicate levels/body/range conditions match the frozen gross design. Long signals never consume
  short state. There is no stop, target, reentry, fee subtraction, tick rounding or old BOTH ledger reuse in gross.
- Entry is exact native open at signal_j+1; exit is exact15:11 close. Invalid entry, endpoint or any held
  minute remains in the opportunity audit; there is no next-observed-minute or last-close fallback.
  A later gap outside the raw hold does not suppress an earlier signal. Scan-prefix search ends on the first
  missing minute rather than skipping toward a later favorable trigger.
- Calendar/early-close exclusions and quarterly second-Thursday+0/1/4/5 guard are preknown. Guard applies to
  today and prior reference, not a future price-jump detector. The code accurately labels this a conservative
  proxy, not verified vendor-switch provenance. Intraday reference ranges may include guard slots as registered.
- Close/open clock fields explicitly disclose zero receipt/processing-delay idealization. They do not prove
  actual receipt or MNQ fill timing. No learned model or fitted preprocessing is used.
- Native MNQ arithmetic is$1.24 commission plus two$0.50 adverse-fill allowances=$2.24RT; raw mean hurdle$4.48,
  minimum100events, and complete endpoint/held/otherwise-eligible scans are a conjunction. Gross mean/t,
  standard deviation/standard error, yearly/side rows, missing paths and cost bridge are retained. Four-tick
  stress is a frozen later cost-only repricing, not simulated by this gross runner.

## Source/run boundaries

The fixed adapter admits exactly ten native NQ2018–22 day/overnight files and isolated allowed-path cache
symlinks. Metadata actual dates, integer clocks and declared years are checked before price parsing. Duplicate
conflicts are rejected and shared-grid values reconciled to the duplicate-audited native fields. Extra cache
CSVs or changed links are refused. No2017 warmup or2023+ source path is admitted.

Gross checks codex/work, byte equality of committed plan/evidence and committed implementation/dependencies,
then hashes fixed inputs. Code binds source spec pin92b1d4c, input/dependency hashes and runtime versions,
and checks hashes again after calculation. A nonblocking hypothesis-local lock and existing verified-marker
guard prevent concurrent/completed alternate-directory reruns. Output artifacts are write-once, with a final
marker hashing every artifact; downstream code must verify all hashes, not merely a favorable gate JSON.
Imports of the H01 module reuse pure helpers only and do not call its strategy, paths, once guard or run function.

Synthetic check command used the requested Python with`-B`, imported the module and called only
`synthetic_checks()`; it did not invoke financial phases or write a synthetic artifact. Final version passed
18 grouped checks, including date/clock validity, exact references, causal perturbations, zero-event schema,
missing entry/PM/prefix/held/endpoint handling and the full gross-gate conjunction.
Runtime: Python3.12.14, NumPy2.3.5, pandas2.2.3.

## Decision and limits

**SOURCE PASS for the committed frozen gross phase only**, after root freezes the exact hash above and effective
registration before prices. No fatal source mismatch remains in that scope. A changed code hash needs source
reconciliation before execution. No stopped strategy, control, historical validation, book bench or promotion
check is attested here; each remains behind its registered gate. Source-level causality cannot establish actual
raw-data clock/coverage, vendor splice fidelity, native MNQ quotes/latency or MC parity. Those remain financial
phase audits and later confirmation limits. Budget counts and research objective were not altered by this review.
