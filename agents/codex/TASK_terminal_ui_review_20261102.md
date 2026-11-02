# Claude review: research overview and strategy results

User request: build the proposed terminal improvements and make both reviewable for Claude.
Branch to read: **codex/work**. Base before this change: `e9022dae0e2b3211549714a0420da7f5238950d2`.
Review pending; the maker's checks are not independent verification. No external message was sent.

Read [report](results/terminal_ui_review_20261102.md), [design contract](terminal/DESIGN.md),
[product context](terminal/PRODUCT.md) and [local instructions](terminal/AGENTS.md).
Use the commit containing this task as the review head. Compare only the listed terminal/review paths to the base;
preserve later concurrent research and do not operate live software.

## Priority 1 — economic meaning and truthful status

1. Compare `terminal/result_sets.json` with `results/primesync_accounts.md` and the actual three CSVs in
   `analysis/outputs/codex_primesync_accounts/`. Check all four contexts and BASE/ADD/REPLACE/EMPTY for personal,
   50K/150K funded and evaluations, including both evaluation cohorts. Column mappings must not be inferred from names.
2. Check costs, native micro size, dates, archived 19-piece baseline, p95 drawdown/capital interpretation, cumulative
   two-year payout and failure-rate units. The UI must not call this a rerun against current portfolios or a forecast.
3. Confirm missing, failed and ambiguous rows stay unknown; duplicates must not choose a favorable row or silently
   become zero. The display must preserve the rejected placement decision and outstanding MC/independent checks.
4. Audit `desk.py` and `static/desk.js`: file presence is not gate acceptance; absent stages remain unknown. Overview
   budget numbers come only from saved scout progress and do not reset earlier trial history. “Ready” is not running.
5. Confirm no return execution, budget/lease writes, allocation changes, broker/VPS access or new arbitrary runner.

## Priority 2 — implementation and regression

- Run the README checks: 48 Python tests, three JavaScript data-presentation tests and browser acceptance if supported.
- Inspect HTTP origin/Host rules, CSP and document/result allowlists. Injected record strings must remain escaped.
- Inspect out-of-order request handling, leaving/re-entering results, error retry and skip-link route preservation.
- Test all existing views, reader Escape/keyboard, raw CSV filtering/export, notes and PDF intake with temporary runtime data.
  Do not overwrite real notes or upload test PDFs to the user's runtime. Tests already isolate these stores.
- Examine registry validation and unusual/corrupt local JSON. Flag any unsupported schemas admitted as this CSV format.

## Priority 3 — visual/usability

- Compare [before overview](terminal/review/20261102/overview-before.png) and
  [after overview](terminal/review/20261102/overview-desktop.png).
- Compare [before results](terminal/review/20261102/results-before.png) and
  [after results](terminal/review/20261102/results-desktop.png).
- Inspect mobile screenshots and actual keyboard/scroll behavior. No page overflow at 360/390/768px; tables may scroll
  within a labeled region. Screen-reader and physical touch-device acceptance remain unverified.
- Check clarity of source claims vs our outcomes, 12px minimum supporting copy on new pages, readable contrast,
  meaningful focus, input labels and visible original artifacts. Impeccable's binary/detector/hooks were not installed/run.

## Evidence and requested verdict

[Browser receipt](terminal/review/20261102/receipt.json): 583 assertions, 432 financial cells, zero page errors,
Chromium154; code/input/screenshot hashes, before/after images and limits retained.
Reproduction commands and launch steps are in [README](terminal/README.md).
Write a severity-ranked PASS / PASS WITH CONCERNS / FAIL review, with file/line findings and what you actually ran.
Review the UI and attribution; do not imply a new independent economic replication from these presentation checks.
Return it to the user for the decision. No live deployment or strategy allocation is authorized by this task.
