# Execution analysis reference library

Summary: Retain useful execution findings from papers, code reviews and our own diagnostics in one place.
Separate source claims, synthetic mechanics and historical tests; none alone establishes live execution savings.
Consult the relevant entries when reviewing fills, slippage, order lifecycle, execution timing or replay tools.
This is a reference library, not a strategy allocation or an automatic request to rerun failed tests.

User standing instruction: 2026-10-29. Initial backfill checked against codex/work
`e170cab70191e4bec62bd1850b8ff50714be6028`: all 136 Markdown result reports were searched for
execution-reference terminology; relevant reports, the builder brief, code workflow and TIER_LIST execution rows
were inspected. This is an initial repository/chat backfill, not a claim to recover every past conversation.
Original reports remain authoritative; this index does not replace them or independently reproduce their numbers.

## Standing rule for future work

For every future paper, code upload, article, repository review or research task:
- When it yields a useful execution method, diagnostic, caution or tool, add/update an entry here even if no standalone strategy qualifies.
- Record source/review links and date, the useful lesson, evidence status, market/platform limits, prerequisites and the smallest useful next check.
- Merge duplicates, preserve negative results and update entries when later verification changes the conclusion.
- Consult relevant entries before new execution/fill work; do not turn unrelated strategy tasks into a library review.
- If a source supports both alpha and execution work, retain the execution lesson here and assess the strategy through the normal evidence/preregistration process.
- Keep execution-only references here. Use TODO's promising-strategy queue only for a specific strategy with documented merits; lack of data alone is insufficient.
- State key findings in chat and link the entry. Saving a reference does not demonstrate savings, authorize purchases or change live code.

## Reference register

### E01 — Subpenny equity trading: passive fills and price-improvement measurement

