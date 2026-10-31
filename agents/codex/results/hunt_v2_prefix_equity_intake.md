# I01 pre-fix relative-equity input intake: NEEDS DATA, no trading test

Summary: two newly discovered public daily-index JSONs were acquired and audited under a committed non-return protocol. Both match their immutable source blobs and pass basic schema/design-OHLC checks, but neither has verified identity, source/event/receipt or revision provenance. The purported SPX series has338–344dates/year and both files stop inDecember2023, so they cannot supply verified current2018–26 cash-index inputs. No signal, return, gross screen or book performance was calculated.

**Budget unchanged:3/60 counted evaluations,2/10 registered hypotheses,2 gross screens; prior t6 remains archived65.** I01 adds0 hypotheses/economic evaluations/screens. H01/H02 stay closed. This is source admission, not H03 or a design-pass candidate.

Mechanism sheet: `agents/codex/evidence/hunt_v2_prefix_equity.md` (NEEDS DATA).
Plan: `agents/codex/plans/hunt_v2_prefix_equity_intake.md`, initialpre-data **b9ae149**, effectiveplan/code **a70ded0**.
Code: `analysis/codex_hunt_v2_prefix_equity_intake.py`, SHA `c104d9c51b7aac190133c5506ffcdaef824a39eb475e2a4eea4c619cef3fbbdd`.
Outputs: `analysis/outputs/codex_hunt_v2_prefix_equity_intake/`; raw/source/manifest/license: `agents/codex/inputs/hunt_v2_prefix_equity_intake/`.

## Mechanism question before new data

Month-end currency hedgers may rebalance foreign-equity hedges as holdings change in value. A separately stated bilateral equal-sensitivity/equal-hedged-notional assumption suggests a lagged US-minus-Eurozone equity-pressure proxy for EURUSD. Actual aggregate hedge exposures/order size and clocks are unobserved. This is NOT a faithful Melvin/Prins replication: exact primary formula/country list were not verified. It differs from already researched post-fix self-price reversal and stock-versus-bond pension proxies, whose selection history remains intact.

A genuine TEST would still need admitted indices, ordinary historical fixing-service/exception evidence, source availability, native M6E costs and small-sample power. An illustrative1.24RT fee+two1.25ticks=$3.74 is cost arithmetic, not a measured or verified trading result. No side, trading window, stop, size or threshold was chosen from these inputs.

## Bounded acquisition and executed audit

Exactly2 raw JSONs, pinned public repository `MohammadrezaAmani/Global-Stock-Market-Indices-Historical-Dataset` at `0e7218912d08aa5bfd9ff67123d44359b1e44eb4`. README/LICENSE/ref/blob metadata were read first. The eight-question sheet, bounded plan, manifest and reviewed auditor were committed BEFORE acquisition. Actual downloads returnedHTTP200 and preserve805312/885971bytes respectively; MIT notice and retrieval/hash receipts retained. No blocked destination, paid source, account, remote code or message was used.

The audit ran2026-10-26T16:40:39.058303Z–16:40:39.102863Z. It decoded numeric JSON tokens as strings, inspected full-file Gregorian DATE metadata, and converted ONLY2018–22 OHLC fields to Decimal for integrity checks. Correct English thousands grouping was supported before acquisition; malformed grouping is rejected. PctChange/AbsChange/Jalali fields, pre2018/2023+ prices, returns, signals, correlations and trading metrics were not converted/calculated.

|Source label|Raw rows|Date metadata range|2018 unique|2019|2020|2021|2022|Basic quality|Admission|
|---|---:|---|---:|---:|---:|---:|---:|---|---|
|SPX (`bourse_sp-500.json`)|2889|2014-10-02–2023-12-15|338|344|344|339|341|PASS|NEEDS DATA|
|EuroStoxx50 (`euro-stoxx-50.json`)|3079|2011-08-14–2023-12-14|251|251|252|250|254|PASS|NEEDS DATA|

Both are descending by date, with0duplicate dates,0conflicting design duplicate keys,0invalid eight-field rows/dates and0invalid design-OHLC records under the frozen checks.1706/1258design rows were converted; non-designOHLC conversion remained0. At least240unique dates in each design year is only a coarse screen, not cash/fixing calendar verification.

SPX338–344unique dates peryear exceed any ordinary US cash-session calendar. This establishes a date/identity question, not that its numerical values are fabricated. No weekend/futures/CFD/forward-filled interpretation was silently assigned and no rows were deleted to force a calendar match. Eurozone's plausible counts alone do not verify identity or publication timing. Both files' latest dates are in2023 despite a2026 README date; missing2024–26 must not become no-trade zeros, extrapolation or a full-history claim.

## Why numerical quality cannot admit the inputs

All five required provenance categories remain UNVERIFIED for BOTH files: originating quote vendor; actual index identity; close/event clock/timezone; adjustment/revision/vintage convention; historical available-at/receipt timing. README labels and metadata are claims to corroborate, not proof. Source Git-blob hashes verify exact retrieval, not economic identity or point-in-time correctness.

|Required later strategy evidence|Status|
|---|---|
|TEST sheet and<=5configuration economic preregistration|NOT reached|
|2018–22 raw gross screen, stopped returns, five metrics/by-side/year|NOT run|
|Once-only selected2023+ historical validation/full2018–26 significance|NOT run|
|Same-exit random-time/random-side placebos and dependence/selection checks|NOT run|
|Current BASE/ADD/REPLACE/EMPTY, whole-contract MC or joint funded/evaluation paths|NOT run|
|Fresh raw-spec promotion checker, MC confirmation or PowerLanguage|NOT run|

Preexecution SOURCE PASS covered strict non-return code and12synthetic groups only; it is not a strategy review. All marker-bound artifact and input hashes were checked after execution without rerunning the audit. Frozen registration manifest remains unchanged; its `prices_fetched:false` describes registration-time state, while `retrieval_receipt.json` records actual later acquisitions.

## Verdict and next step

**Do not admit these files for strategy testing.** Preserve I01 as a completed rejected/unresolved input intake; do not repeat its unchanged audit, use the bad-calendar label as cash-index identity, or rescue missing history with synthetic data. A genuinely different provider/provenance panel needs a separately bounded intake before admission. Source-only search may continue; this is not evidence the public universe is exhausted, a new user-action blocker, trading approval or a reason to pause v2 before its stopping condition. The nine uploaded templates remain unexecuted references; t6 and its alerts remain stopped.
