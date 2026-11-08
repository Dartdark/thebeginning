# Bridge gap/build follow-up: partial explanations; original roll provenance unresolved

Summary: Native source and all five 2018–22 exports remain byte-for-byte unchanged. After regular closures, the verified Bush closure and **tentative** holiday matches, 3,964 minutes remain in 1,327 unresolved segments. Another owned NQ history has positive-volume bars at 1,113 of them. Two large 2020 gaps coincide with historical vendor capture-degradation reports. No original build receipt or dated-contract roll mapping was recovered.

## Scope and reproduction

Follows [the acquisition audit](bridge_history_20261108.md). Read AGENTS.md/BUILDER_BRIEF.md and stayed on `codex/work`. Script: `analysis/codex_bridge_gap_provenance_20261108.py`. Outputs: `analysis/outputs/codex_bridge_gap_provenance_20261108/`, including `summary.json`, `classified_gap_intervals.csv`, `unresolved_runs.csv`, `off_schedule_observed.csv` and dated `source_receipts.json`.

```text
python analysis/codex_bridge_gap_provenance_20261108.py --out analysis/outputs/codex_bridge_gap_provenance_NEW_UNIQUE_FOLDER
```

Uses Python stdlib and refuses an existing output directory. Completed with source/export hash checks before/after, comparison-input hashes and Python compilation. Existing exports remain in `scratch_data/codex_bridge_20261108_01/`. No imputation, merging, strategy returns, backtests, rebuild, installer execution, authentication, API-key, broker-setting, live-chart or VPS access. The Bridge was not reopened; no vendor message or purchase was made.

## Classifying absent timestamps

Expanded the original 3,480 between-bar intervals into absent minute-close labels, clipping the initial interval to January 1, 2018. The observation envelope ends at the last 2022 bar, December 30 at 17:00 ET. This is neither an outage count nor a complete exchange calendar. Categories are mutually exclusive.

| Classification | Minute labels | Status |
|---|---:|---|
| Normal weekends | 764,400 | Regular weekly hours |
| Daily 17:01–18:00 ET maintenance | 62,640 | Regular daily hours |
| Historical 16:16–16:30 ET pause | 13,649 | CME verifies removal from June 28, 2021 |
| December 5, 2018 Bush closure | 435 | CME verified; 15 other closure labels already belong to historical pause |
| Holiday-calendar candidates | 27,136 | Tentative, not individually exchange-certified |
| Residual unresolved | **3,964** | No exact source/status reconciliation |
| Total within ledger | 872,224 | Reconciled sum |

CME's [June 2021 notice](https://www.cmegroup.com/notices/electronic-trading/2021/06/20210621.html) confirms the pause change and normal session/maintenance hours. Its [Bush announcement](https://investor.cmegroup.com/news-releases/news-release-details/cme-group-us-equity-interest-rate-markets-close-national-day) confirms the December 5 close at 08:30 CT and normal evening reopening.

