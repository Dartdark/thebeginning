# Initial autonomous SSRN scout cycle: WATCH / metadata source leads, no return tests

Summary: Daily SSRN research scout is configured and confirmed enabled; the terminal now displays discovery and analyst records.
Three metadata leads were triaged; two warrant source follow-up, but no full paper was obtained and neither is TEST-eligible.
The concrete new clock finding is a2021 index-snapshot shift omitted by the earlier failed ZN protocol; net alpha is unverified.
43 engineering tests pass. New hypotheses0/10, economic definitions0/30, return tests0; no active lease or allocation change.

Date:2026-10-29. Work branch:codex/work. Fetched parent at cycle start:49b48b8064a57a13fd114ee9d527c69cc7c58f0a.
Operating contract: [WORKFLOW](../research/scout/WORKFLOW.md). [Progress](../research/scout/progress.json).

## Findings and four questions

| Paper / source status | What is it about? | What does it find? | Why could it make money? | Can we build on it? |
|---|---|---|---|---|
| [Buying Duration, SSRN7601879](scout_buying_duration_20261029.md), October12 2026; abstract only, PDF403 | Government-bond index-duration demand at month-end | Authors claim1.19bp versus0.07bp otherwise; not reproduced. Provider independently documents the US snapshot moving14:00→15:00CT effective2021-01-14. | Benchmark deadlines may concentrate duration purchases; net executable return is unknown. | Worth a clock-aware source/data audit. The old13:59CT exit lost$31/ZN net,t−1.4;2023+−$79.7. Preserve that failure; do not retune it. Full paper, exact clocks and as-of forecasts precede any TEST decision. |
| [Auctions, Announcements, and Abnormal Returns, SSRN5207418](scout_fx_auctions_20261029.md), March20 2026 revision; April2025 indexed first page only | Treasury auctions interacting with following-day macro-announcement FX returns | Authors claim roughly8bp foreign-currency appreciation; pooled universe, return window and net costs unreviewed. | Proposed dealer-capacity/safe-asset-demand spillover. Causation and accessible profit are unverified. | Worth source follow-up; owned6E/auction files and free Fed/BEA calendars help. Full source, historical release calendar, native contracts/rolls and source clocks remain missing. Apex15:59CT compatibility is unknown. |
| [Hedging Expiring Index Options, SSRN7330098](../research/scout/records/7330098.json), August2026 metadata only | Cash-settled SPX-option hedge unwinding before expiry | Abstract claims effects on futures returns/volatility in the last30minutes. No table/rule reviewed. | Dealer hedge liquidation is a proposed pressure channel; direction requires signed positions. | Metadata triage only. Proprietary dealer-position dependence and existing expiry/gamma families need full-source/dedup review before proposing a strategy. No TODO strategy added from this abstract alone. |

The first two are specific unverified research leads in TODO, not trading candidates or completed full-source reviews.
The dated benchmark-clock and event-classification lessons were merged into [execution reference E11](../EXECUTION_REFERENCES.md).
No material source gaps were filled with secondary recaps, revised inputs, price-spike event labels or fictitious returns.

## Access and acquisition evidence

- The actual Crossref discovery made one network request, received a proxy403, and skipped the remaining three queries.
  Connected indexed search supplied the fallback; [receipt, queries and primary URLs](../research/scout/runs/20261029_initial_access.json).
- ZN2018–22 native minute files exist and their headers/date fields were inspected; no returns were computed.
  A public March2020 provider forecast example was read, but no complete as-of forecast panel was acquired.
- Owned6E2017–26/auction files were inspected; Fed/BEA pages were readable. HKUST manuscript fetches timed out,
  BLS was inaccessible and FiscalData returned403. Exact failures/URLs are retained in the FX source report.
- Full-source review count0, new hypothesis count0, new economic definitions0. No evidence sheet reached TEST,
  so no economic preregistration, trial reservation, progress lease, historical validation or account simulation was opened.
  Earlier t6/Hunt and repository trial/selection history were preserved.

## What now runs

The native app automation **SSRN research scout**, ID6ae3863373308191b6f40c63f610a800, has daily recurrence
and was confirmed enabled by the app lookup. [Observed status receipt](../research/scout/runs/20261029_automation_status.json).
The provider did not supply a next-run timestamp. This is configuration/observation evidence, not a guarantee
of future source access, an available execution workspace, completed tests or phone notification delivery.

Scheduled Codex work performs the source/evidence/testing workflow with the user as overseer. The local terminal's
Discover button performs bounded public metadata requests only. It does not run a model or economic code.
The UI reads saved analyst JSON dispositions and four-question answers after pulling codex/work and refreshing;
there is no live synchronization. [Launch and operating notes](../terminal/README.md).

The initial budget is10 hypotheses/30 economic definitions, including controls/gross screens, max1 new hypothesis
and3 full-source reviews per cycle, max3 candidate/5 total definitions per hypothesis. An eligible test requires
committed evidence/preregistration/code/input hashes, checked-head lease and budget reservation. The admission CLI
checks artifact associations, frozen manifests and append-only counts. It does not certify source reading,
economic merit, semantic family identity, complete imported-code dependencies, remote freshness after fetch,
independent verification or later account gates. Failed design gates stop; no weakened data or cost gate is allowed.

## Engineering validation and limits

Configured Python: `/workspace/venvs/thebeginning/bin/python`.
From `agents/codex/terminal`: `python -m unittest -v test_terminal.py test_scout.py test_scout_gates.py`.
**43 tests pass**:8 local HTTP integration,12 metadata-discovery and23 synthetic artifact-admission tests.
`node --check agents/codex/terminal/static/app.js` and `git diff --check` also pass.
[Reproducible commands and actual test receipt](../research/scout/runs/20261029_engineering_checks.json).
UI VM smoke checks passed; browser visual QA was unavailable. No market return test ran.

Progress retains per-ID/revision/disposition notification keys for one combined app alert. Routine unchanged
failures are not alerts. No external messages, live strategy, allocation, trading plan, VPS, broker or key changes.

For Claude: `agents/codex/results/scout_cycle_20261029.md` plus the two linked source/evidence records.
