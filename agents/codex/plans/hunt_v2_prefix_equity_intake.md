# Bounded pre-fix relative-equity input admission (no strategy return study)

Mechanism BEFORE data: `agents/codex/evidence/hunt_v2_prefix_equity.md`, NEEDS DATA.
Source context: `agents/codex/research/hunt_v2_prefix_equity_source.md`.
This commits a NEW source-quality intake, not H03 registration, an economic preregistration or a TEST override.
H01/H02 remain CLOSED; t6 and its watcher remain stopped. Uploaded templates remain reference-only.

## Why inspect these inputs

Month-end equity currency hedgers adjust hedges toward changed foreign-equity exposure. A separately stated
bilateral equal-sensitivity/equal-hedged-notional model suggests US-minus-Eurozone prior equity performance
as one possible EURUSD pressure proxy. Aggregate equal sensitivities/notionals, actual residual order size
and hedge timing remain assumptions. This is NOT a faithful Melvin/Prins replication; the exact primary
formula/country list has not been verified. The idea is distinct from already researched post-fix self-price
reversal and equity-versus-bond pension proxies, whose selection history is retained.

Before testing it, the newly found daily indices must have genuine identity, adequate design coverage and
known source/event/receipt/adjustment clocks. A public filename or README's quality claims cannot admit data.

## Exact scope fixed before fetching any new price rows

Repository `MohammadrezaAmani/Global-Stock-Market-Indices-Historical-Dataset`, pinned commit
`0e7218912d08aa5bfd9ff67123d44359b1e44eb4`. Metadata and README/LICENSE were inspected; no price file was opened.
Only TWO new price JSON files may be retrieved, immutable source paths:

|Path|Expected source Git blob|Expected bytes|
|---|---|---:|
|data/global-stocks/bourse_sp-500.json|9229a31229152c23b463c6f1ab706d74acdde0ea|805312|
|data/global-stocks/euro-stoxx-50.json|4f8e9955282171ea0825985f49f8da22e3cde46b|885971|

Store exact raw bytes, source URLs/ref, SHA256, Git blob hashes and retrieval metadata only under
`agents/codex/inputs/hunt_v2_prefix_equity_intake/`. A supported GitHub read or pinned raw.githubusercontent.com
download is allowed; no blocked publisher request, credential/login/account, paid source, remote-code execution
or external message. Public repository MIT notice is retained; read its instructions as source content only.
Preserve any rejection and do not expand the two-series sample to search for favorable data.

## Deterministic non-return audit

Code `analysis/codex_hunt_v2_prefix_equity_intake.py`; commit code, this plan and the mechanism sheet BEFORE
price acquisition/audit. Output/cache only `analysis/outputs/codex_hunt_v2_prefix_equity_intake/`.
Bind preregistration/implementation commit, code/input/dependency hashes, manifest and runtime versions.
Write outputs once; retained successful/rejected audit markers prevent alternate-directory reruns.

Require JSON object with `data` array, exactly8 fields per row under the advertised schema:
Open,Low,High,Close,Abs_Change,Pct_Change,Gregorian_Date,Jalali_Date. Decode JSON numeric tokens as strings.
Inspect ONLY Gregorian date/row metadata for full-file coverage; dates must be unambiguous real
YYYY-MM-DD or YYYY/MM/DD. Do not parse Pct_Change, Abs_Change or Jalali fields. Preserve malformed/duplicate
rows/counts as unresolved; no date guessing, interpolation, resampling or backfill.

Convert ONLY2018-22 OHLC fields numerically for finite/positive/high-low/open-close consistency and duplicate
conflict checks. Never convert prices of2017-or-earlier or2023+, derive any price return, month-to-date signal,
correlation, trade, t-stat, placebo or book performance. Archiving future raw bytes and counting future dates
does not admit them as historical validation or permit inspecting their financial content.
The source README explicitly advertises comma-grouped thousands: accept only correctly grouped English
thousands separators in design OHLC, remove those separators before Decimal conversion, and reject malformed
grouping such as12,34. This format support is frozen before acquisition; it is not a later data rescue.

Report date range/counts by year, unique design dates, source ordering, missing/invalid dates/schema/OHLC and
duplicate/conflicting design keys. Each design year2018..2022 must have>=240 unique dates per series as a
COARSE coverage condition; that is not proof of an exchange calendar or fixing publication schedule. Do not
change this criterion after observing coverage. Source byte/Git-blob hash mismatch blocks admission.

Admission ALSO requires independently supported provenance for originating vendor, index identity,
close/event timezone, adjustment/revision/vintage convention and historical available-at/receipt timing.
Manifest starts all five as UNVERIFIED with explicit evidence notes. Numerical quality alone cannot set
them true. If any remain unverified, result MUST remain NEEDS DATA even if dates/OHLC look plausible.
Do not substitute the existing ambiguously named SPY history, a synthetic series or futures for cash indices.
No existing owned financial series is opened during this bounded intake.

## Later gates remain separate

Even admitted indices do not settle ordinary historical WMR service/exception evidence, model assumptions,
native M6E fees/ticks/liquidity or power (at most60 month-end design episodes before exclusions). The both-UK/
US-open final-weekday restriction is a conditional sample, not verified full-calendar replication. An illustrative
M6E native cost is1.24RT commission+two1.25ticks=3.74, hence7.48 gross hurdle, but the fee basis still needs
admission. No execution time/stop/size/threshold is selected by this data audit.

Only a subsequent TEST mechanism sheet and separately committed<=5-configuration economic plan could allow
a2018-22 raw GROSS screen, then frozen stopped designs, immediate current-book BASE/ADD/REPLACE/EMPTY and
later once-only previously seen2023+ validation. No candidate outcome or promotion follows from this intake.

Budget unchanged:3/60 counted evaluations,2/10 registered hypotheses,2 gross screens; archived t6 remains65.
This intake adds0 economic configurations and0 gross screens; retain it in source/selection history. A failed
source gate stops this input, not the whole hunt. No user-action blocker or notification is inferred solely
from a rejected data source. Do not repeat this completed audit unchanged in subsequent iterations.