Holiday screening rules are explicit in the script, including the partial Good Friday session in 2021. A [maintainer calendar implementation](https://raw.githubusercontent.com/rsheftel/pandas_market_calendars/master/pandas_market_calendars/calendars/cme.py) cross-checks that exception and the pause change, but its generic early-close rules differ from observed historical 13:15 ET closes. It was not treated as exchange authority. Full year-specific CME holiday schedules were not recovered. Thus **31,100 labels** (27,136 tentative holiday labels plus 3,964 residual labels) still lack complete direct historical-calendar/status certification.

Residual counts by calendar year: **2018: 674; 2019: 346; 2020: 2,839; 2021: 82; 2022: 23**. They form 1,327 segments; 991 are single-minute segments. A scheduled break can split one original gap into multiple residual segments.

## Material remaining gaps

Times below are ET close labels; counts exclude regular closures.

| Date and intervals | Residual minutes | Corroboration |
|---|---:|---|
| 2020-02-28, 11:00–16:15 and 16:31–17:00 | **346** | Other owned exports contain positive-volume bars for all 346. Historical vendor degradation issue includes this date. |
| 2020-06-30, 10:12–16:15, 16:31–17:00 and 18:01–20:00 | **514** | Other owned exports contain 513 positive-volume bars. Historical vendor degradation issue includes this date. |
| 2019-02-26, 19:42–22:45 | 184 | No counterpart bars. CME technical halt is a candidate; direct original CME post returned 403. Exact instrument-status boundaries unverified. |
| 2018-04-29, 18:01–18:30 | 30 | Delayed Sunday first observation; no counterpart or primary event record recovered. |
| March 2020 cluster | Various | Circuit-breaker/limit-state period; not every overnight no-print interval can be classified from bars. |

The [historical Databento issue](https://issues.databento.com/b/6vrl98vl/feature-ideas/support-downloading-of-on-demand-zip-files-for-batch-jobs-in-the-python-client) appeared in search-indexed primary-vendor content, attributed to September 14, 2023, listing degraded GLBX.MDP3 captures including February 27–28 and June 30–July 1, 2020. The direct old issue URL now returns a generic board. This is dated corroboration, not verified current fix status or precise NQ outage boundaries; its approximate June 30 capture-stop time differs from the Bridge gap start. `source_receipts.json` preserves this access limitation. The owned counterpart bars strongly support incomplete Bridge history on the two 2020 dates; they do not establish its exact failure mechanism.

The [NYSE regulatory filing](https://www.govinfo.gov/content/pkg/FR-2021-10-19/pdf/2021-22685.pdf) identifies March 9, 12, 16 and 18, 2020 market-wide halts. It does not authenticate all NQ overnight gaps. Current rules were not substituted for historical status records. Databento's [OHLCV documentation](https://databento.com/docs/schemas/ohlcv) omits records without trades, but Bridge's own no-print/correction engine policy was not recovered. Therefore absent bars cannot all be called feed failures or all be treated as no-trade minutes.

## Owned-data cross-check and one observed anomaly

Compared the ten existing `data/NQ_1min_2018.csv` through `...2022.csv` and `data/NQ_1min_ON_2018.csv` through `...2022.csv` files. `analysis/grid24.py` documents CT minute-close labels; added one hour for ET. In a deterministic sparse sample, 1,748 same-label comparisons yielded 1,703 exact OHLC matches, including 1,702 OHLCV matches. One-minute shifts yielded only 2 or 3 OHLC matches and zero OHLCV matches. This supports clock alignment without selecting on returns.

Other owned positive-volume bars exist at **1,113 of 3,964** residual timestamps. This is not an independent raw exchange feed or certified dated-contract match; common identical bars may share an upstream source. It supplies no missing aggressor split. No values were imported into Bridge history.

One existing bar falls inside the historical pause: **2018-04-10 16:16 ET**, volume 1 at 6624.00. Preserved in place and flagged separately. Raw trade/status timing is needed to distinguish a boundary print, reporting convention or error. It explains the one-minute difference from a simple absent-pause grid count.

## Original roll/build metadata search

- Inspected research-data inventory in `C:\OFB`, including hidden filename inventory while excluding credential/config contents. No raw-data directory, build receipt or mapping sidecar was recovered. No matching top-level Bridge/MatFin/OFB directory was located under AppData or ProgramData. This is a scoped search, not proof that no record exists anywhere on the computer.
- Inventoried five downloaded Bridge ZIPs: installer/manual distributions 2.9.3, 2.9.4, 2.9.5, 2.9.6 and 2.9.13. Their entries contain no data-build manifest or contract map. No installer was run. Archive/manual hashes are in `summary.json`.
- Native CSV carries no contract ID, raw symbol, adjustment flag or build ID. Bar/bin filesystem mtimes report October 13, 2026 in local host metadata; current executable reports 2.9.13. Copyable filesystem dates and present executable version do not identify the original builder.
- Original archive manual and installed manual both describe ET close bars and joining prices/features on the same contract roll. Their covers say 2.7 and 2.9.6 respectively. Neither supplies the original dated roll table. First 16 hist/depth header bytes were recorded as opaque hex; no undocumented field was presented as an engine version or mapping, and no DLL/licence check was bypassed.
- Prior UI observation identifies the current `NQ.v.0` request setting. [Databento's official definition](https://databento.com/docs/conventions/symbology) uses previous-day volume ranking, rank zero for the highest volume, and original unadjusted continuous prices. This clarifies the **symbol**, not the existing file's original request or later splice/transformation. No roll dates were inferred from price jumps.

Original dataset/schema, request parameters, dated raw-symbol/instrument-ID mapping, roll-effective clocks, adjustment/splice policy, engine/configuration and exceptional-trade/correction policy remain unverified. Free symbology resolution requires an authenticated API workflow, so it was not attempted under the no-key-access boundary. Even a current mapping response would require reconciliation to the captured build.

The smallest remaining check is a **pre-existing build receipt tied to source SHA256** `2aef36dd53848cb50f90bc7007dcae7216428a3a13f95d668713fa07cc973377`, containing those parameters and mappings, plus native trade/status evidence for listed gaps and historical CME schedules. No repeated rebuild or synthetic repair is justified by this audit. Full-session scope remains established; gap-free coverage and original roll/build provenance remain uncertified.
