# H07 source-only LDF / owned-RS interface

No actual RS Date/Time/Price/exit/P&L cell values, native marks or new returns were read for this note.
The workbook was inspected only as opaque bytes, header labels, XML cell/style attributes, merge
coordinates and Settings column-A key labels. Settings column-B values remain unread until a committed
source admission. No H01/H04 maker or outcome reconstruction was run; those studies stay closed.

## Immutable parent interface

`analysis/outputs/codex_hunt_v2_ldf_delta/gross_events.csv` has no explicit event ID. The zero-based
original row position is the canonical `event_id` assigned by the committed H01 design; retain its
CSV record ID too. Before outcomes select only date/year/side, decision_j840, entry_label_j841,
exit_label_j870, atr/day_move, immutable entry_open and ATR reference metadata. Never select the
OF masks, exit_close, gross or net columns during H07 source/support admission.

The existing `design_BASE_trades.csv` contains event_id, day, entry_j/exit_j, entry/exit, side/kind,
stop_points, ATR, native gross/commission/slippage/net and the unchanged protected BASE positions.
It is an immutable later economic reference, not a source of the new gate. Reuse its masks after
support/gross gates; do not execute H01 again or nominate LEGACY/STRICT30. Stop remains0.25ATR rounded
up0.25point, entry protection active, no target, C870 time exit. Masking a consumed BASE ticket cannot
free another LDF entry. The new native marks are only C840 and O541 from the exact H01-bound2018–22
day/night files, selected by parent date/key before value conversion.

## Exact RS workbook metadata

Path: `mc_reports/Backtesting Strategy Performance Report _ @NQ - 1 Minute Relative Strength.xlsx`.
Size7,354,434bytes; SHA256`6cc3bedab9b44a0598339c177eaa2933bf0c0e01de29af1fe3a6b4f1ade69977`.
List of Trades is `xl/worksheets/sheet3.xml`, header row3; Excel1900 date system (`date1904=false`).

|Column|Header|Observed metadata, not values|
|---|---|---|
|A|Trade #|Explicit two-row merges, e.g.A4:A5; use the declared top-cell identity only within its merge|
|B|Order #|Physical cell exists on both rows; retain as metadata, no clock inferred from its number|
|C/D|Type / Signal|Event and source-order identity fields|
|E|Date|Numeric XML type n, style7, builtin numFmt14 `mm-dd-yy`|
|F|Time|Numeric XML type n, style8, builtin numFmt21 `h:mm:ss`|
|G/H|Price / Contracts|Entry price and position-quantity metadata only as separately authorized|
|I:P|Profit/cumulative/run-up/drawdown|Outside H07 source/feature input; never interpret these cells|

The physical schema has2,408 Date/Time cells and1,204 Trade# top cells; these are XML cell counts,
not an independently validated trade sample. Missing exit Trade# cells follow declared merge ranges,
not permission for arbitrary forward-fill. Settings is sheet8. Column-A schema includes Symbol Name,
Compression, Start Date, End Date, TradeDir, NumContracts, DecideHHMM, FlatHHMM, RTH bounds and the
remaining RS parameters. Their actual values and claimed coverage must pass before absent rows can
be called FLAT. No independent completeness or actual live-position claim follows from the filename.

## Frozen codec and causal interpretation

Format21 is a nonelapsed time-of-day display, unlike `[h]:mm:ss`. Excel serials can contain an integer
day plus fraction. The installed openpyxl3.1.5 conversion source uses divmod(serial,1); its millisecond
rounding is not the proposed strict H07 codec. Use Decimal for raw Date/Time strings, keep integer
parts, require a nonzero Time integer part to match Date's integer part, and compare any nonzero Date
fraction with Time's fraction. A date-only zero fraction is not an asserted midnight clock. Require
minute resolution within the prebound1e-4second tolerance; no timestamp offset or string-format search.
The source of this finite codec is the exact workbook's style metadata, not a search for profitable
entry matches. It neither reruns nor clears H04's failed raw-spec/source study.

Filter2018–22 by Date's day before Time, Type/Signal, entry Price, Contracts or event-ID conversion.
Never access exit Price or realized results. Global malformed/duplicate/pair/order/overlap faults block
the entire source before features. After that source gate, only the as-of event prefix through C840
can affect state. Boundary840 is UNKNOWN KEEP; future exits cannot turn an earlier state unknown or
change a mask. Exact native basis comparison is MC entry against O541, with no nearby-minute search.
Zero gross mark keeps; missing/mismatched required basis keeps unknown and remains in support counts.

The primary equals same-side-open overlap AND an adverse C840-versus-O541 sign on exact-basis rows.
The unselectable overlap and all-parent PRICE_0901 controls plus the two frozen conditional nulls are
therefore essential. Root owns all gates, support counts, later economic accounting and selection.
This note adds0hypotheses,0gross screens and0economic evaluations; no actual feature mask is computed.
