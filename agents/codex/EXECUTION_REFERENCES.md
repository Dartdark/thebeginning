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

- Nocturne follow-up2026-10-30 ([assumed replay](results/nocturne_20261030.md)): native MNQ fees must be
  recomputed rather than dividing NQ net by10. Distinguish market-entry/time-exit slippage from limit-target
  execution; charge each reentry separately. Our$1.24RT fee assumption is not a verified broker statement.
  Positive source-cost results do not establish native funded-account performance.

- Video Drift follow-up 2026-10-30 ([frozen reconstruction](results/drift_video_20261030.md)):
  when a daily circuit breaker counts **net losing trades**, altered fees/slippage can change later eligibility.
  Replay the counter under the stressed cost view; recosting an unchanged ledger is only a fixed-ledger sensitivity.
  Report stressed fee/slippage subtotals consistently with stressed net. The nominal-bracket replay found $4.35 per
  MNQ after assumed $1.04 RT fees and one tick per market/stop fill; it failed advancement gates. These are research
  assumptions, not native broker fees/fills or measured execution savings. Future parity work needs actual quotes,
  contract IDs, source counter settings and fees; no live change follows.

- QuantJourney Donchian example, 2026-10-30 ([source/data-gate audit](results/qj_donchian_20261030.md)):
  reconcile contract multipliers consistently across fills, open notional, realized/open P&L, weights and NAV.
  The published packet's open-position value is quantity×price without multipliers, while its separate exposure
  table includes them. Arithmetic verifies that reporting discrepancy; it does **not** establish that headline NAV
  is wrong. Daily resizing can split FIFO lots, so fill count need not equal twice the lot count; validate actual
  quantity/cash reconciliation instead. Source statistics remain unreconciled;17 synthetic/arithmetic checks are
  not a historical alpha or native-fill replication.
  A 25% per-market notional cap plus whole contracts can zero all positions at small capital. ATR-sized volatility
  without a stop is not a maximum-loss cap. A reference margin cap and full-notional cash bookkeeping do not model
  futures variation margin, current buying power or executable dated rolls. For multiweek carry, removing a splice
  bar from an unadjusted continuous series does not supply roll trades/cashflows. Needed next: contract IDs, actual
  roll schedule/fills/fees and a daily NAV-to-lot ledger reconciliation; no strategy/account/live change is authorized.

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

- Added2026-10-29: **benchmark clocks change by era.** Bloomberg's [October15 2024 methodology](https://data.bloomberglp.com/professional/sites/27/Fixed-Income-Index-Methodology.pdf),
  printed p.80, moves ordinary U.S. Treasury index pricing15:00→16:00 NewYork (14:00→15:00CT), effective2021-01-14.
  Early-close pricing has separate dated exceptions, including January14–November25 2021. Use named timezones and
  an explicit event calendar; a provider snapshot is not an executable futures fill. The old ZN month-end test's13:59CT
  endpoint omits the later deadline, without invalidating its reported losses. [Source/clock audit](results/scout_buying_duration_20261029.md).
  Evidence: provider rule independently checked; [NYFed September22 2026](https://libertystreeteconomics.newyorkfed.org/2026/09/treasury-trading-at-the-close/)
  describes volume moving with the clock. No market-data reproduction, net alpha or execution saving established.
  Next check: pin source version, map ordinary/early-close regimes and audit bar labels, available-at forecasts and
  first executable fills before any deadline-based research. Full source paper remains inaccessible; no rule is selected.
- The [FX auction/source audit](results/scout_fx_auctions_20261029.md) also found that the repository's general macro-day
  proxy uses realized07:30–07:35CT ranges. This can support retrospective diagnostics, not a pre-release calendar
  signal. Use independently published schedules with available-at times; do not select a pre-news trade from the
  news-window price spike. This is a code/timing observation, not verified FX alpha or a changed execution rule.
- [ZN timestamp-only follow-up](results/scout_7601879_testability_20261029.md): an observed last data date is not
  an authoritative rebalance calendar. Missing2020-11-30 daytime records makes a last-observed-date rule select
  November27. Holiday/early-close flags are not automatically missing expected bars. Audit provider events against
  native dated sessions; do not forward-fill a missing session or infer that event eligibility from the remaining rows.
- [Calendar acquisition](results/scout_fx_calendar_acquisition_20261029.md) retained943 primary calendar/header facts.
  Scheduled archive copies, release headers and first-announced calendars are different evidence. The2019 BEA shutdown
  canceled planned releases and changed estimate labels; do not use a later revised calendar to assume knowledge before
  a canceled event. Fed statement documents include unscheduled actions and cannot all select a pre-announcement trade.
- [Weekly claims intake](results/scout_claims_calendar_acquisition_20261029.md) recovered two official2019 releases
  omitted by a secondary calendar after old URLs failed. Retrieval failure is not proof that an event did not occur:
  keep unresolved events visible and distinguish corroborated dates, printed embargo clocks and actual feed receipt.

- Added2026-10-29: [spread-strategy feasibility](results/scout_spread_strategy_feasibility_20261029.md)
  distinguishes a contemporaneous monthly position/curve regression from a forecast available before entry.
  A public weekly basis-reversal notebook discusses settlement availability and delays execution one day;
  that is a secondary implementation assumption, not verified primary timing or our replicated savings.
  Freeze publication/receipt and first executable prices before using final settlements to select a position.

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

- Nocturne follow-up2026-10-30 ([review and assumed replay](results/nocturne_20261030.md)): group initial entry
  and reentry into one night before resampling; trade-level bootstrap can break the dependence that creates
  account losses. A fixed small target with no stop can show high win rates while rare nights exceed the loss
  allowance. Conditional arithmetic on the user's reported568pointnight is$4544/$5680at4/5MNQbefore costs,
  not a verified native fill or breach probability. Simulate intranight liquidation, fees, current cushion and
  post-payout floor before interpreting a first-payout probability. EOD trail updates do not establish that an
  intranight breach may be ignored. Evidence: source claims plus one assumed2018–22replay/self-audit, no independent
  replication or measured execution saving. The candidate fails its filter-value gates; no account test is earned.

<!-- E16-E26 added by Claude (master session) and E27-E28 by the Papers session, 2026-10-29; renumbered from E12-E24 after Codex's E12-E15 -->

### E16 — Vault Break live exit slippage: stops worse than the 1-tick assumption, targets better

Source: live trade logger (`live/trades/*.csv`), [account_tools.slippage](../../analysis/account_tools.py), dashboard panel. Claude, 2026-10-29.
- Use: compare live exit prices with the backtest's fill convention per exit type, not one blended slippage number.
- Evidence (native fills, small sample): through 10/28, 11 VB target exits averaged 1.45 ticks *better* than the 40-pt target (worst 0); 9 stop exits averaged 1.78 ticks *worse* than the 75-pt stop (worst 8 ticks, 10/27), against 1 tick assumed.
- Limits: prices are MultiCharts' position prices in AA mode as logged at bar close, not reconciled with Rithmic's fill report; exit type is classified by distance (±3 / ±6 pts); 20 fills from two accounts on the same signals are fewer independent events.
- Next check: when ~30 stop fills exist, rerun the VB funded / evaluation benches with the measured stop slippage (or 2 ticks) as a sensitivity; reconcile a few rows with the Rithmic fill export.
- Status: watch item on the dashboard ('WORSE than backtest'); no plan change.

### E17 — Fast-market protective stops: Rithmic rejects stops already through the market

Sources: [MULTICHARTS_PITFALLS.md](../../MULTICHARTS_PITFALLS.md) 'Live order rejections', [LESSONS.md](../../LESSONS.md). Live incidents 2026-10-14 (ONB entry stop) and 2026-10-16 (EOS protective stop, 8:34 CT).
- Use: after a fill at the 8:30 open or after a fast move, a stop sent at the bar close can sit on the wrong side of the market; Rithmic rejects it ('Invalid StopMarket order parameters') and the position is left naked. MultiCharts retried 20 times in one second.
- Evidence: native rejections in the Order tracker. Fix in all live strategies: bar-close stop guard (exit at market when the bar's High/Low trades at or through the stop level); raised break-even/trail stops exit at market when at or beyond the close.
- Limits: the guard acts at bar close, so on a 30-min chart (VB) an unprotected position can run up to one bar. Backtests are unchanged (the stop fills inside the bar).
- Next check: count guard exits vs normal stop fills in the logger; compare their slippage with E16.
- Status: implemented guard; execution caveat for every new stop-based strategy.

### E18 — MultiCharts fill conventions vs research rebuilds (touch fills, tick units, Volume vs Ticks)

Sources: [TIER_LIST.md](../../TIER_LIST.md) 'MultiCharts parity 2026-10-25', [MULTICHARTS_PITFALLS.md](../../MULTICHARTS_PITFALLS.md). Related: E08.
- Use: know which side is optimistic before comparing a MC report with Python.
  - MC fills limits on a touch by default: Kusho v9 got +$48k gross over the rebuild's 1-tick-through fills (3,086/3,211 trades identical); the rebuild's $108 a trade is the honest number, not MC's $117.
  - "Fill limit price exceeded by 1 points" means 1 *tick* (MC's 'point' = smallest price unit). Of 896 VB target fills, none was touch-only, but 43 had only 0.25–0.75 pt through: our 1-full-point Python rule is stricter than MC.
  - Intraday `Volume` in MC is up-tick volume; `Ticks` is the total. A Python replay of a Volume-based rule is approximate.
- Limits: parity of bars / P&L is not broker fill evidence (see E04, E08).
- Next check: when a new MC report arrives, state its limit-fill setting and rebuild with trade-through fills.
- Status: standing convention: research uses trade-through fills; MC touch fills are treated as optimistic.

- Nocturne2026-10-30: a discretionary next-bar reentry must wait for the target's5minute bar to complete;
  an intrabar target fill does not authorize another fill earlier in that same bar. Freeze target-reference
  versus actual-fill anchoring and the trade-through rule; a replay convention is not source-code parity.
  [Frozen assumed implementation and limits](results/nocturne_20261030.md); synthetic lifecycle checks only,
  not evidence of queue execution or live fill improvements.

- Video Drift 2026-10-30: freeze whether “first counterbar” means a color transition or the first opposing
  bar after an arm, whether trend state updates every 5 or 15 minutes, and whether two losses means total or
  consecutive. A close-stamped minute at decision+1 opens at the decision's civil-clock boundary. A related
  strategy name does not establish source-engine parity. [Second-agent implementation audit](results/drift_video_20261030.md)
  checked trailing signals and saved paths; author-code/MC/native-fill parity remains unverified. Its half-day
  cutoff repair retained the first failed run and followed the original committed rule, without a rescue search.

### E19 — Session clocks: early closes, halts, SetExitOnClose and time zones

Source: [MULTICHARTS_PITFALLS.md](../../MULTICHARTS_PITFALLS.md) (2026-10-17 to 10-25).
- Use: a fixed-time exit never fires when the session ends early; the position rides the halt and exits at the next session's first bar (an Apex violation live).
- Evidence (MC trade lists): Monday Long 2023-07-03 held 08:31 → 17:05; NFP Fade 2023-04-07 (Good Friday) held to Sunday 17:05; FC 2B held 26 holiday trades to the 17:00 reopen; `SetExitOnClose` on a 24-h chart closed 47 Twin Continuation trades at midnight, not 15:59.
- Also: COMEX/NYMEX symbols (@GC, @CL) run on New York time in our MC while @NQ/@ES are Central; mixing them on Exchange time misplaces entries by one hour.
- Next check: for every new strategy, scan the MC trade list for exits after 15:59 CT or on a later date; list early-close days (Jul 3, Black Friday, Dec 24, Good Friday, Monday holidays).
- Status: standing check; `IsEarlyClose` list + early flatten in the live strategies.

### E20 — Order routing and account binding (symbol mapping, copied charts, broker profile)

Source: [MULTICHARTS_PITFALLS.md](../../MULTICHARTS_PITFALLS.md); live incidents 10/16, 10/20, 10/26.
- Use: an order can be sent correctly by the strategy and still never reach the right account.
  - `@MNQ` (dxFeed continuous) must map to the real contract for Rithmic (MNQZ6); the mapping is stored per MC installation (the VPS had the default and VB was rejected on both accounts 10/20). Change it at every roll (next ~12/11: MNQZ6 → MNQH7).
  - A copied chart keeps the strategy's account: 10/26 account #3's 150K-sized VB (20 MNQ) went to #2, which held 28 MNQ instead of 8.
  - A chart left on MC's default Interactive Brokers profile sends nothing to Apex.
- Evidence: native rejections and Order tracker rows.
- Next check: after every copy, roll or new machine: check each strategy's Auto Trading account and one manual 1-MNQ test order after the close (pre-flight checklist).
- Status: checklist items + watchdog rejection alerts.

### E21 — Broker-side liquidation vs chart state (Apex daily loss limit, chart thinks it is still in)

Source: [MULTICHARTS_PITFALLS.md](../../MULTICHARTS_PITFALLS.md) 'Apex daily loss limit vs the strategy', 2026-10-19.
- Use: when Apex liquidates (daily loss limit), MC does not see the exit, keeps its position and re-sends exits ('Account is done for day', price 0.00 in the tracker). Next day those exits would be accepted and open an unplanned position.
- Evidence: live 10/19, VB long 8 closed at −$1,017 mid-bar by Apex. VB's $1,200 stop exceeds the $1,000 daily limit, so a full VB loss is cut at about −$1,000 (the evaluation simulator models this).
- Next check: after any Apex lock, AA off/on (Flat) on every affected chart; the watchdog's MISMATCH alarm (chart vs broker position) covers it during RTH.
- Status: procedure + alarm.

### E22 — 'Running' is not 'trading': compile failures, half-closed MultiCharts, heartbeat

Sources: [MULTICHARTS_PITFALLS.md](../../MULTICHARTS_PITFALLS.md) (10/27 ONB, 10/29 VPS session), [LESSONS.md](../../LESSONS.md), [watchdog.ps1](../../live/vps/watchdog.ps1), [Strategy_Heartbeat_Snippet.txt](../../apex_strategies/Strategy_Heartbeat_Snippet.txt).
- Use: an opportunity cost that no fill report shows. 10/27 Overnight Bias ADX30 signalled long 10:00 → 14:30 (+135 pts, ~$1,080 on #2, ~$3,240 on #3 gross) but sent nothing: the code had not compiled, while the chart, AA button and logger looked normal. 10/29 a half-closed MC copy on the VPS blocked the restart ('session terminated').
- Evidence: missed-trade panel (7 quiet days, backtest chance ~5%) and the chart's trade list.
- Fix: strategy heartbeat (SIG rows) checked by the watchdog every 5 min; missed-trade (silence) panel on the dashboard.
- Next check: when the heartbeat alarm first fires for real, confirm it caught the stopped strategy within one check.
- Status: monitoring in place; counts as 'genuinely missed orders' in the minimum record below.

### E23 — Logger and account fields: what each number really is

Source: [Apex_Chart_Monitor.txt](../../apex_strategies/Apex_Chart_Monitor.txt), [dashboard_data.py](../../analysis/dashboard_data.py), ACCT rows 2026-10-29.
- Use: interpret live records correctly before computing costs.
  - Rithmic reports NetWorth 0 for Apex accounts; Equity = the account balance (matched the Order and Position Tracker: −02 $50,764.42, −03 $147,822.60).
  - Whether Equity includes open P&L is unverified (decides Target Guard v2's `EquityHasOpenPL`).
  - Logger POS rows are chart state at bar close (bar_time = bar-close label), not fill clocks; CLOSE rows carry MC's prices, not the broker's fill report (see E04).
- Next check: read ACCT rows during the next open trade: does Equity move with open P&L?
- Status: open measurement; Target Guard v2 not installed until answered.

### E24 — Opening-print fills: the Sunday reopen push

Source: [WATCHLIST.md](../../WATCHLIST.md) item 22, `analysis/sunday_reopen_test.py`, 2026-10-18 / 10-21.
- Use: a backtest that fills at the first print of a session can't be traded by an order sent after the print.
- Evidence (historical test): NQ 2023–26 $182 a trade (t 2.6) filled at the first print, $162 at 4 ticks worse; entering one minute late loses; 17:01 → 17:15 entry +$10 (t 0.2).
- Limits: only a pre-open order on the indicative price could capture it; no live fills yet.
- Next check: ~20 forward paper reopens logging first print vs fill; keep only if ≥ ~$80 per NQ after real slippage.
- Status: C, on the watchlist.

### E25 — Order-book / order-flow features do not predict NQ at 5–30 min

Source: [TIER_LIST.md](../../TIER_LIST.md) 'Order-flow prediction (The Bridge MBO, 2018–2026)'.
- Use: a negative reference for any 'read the book to time the entry' idea.
- Evidence (historical test): 39 features (delta 5–30 min, book/count imbalance, depth 10/50, pulled orders, queue depletion, icebergs, big prints, walls) vs the next 5/15/30 min: correlations −0.008 to +0.013, costs need ~0.05; the best (50-level depth) as a 15-min trade: 2018–22 $4, 2023–26 −$24.
- Limits: tested as predictors of direction, not as fill-timing tools for an existing signal.
- Next check: none unless a new mechanism (e.g. timing an existing entry inside its minute) is pre-registered.
- Status: F as alpha; do not repeat under a new name.

### E26 — Placebo levels: 'price reacts at level X' often isn't about X

Source: Prior VWAP Trap review, [checks/candidates/prior_vwap_trap/REVIEW.md](../../checks/candidates/prior_vwap_trap/REVIEW.md), `analysis/prior_vwap_trap_test.py`, 2026-10-29.
- Use: before believing a level-based behavior (prior VWAP, ORB high, pivot), run the same rule at nearby random levels.
- Evidence (historical test): 1,804 trades, $153 per NQ, t 3.2 at the prior-day VWAP, but placebo levels nearby performed nearly as well: the edge is mostly momentum + the trailing exit, not the level.
- Next check: apply the placebo-level control to every level strategy (standing in DEVELOPMENT_PROCESS stresses).
- Status: market-behavior reference; strategy ranked B, not in a plan (50K evaluation pass rate falls with it).

### E27 — Opening imbalance: market orders at the stock open sit on the exploited side

Source: Branch & Ma, SSRN 3259614 (paper, user upload 2026-10-29); `analysis/on_id_reversal_quartiles.py`, TIER_LIST F row.
- Use: in single stocks the open is set by the market maker against the overnight order imbalance and overshoots; the paper advises against market orders at the open. For NQ / ES futures (continuous Globex trading, no specialist open) the mechanism is absent.
- Evidence (author claim + historical test): stocks 2011-17 reverse overnight moves intraday, but SPY's overnight / intraday correlation is now slightly positive. NQ / ES 2018-26 (15:00 -> 08:30 vs 08:30 -> 15:00 CT): corr +0.00 / −0.03, no monotonic quartile pattern; fading top / bottom quartiles 2018-22 −$95 / −$60, 2023+ +$184 / +$167 (t 0.9 / 1.3).
- Limits: says nothing about the 08:30 fill itself (see E24 for opening-print fills).
- Next check: none; do not re-test overnight -> intraday reversal on index futures (also SSRN 2730304, F).
- Status: negative reference for futures; stock-only lesson.

### E28 — Retail open-buy / close-sell flow (Korea) does not show up in NQ / ES

Source: Ahn, Fan, Noh & Park, SSRN 4752520 (paper, user upload 2026-10-29); `analysis/retail_gap_cot_test.py`, TIER_LIST F row.
- Use: the paper verifies with trade-level investor IDs that Korean retail (mobile, young, male day traders) net buys at the open auction and net sells at the close; institutions do the reverse. It widens the overnight − intraday gap in high-retail stocks / months.
- Evidence (historical test): on CME index futures with CFTC small-trader and micro-share proxies, high-retail weeks show a smaller NQ gap (t −1.8), ES none.
- Limits: COT proxies are weekly positions, not intraday flow; the micro series starts 2020-08.
- Next check: none unless intraday retail flow data (e.g. small-lot aggressor volume by minute) is added.
- Status: negative reference for futures.

### E29 — Expiry hedge removal, signed inventory and cumulative snapshots

Source: Amaya/Garcia-Ares/Pearson/Vasquez, *The Price Impact of Hedging Expiring Index Options*, August13 2026,
[public paper](https://algoseek.com/wp-content/uploads/2026/10/ssrn-7330098.pdf), Sections2.1 and3.3–3.4,
printed pp.6–7 and13–15. [Full-source review](results/scout_7330098_testability_20261029.md).
- Use: cash-settled option expiry removes option delta while its hedge can remain; hedge liquidation and gamma
  rebalancing are different flows. Signed option inventory determines the estimated unwind sign; unsigned OI,
  aggregate gamma and futures aggressor flow do not identify that inventory.
- Evidence: source method and published return-group claims inspected, not independently reproduced. No net alpha,
  measured fill benefit or account contribution verified. Local paper bytes/hash and a complete signed book remain unavailable.
- Clock/accounting: the source labels minutes at their start and uses end-minute quotes. A15:30ET label may need
  data through15:31ET, then publication/receipt/processing lag. Never fill at the label time with later information.
  Reconstruct positions from series inception; the latest cumulative snapshot is not an incremental flow to sum repeatedly.
- Limits: SPXW dealer delta is not NDX GEX/OI or NQ tape delta. Cboe T+1 trade detail cannot be a same-day forecast.
  Later data specifications, corrections and GTH coverage must not be imposed on earlier history without reconciliation.
- Next check: obtain a lawful sample and audit one series' initial inventory, signed contracts, complete sessions,
  corrections, cumulative snapshot differences, option delta units and actual data receipt before any proposed fill.
- Status: retained execution/input-method reference and specific TODO lead; no return test or execution saving established.
- [Data acquisition](results/scout_spx_positions_acquisition_20261029.md): the official2026 Cboe filing describes
  one-minute intervals delivered2–5minutes after their end and a product introduced in2025, despite earlier backfilled
  trade timestamps. A historical timestamp is not proof of contemporaneous subscriber access. The published2022H2
  sample offer does not itself provide starting inventory, Greeks, receipt history or an activated data entitlement.

### E30 — Listed calendar spreads versus separate-leg execution

Source: Ma, Serra, Peterson and Irwin, [SSRN7425358](https://ssrn.com/abstract=7425358),
[conference-version review](results/scout_7425358_20261029.md), retained2026-10-29.
- Use: compare a listed two-month spread with executable synchronized leg quotes; account for fees, delay,
  partial fills, shared implied liquidity and contract identity. Continuous prices cannot supply either book.
- Evidence: full conference-source review only. Authors report lower quoted execution costs in grains/livestock;
  no independent quote replay, actual savings, net strategy returns or causal verification here.
- Limits: quoted tightness and common-price contribution do not certify actual fills or a tradable lead.
  Design counterfactuals and price-limit exclusions require care; ES/NQ/micro transfer is unverified.
- Next check: obtain a lawful synchronized sample of listed-spread and both leg books plus security definitions,
  audit clocks/size/rights, then preregister any economic execution comparison before outcomes.
- Status: execution reference, not a directional strategy or allocation. Official sample download was blocked;
  record the gap and continue research on other leads.

### E31 — Closing-auction state, final print and executable entry are different clocks

Sources: Challet/Gourianov [arXiv1802.01921v2](https://arxiv.org/html/1802.01921v2), Sections2/4;
Bogousslavsky/Muravyev [2020 primary PDF](https://www.aeaweb.org/conference/2021/preliminary/paper/H9T4hef7),
Sections3.2–3.4 and AppendixD.2. [Cycle review](results/scout_closing_auctions_cycle_20261029.md).
- Use: distinguish indicative-price changes, continuous-book quotes, published final auction prints and later
  executable quotes. A signal defined using the final print cannot enter retrospectively at that same print.
  Freeze a pre-auction order protocol or a post-auction later-fill protocol before returns.
- Evidence: primary-source inspection only; no own net returns or measured execution benefit.
  The sources document asset-dependent indicative dynamics, throttled updates and temporary auction deviations.
- Limits: an indicative price is not a standing executable quote. After-hours interval VWAPs and regression
  reversals are not guaranteed fills. Daily closes/returns cannot reconstruct all auction states.
  Historical rule/cutoff claims and malformed rendered equations need primary venue/formula validation.
- Data/next check: original messages, revision/quantity semantics, actual dissemination and receipt evidence,
  auction prints, eligibility rules and synchronized executable quotes. Missing states stay unknown, not zero.
  Cluster by auction/day; do not count thousands of correlated updates as thousands of events.
- Status: existing SPY/QQQ research-family refinement; NEEDS DATA. Price-only proxies and index-rebalance
  reversal failures remain failures. No logger, live-system or allocation change.

### E32 — Currency fixing clocks and dealer versus client returns

Source: Krohn/Mueller/Whelan, [SSRN3521370](https://ssrn.com/abstract=3521370), published2024,
SectionsI,V.C,VI.E/TableX; [review and completed screen](results/scout_3521370_20261029.md).
- Use: separate benchmark calculation, publication, customer execution and hedge clocks. The source distinguishes
  ECB14:15calculation/16:00publication after2016 from the new WMR14:00Frankfurt turning point. Convert civil
  timezones by date; publication delay does not require waiting if no published rate enters the signal.
- Evidence: source says dealer liquidity provision can earn positive returns while client marketable reversal
  trades lose after costs. Do not assign a dealer's customer spread to our futures market orders.
  Our single2018–22standard6E reference screen found$17.52gross versus$19.75cost, net−$2.23(t−0.21).
- Limits: a reference-price rejection is not a quote/fill replay, M6E result, causal reproduction or measured saving.
  Reader text was captured; original author data and figure pixels were not reproduced.
- Prerequisites/next check if a distinct future execution task warrants it: native contract/quote/fill clocks,
  contemporary benchmark rules and actual fee/venue role; no retuning this failed definition.
- Status: rejected directional screen, retained execution method; no account/allocation change.

### E33 — Treasury benchmark pricing clocks changed in2021

Source: Dyer/Fleming/Shachar, [NYFed September22 2026](https://libertystreeteconomics.newyorkfed.org/2026/09/treasury-trading-at-the-close/);
[completed clock-aligned screen](results/scout_treasury_close_20261029.md).
- Use: distinguish CME settlement, cash-bond index valuation and futures order/fill timestamps.
  Bloomberg moved its USD bond-index strike from15:00ET to16:00ET on January14 2021.
  Civil-time conversion and historical effective dates must be frozen before outcomes.
- Evidence: official research documents volume migrating to the new clock, especially at month-end.
  This establishes timing, not guaranteed directional demand or execution savings.
  Our175-event2018–22intraday ZN adaptation earns$15.89gross but loses$29.86net at$45.75RT cost;
  the clock correction does not rescue the rejected month-end family.
- Limits: original multi-day paper and cash-bond volumes are not one-hour executable ZN returns.
  Continuous prices, one-minute stops, early-close calendars and native costs remain relevant.
- Next check: use current primary index/venue timing for any independently warranted execution study;
  require native quotes/fills before claiming savings. No retuning this failed definition.
- Status: retained clock reference; directional adaptation rejected. No live/system changes.

### E34 — Calendar counting, closed sessions and intraday adaptations

Source: Cieslak/Morse/Vissing-Jorgensen, [SSRN2687614](https://ssrn.com/abstract=2687614),
2018-02-12manuscript/Table1 and [completed RTH adaptation](results/scout_2687614_20261030.md).
- Use: keep the paper's weekday clock separate from tradable sessions. Holidays can occupy a cycle slot while
  closed/short sessions generate no full-session order. Determine closures independently of returns; an otherwise
  expected missing session stays unknown. Our484candidate endpoints are observed; non-event2020-11-30is unknown.
- Evidence: source review plus self-audited reference screen, not native fills or independent economic verification.
  Full-day cash-equity findings did not yield a profitable RTH adaptation here:−$95.53gross/−$125.53net per ES.
- Limits: omitting overnight exposure changes the economic rule. A failed intraday adaptation does not reject the
  original full-day result; a positive one would still require contract/path, protection and native account-cost checks.
- Next check for a distinct future study: explicit clock/session census before outcomes. Do not retune this family.
- Status: execution/input-design reference; no claimed saving or allocation.

### E35 — GreenORB: fill-anchored targets, engine callbacks and source parity

Source: user-uploaded GreenORB PDF/post and Liqport class, 2026-10-30.
[Saved test/review](results/greenorb_20261030.md), [frozen plan](plans/greenorb_20261030.md).
Related: E09 native micro accounting, E18 fill/volume conventions, E19 session clocks.
- Use: when a target is R times the actual fill-to-stop distance, changing entry slippage changes its price and
  potentially its exit. Rebuild the target in an execution stress; subtracting extra fees from an unchanged ledger
  answers a different question. For this declared source, adverse two-tick fills and four-tick fills were tested
  separately, retaining both exact and fixed-ledger sensitivities.
- Timing: at the OR-end instant, base-bar and five-minute callback ordering can determine which three candles
  sit in a rolling buffer. The indicator class and callback scheduler were not supplied. Implementing prose's
  intended opening bars does not establish exact engine parity. Count limit validity in the callback's actual
  units (here one-minute ticks), and distinguish marking a direction as traded on order placement from an actual fill.
- Evidence: source inspection, pre-return synthetic path/gap/trade-through tests and a maker-audited historical
  NQ-data proxy. One-MNQ design net was $5,828.40 at two ticks and $5,623.40 at four ticks; no current-account,
  native MNQ, Liqport trade-match or independent verification result. Strategy controls failed; no allocation earned.
- Limits: observed-bar NQ VWAP with missing overnight prefix minutes is not full native MNQ VWAP. Missing day
  paths, including circuit-breaker/stress dates, remain unknown; do not book them as zero or infer risk from their
  absence. Intraday flatness does not eliminate overnight VWAP roll-splice effects. A median drawdown rank among
  shuffled days tests sequence luck, not source selection or the existence of an edge.
- Prerequisites/next check when a future parity task needs them: native contract/volume and trade ledger,
  indicator/session settings and callback trace; align signal, submission, next-open fill, protection activation
  and target price. Do not retune this failed strategy or install the supplied class to resolve a research question.
- Status: execution reference retained; failed strategy test remains a separate negative evidence record.

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
