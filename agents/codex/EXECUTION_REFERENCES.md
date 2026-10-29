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
- Retained entry-timing idea (user-supplied Davey webinar discussion): record prices at −5/−2/−1/0/+1/+2/+5 minutes around verified signal/fill anchors for VB, evaluation ONB_ADX30 and Bridge Monday. Two accounts on one signal count as one market event; preserve separate account fills. Before Sunday's reopen there is no current-session quote; do not substitute Friday observations.
- This is descriptive: a better later price does not establish that delaying the entry improves the strategy. Any timing experiment must include missed trades, changed exits and costs under a separately frozen plan.
- [Bid/ask logger proposal](proposals/Apex_Trade_Logger_bidask.txt): chart snapshots do not establish broker submission/fill-time quotes or verified freshness. Separate research-chart validation and responsible review remain prerequisites; no deployment follows from retention.
- Related operational reference: [stateful watchdog proposal](proposals/watchdog_stateful_proposal.md). Fresh persistent mismatches and today-only rejection evidence concern monitoring, not alpha or execution savings; the draft's integration/deployment status must be checked separately.

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

### E10 — Liquidity compensation, turnover and costs

Source: Swan (2002), [SSRN 251399](https://ssrn.com/abstract=251399).
[Saved review](results/equity_premium_liquidity_review_20261029.md). Retained by user 2026-10-29.
- Use: distinguish turnover from spread, depth, impact and resilience; distinguish compensation for illiquidity from predictive alpha. Large trading volume need not imply cheap executable liquidity.
- Evidence: historical asset-pricing model and fits, not independently reproduced. Model-implied trading benefits are not cash trading profit.
- Limits: historical equity-versus-Treasury estimates do not establish current futures costs, a directional signal or a benefit from increasing turnover.
- Next check when relevant: measure actual same-contract spreads, depth/impact where available, fees and adverse fills in the relevant market state; never import the paper's historical cost percentages into ES/NQ tests.
- Status: retained contextual liquidity-risk reference; no strategy trial or allocation.

### E11 — Event-information clocks and attribution

Source: Ahluwalia, [SSRN 7674953](https://ssrn.com/abstract=7674953).
[Saved review](results/fomc_monthly_coefficients_review_20261029.md), 2026-10-29.
- Use: separate returns before the event, statement, press conference and later windows; a feature measured over an event window is unavailable at that window's start.
- Evidence: source-only review of monthly FOMC coefficient decomposition and predictor overlap; no execution savings independently measured.
- Limits: regression-coefficient shares are not trade returns; covariance with a future surprise is not a signal available beforehand.
- Next check: record publication/receipt, measurement-window end, decision and first executable fill; fit any forecast transformation on past data only. Reconcile the same events and controls across attribution windows.
- Status: timing/measurement reference; no FOMC strategy reopening or automatic experiment.

### E12 — Realized-variance measurement: microstructure noise, units and availability

Source: Zhou (2018), [SSRN 1783624](https://ssrn.com/abstract=1783624), pp.4–5 and Figure 1 p.27.
[Review](results/variance_risk_premium_review_20261029.md), 2026-10-29.
- Use: high-frequency squared returns can be contaminated by microstructure frictions; a noisier variance estimate is not necessarily more accurate just because sampling is faster.
- Evidence: source methodological discussion, not a newly reproduced estimator comparison or execution-cost study.
- Limits: IV minus RV needs variance units and matched horizons/sessions; volatility differences, daily futures proxies and retrospective realized variance are different quantities. Do not subtract next month's realized variance to construct a signal supposedly known today.
- Next check when using variance inputs: document return sampling, overnight handling, price source, percentage/decimal scaling, annualization and available-at timestamps before testing. Audit candidate estimators without choosing on strategy P&L.
- Status: measurement reference for execution/risk inputs; no spread, slippage saving or standalone intraday alpha established.

- Later check2026-10-29: [monthly VRP proxy diagnostic](results/vrp_monthly_proxy_20261029.md) preserves a failed
  daily-risk gate despite known monthly entry/exit prices. Endpoint profitability and endpoint drawdown do not
  certify daily paths, margin or execution savings. The existing file named SPY_daily.csv was not treated as SPY
  or used to repair missing native ES marks; its scale and timestamp convention require independent verification.
  The positive-VRP filter underperformed matched constant exposure; no execution change is supported.

### E13 — Buybacks: all-in execution costs versus terminal market outcomes

Source: Gumport, *The Buyback Monitor – July 2009*, [SSRN 1433183](https://ssrn.com/abstract=1433183).
[Saved review](results/buyback_monitor_review_20261029.md), 2026-10-29.
- Use: reconcile executed quantities/prices, fees and financing/hedging legs; distinguish implementation shortfall from a subsequent change in market value. Freeze benchmark and measurement horizon before comparing policies.
- Evidence: retrospective corporate repurchase accounting and appendix summaries of other case studies; not independently reproduced and not an executable strategy test.
- Limits: a July 2009 terminal mark does not prove bad execution, causal value destruction or future returns. Authorizations, ASR deliveries, dealer hedges and actual market purchases are not interchangeable. Historical fee/regulatory claims are not current CME facts.
- Next check when relevant: inspect original program/contract disclosures and actual executions, costs, benchmark definitions and publication clocks before estimating an execution saving or a directional flow.
- Status: execution/accounting reference; original ASR/commission publications are leads only. No automatic backtest, data purchase or strategy-queue promotion.

### E14 — Overnight/intraday attribution and causal price-impact claims

Source: Knuteson, [SSRN 3705017](https://ssrn.com/abstract=3705017).
[Saved review](results/overnight_intraday_knuteson_review_20261029.md), 2026-10-29.
- Use: split frozen strategy P&L into non-overlapping overnight/intraday components and reconcile costs, rolls and inventory to the total; do not assign overnight equity exposure to an intraday signal.
- Evidence: source-only review of cumulative index/ETF charts through 2020; manipulation is the author's explanation, not established causal evidence.
- Limits: differing histories, adjusted/raw prices, dividends, official opens and actual auction fills require separate checks. Stock-index components are not executable futures cash flows; the paper notes the U.S. index divergence stopped after 2008.
- Next check when relevant: audit session clocks and price adjustments, then attribute an existing fixed ledger. Own-order price impact requires actual order/quote records and a credible benchmark; a subsequent market move alone is insufficient.
- Status: measurement reference, not a new overnight strategy, verified execution saving or reopening of prior tests.

- Factor-aware extension: Ye, Jiang and Luo, [SSRN 4138715](https://ssrn.com/abstract=4138715), [review](results/factor_beta_sessions_review_20261029.md), 2026-10-29. Stock-factor beta premiums can reverse by session and country. Compare like-for-like exposures, calendar periods and price/dividend adjustments before attributing timing gains.
- The source's prior-month ranking betas are trading-time candidates; full-sample post-ranking chart betas are descriptive only. Statistical factor slopes are not net execution savings. T+1, short availability, suspensions and auction fills require explicit local-market treatment.

- Follow-up [restricted S&P500 screen](results/factor_beta_sessions_test_20261029.md): both design baskets fail assumed net-cost gates; acquisition-related missing selected days prevent a continuous executable ledger. Raw versus split-adjusted price conventions affect nominal filters and integer quantities. Preserve unresolved executions and settlement/cash treatment; do not zero-fill or relabel a conditional series as verified trading P&L.

### E15 — Overnight tail risk versus ordinary volatility

Source: Riedel and Wagner (2015), [SSRN2494387](https://ssrn.com/abstract=2494387).
[Saved review](results/overnight_tail_risk_review_20261029.md), retained2026-10-29.
- Use: low overnight volatility does not establish small extreme-loss exposure, reliable stop fills or adequate margin.
  Keep cash-session closure, futures maintenance breaks, halts and Sunday reopens distinct.
- Evidence: source TGARCH/GPD estimates on historical cash indices, not independently reproduced. In the NASDAQ
  illustration,99.9% VaR is4.951% overnight versus4.586% intraday; overnight VaR is LOWER at the other displayed levels.
- Limits: standardized tail shape, total VaR, expected shortfall and executable account losses are different quantities.
  Failing to reject a zero tail shape does not establish Gaussian innovations or absence of intraday extreme risk.
  NASDAQ Composite is not NQ; historical index openings are not executable futures fills. Illiquidity is a proposed
  mechanism, not causally identified by the return distributions alone.
- Next check when reviewing a fixed overnight candidate: preserve chronological native-contract marks and losses,
  session/weekend exposure, gap-through-stop fills and liquidation/margin timing. Compare volatility and empirical
  tail losses; fit any EVT model using a separately preregistered past-only/calibration protocol.
- Status: risk/execution reference; no demonstrated alpha, sizing change, trading allocation or new return test.

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
