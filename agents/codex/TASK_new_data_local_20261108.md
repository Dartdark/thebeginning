# Local task: acquire free primary research data

Summary: The cloud acquired six commodity leveraged-fund histories and three Cboe indices as public secondary copies.
Direct primary downloads were blocked by cloud networking. Acquire the originals locally, reconcile the archive,
repair BOIL precision if the originals permit, and save new scheduled-flow/funding data. No returns or live changes.

## Scope and branch

Read `AGENTS.md`, `agents/codex/BUILDER_BRIEF.md` and
`agents/codex/inputs/new_data_20261108/README.md`. Fetch and normally merge `origin/codex/work`; preserve uncommitted
and existing research. Work/commit/push only on `codex/work`. Use configured Python; the downloader uses only the standard
library. No paid access, purchases, account activation, credentials, live/VPS/broker files or external messages.
No duplicate automation, scout cycle, trial reservation or strategy backtest in this acquisition task.

## Run the existing downloader

From the repo root, choose a fresh dated destination (substitute another suffix if it exists):

```bash
python analysis/codex_new_data_20261108.py fetch-primary --only funds,fund_documents,indices --output scratch_data/new_data_primary_local_01
python analysis/codex_new_data_20261108.py fetch-primary --only fed_documents,fed_operations,funding,buybacks --output scratch_data/new_data_macro_local_01
```

The CLI refuses an existing output directory, saves raw bytes/headers/hashes/receipts, follows Fiscal Data page counts,
rejects HTML in place of data, and returns a nonzero exit code if any job fails. **Inspect the receipt after failure;
successful independent downloads remain saved.** A downloaded JSON body is not proof of complete historical coverage.
All exact URLs and dates are in `agents/codex/inputs/new_data_20261108/primary_sources.json`.
Use normal official downloads; respect restrictions. If a site still fails, save the failure and move on.

## Priority 1 — commodity funds, especially gold

Official source: <https://www.proshares.com/our-etfs/leveraged-and-inverse/ugl> and the equivalent fund page for
GLL, UCO, SCO, BOIL and KOLD. The NAV History links point to
`https://accounts.profunds.com/etfdata/ByFund/<TICKER>-historical_nav.csv`.

Acquire full launch-to-current NAV files, current `<TICKER>-psdlyhld.csv`, `etf_splits.csv` and current fund pages.
Retain original Date, NAV, Prior NAV, NAV change, **Shares Outstanding (000) with its full decimal precision**, AUM,
download receipt/headers and source URLs. Parse the original headers, not the secondary archive's normalized schema.
Reconcile all overlapping dates and numeric fields to the six secondary histories. Preserve split basis and units;
report revisions/truncation rather than overwriting either version. Compare asset identity before/after conversions.

**Known issue:** BOIL has 1,178 mismatches above 1%, including 40 in 2018–22, and 82 zero-share rows in the secondary copy.
Its collector rounds shares to a whole share. Restore only what the original sponsor precision supports; do not reconstruct
shares with AUM/NAV. Five other funds passed this simple identity, not primary authentication or historical clock gates.
The existing intake has no duplicate dates and 1,259 shared 2018–22 rows per fund.

Save dated current snapshots now. Historical original publication/revision clocks, creations/redemptions offset,
mandate changes, actual benchmark contracts/roll weights and reset/NAV times remain separate gates. Read dated prospectuses
or sponsor notices where freely available; save links and source documents. Current holdings must never be projected
back into 2018–22. A successful download does not admit an exact historical reset-pressure signal.

## Priority 2 — original Cboe risk-state histories

Download VVIX, SKEW, VIX9D, **GVZ and OVX** from the manifest's official
`https://cdn.cboe.com/api/global/us_indices/daily_prices/<INDEX>_History.csv` links.
Compare the first three with the saved secondary closes on all overlapping dates; extend through latest available.
Retain unfilled missing dates, methodology changes and prelaunch/back-calculated flags. Specifically verify whether
SKEW 2018-12-03 and 2019-07-05 exist in the primary history. Source cache VVIX/SKEW OHLC columns are synthetic copies
of close; do not preserve those as real intraday information. Current revised daily histories do not resolve original
same-day publication times. No dealer-gamma or signed option-position claim follows.

## Priority 3 — scheduled Treasury flow and funding

- NYFed: <https://markets.newyorkfed.org/static/docs/markets-api.html> and YAML specification in the manifest.
  Download annual 2017–2026 Treasury-operation result details and reference rates. The included endpoint patterns
  are corroborated by a public client; **verify them against the primary spec**, including historical query limits,
  pagination and event-count completeness. End 2026 at 2026-11-08, then record any newer acquisition separately.
  Preserve rate type/effective date/rate/percentiles/volume/revision flags. SOFR live begins in 2018; don't invent 2017 SOFR.
  Results are post-operation outcomes; obtain original dated operation announcements/schedules and changes separately
  wherever the official site provides them. Save announcement, start, end, result and settlement clocks separately.
- Treasury buybacks: <https://treasurydirect.gov/auctions/buy-backs/>; Fiscal Data `buybacks_operations` and
  `buybacks_security_details` are separate paginated tables. Keep operation ID/date, bucket, type, announced cap,
  start/end/settlement times, CUSIPs, coupon/maturity, offered/accepted amount, accepted price, plus announcement/result
  links and any special notices. Follow the official links to save the relevant XML/PDF announcements/results,
  tentative schedules and the XML schema/change notice. The downloader saves the two data tables, **not these linked
  documents**. Filename GMT/start time is not the announcement publication time. Verify the historical ET offset.
  Regular modern buybacks begin 2024; any small historical test operations are separate. No 2018–22 regular-program
  design sample exists, and results must not be treated as pre-operation forecasts.

## Finish

Write a five-line-Summary acquisition/reconciliation report with actual coverage/counts, changes versus secondary,
BOIL disposition, missing fields/clocks, exact errors and what becomes feasible. Save normalized files separately,
leaving `available_at` unknown until supported. Transfer raw data (gzip if large), original+compressed byte counts/SHA256,
source/receipt manifest and audit script/report under a new `agents/codex/inputs/` folder; do not commit local credentials.
Update `agents/codex/DATA_NEEDED.md` without deleting past failures or reviving rejected strategies.
Commit/push `codex/work` and show the key results in chat. The source/clock gate and any later preregistration remain
separate; this task itself does not authorize a new strategy test or a portfolio change.
