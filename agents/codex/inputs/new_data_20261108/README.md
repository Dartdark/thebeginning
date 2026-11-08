# Free research-data intake — 2026-11-08

Status: **secondary copies acquired; primary-source comparison and historical information clocks pending**.
No signal, strategy returns or portfolio test was computed. Preserve the owned histories elsewhere in the repo.

- `secondary_sources.json`: exact public GitHub URLs, pinned source revisions, byte counts and original Git blob IDs.
- `raw/daggerok/`: six ProShares commodity funds, all history pages, current holdings/metadata, source README,
  license and the source collector **as text for provenance inspection**. The collector was not executed or installed.
- `raw/gianni04/`: three cached Cboe index series plus README, license and the cache/fetch module as text.
- `audit/normalized/`: six date/NAV/shares/assets CSVs and three date/close CSVs. No fill, rounding repair,
  historical reweighting or inferred publication timestamp. `available_at` is deliberately blank.
- `audit/quarantine/BOIL_flagged_rows.csv`: 1,178 rows fail the 1% NAV × shares/assets check; 82 contain zero
  shares. These rows include 40 in 2018–22. **The BOIL history is quarantined as a dataset**, including its normalized
  copy. Never infer missing shares from assets/NAV and call the result an observed creation/redemption history.
- `audit/source_checksums.json`: all 49 original files verified against their expected Git blob ID/size and SHA256.
- `audit/qa_summary.json`: coverage, pagination, dates, basic identities and gaps. These are QA results, not input admission.
- `primary_sources.json`: 47 explicitly scoped primary download jobs for a local computer.
- `initial_primary_probe.json` and `primary_probe/acquisition_receipt.json`: 18 actual failed cloud requests in total;
  each failed with `Tunnel connection failed: 403 Forbidden`. No primary data payload was acquired.

The ProShares secondary parser rounds `Shares Outstanding (000) × 1000` to a whole share
(`raw/daggerok/scripts/update-data.ts`, `parseNavHistoryAll`). That loses precision for split-restated small counts;
BOIL's historical zeros/mismatches require the original sponsor CSV. No conclusion about sponsor data quality follows.
Even where the identity passes, reconcile the original file and historical adjustment basis before using share changes.
The archive's README statements about splits/publication are source claims, not independent timing certification.

VVIX/SKEW source OHLC columns repeat the daily close and their volume is a placeholder. The normalized files retain
**daily close only for all three indices**. Do not use these caches for intraday bars, spreads, fills, dealer positions,
or option surfaces. SKEW is missing 2018-12-03 and 2019-07-05 relative to the shared fund-date calendar; neither date is
filled. That comparison is not an independently certified exchange calendar. VIX9D's prelaunch values are back-calculated;
the 2011 warm-up is not a contemporaneously observed trading signal. Exact release clocks remain unresolved.

Current holdings dated 2026-11-06 are a single snapshot. Current UGL/GLL benchmark is the Bloomberg Gold Subindex;
UCO/SCO use the Bloomberg Commodity Balanced WTI Crude Oil Index; BOIL/KOLD use the Bloomberg Natural Gas Subindex.
Do not map a current futures/swap snapshot backwards or treat a continuous front-month contract as those benchmarks.
Fund inflows/redemptions, swaps, roll weights and changed mandates can alter the exposure adjustment.

The source repositories carry MIT licenses (retained here). Their code license does not establish unrestricted
redistribution rights to the underlying publisher's market data. Keep this research archive/provenance intact.

Reproduce the offline checks into a **new** output directory:

```bash
python analysis/codex_new_data_20261108.py audit --output scratch_data/new_data_audit_check
```

Reacquire pinned public secondary bytes (normal public HTTPS only; stops on blob mismatch):

```bash
python analysis/codex_new_data_20261108.py fetch-secondary --output scratch_data/new_data_secondary_copy
```

For primary originals, follow [`TASK_new_data_local_20261108.md`](../../TASK_new_data_local_20261108.md).
This is an acquisition task, not a new strategy trial, scout run, trading-plan change or background schedule.
