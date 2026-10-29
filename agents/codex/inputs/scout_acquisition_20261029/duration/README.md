# Partial Treasury duration data acquisition

Actual numerical facts acquired on2026-10-29 through the connected public PDF reader, then transcribed into
structured inputs. These files are **partial source data**, not a complete point-in-time history or TEST admission.

- `provider_forecasts.csv`: four actual provider forecast-table rows; three are in2018–22 and one is April2023.
- `institutional_quotes.csv`: three explicitly separated IMF quotations/references. April2020 was reported on
  May1 and August2020 is referenced only in the November30 issue; neither is an eligible pre-event forecast.
- `observations.json`: canonical transcribed values, named sources/pages, version/as-of context and limitations.
- `coverage_2018_2022.csv`: all60 calendar-month slots, with missing data visibly empty rather than imputed.
- `manifest.json`: validator output, counts, file/source-code hashes and zero-return record.
- `search_receipts.json`: actual queries, source reader access and excluded/inaccessible routes.

`reported_change_years` is a duration change in years, not a price return. Source types and `data_kind` must be
retained; institutional quotes cannot be silently promoted to original provider forecasts. All `available_at`
and original publication clocks remain blank, with `point_in_time_eligible=False`. As-of dates, dated covers,
PDF URLs and a market-table update clock do not independently establish when an investor could receive the forecast.

Reproduce and validate from repository root:

    /workspace/venvs/thebeginning/bin/python analysis/codex_acquire_duration_free_data.py

The script checks unique IDs, dates, units, original-table arithmetic, explicit unknown clocks and source separation,
then writes the CSVs/manifests. This verifies transcription consistency, not the truth of the sources or their
economic predictability. No numeric price input, return, strategy selection or backtest is computed.

Only numeric facts and our own annotations are retained. The source PDFs and their copyrighted prose are not
redistributed; no PDF-byte hash is claimed. Links point to the publicly read originals/mirrors. The SSRN7601879
manuscript remains unobtained and no entry/exit rule has been recovered from these provider reports.