Source: Delassus and Tyč (2010), [SSRN 1651201](https://ssrn.com/abstract=1651201).
[Saved review](results/subpenny_equity_paper_review_20261029.md). Retained 2026-10-29.
- Use: distinguish spread savings from directional alpha; a price touch or a nearby trade print does not establish a passive fill or queue priority.
- Evidence: published historical equity observations, not independently reproduced. The nearest-cent proxy is not a verified contemporaneous NBBO comparison.
- Limits: equity venue/tick rules and historical access do not establish current CME behavior or a particular futures trade-through threshold.
- Next check when relevant data arrives: align actual same-contract bid/ask, order/fill times, fees and subsequent midquote markouts; passive fills additionally require queue/fill evidence.
- Status: contextual execution reference; no new strategy trial or measured ES/NQ saving.

### E02 — Equity Trading in the 21st Century: bibliographic execution reference

Source: Angel, Harris and Spatt (2010), [SSRN 1584026](https://ssrn.com/abstract=1584026);
user-uploaded PDF and review in this chat, 2026-10-29.
- Status: retain the citation for later execution research. No standalone saved review was published.
- Evidence boundary: no independently verified ES/NQ execution saving or strategy return. Consult the original source for any future detailed source review.
- Next check: use only when a concrete execution question requires this market-structure reference; no return experiment is started by this entry.

### E03 — SniperAlgo: order lifecycle and cancellation accounting

[Review](results/sniper_execution_review_20261027.md), [evidence](evidence/sniper_execution_20261027.md).
Source pinned vn.py class; reviewed 2026-10-27.
- Use: separate an execution helper from an alpha signal; a supplied price cap and quote trigger do not guarantee a fill or improvement.
- Evidence: fourteen disconnected synthetic scenario groups, zero economic trials. Constructed cases exposed invalid-quote handling, delayed old terminal callbacks and delayed trade-report overfill risk.
- Limits: synthetic behavior is not a measured incident probability, gateway integration pass or historical cost result. The class is not a MultiCharts drop-in.
- Next check: first verify ID-specific lifecycle, cumulative/pending-fill reconciliation, quote validity and external timeout/risk handling with the actual gateway event contract in a disconnected environment.
- Later economic work requires a frozen parent strategy and complete quote/order replay including partial fills, latency, cancellations and missed opportunities.
- Status: execution-code reference; no standalone place in any of the five account homes.

### E04 — Existing offline execution diagnostics: clocks, coverage and attribution

[Report](results/execution_diagnostics.md), [plan](plans/execution_diagnostics.md).
- Use: reuse the existing offline schema and tools before building another reconciliation system.
- Evidence: the retained October 20–21 sample contains three market events across six order rows, not six independent signals. Account assignment, signal/submission clocks and contemporaneous quotes remain incomplete.
- Limits: platform generation/status times are not verified broker latency. Chart labels and bar-derived trade times are not actual fill clocks; a chart quote snapshot may occur after the fill.
- Next check: obtain/review complete account-attributed native order/execution exports, same-contract quotes, timezone mapping and signal coverage; keep unavailable quantities unknown.
- Status: diagnostic infrastructure and partial observations; no demonstrated spread cost, delayed-entry benefit or execution saving. The logger proposal remains uncompiled/uninstalled in this evidence.

### E05 — Limit-for-market substitution: opportunity cost can exceed the tick saved

Sources: [existing TIER_LIST entry](../../TIER_LIST.md), [test script](../../analysis/limit_entry_test.py), 2026-10-18.
- Use: include missed winners and no-fills when comparing passive and market entries.
- Evidence: repository-reported historical tests, not rerun for this library. Decision-close limits 0–2 ticks better, working 1–5 minutes with one-tick trade-through, were worse across the tested strategies/settings.
- Decisive examples: ES MOC lost approximately $76–109 per signal versus original execution despite 65–98% fill rates across the study; missed MOC trades averaged $417–491. Units are the original study's mini-contract comparison, not native micro savings.
- Limits: this rejects those tested substitutions, not every possible limit policy or the exact SniperAlgo.
- Next check: inspect the existing ledger and settings first; require a distinct mechanism and frozen replay before any new economic test.
- Status: negative execution evidence; do not repeat the same search under a new name.

### E06 — Fast-alpha delayed-entry/exit overlay: timing and random-delay controls

Sources: Zarattini and Pagani, Concretum QuanTips #2 (2026);
[existing TIER_LIST entry](../../TIER_LIST.md), [test script](../../analysis/fast_alpha_test.py).
- Use: a small reversal tendency does not imply a useful execution delay; compare with random delays and keep the same eligible signals.
- Evidence: repository-reported historical tests, not rerun here. The standalone effect was about $6 gross per NQ against $17.25 costs.
  The paper-style breakout overlay weakened recent results ($102 versus $116 per trade); plan overlays generally lost relative to original timing.
- Limits: historical overlay results are not broker latency estimates or validation of a new delay policy.
- Next check: reuse original controls and ledgers before proposing another delay; include missed entries, changed exits and opportunity cost.
- Status: negative/cautionary execution reference, not a new alpha candidate.

### E07 — Almgren–Chriss / TWAP and event replay tools

[Public-repositories review](results/public_repositories_review.md), 2026-10-26.
- Use: order slicing trades market impact against price risk; Nautilus is a possible later quote/order replay sandbox.
- Evidence: selected source/API inspection only. The cited Freqtrade slicing example exists; no execution saving, package integration or native CME parity was established.
- Limits: slicing a small micro order can sacrifice a short-lived signal; a framework cannot supply missing quotes, auction history or queue evidence.
- Next check: establish actual parent-order size versus liquidity/impact first. With suitable data, reproduce one identical order/trade sequence against the existing engine before broader integration.
- Status: educational execution concepts and potential tooling; no installation or migration approved.

### E08 — Vault Break fill parity versus economic robustness

[Saved audit](results/vb_parity_stress.md), [preregistered parity amendment](plans/vb_parity_trade_through_amendment.md).
- Use: distinguish reproducing a platform export from choosing an economically favorable fill assumption.
- Evidence: repository audit reported 1,736/1,743 MC entries matched (99.60%), with exact matched gross P&L at a registered 0.25-point target-through parity convention.
  The original one-point research convention remained the stress denominator; no preferred replacement was selected.
- Limits: matching bars/P&L does not establish broker timestamps, queue priority, spread or intraminute path. The result is specific to this export/settings.
- Next check: preserve residual mismatches and exact MC settings; compare new native fills without silently changing the research convention.
- Status: historical parity evidence and sensitivity audit; no blanket relaxation of fill rules.

### E09 — Native micro costs, turnover and roll reconciliation

[6E package review](results/six_e_cross_asset_review_20261027.md), 2026-10-27.
- Use: measure arrival-mid shortfall, spread, native-tick stresses, integer quantities and total turnover; a +2 to −2 reversal trades four contracts.
- Evidence: methodological requirements from the source review, not verified M6E execution results.
- Limits: mini-price histories and back-adjusted signals are not a native micro fill/cash ledger. Avoid double-counting spread inside slippage.
- Next check: reconcile actual contract IDs, as-of rolls, orders/fills/fees and marked daily P&L before portfolio claims.
- Status: execution/accounting reference; the strategy's separate verification status remains in its report and TODO.

## Minimum record for any later execution comparison

Freeze parent signals, decision times, quantities, protective exits and eligible opportunities.
Retain filled, partial, cancelled, rejected and genuinely missed orders; report coverage gaps.
Align information availability, submission, acknowledgement, cancellation and fill clocks, preserving actual contracts.
Separate spread, commission, adverse price movement, latency assumptions and opportunity costs without double counting.
Compare paired outcomes with original execution, including no-fill consequences and account constraints at native integer size.
Use evidence sheets and committed preregistration before new return tests; preserve trial limits and cheap-screen gates.

## Maintenance entry template

Source/review + date:
Execution question and useful lesson:
Evidence: author claim / source inspection / synthetic mechanics / historical test / native fill evidence:
Market/platform and timing limits:
Data/prerequisites:
Smallest justified next check:
Status and superseding evidence:
