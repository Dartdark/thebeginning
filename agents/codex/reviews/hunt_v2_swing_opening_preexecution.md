# H03 ST opening-flow gate: source PASS before data

Independent source/synthetic preexecution review,2026-10-26. This is **not** a promotion checker, raw-data
rebuild, stopped-strategy review or financial result. No native prices, classified-flow rows, MC trade-list
body, prior economic outputs, new signals or return outcomes were opened. Only this review file was written.

Reviewed AGENTS/BUILDER_BRIEF/RESEARCH_CONTROLS, TEST-for-preregistration evidence, H03 plan, archived literal
STv3 source/manifest, gross implementation and its pure/shared dependencies. Parent source is7f0800f,
SHA25688689848107edfc2cd4f704b0b5f9030b7695a92dcade38ec112f3b2f8509377; its archival copy is not a new PL draft.
Initial preregistration is e533b60. Root must commit the final pre-data clarifications and implementation
and use that effective commit for byte-bound plan/evidence/source verification before authorizing data.

Final reviewed code: `analysis/codex_hunt_v2_swing_opening_gross.py`.
SHA-256: `ab2efb88a1b492eacf01cec032b57f2a27aa1fde166dfee9d1cb5d8ac8377a56`.

## Source issues resolved before outcomes

- MC entry metadata now rejects duplicate eligible design dates and invalid/ambiguous entry metadata even
  when matching fractions would otherwise pass. Retained source row IDs identify matches, unmatched rows,
  invalid rows and date-only calendar/warmup exclusions. Equivalent serialized integer sides1/-1 and1.0/-1.0
  (additional trailing zeros only) canonicalize to the same sign; non-integer values are rejected.
- Literal trading-day skips do not prove an actual shortened reference session. Known-short coverage uses
  shared early/holiday status only, not a normal Dec31 or weekend. Normal sessions need390 contiguous bars;
  weekend references remain unresolved. Literal DH/DL storage itself is preserved.
- The nineteenth-to-twentieth store becoming known through a pre08:31 backstop is recognized before entry;
  a missing current08:31 remains an unresolved prefix, not silently lost warmup. Discarded unexplained
  normal-session references retain the frozen20-actual-store lineage fault, without inserting/reordering
  history. Invalid protective geometry is separately flagged.
- Positive total classified quantity means a positive AGGREGATE15-minute tape, with finite nonnegative
  quantities each minute. Valid zero-quantity minutes are observed. Observed P/D zero is known-neutral KEEP;
  invalid/missing/unmatched or aggregate-zero data is UNKNOWN KEEP. These definitions were clarified before data.
- Entry extraction and MC ENTRY audit now precede raw endpoint/return attachment. A failed MC audit cannot
  access the raw exit window through that path: it saves a retained PRE_GROSS rejection with zero raw screens,
  zero economic evaluations and a completed marker. Both pre-gross and gross markers prevent reruns.

## Literal parent and causal entry checks

Shared Grid24 is storage only. Parent references use the latest20 actually STORED RTH ranges and latest2
stored extrema, not ATR, true range or normal-calendar replacement slots. Literal v3 at15:00 storage,
new-date pre08:31 partial backstop,08:31 overwrite and later-start mixed-state behavior are preserved/audited.
Feature values are captured before today's session can enter its own reference history. Normal-reference
completeness is390 native minutes08:31..15:00; known-short contiguous extents are recorded. Mixed/internal-gap/
missing-normal-end/lineage faults remain on events and veto gross admission rather than being repaired.

The union of literal v3 holiday rules and shared known holidays/early closes applies before entry. Good Friday
and national mourning additions are disclosed replay-versus-published differences. No `g.trading`, `last_j`,
current final-session membership, missing-bar jump or final-bar fallback gates earlier entries.

At08:31, open/high/low must be inclusively inside prior levels. A strict breach through08:45 disarms; touching
alone does not. Paired stop orders issued08:45..14:29 can first fill native labels08:46..14:30 (j526..870).
Opening gaps receive the worse native open. Both-level minutes use the shared nearer-extreme convention,
ties high first, with ambiguity retained. Exactly one parent entry/day means a wholesale removed day cannot
free capacity for a different later ticket. No protection, target, BE or stopped P&L engine is imported/called.

