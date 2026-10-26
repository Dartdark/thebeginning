# H03 MC clock codec and retained source-quality review

2026-10-26. Scope: source code/provenance plus the explicitly authorized SAVED entry/reference/calendar
audits only. No raw native/OF file, grid, liquidation endpoint, stopped engine, MC exit/net field, gross return
or economic output was opened/calculated. Only this review file was written. Original16ed951 code and
`pre_gross_verified_execution.json` remain intact. H03 stays CLOSED; this does not authorize a financial retry.

## Codec diagnosis

The original parser admitted colon clocks or ISO-date+colon-clock and rejected integer HHMM strings.
Root's restricted metadata examples were t_in848,1145,900. These are consistent with08:48,11:45,09:00
under the repository's independent export convention, rather than elapsed-minute encodings.
There is no reason to report zero original parser matches as an economic/raw-spec replication failure.
It is a clock serialization failure before that comparison could be interpreted.

Independent SOURCE support at pinned7f0800f:

- `checks/candidates/fc_2b/mc_to_trades.py:10` is a generic MC List-of-Trades→checker-CSV exporter. It constructs
  `t_in` using `pd.to_datetime(e["Date"]).dt.strftime("%H%M").astype(int)`. This explicitly produces integer HHMM.
- `analysis/grid24.py:jof` documents and converts HHMM to native minute column with hour*60+minute.
- `analysis/portfolio.py:45` converts MC entry timestamps through `et.dt.hour*100+et.dt.minute`, then jof.
  These conventions were inspected as source only; neither importer/exporter was run.
- `checks/candidates/swing_target/mc_trades_v3.csv` was introduced at9f73273 together with the MCv3 workbook.
  The retained afde088 manifest pins that CSV's Git blob99f2ecd2be24d8f5523c1deb31d9a0638f036de6 and
  SHA256ee4776e1fe7abc32ff42074579836bfe42301b24e986cf7f85f1e9231f75eb34.

The scoped source/history search did **not** recover a dedicated STv3 converter invocation. Therefore the
diagnosis has independent repository-convention and observed metadata support, but the exact producer chain
is not fully recovered. Do not call it certified ST-specific conversion provenance or infer chart timezone
from favorable matching. No arbitrary offset, minute-label shift, rounding or tolerance search is justified.

A separately committed, entry-metadata-only diagnostic may interpret strict3/4ASCII-digit HHMM with valid
hour/minute bounds and compare SAVED parent entries to the same design MC entry fields. Keep the original
±.25point/±1minute/both90% thresholds and duplicate/ambiguity gates. Exclude2023+ before entry/time conversion,
retain calendar differences and source IDs, and read no native source, raw exit, stopped result or MC net.
Such a diagnostic corrects reporting; it cannot reopen the rejected financial phase or count as a gross screen.

## Independent reconciliation of retained quality flags

The three reviewed artifacts' SHA256 values match their original16ed951 pre-gross marker:
`parent_entries.csv`, `gross_stored_reference_audit.csv`, `gross_calendar_audit.csv`.
That marker records phase pre_gross and raw_returns_calculated=false.

Restricted columns read: entry date/ID, stored-reference IDs/dates, unresolved/geometry/lineage flags;
reference coverage/status/counts; and calendar/prefix status. Entry/reference prices and OHLC ranges were
not needed or read. The331 parent entries include34 distinct entries flagged reference-unresolved.
Every one reconciles exactly to at least one incomplete stored reference among the20 IDs it used.
None of these34 flags depends on the lineage or protective-geometry supplements. There are12 incomplete
stored references overall;11 are used by those34 entries, with overlapping exposures.

|Used reference date|Normal/known-short|Valid bars|Expected under frozen policy|Missing/invalid|
|---|---|---:|---:|---:|
|2018-04-30|Normal|389|390|1|
|2018-07-26|Normal|388|390|2|
|2018-08-28|Normal|386|390|4|
|2019-12-05|Normal|388|390|2|
|2020-01-20|Known short|209|210 contiguous511..720|1|
|2020-03-09|Normal|376|390|14|
|2020-03-12|Normal|377|390|13|
|2020-03-16|Normal|376|390|14|
|2020-03-18|Normal|377|390|13|
|2021-09-17|Normal|389|390|1|
|2022-03-08|Normal|388|390|2|

These are genuine FAILS of the frozen completeness definition. They do **not** by themselves prove
corrupted data or a defective feed. In particular, the March2020 dates/counts are consistent with known
market-wide circuit-breaker episodes; this restricted audit does not independently certify each missing
minute's cause. A legitimate exchange halt also violates the registered uninterrupted390-bar requirement.
Do not fabricate prints, backfill, relax the registered policy or call a changed halt protocol an unchanged
implementation. The known-short2020-01-20 reference fails its own contiguous-prefix policy, not a demand
for closed-market afternoon bars.

The five otherwise-eligible prefix failures also reconcile to the retained calendar:

|Date|Recorded failure|First invalid native label|
|---|---|---|
|2018-07-26|Live-order prefix|823=13:43CT|
|2020-03-16|Early prefix|512=08:32CT|
|2020-03-18|Live-order prefix|719=11:59CT|
|2020-11-30|Missing session start/no native row|No observed minute|
|2021-09-17|Early prefix|512=08:32CT|

All five are marked allowed normal-calendar days with history ready, so the plan requires unresolved-prefix
vetoes. They are not warmup or preknown closed-day skips. Their actual market/data causes remain unverified
within this saved-audit scope. No missing entry or potential outcome was guessed.

## Verdict

**Clock parser limitation confirmed; financial rejection remains.** Correcting the metadata codec may change
reported MC entry matches, but34 affected-reference events and five prefix failures independently violate
the frozen admission policy. No gross endpoint/return, stopped design, historical validation or book bench
is warranted for closed H03. Any future halt-aware or repaired-source hypothesis would require a distinctly
justified source/mechanism decision and new pre-data registration; this review supplies no permission to
rescue this family. Budget/progress and the original marker were not changed. No economic success, strategy
milestone, trading approval or external delivery claim follows from this review.