## Feature, MC-entry and raw gate checks

The feature is exactly15 completed native-equivalent minutes511..525. OF ET labels map CT by minus60minutes,
with shared US DST dates. Native/source OHLCV, volume==upvol, nonnegative classified quantities, buy+sell==
native volume and close difference<=.25 are checked before known classification. DROP only strict P*D<0;
zero and unknown states KEEP under the definitions above. It does not cancel one side or resize tickets.

Information fields name the08:45 close event/availability/decision under an explicit zero receipt-delay
idealization, and bound the first possible native fill interval. This is not verified receipt or micro fills.
MC parsing selects ONLY date/side/entry/t_in strings. Date is parsed first, then only eligible2018–22 entry
metadata is converted. Future financial fields and MC exit/kind/gross/net columns are not loaded/interpreted.
Strict CT time/ISO-date+time syntax and row-date identity are enforced, with no timezone/date guessing.
One-to-one date/side/entry<=.25 and entry-label<=1minute matches must satisfy BOTH>=90% fractions plus metadata
PASS. Calendar exclusions are date-only records, not hidden entry/return selection.

Only after MC ENTRY PASS does the raw helper attach native OPEN900 (15:00 close label,14:59 wall) as exit,
with NO stop/target/BE/fees/slippage. Coverage is entry..899 plus positive finiteO900; later exit-minute HLCV
does not veto an already liquidated position. Every unresolved endpoint/path, otherwise-eligible prefix and
used reference remains visible and fails the conjunction. Raw BASE/KEPT/REMOVED all/year/side summaries retain
totals, means,t,SD,SE and counts. Gate requires>=100kept, mean>=$4.48/MNQ, strictly>90%known-flow coverage,
complete relevant paths/references/prefixes, finite endpoints and MC ENTRY admission. Assumed native cost is
$1.24RT plus two$0.50 adverse-fill allowances=$2.24; the raw hurdle is2xcost, not a net significance test.

## Run boundaries and verification

Native allowlist is NQ DAY2018–22 plus the owned2017 archive for features only. OF inputs are restricted to
2018–22 annual sources. No ON or2023+ native source, old financial runner/output,2017 trade or MC exit/net
calculation is admitted. Metadata actual dates/integer clocks/years precede price parsing; duplicate conflicts
are rejected and shared-grid fields reconciled. Isolated allowed-path cache links reject unbound files.

The runner checks codex/work, exact committed plan/evidence/archive/manifest, committed HEAD implementation
and dependencies, pinned parent bytes, and existing completion markers before data. Native/OF/MC and code/
source hashes are bound and rechecked after execution. A nonblocking fixed local lock, write-once artifacts,
attempt log and final artifact-hashed pre-gross OR gross marker preserve outcomes and prevent alternate-path
retries. All runtime writes/cache remain under the allowed H03 output prefix.

Final source passed19 grouped synthetic checks with `/workspace/venvs/thebeginning/bin/python -B`, calling
ONLY `synthetic_checks()` in memory, without a financial phase or output write. Checks include literal history,
last-entry boundary, worse gaps/ties, scan/held gaps, zero/unknown flow, neutral/zero-minute handling, missing-start
backstop, reference classification/lineage, MC metadata/IDs/future poison, and a poison attachment proving
failed MC entry parity cannot call raw-return attachment. Python3.12.14, NumPy2.3.5,pandas2.2.3.

## Decision and limits

**SOURCE PASS for the final frozen pre-gross-entry/raw-gross implementation only**, after root commits the
reviewed hash/effective registration before data. No fatal source mismatch remains in that scope. A changed
hash requires reconciliation. Actual data quality, entry parity, raw effect and conditional costs remain
unobserved by this reviewer. No stopped returns, book improvements, placebos, dependence check, MC execution
parity or promotion is attested. The final plan has five potential configurations: three nominal only after
gross PASS, two delayed only after nominal design+immediate bench PASS; PRICE_UP/DOWN and delayed raw screens
are not authorized. Budget/progress were not modified by this review. No strategy/PL/live permission follows.
