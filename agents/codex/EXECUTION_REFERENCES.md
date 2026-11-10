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
- Scout source-only additions follow the user's later completed-results-only notification rule: save supporting lessons and continue discovery; no standalone execution-reference alert.

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
- Evidence: repository-reported historical tests, not rerun for this library. Decision-close limits 0–2 ticks better, working 1–5 minutes with one-tick trade-through, were generally worse. One EOS setting was marginally positive (+$0.70 per original signal); do not describe every setting as losing.
- Decisive examples: ES MOC lost approximately $76–109 per signal versus original execution despite 65–98% fill rates across the study; missed MOC trades averaged $417–491. Units are the original study's mini-contract comparison, not native micro savings.
- Limits: this rejects those tested substitutions, not every possible limit policy or the exact SniperAlgo.
- Next check: inspect the existing ledger and settings first; require a distinct mechanism and frozen replay before any new economic test.
- Status: negative execution evidence; do not repeat the same search under a new name.

**2026-11-08 MAE follow-up:** Gandhi/MTS Institute, [SSRN 7063478 full review](results/ssrn7063478_review_20261108.md),
July 2026, 12 pages; [seven-case source/mechanics audit](../../analysis/codex_mae_entry_7063478_audit.py).
The author reports Nifty Sharpe 1.38→3.33 at a selected 0.25% adverse offset, retaining 2,448/3,908 trades with
6.02 bp round-trip modeled costs. This is same-history selection on a proprietary signal, not independent net
execution verification. MAE used to diagnose a causally resting limit is not automatically look-ahead, but an
aggregate excursion cannot establish first fill, time-in-force eligibility, queue/partial fills or post-entry paths.
Touch eligibility (`MAE >= offset`) is weaker than trade-through. The source's claim that all missed trades must
have been profitable is false: an entry 100 / low 99.80 / exit 99.90 misses a 99.75 limit and still loses.
Preserve nonfills on the original signal/calendar denominator and distinguish fixed virtual-parent exits from
fill-anchored child brackets. Trade-order permutations condition on assumed selected returns; they do not validate
threshold choice or future edge. Seven invented checks passed; zero market tests or measured savings.
This percentage-limit rule is distinct from E06's opposite-five-minute-return policy. Prior negatives do not prove
this exact offset fails, and its headline is insufficient merit for a new cross-book rescue sweep. No new queue,
acquisition task, paused-program restart, allocation or live change follows.

**Later explicit user test, 2026-11-08:** [selected-book outcome](results/mae_selected_20261108.md),
[frozen causal limit runner](../../analysis/codex_mae_selected_20261108.py).
The user requested a test after the source review. Vault Break, FC2B and S47 were selected before new returns;
only the fixed 0.25% adverse offset was tried, with one-minute activation, one-tick trade-through, unchanged
virtual-parent exits and one-MNQ costs ($1.24 RT / one adverse market-stop tick; doubled stress).
Design 2018-04-02–2022-12-30: FC2B net $11,990.50→$1,358.38 and S47 $14,126.42→$6,228.92, both worse in every
design year. Their missed BASE trades earned $23,225.62 / $19,883.00, exceeding filled-entry price gains
$12,476.50 / $11,878.50. VB's incomplete subset improved $1,089.68 but stayed negative, paired t 0.66, with
106 unknown paths; this is not evidence of a full-VB gain. No profile passed. Nine definitions ran, six nulls
unused; no controls/2023+/native account stages were earned. Fixed virtual-parent replay is not regenerated
native brackets, tick/queue parity or measured account protection. No offset/side/window rescue or book change.

### E06 — Fast-alpha delayed-entry/exit overlay: timing and random-delay controls

Sources: Zarattini and Pagani, Concretum QuanTips #2 (2026);
[existing TIER_LIST entry](../../TIER_LIST.md), [test script](../../analysis/fast_alpha_test.py).
- Use: a small reversal tendency does not imply a useful execution delay; compare with random delays and keep the same eligible signals.
- Evidence: repository-reported historical tests, not rerun here. The standalone effect was about $6 gross per NQ against $17.25 costs.
  The paper-style breakout overlay weakened recent results ($102 versus $116 per trade); plan overlays generally lost relative to original timing.
- Limits: historical overlay results are not broker latency estimates or validation of a new delay policy.
- Next check: reuse original controls and ledgers before proposing another delay; include missed entries, changed exits and opportunity cost.
- Status: negative/cautionary execution reference, not a new alpha candidate.

**2026-11-08 current-book follow-up:** [completed design report](results/fast_alpha_books_20261108.md),
[frozen execution runner](../../analysis/codex_fast_alpha_books_20261108.py),
[reconciliation/coverage](../../analysis/outputs/codex_fast_alpha_books_20261108/reconciliation.json).
The owned seven-page source uses five-minute **close-to-close returns**, not candle close minus open.
An opposite return only triggers a next-minute market order; it does not guarantee a better price or passive fill.
The preregistered fixed-parent execution wrapper covered 24 instrument/version streams mapped to all five books,
with BASE/ENTRY/BOTH and 72 executed design definitions (48 reserved null definitions unused).
Design 2018-04-02–2022-12-30, one native micro, $1.24 round-trip commission plus one adverse tick per market/stop fill:
none passed. All six streams without unresolved paths lost net dollars under both delay policies.
Positive conditional effects in other streams were weak/incomplete; selected complete-case baselines are not
full-strategy estimates. No random-delay/drop, 2023+ validation or account stage was earned.
Delaying stops can increase losses: the observed Kusho paired extra adverse excursion reached $660.50 per micro
and the maximum additional hold was 60 minutes; these are minute-model observations, not account-floor replay.
Keep the original search history and amended source clocks; no waiting-window rescue, deployment or allocation follows.

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

- [US100 Donchian source audit, SSRN6722841](results/ssrn6722841_review_20261108.md), 2026-11-08:
  author code uses closed-bar signals, once-per-new-bar trailing management and a broker-dependent
  fixed-reference-risk minimum-lot eligibility filter. Preserve these clocks/eligibility in a port;
  its default session filter is off and no mandatory daily flatten is implemented. Author closed-trade
  Monte Carlo is not marked-equity or intraday trailing-floor validation. Static public-source findings
  only; no compilation, native futures replay, measured savings or independent profitability result.
  Exact uploaded/public PDF equality remains unverified due to unavailable execution workspace.


- [Bitcoin inverse-futures allocation](results/bitcoin_inverse_3441913_review.md), Deng et al., SSRN3441913,
  uploaded2019-08-23 version: a $K inverse contract earns `K*(1/Fentry−1/Fexit)` BTC when long; USD P&L needs
  an explicit spot conversion/collateral ledger. Inverse is settlement convention, not short direction. Both
  source-calibrated positions are long BTC. CME linear futures and index levels are not interchangeable executable inputs.
  Continuous utility-optimal controls omit native rebalancing cost and liquidation; near-singular covariance can magnify
  allocation estimates. Main formula agrees with the matrix solution; rendered AppendixB.2 has a contradictory sign.
  Evidence: source inspection and synthetic formula/payoff checks only; source Sharpe4.86–5.07 over111days is unreplicated.
  [User-requested strategy code](results/bitcoin_inverse_3441913_build.md) now has20 passing synthetic checks for reciprocal
  entry basis, partial closes/reversals, native BTC fees and a reconciled quote-priced BTC/USD cost bridge. Pooled research
  wallet transfers are not verified cross-venue settlement; ordered proposals are not actual fills. No return test added.
  Four BitMEX API probes hit proxy403. Need identified dated contracts/spot clocks, native lots/marks/margin and conversion
  before a return test; a perpetual adaptation also needs its own funding. No verified execution saving or current placement.

- [Leveraged Fibonacci paper review](results/ssrn2011743.md), SSRN2011743, retained
  2026-10-30: distinguish margin allocation, notional leverage and loss-at-stop.
  A 60% equity margin commitment at 10x implies 6x equity notional under a simple
  fixed-exposure illustration, not 60% notional or a 60% loss cap. Reserves and
  maintenance margin do not guarantee maximum loss; suggested option hedges require
  explicit expiry/strike/premium and marked cash accounting. Confirming a signal
  at a daily close does not establish a fill at that same close. Source review and
  conditional arithmetic only: no verified return, fill, savings or new strategy test.

- Replay readiness 2026-10-31 ([report](results/swing_replay_readiness_20261031.md)):
  a MultiCharts exit row labeled `open` is a valuation mark, not a closed fill.
  ONB ML's final export mark maps to an exit before entry and crashes a clean
  funded-cache rebuild. Explicitly excluding this sentinel permits the 343 closed
  ONB paths to build; other cross-date closed trades remain errors needing their
  own handling. Never use a generic reversed-time filter that silently removes
  real overnight/holiday holds. Verified report/parser behavior only; corrected
  ST account replay and native-fill parity remain unverified.

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

- Weekly cross-review2026-10-30 ([independent findings](../cross_review/2026-10-30_codex.md),
  [correction proposals](proposals/weekly_cross_review_20261030.md)): numeric exit kinds are part of the accounting
  interface. Swing Target's text `reason` replaced numeric `kind`, so target cost handling and protective-stop
  exit-minute capping differed from its recorded fills. A fixed-ledger check, retaining holiday repairs, changes
  closing cashflow by$132/MNQ total and48daily minima. The [extended-grid paired replay](results/swing_kind_replay_extended_grid_20261031.md)
  subsequently ran 500 two-year histories per account size: old/fixed swaps have identical two-year payouts and failure flags;
  first-year average payouts change +$2 (50K) and -$8 (150K). Better isolated accounting does not establish
  monotone account payouts. The 50K swap's earlier benefit was not reproduced on this frozen sample; the 150K
  comparison was favorable, subject to the historical-roster and simulator limits in the report. Concurrent
  [common-coverage results](results/swing_kind_replay_20261031.md) are inconclusive for both swaps; preserve
  the different seeds/universes and do not select the most favorable run or pool overlapping samples.
  Preserve schemas, assert numeric enum sets, and reconcile closed cash and marked paths before account claims.
  This is existing-ledger accounting evidence, not a new strategy, native-fill result or plan change.

- Swing Target account replay 2026-10-31 ([results](results/swing_replay_20261031.md)): 500 paired two-year histories
  per account, fixed empirical pool through 2026-10-09. The $132/MNQ fixed-ledger improvement changes neither
  selected replacement's two-year payouts nor failures in this sample; year-one mean changes are +$7 (50K)
  and +$20 (150K), with intervals spanning zero. An accounting correction is necessary but does not establish
  portfolio superiority. Against base, 50K VB replacement has two-year −$83 and failures +0.6 pp; 150K DT replacement
  +$43 and −0.4 pp; both inconclusive. These are legacy NQ-equivalent bench costs, not native fee/fill evidence.
  Rebuild also exposes an unfinished MC `Signal=open` valuation with a 00:00 exit sentinel: exclude it explicitly
  from completed-ticket paths rather than infer a next-date fill or drop all same-bar trades. The general
  builder still needs that upstream repair. No live/plan change or standalone strategy promotion follows.

- Leung et al. (2015), SSRN 2695405 ([full-source review](results/leung_futures_2015_review.md)):
  mean-reverting spot alone does not establish positive futures drift; separate historical P estimates from Q
  curve calibration. The paper's Eq2.12 inequality reverses when mu_Q < mu_P; a deterministic Ito check using
  its Figure4b parameters confirms the sign qualification. Its printed stopping generators also use Q drift
  despite P-valued objectives; absent author code, the numerical implementation remains unverified.
  Two fitted VIX curves and numerical stopping boundaries are not historical net trading returns. Its roll
  yield is a price-difference decomposition, not automatically a percentage return or a roll-date cash payment.
  Translate price-value objectives into actual futures margin/cash and native costs before account claims.
  Evidence: full uploaded 2015 PDF and deterministic arithmetic only; no return test or live change.
  Limits/next check: no owned dated VX/spot curve panel; a separate justified project would first reconcile
  one timestamped curve, physical/pricing calibration and a cash ledger. No current NQ/ES/Apex allocation earned.

E09 source follow-up — Dogs of the Dow conceptual review, SSRN2697334 (2026-10-31):
[review](results/dogs_dow_2697334_20261031.md). The source describes mixed cited evidence and cases where
apparent outperformance disappears after risk, costs and taxes; it performs no original execution/return test.
For any separately justified equity replication, reconcile actual price P&L, dividend cash, corporate actions,
fees and taxes. Do not double-count distributions through adjusted prices plus cash credits. That cash-accounting
check is our implementation lesson, not an execution saving measured by this paper. Historical yield ranks need
as-of dividends and membership; yield alone does not establish safe recovery or current net alpha.
No strategy trial, promising-queue entry, plan placement or execution-policy change is earned from this source.

### E10 — Liquidity compensation, turnover and costs

- [Ates–Wang floor/screen FX review](results/ssrn754946.md), SSRN754946, May 2005:
  2003–04 electronic venues had tighter reversal-estimated spreads and an increasing
  price-discovery role. This is historical venue evidence, not a profitable lead/lag
  signal or our executable savings. Preserve quote-versus-trade estimator distinctions,
  stale-price/receipt clocks, contract/tick regimes and Hasbrouck ordering bounds.
  Daily fitted weights and full-contract-period volatility buckets are retrospective;
  no entry can use them as contemporaneously known features without a past-only redesign.
  Owned one-minute 6E OHLCV lacks the paired venue histories and executable quotes.
  Source inspection and table-arithmetic checks only; no empirical replication or
  strategy-return trial. Two visibly inconsistent source-table cells remain unresolved.

- Event-time follow-up, retained 2026-10-30: Bowe, Hyde and McFarlane (2007),
  [SSRN 1025241](https://ssrn.com/abstract=1025241), [full review](results/mexder_duration_1025241_review.md).
  Historical MexDer TIIE28 duration/volume effects depend on structural specification and processed event clocks.
  Equal-price thinning, same-time aggregation, overnight compression and seasonal adjustment alter what duration
  and volume measure. Preserve contract/event identity and available-at clocks before comparing fills or impact.
  A current-trade explanatory coefficient is not a pre-order forecast, a negative signed-volume coefficient is
  not a short signal, and a model-implied liquidity share is not achievable execution savings.
  Printed-table audit finds Table6's spread formula does not reproduce its headline using either Table4 panel;
  nearby duration/volume t-statistics are weak under two-sided inference. Source data and transformations remain
  unverified. Retain measurement/model-risk caution only; no alpha trial, cost calibration or live-order change.


Source: Swan (2002), [SSRN 251399](https://ssrn.com/abstract=251399).
[Saved review](results/equity_premium_liquidity_review_20261029.md). Retained by user 2026-10-29.
- Use: distinguish turnover from spread, depth, impact and resilience; distinguish compensation for illiquidity from predictive alpha. Large trading volume need not imply cheap executable liquidity.
- Evidence: historical asset-pricing model and fits, not independently reproduced. Model-implied trading benefits are not cash trading profit.
- Limits: historical equity-versus-Treasury estimates do not establish current futures costs, a directional signal or a benefit from increasing turnover.
- Next check when relevant: measure actual same-contract spreads, depth/impact where available, fees and adverse fills in the relevant market state; never import the paper's historical cost percentages into ES/NQ tests.
- Status: retained contextual liquidity-risk reference; no strategy trial or allocation.

### E11 — Event-information clocks and attribution

- Bridge history follow-up, retained 2026-11-08: [gap/build audit](results/bridge_gap_provenance_20261108.md).
  Missing one-minute bars mix normal closures, historical schedule changes, no-print intervals and source
  omissions. CME's daily 15-minute pause ended June 28, 2021; current hours cannot be applied retrospectively.
  After scheduled closures and tentative holiday matches, 3,964 labels remain unresolved; other owned
  positive-volume bars corroborate 1,113. They do not restore missing aggressor sides or executable fills.
  Current NQ.v.0 semantics do not certify original dated rolls/build provenance. Preserve raw hashes and
  require source/status, mapping and clock reconciliation before replay/fill claims. Original exports
  unchanged; no imputation, return test, execution-saving estimate or live/platform change.

- Crypto regime/insurance follow-up, retained 2026-11-08: Han,
  [SSRN 6477100 full review](results/ssrn6477100_review_20261108.md), March 2026, Tables 1/3/7/8 and pp. 7–15.
  A regime labelled from final-period buy-and-hold return is unavailable at entry. A causal EMA can avoid that
  particular leak while its chosen strategy/threshold still carries selection and dependent-sample risk.
  Source EMA switching improves mean period return −2.27%→−0.64% (unadjusted paired p=.036); both remain losses.
  Relative bear outperformance can be lower beta/cash exposure, not profitable insurance or protection before
  an account breach. All fee-study means are negative, including .1% cost; no low-fee viability or measured saving
  follows. No actual human intervention policy was tested. For separately justified comparisons, freeze feature/
  sentiment availability, first fills, cash-versus-hold behavior and matched exposure/turnover controls before
  dependence/selection-aware inference and native paths. Source/arithmetic review only; zero return trials,
  no new monitor/switch/queue candidate or book change. Do not infer competing bot orders from price patterns.

- Commodity-turning-point follow-up2026-11-02: [source-method review](results/scout_overreaction_source_gate_20261102.md),
  Borgards/Czudaj/Hoang2021, DOI10.1016/j.resourpol.2020.101966. Capturing a fixed fraction of an ex-post reversal
  does not define causal entry/exit availability. The inspected model assumes20%capture and omits fees/slippage;
  no net return or execution saving reproduced. An extremum event time differs from its confirmation time;
  distinguish descriptive labels from executable fills and keep quote gaps visible. Reject this convention at
  the source gate; a different real-time rule needs independent merit and preregistration, not a rescue variant.

- Recursive-smoother follow-up, retained 2026-10-30: Harris and Yilmaz,
  [SSRN 1259661](https://ssrn.com/abstract=1259661), [full review](results/fx_low_frequency_1259661_review.md).
  A full-history smooth trend is not a historical signal vintage. Their illustrative decomposition is explicitly
  full-sample; their trading evaluation is described as recursive. Do not conflate those or diagnose a leak merely
  from the use of HP/kernel smoothing. Freeze each signal's available-at data and specify whether the prior
  endpoint is refitted at today's decision or retained from its earlier vintage. Their returns include carry and
  ignore trading costs; neither smoothing accuracy nor low turnover establishes executable net savings.
  Monthly spot/forward carry and dated-futures collateral/roll accounting are different implementations.
  Evidence: source inspection plus public FX data intake only, no strategy or execution-return replication.

- WASDE follow-up, retained 2026-10-30: Zhang, [SSRN 4841490](https://ssrn.com/abstract=4841490),
  [full-source review](results/wasde_volume_4841490_review.md). An announcement-day-inclusive return is not
  necessarily executable using a forecast revealed that day. Monthly USDA forecast revisions are not consensus
  surprises; unsigned futures/options volume is not signed informed flow. The source's same-month non-event
  volume baseline can include future observations and cannot directly become a pre-event feature.
  Source regressions are not net trade returns or measured execution savings. Confirm historical release/session
  regimes, input publication/receipt, option-underlying mapping, pre-event aggregation and first executable price
  before a separately registered test. More event volume does not establish lower spreads or price impact.
  Matching agricultural/options data and exact specifications are missing; zero return trials and no live changes.

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

### E11 follow-up — Speed competition depends on information and repeat participation

Source: He and Kang, *Speed Competition and Strategic Trading*, [SSRN 4940960](https://ssrn.com/abstract=4940960),
uploaded manuscript; [review and formula audit](results/speed_competition_4940960.md), 2026-10-30.
- Useful lesson: distinguish signal arrival/quality, execution speed and the ability of fast traders to participate
  again later. In the benchmark, fast traders trade early only and speed competition has a hump-shaped effect on
  final price informativeness. Allowing them to trade both rounds improves informativeness in the reported numerical
  extension. Neither conclusion determines an outside trader's return or optimal delay.
- Evidence: analytical results and source numerical illustrations, with a scoped independent precision-formula
  check. The source's institutional-ownership/future-earnings empirical section is proposed, not estimated.
- Limits: private fundamental knowledge or private signals, strategic risk-neutral traders, random liquidity noise;
  no calibrated NQ/ES participant panel, native latency/fills or measured cost savings. Minute event rates do not
  identify the number of informed fast traders. Future earnings used for evaluation must not become trade features.
- Next check only for a separately justified execution problem: timestamped native orders/quotes, information
  events and identifiable participation, then fixed-parent-signal delay comparisons including noncompletion,
  adverse selection and costs at actual size. No infrastructure, protective-order or live-policy change follows.
- Status: execution/identification reference; DON'T TEST as source-defined alpha, zero economic return trials.

E11 follow-up — Song et al.2015, SSRN2631135, retained2026-10-31:
[review/data gate](results/news_sentiment_2631135_20261031.md). Weekly news features must use available entity-level
analytics and wait until all included articles/scores have arrived before a later fill. News source timestamps,
analytics availability/receipt and subsequently corrected archive/model versions are separate clocks. Sample API
messages are not historical entitlement or point-in-time coverage. Preserve missing news, duplicates and revisions.
The source's weekly10%loss review is not an intraday protective stop; its reported strategy DD is49.09%/56.37%.
Evidence: source/schema inspection plus two feature-arithmetic fixtures; no independent return, execution saving
or live-policy change. Need actual dated article/entity/price ledgers and explicit loss-review execution first.

E11 follow-up — NG export precision and exchange-clock audit, retained2026-10-31:
[Corrected intake](results/ng_corrected_intake_20261031.md). A chart showing0.001ticks did not make a two-decimal
CSV native precision: all4,346,668old OHLC cells lay on0.01; the replacement has10,624,829sub-cent cells on the
proper0.001grid. Existing exporter Decimals3and full-window inputs repaired this without a code change.
MultiCharts Exchange labels use QuoteManager's configured exchange timezone. Repaired NG's18:01reopen/17:00close
supports NewYork labels; verify configuration before mapping an EIA10:30ETrelease to raw minutes. Do not choose
between clocks on P&L. Evidence: raw-file counts, user settings screenshots and winter/summer conversion fixtures;
not measured fills, strategy profit or execution savings. Full native contract/roll/event/cost admission remains open.

E11 follow-up — full NG announcement source supplied, retained2026-10-30:
[Review](results/ng_3575861_full_review_20261030.md), SSRN3575861, pp19–20 Table8. Use executable sides:
the paper's later-panel gross2.91% becomes−0.90%atbid/ask before funding. Its positive-surprise pre-announcement
subsample uses a value known only after entry, so it cannot supply a causal pre-entry filter. Evidence is source
inspection/Table8extraction, not verified fills or savings. Full-source reading closes the calendar-short nomination;
no native return or account stage is earned. Preserve individual contracts, actual release calendars, source
annualization and time-zone mapping for any separately justified future comparison. No live changes.

### E12 — Realized-variance measurement: microstructure noise, units and availability

- Monthly trend/risk follow-up, retained 2026-11-08: Shi and Lian,
  [SSRN 5140633 full review](results/ssrn5140633_review_20261108.md), February 17, 2025, pp. 17–25 and 33–35.
  Compare trend filters using their return-weight kernels and effective horizons before treating a different
  indicator as new information. EMA centers of mass in the source are not standard EMA periods. A centered
  smoother uses future observations; a causal rolling estimate needs its own as-of vintage and first-fill clock.
  Inverse-volatility weights do not equalize covariance-aware risk contributions or guarantee portfolio risk:
  the source's approximate 12% portfolio-volatility objective accompanies 18.51% reported realized volatility.
  The combined 1/3/12-month basket's 16.24% annual return / 0.88 Sharpe / −22.63% drawdown is an author claim,
  without a Table 6 transaction-cost bridge, not verified net returns, execution savings or intraday protection.
  Monthly crisis alpha does not establish an offset before an Apex breach. For separately justified research,
  inspect lagged covariance, leverage/margin, netted integer positions and complete native paths before account
  conclusions; do not use this reference to rerun the already-studied generic trend family. Zero new return trials.

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

- Weekly cross-review2026-10-30: a fill-sanity gate must retain legitimate closed same-chart-bar trades;
  separate delay-eligible trades and open-position sentinels. The new L1/G10 wrapper omitted572of1756closed
  Vault Break rows. A synthetic impossible same-bar fixture passed the wrapper despite failing direct fill sanity.
  This establishes incomplete gate coverage, not invalid historical fills. Publish expected/checked/missing counts
  before claiming every fill passed. [Evidence and proposed deciding check](../cross_review/2026-10-30_codex.md).

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

- Weekly cross-review2026-10-30 ([findings](../cross_review/2026-10-30_codex.md)):
  liveness requires a recent capture, not merely a row that was fresh when written. Pinned premarket code accepts
  stale00:05ACCT/POS/SIG snapshots as ALL GREEN; a healthy process line does not establish chart activity.
  The account-floor watchdog scan also contains a literal U+0002 path byte and cannot enumerate normal daily logs.
  Offline byte/path and fake-file checks reproduce these source defects. The installed VPS copy and PowerShell
  runtime were not inspected; correction/deployment is not performed or certified here. Use an injected timezone-aware
  as-of clock and disconnected temporary-log fixtures before relying on monitoring coverage.
- [Post-fix acceptance follow-up](results/weekly_fix_followup_20261030.md), Claude302abe2: the malformed log path
  is repaired and the exact midnight-snapshot fixture now alerts. Remaining fake-log cases still return ALL GREEN
  for a21-minute effective feed age and for fresh ACCT alongside stale POS/SIG. Add elapsed time to captured
  bar age; age each record type independently; fixed UTC−5 is wrong after the DST change. Source correction,
  PowerShell runtime and installed behavior remain separate evidence states. No live-system change was made here.
- [Latest reply checked](results/weekly_fix_reply_20261030.md), Claude724d1bb: timezone-aware clocks and separate
  POS/SIG ages now work in the named fixtures. Effective feed tolerance was also raised from15to45minutes;
  the21-minute case remains green under that changed policy. Archived ACCT cadence is mixed, not universally30minutes.
  Preserve per-chart capture/feed-clock justification and installed acceptance as separate requirements.

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

E30 source follow-up — Till/Eagleeye (2017), SSRN2942340, reviewed2026-10-31:
[full review](results/till_2942340_20261031.md). A storage operator's buy-summer/sell-winter transaction includes
physical delivery, storage capacity, financing and operating costs. Futures-only spread P&L is not the same locked
margin. Index-roll anticipation needs actual two-maturity identities, both-leg cashflows and synchronized execution;
price pressure can be anticipated and disappear. The article provides examples, not measured net returns or execution
savings. Retain existing quote/sample gates; no continuous-price replacement or new economic trial is justified.

E30 acquisition follow-up (2026-10-31): [actual wheat data audit](results/commodity_roll_data_20261031.md).
Downloaded multiple-price fields with maturity IDs are better than continuous prices, but their selected annual
December holdings need not match a benchmark's nearby roll. A mini-price series cannot inherit standard-contract
liquidity or execution costs. Any paired intraday observation is not a complete synchronized executable path.
No return or execution-saving test was run.

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

E34 follow-up2026-10-31 — [calendar-overlap source assessment](results/scout_owned_data_discovery_20261031.md),
SSRN6818821, author-uploaded selected sections, not a complete paper replication. A close-to-open outcome signed
by the completed day's close cannot assume the direction is known before a guaranteed same-close entry. Bind
signal availability and order acceptance separately; a later futures entry or reopen changes the return interval.
Date-only provisional2018–22audit finds0/20quarter ends on third Fridays and0/5June last Fridays on third Fridays;
check source prose against actual calendar code. This does not disprove daily LETF overlap or estimate a saving.
Next check for an eligible new study: freeze exact kernels/intensities and official calendar provenance before returns.

E34/E18 discovery note2026-10-31 — SSRN7458058's abstract describes an NG fill-convention bracket and matched
random-entry populations with identical exits/costs. Useful proposed controls; full paper/rule/tape not obtained,
so its numerical advantage is an author claim, not verified execution savings. Minute OHLCV cannot establish
queue position or first-tape-print fills. Record the fill bracket for future execution studies; do not infer an NG
strategy from generic mean reversion. See the same discovery report and per-paper7458058record.

E34 follow-up2026-11-01 — [public daily-input intake](results/scout_expanded_data_intake_20261101.md).
Use: a public continuous daily replication panel is not a dated-contract ledger or an intraday fill/adverse path.
The acquired84-series panel and separate oats/OJhistories have different constructions. Supplemental2018–22
date-label counts include multiple observations on1,257oats and1,260OJdates; do not choose daily last rows
without a verified settlement/receipt clock. Name/coverage matches are not native contract certification.
Evidence: pinned downloads, hashes and schema/date/value-quality scans only; no strategy returns or execution savings.
Limits: no input admission, source roll replication, integer portfolio or funded inference; raw data remain local.
Next check for an eligible future study: reconcile one complete source-compatible formation/roll month and preserve
missing observations. Do not fill returns with zeros or import third-party proportional costs as broker tick fees.

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

### E36 — Stop-limit protection: price control is not a loss cap

Source: user-pasted QuantJourney O08 daily-SPY/QQQ/IWM example and screenshot, 2026-10-30.
[Saved review](results/qj_stop_limit_20261030.md), [pretest plan](plans/qj_stop_limit_mechanics_20261030.md).
Related: E03 order-state reconciliation, E05 missed fills/opportunity costs, E18 bar-fill conventions.
- Use: a sell stop-limit can activate after a gap yet remain unfilled below its limit. A hypothetical entry $100,
  stop $96/limit $95.50 remained held through prices $90 then $80 in our fixture. Price control on completed fills does
  not cap the open-position loss; commission also reduces net proceeds below the gross fill-price floor.
- Evidence: eight predeclared synthetic scenario groups executed the archived strategy class and unchanged public
  execution modules at QuantJourneyOrg/quantjourney-bt commit4f403d8. The source's separate daily protection branch left
  the entry day unprotected, consumed a simultaneous bearish crossover, and kept its protection flag set after
  an injected order rejection. Ordinary cancellation/exit and a partial-fill remainder case behaved as recorded.
- Limits: public engine 0.12.5 is not certified as the packet's 0.10.0+private engine. These constructed mechanics
  are not observed failure rates, native fills, execution savings or an independently reproduced return test.
  The educational source's reported 1.99% CAGR/0.02 Sharpe provides no demonstrated current-account contribution.
- Prerequisites/next check for a separately justified execution project: actual parent/child order IDs and states,
  entry-fill/protection clocks, post-trigger quotes/prints, partials, cancellations and explicit fallback/deadline
  policy. A boolean set at submission is not proof of accepted protection. Bar high/low alone cannot establish queue fills.
- Status: execution reference retained; zero economic return trials, no plan placement or execution-policy change.

### E37 — Realized payoff expectancy, costs and account survival

Source: user screenshots of Veles, *Wrong 80% of the Time and Still Winning: Paul Tudor Jones and the Payoff Equation*,
reviewed 2026-10-30. [Saved review](results/payoff_equation_review_20261030.md). Original PDF/version not authenticated.
Related: E09 cash/cost reconciliation, E15 tail risk, E35 fill-anchored exits and E36 nonguaranteed protection.
- Use: for nonzero closed outcomes, expectancy is `pW-(1-p)L`, with realized net winner/loser magnitudes.
  A target-to-stop setting is not the realized average-win/loss ratio. Do not subtract fees twice when outcomes
  already include them; when using gross outcomes, include all execution costs explicitly. Track zero outcomes separately.
- Evidence: deterministic arithmetic independently checked, including 20% wins/5x payoff -> +0.20 average-loss units.
  Higher payoff with a lower win fraction need not improve expectancy. Celebrity fund statistics remain unverified;
  Odean's primary table supports the cited disposition effect, not a futures alpha rule.
- Limits: average realized loss is not necessarily initial stop risk or margin. Closed trades alone can omit open
  losses; positive expectancy can coexist with long losing streaks and an account breach before the next winner.
  A last 50 trades snapshot does not establish stable after-cost edge or valid current-account placement.
- Prerequisites/next check when a separately justified strategy is tested: reconcile quantities, closed/open cash,
  protective fills, costs, timing and full daily marks; evaluate actual integer-size account paths. Any target/stop
  change alters outcomes and must pass the existing preregistration/trial/account gates.
- Status: risk/execution diagnostic reference; no standalone candidate, new return test or plan/exit change.

- Follow-up: Maymin and Maymin, [SSRN 1896146](https://ssrn.com/abstract=1896146),
  [full-source review](results/optimal_indicator_framework_1896146_review.md), retained 2026-10-30.
  A known conditional mean gives a maximum-gross-return direction rule under a notional cap; conditional
  first/second moments give a different information-ratio sizing rule. These are theoretical benchmarks, not
  estimated net execution savings. The source explicitly allows easier or cheaper execution to favor another rule.
  Turnover costs depend on the previous position; bounded notional does not model Apex's intraday floor or payouts.
  Before applying this to a separately justified predictor, freeze availability/label clocks, past-only estimates,
  turnover, integer quantities and cost accounting; compare net account paths against the unchanged base.
  No predictor, return trial, size change or implemented execution change follows from this review.

- Harris source follow-up ([SSRN2810170 review](results/ssrn2810170_review.md)): identical toy returns/mean/sample SD/final wealth can produce different chronological drawdowns. Our supplied-number audit gives10% versus27.1%, correcting the source's approximately33% second value. This illustrates path risk, not measured Apex probabilities. Historical-bootstrap and significance results do not guarantee stability through an unseen regime; source p.8's quoted mean/SD also fails to establish its “more than7 SD” claim. No market return replication or native execution result; preserve existing statistical, chronological account and frozen monitoring gates.

### E38 — Commodity stop overlays, exposure redistribution and return/NAV accounting

Source: Hossein Rad, December 2012 EDHEC MSc thesis, SSRN 2614241; uploaded full 56-page PDF reviewed 2026-10-31.
[Saved review](results/rad_double_sort_review_20261031.md), [feasibility sheet](evidence/rad_double_sort_20261031.md).
Related: E09 cash/contract accounting, E15 tail risk, E36 nonguaranteed protection, E37 payoff/account survival.
- Use: distinguish a daily-close calculation affecting the following day from an accepted intraday protective order.
  Removing one position and redistributing its weight among survivors can preserve gross exposure and increase
  concentration. It is a different experiment from holding the freed risk in cash. Record both trade removal and
  exposure transfer, their fees and decision-to-fill clocks; reopening needs explicit state and weight rules.
- Evidence: full-source inspection and deterministic arithmetic only. The source reports a 5% whole-book overlay
  reducing 30-day 99% VaR 20.27%→13.76% and annual volatility 24.91%→22.47%, while annual excess return 20.22%→19.93%,
  before costs. Preserve that reported risk reduction rather than saying every stop failed; no raw returns or
  independent economic replication support it. Paired daily-mean p=0.079 does not test the VaR change's significance.
- Accounting lesson: instrument log returns, portfolio simple/log returns, additive fixed-notional P&L and compounded
  NAV are different quantities. Here Table 1's 663.66% sum gives 1+6.6366=7.6366, matching the author's $7.63 chart;
  it is not reconciled compounded wealth. Exponentiating the sum also does not repair weighted long/short log
  accounting. Reconcile actual quantities, variation margin, collateral, rolls, open marks and costs first.
- Limits: monthly eight-position commodity book at 2x gross exposure is ineligible for the four Apex homes as written.
  Selected thresholds, missing-return weight redistribution and ambiguous trigger/reopening details prevent an
  execution saving or maximum-loss claim. The source's stop overlays are not evidence to remove current protection.
- Prerequisites/next check for a separately justified project: identified contracts, both signal maturities and
  availability clocks, exact trigger/weight/cash policy, executable next-day prices and native fees; reconcile one
  formation/roll month before any return study. Non-positive prices cannot silently disappear from a log-return test.
- Status: execution/risk/accounting reference retained; no new return trial, account placement or exit-policy change.
  [Offline build checkpoint](results/rad_double_sort_build_20261031.md) adds strict missing-panel, contract/clock,
  integer reference-notional and delivery-action checks. Its23 synthetic cases do not verify historical fills or NAV.

### E39 — Unfinished MC positions and stale report coverage during a data rebuild

Source/review + date: [extended-data audit](results/extended_data_refresh_20261030.md), 2026-10-30;
Claude source snapshot `86df2c0`, `analysis/codex_refresh_audit.py` and its saved coverage tables.
- Use: distinguish a report's `open` sentinel from an actual exit, and price-history coverage from strategy-ticket coverage.
- Evidence: reproduced standard-builder failure on a funded-ONB EntryShort at 10/12 09:15 paired with an `open` ExitShort
  labeled midnight. It creates exit-before-entry indices and an empty path. A scoped adapter excludes the unfinished
  position; the complete original rebuild succeeds with 343 closed ONB trades. Five regression checks pass.
- Coverage: raw NQ through 10/30; dashboard cache through 10/09; the four live-strategy reports end 10/09–10/13.
  Importing old tickets onto a longer grid does not regenerate signals; padded zero days are not verified no-trade days.
- Limits: no current missed-trade count, native broker fill finding, strategy improvement or current-plan revalidation.
  Production importer is unchanged; the adapter is an offline research artifact.
- Next check: fresh same-input reports, explicit cache coverage gate, then expected/chart/broker reconciliation;
  earlier unavailable chart logs remain unknown. Related: E04 (record semantics), E23 (account/logger fields).

### E09 follow-up — common-coverage account-state replay (2026-10-30)

[Fixed-ledger account replay](results/swing_kind_account_replay_20261030.md) adds 1,000 paired histories per
account/cohort over a common-source window ending July 7. Numeric kinds restore $129/MNQ and change 48 daily
minima; 160 exact canonical-simulator parity checks pass. This does not imply monotone payout improvement:
150K recent-pool first-year payouts decrease $6 while two-year payouts and blown share are unchanged.
The adopted replacements do not clear both base and empty-slot comparisons. Evidence is historical simulated
accounting with inherited path approximations, not native fills or a plan change. The broader-window replay
above uses a different pool and seed; the two reports consistently leave adoption unproven.

### E40 — ES order-flow shocks are absorbed within one second; macro releases raise price impact

Source: Takahashi, arXiv 2508.06788 (paper, scout 2026-10-29); papers/SCOUT_LOG.md.
- Use: one-second structural VAR on ES returns and order-flow imbalance per 15-minute interval: impulse responses die out almost entirely within a second; around macro announcements price impact per unit of flow rises, flow impact falls, return volatility spikes. Spreads / liquidity drive intraday variation of impact.
- Evidence (author claim): ES E-mini, one-second data, heteroskedasticity-identified SVAR.
- Limits: no trading test; confirms E25 (order flow doesn't predict NQ at 5-30 min) at the 1-second end; release-time fills pay more impact.
- Next check: none; relevant when sizing orders at 07:30 / 09:00 CT releases.
- Status: market-behavior reference.

### E41 — No-stop overnight edges: a protective stop can delete the whole edge

Source: Nocturne research note (L. Franceschetti, user upload 2026-10-30), rebuild [nocturne_test.py](../../analysis/nocturne_test.py). Claude, 2026-10-30.
- Use: before bolting a stop onto a strategy that was found without one, test it: the profit may come from holding through the drops.
- Evidence (historical test): NQ long 17:05 -> 07:20 with an R^2 filter, 1,449 nights 2017-26: no stop $90 a night (t 2.56), worst night -$11,402;
  with a 0.5 x 15-day ATR stop $39 a night (t 1.35), 2024-26 negative. Overnight Tick / VIX (plan, no stop either) shares 338 of its nights.
- Limits: one rule, one stop width; Apex evaluations can't carry an unbounded night (floor touched intraday = failed, see E21).
- Next check: size no-stop overnight pieces so the worst historical night stays below half the account's trailing room.
- Status: market-behavior reference; Nocturne C, watchlist.

### E42 — Backtest-live parity: six implementation defects and a ten-point checklist

- Source-version follow-up, retained 2026-10-30: Krishnamurthy, [SSRN 3124271](https://ssrn.com/abstract=3124271),
  [full-PDF and figure review](results/mean_reversion_beta_zero_3124271_review.md). A reported year of paper trading
  used a one-day liquidity lookback; the intended five-day version was subsequently backtested without reported
  prospective validation. A forward record validates only the implemented frozen version, not its revised intent.
  Preserve code/input hashes, ranked holdings and order clocks with each report, and keep old/new evidence separate.
  A zero-beta target does not establish realized neutrality or protection from sector/news, borrow and funding losses.
  Evidence: author screenshots and admitted code correction, not independently verified fills or execution savings.
  No current strategy rerun, monitoring installation or portfolio change is warranted by this note alone.

Source: Vidovich & Zerjal, arXiv 2610.21846 (paper, scout 2026-10-30); papers/SCOUT_LOG.md.
- Use: one live intraday stock system, six defects that summary statistics never showed: (1) default data feed carried
  0.1-2% of the real opening-minute volume, (2) dividend-adjusted history vs unadjusted live fills, (3) a field only the
  backtest had, (4) UTC timestamps read as New York time, (5) the replay requested different inputs than live, (6) settings
  switched on that never reached the order code. None was found from results; each by one concrete look (one live trade
  against the cache, one bar from several sources). Matching decisions on 7 of 8 live days did not catch a broken harness.
- Our equivalents: (1) MultiCharts `Volume` = up-ticks vs our CSV totals (FC 2B near-threshold mismatches); (2)
  unadjusted continuous futures, roll jumps at 03:32 / 17:01 CT (drop roll bars); (4) the CL Sunday report runs on Eastern
  time (found by `analysis/leak_checks.py` L1 at −60 min, 2026-10-30); (6) the account field on copied charts sent #3's
  150K-size orders to #2 (MULTICHARTS_PITFALLS, 10/26). Their checks we already run: replay live trades and match prices
  (`analysis/live_vs_backtest.py`, Apex Trade Logger), daily live-behaviour checks (`analysis/vps_health.py` vs
  `live/expected_setup.json`), fill-in-bar check (leak_checks L1).
- Gaps to close (smallest next checks): test every timestamp helper on a winter and a summer day (DST weeks where London /
  Chicago offsets differ); after any data rebuild, match one live fill to the tick; for each MultiCharts input, confirm in
  the trade log that changing it changes an order (e.g. size inputs after cushion sizing).
- Status: process reference; no strategy.


### E43 — Better trade accounting need not improve funded-account outcomes

Additional replay: [5,000-history rebuilt bench](results/swing_target_exit_replay_20261030.md),
source 86df2c0. Same $132/MNQ ledger correction; selected corrected-minus-legacy
two-year payouts +$2 (50K) / -$2 (150K), with paired 90% intervals crossing zero.
The rebuilt day universe extends to 10/30, unlike the other frozen 10/09 replays;
do not pool them or attribute cross-run differences solely to the accounting fix.

Source/review + date: [Swing Target exit-kind replay](results/swing_kind_replay_20261031.md), 2026-10-31; runner `analysis/codex_swing_kind_replay.py` and retained paired histories.
Execution question and useful lesson: numeric exit types govern both fill costs and the final adverse mark. After correcting them, replay the account; payout timing and subsequent integer sizing can change the sign of the effect.
Evidence: synthetic stop/target fixtures plus historical account simulation, 500 paired 500-day histories per account. Corrected ST nets gain $132 total per MNQ, but the 50K ADD arm has one additional failed history (7.8% -> 8.0% blown); selected 50K/150K replacements have unchanged two-year outcomes versus legacy and do not establish gains versus BASE.
Market/platform and timing limits: historical roster and repaired CODE_BE ledger, not exact holiday-skipping v3 or today's T_ONESIDE roster; inherited continuous bars, NQ/10 fees, OT/CLS adverse and MOC close-mark approximations. No native fill evidence.
Data/prerequisites: frozen ledger, minute grids, hashed MultiCharts reports, shared simulators, paired block histories and EMPTY controls; full manifest retained.
Smallest justified next check: independent review of this replay; separately preregister current-roster/exact-v3 validation at actual micro fees before changing the adoption rationale.
Status and superseding evidence: adapter mechanics verified; account adoption gains inconclusive. No live or plan change. Claude's three colliding E29-E31 additions are preserved as E40-E42 during this handoff merge; existing Codex E29-E38 identifiers are retained.

### E44 — Weekly COT inventory changes do not identify executable order flow

Source: Kaul, Naranjo and Stefanescu, [SSRN 2311859](https://ssrn.com/abstract=2311859),
[full-PDF review](results/ssrn_2311859_review_20261030.md), retained 2026-10-30, printed pp. 7–8, 13–18, 21, 29.
- Use: distinguish changes in group long-minus-short inventories from signed transactions or actual liquidity demand.
- Evidence: author regressions relate Tuesday-to-Tuesday commodity returns to same-period and lagged position changes.
  Friday publication prevents treating same-week positioning as a pretrade signal; even the lagged week partly elapses
  before publication. Historical semi-monthly observations before 1991 were backfilled, not necessarily then public.
- Limits: no native orders, spread/fill measurement, causal identification or demonstrated net trading returns.
  Energy is an exception to several pooled findings; the sample excludes NQ/ES. Price-impact coefficients are standardized,
  not dollar savings or an instruction to follow/fade speculators.
- Next check only for a separately justified proposal: exact publication/vintage clocks, native contract identity and
  a prespecified executable window, with costs and ordinary momentum/reversal controls before return selection.
- Status: source/measurement reference; no new economic trial, trading grade or plan change.

Source-specific follow-up, 2026-10-30: Laubsch, Smales and Vo (2023),
[SSRN 4534852](https://ssrn.com/abstract=4534852), [full uploaded-paper review](results/cot_52week_4534852.md).
Across 12 commodities in 1992–2022, commercial position responses are contrarian and non-commercial responses
follow momentum, moderated at 52-week highs and accentuated at lows. These explain positions, not an executable
return signal; the source finds little timing ability. For CL, Table 4 position→return p-values are 0.280/0.566
(commercial/non-commercial); gold 0.623/0.738. Tuesday-to-Tuesday returns partly elapse before normal Friday
publication, so lagged regressors do not alone establish an available signal. CFTC classifications describe
predominant business purpose, not each order's motive or liquidity role. No forced order/deadline, net strategy
return or intraday transfer is established. Retain as a negative predictive/clock caution, not another COT sweep;
zero new return trials. Any later causal rule needs actual release/receipt times and a price-only baseline.

### E45 — Cointegrated log prices do not specify an executable futures hedge

Source/review + date: Ungever (2015), [SSRN2896370](https://ssrn.com/abstract=2896370),
user-uploaded full text; [review](results/agri_cointegration_ssrn2896370.md), 2026-10-30.
Execution question and useful lesson: translate a statistical log-price spread into
explicit native-contract quantities, multipliers and roll/cash accounting. Equal
dollar legs and cointegration coefficients do not automatically imply identical
portfolios or market neutrality. Resolve trade direction before implementing it.
Evidence: source inspection, not return replication. Upper-bound prose on p.30
shorts cotton/buys coffee; the profit equation on p.31 is long cotton/short coffee.
Costs are ignored (p.27); only two/three completed trading-period trades support
the reported annualizations. No independently verified execution savings or alpha.
Market/platform limits: Bloomberg daily rolled agricultural futures, 2004–15;
trading holds average 159/142 days. Not intraday Apex or NQ/ES evidence.
Data/prerequisites: timestamped native-contract prices, unambiguous leg direction,
integer hedge and rebalance rule, both-leg and roll costs, capital/margin definition,
and per-trade ledger. Matching local price histories were not found.
Smallest justified next check: only reconsider with corrected source specification
and stronger independent net evidence; no proxy or intraday conversion is earned.
Status: retain accounting/implementation caution; source-defined strategy rejected
at evidence gate, zero return trials, no promising-candidate or trading-plan change.

### E46 — Spot market power: endogenous supply incentives and hidden participant identity

Source: Muermann and Shore, *Spot Market Power and Futures Market Trading*, March 2005, SSRN 681202;
uploaded 36-page full text. [Review](results/spot_market_power_681202_20261030.md),
[evidence decision](evidence/spot_market_power_681202_20261030.md). Related: E09 complete leg/cash accounting,
E10 liquidity compensation, E11 information clocks and E29 signed participant positions.
- Use: distinguish profits earned by controlling physical supply from profits available to an outside observer.
  Futures positions can change the supplier's subsequent optimal spot action; market makers anticipate that incentive.
  Hidden participant identity matters, so aggregate volume or commercial positioning is not an identified producer signal.
- Evidence: analytical equilibria and source inspection only. In the concealed-position model, the producer randomizes
  direction; the separate non-producer model earns on an earlier derivative while accepting losses on later price-moving
  trades. Retain both legs and exact contract payoffs. No empirical return, measured price impact or execution saving.
- Limits: stylized linear demand, competitive risk-neutral market makers, specified inference/beliefs and no effective
  storage; Section 4's initial contract pays on an intermediate futures price. No calibrated contemporary NQ/ES/CL rule.
  The complete-hedging impossibility concerns price-contingent contracts in the model; demand-contingent contracts
  provide an explicit complete-hedging exception. Historical oil-liquidity remarks are not current CL observations.
- Data/next check only for a separately justified event: legally observable, as-of actor-linked positions, physical
  supply/inventory decisions, contract-stage payoffs, contemporaneous quotes and native costs; audit availability and
  directional identification before returns. Our aggregate COT and continuous OHLCV do not supply these states.
- Status: execution/market-structure reference; no new return trial, strategy queue entry, allocation or live change.

Delegation/information-production follow-up: Kyle, Ou-Yang and Wei, *A Model of Portfolio Delegation and Strategic
Trading*, May2010, [SSRN1360783 review](results/portfolio_delegation_1360783_review.md),
[evidence](evidence/portfolio_delegation_1360783.md). Source-only theoretical result: incentives change information
acquisition, effective risk aversion and impact jointly; higher incentives increase effort but need not raise trading
intensity. More uninformed trading can increase price informativeness for sufficiently risk-tolerant managers.
Total observed volume is not identified uninformed demand, and estimated price impact is not an unconditional
informativeness measure. Informational rents in the model require a private payoff signal, not a public-volume rule.
The p.23 inverse-square lambda asymptotic contradicts adjacent prose; resolve before numerical implementation.
Owned OHLCV/COT do not identify private signals, compensation or participant hedges. A simulator is feasible, but
no executable signal, measured execution saving, return test or plan placement follows. Retain theory reference only;
any later empirical extension needs its own observable states, availability clocks and preregistration.

### E47 — Obizhaeva–Wang: replenishing depth and large-order execution

Source: [SSRN 666541](https://ssrn.com/abstract=666541), uploaded June 8, 2005 draft,
[review and data gate](results/ssrn666541.md), [model arithmetic](../../analysis/outputs/codex_ssrn666541/model_arithmetic.json).
- Use: distinguish standing depth from replenishment. Under the paper's risk-neutral
  constant-depth/exponential-recovery model, an optimal fixed-parent-order schedule
  combines initial/final blocks with continuous middle trading; risk aversion changes it.
- Evidence: source's analytical result. Our arithmetic reproduces Table 2's rho T=2
  savings of 4.32% and 11.92% under two permanent-impact assumptions. These are modeled
  impact-cost reductions, excluding spread/commissions, not returns or measured CME savings.
- Limits: given parent direction/quantity, simplified exogenous book dynamics, no new
  empirical alpha test or NQ calibration. Owned one-minute OF summaries do not identify
  event-level replenishment, parent orders or queue outcomes. Small integer micro orders
  can lose signal value by waiting; protective stops are not discretionary parent orders.
- Next check: establish material self-impact using native fills and synchronized quotes/depth
  before testing any slicing schedule; then include latency, noncompletion and opportunity cost.
- Status: execution reference only. Zero strategy-return trials; no plan or live changes.


### E49 — EIA surprise labels, tick-rule signs and announcement execution clocks

Source/review + date: Rousse and Sévi, [SSRN 2874907](https://ssrn.com/abstract=2874907), uploaded 2016 working paper;
[full review](results/rousse_sevi_oil_2874907.md), 2026-10-30.
- Use: verify information availability and order-flow sign before deriving an event trade from a conditional chart.
  A surprise classification using the released actual cannot select a pre-release entry. Window OI is known after
  its tape arrives; a post-release strategy must enter after public data receipt and misses the initial jump.
- Evidence: source claims 402 inventory announcements in 2007–14, with 43 positive 3σ surprises and about −0.25%
  preceding drift. Table 3's positive-surprise OI coefficient is −3.529 (t=−3.154); this is not a strategy-return t.
  Abstract/body buyer wording conflicts with OI=(B−S)/(B+S), negative coefficients and the selling conclusion.
- Method limits: second-level volume-weighted transaction prices followed by tick-rule signs are not reproducible
  from minute OHLCV. Normalized imbalance alone does not measure dollar demand or prove information leakage.
  Forecast cross-sectional SD cannot be replaced by historical SD of inventory changes.
- Prerequisites: survey vintages/median/dispersion, matching first-release actuals, exceptional event/receipt clocks,
  sequenced same-contract tape, native CL/MCL costs and a causal rule. The strongest window is tied to the sample's
  former pit opening; persistence after the source-noted 2015 pit closure is unverified.
- Next check only with matching new inputs: one-event series/clock/tick-sign reconciliation, then no-return power
  census. Old EIA price-only follow/fade studies are already negative; do not substitute them for a replication.
- Status: execution/research reference; no new economic trials, net-return demonstration or allocation.

### E48 — Slow FX signal diversification needs roll, cash and selection-clock reconciliation

Source/review: Srivastava et al., *A Multi Strategy Approach to Trading Foreign Exchange Futures*, January 25, 2019,
SSRN 3322717; [uploaded-paper review](results/fx_multistrategy_3322717.md).
- Useful lesson: walk-forward allocation weights do not establish past-only selection of the strategies being weighted.
  Risk targeting and more futures symbols also do not eliminate shared USD exposure or executable roll/collateral costs.
- Evidence: author tables report single-signal Sharpe 0.55, shared-weight best 0.67, currency-specific best 0.88;
  source-table audit only, no independent return replication. The narrative calls a different optimizer best despite
  Table 4's 0.35 versus 0.67; source settings/pruning need clarification before implementing the claimed winner.
- Limits: daily multi-day FX allocations, monthly combination rebalancing; no measured fill savings or NQ/ES edge.
  No disclosed executable cost decomposition, native integer sizing or Apex daily-flat protocol.
- Next check: source clarification and one dated formation/rebalance/roll month with futures cash/fees and
  yield availability reconciled. Owned 6E alone does not supply the eight-currency panel.
- Status: methodological/accounting reference; personal research lead parked, no return test or live change.
  [Requested code-building checkpoint](results/fx_multistrategy_build.md): a declared Python interpretation now
  produces as-of reference positions with clock/contract/risk/margin checks; 26 synthetic mechanics tests pass.
  Static-exposure sleeve covariance is not the source's historical dynamic-sleeve return covariance. No native
  execution, roll/cash reconciliation or economic validation was established by this build.

### E50 — Treasury volume/OI proxies, contract construction and liquidity measures

Source/review: Wenchao Liao, 2008 CUNY dissertation, SSRN1028432; [review](results/ssrn1028432_review.md), archived uploaded PDF and source manifest.
- Execution question/useful lesson: distinguish active-contract liquidity from aggregate activity, and volume from spread/depth/resilience. Volume is not identified speculative flow; total OI is neither identified hedging nor signed demand.
- Evidence status: author-reported daily 1991–2006 Treasury VAR associations, not our replication. Positive volume/volatility association and volume persistence; OI effects depend on contract construction and risk estimator. Chapter2 depth/squeeze material reviews other sources, not new native fill evidence.
- Timing/platform limits: daily data and old Treasury market structure; no demonstrated NQ/ES transfer, execution improvement, price-direction strategy or modern broker fills. Daily finalized OI requires a verified availability clock; adjacent-day interpolation would introduce future information in a live predictor.
- Data/prerequisites: contract-specific daily settlement/high/low/volume/OI, delivery/roll metadata and release/revision clocks. Inspected owned ZN minute schema lacks OI and contract ID; weekly COT is not a daily substitute.
- Smallest justified next check: when a separately specified risk/execution hypothesis exists, establish these fields and compare past-only forecasts against volatility/calendar/roll controls before costed account tests. No acquisition or return study is triggered by this source alone.
- Status: retained methods/execution reference; zero new return trials or measured savings. Related E10 (liquidity/turnover), E12 (risk measurement), E25 (predictive horizon limits).

### E51 — Dated volatility futures: maturity clocks, RMS units and signed hedges

Source: Donninger, *VIX Futures Basis Trading: The Calvados-Strategy 2.0*, January 2014 Rev.1, SSRN2379985.
[Review and completed component test](results/calvados_2379985_20261030.md),
[frozen protocol](plans/calvados_2379985_20261030.md). Related: E09 contract/cash accounting, E12 volatility
measurement, E15 overnight tails, E19 session clocks, E30 paired-leg execution.
- Use: preserve individual expiry identities and actual trading-day maturity. A generic NYSE calendar omits the
  shortened December 5, 2018 VX session; Wednesday-only expiry rules miss holiday-shifted Tuesday contracts.
  VX settlement reference moved 15:15 to 15:00 CT on October 26, 2020. A settlement-based feature becomes available
  after confirmation, not at the start of its calculation interval; a next-session daily Open is only a fill reference.
- Units: the source RMS10 is the root mean square of ten same-contract daily price changes, without demeaning.
  It is not sample SD or return volatility. Basis convergence compensates short-volatility risk; it is not cash carry
  arbitrage. VX outright tick is 0.05 points/$50 at the $1,000 multiplier, distinct from spread ticks or NQ costs.
- Hedge: source Eq7 implies `b1+b2*TTS`; printed Eq8 multiplies the coefficients and contradicts its own sign
  discussion. For n short VX, signed ES quantity is `n*1000*(b1+b2*TTS)/(0.01*SPX*50)`, ordinarily negative.
  Integer rounding, contract rolls and adjustment clocks must be explicit; a linear hedge does not remove jump risk.
- Evidence: full-source and PDF-image inspection, primary Cboe clock/holiday notices, signed-unit synthetic checks,
  and an audited fixed-one-VX 2018–22 historical component test. That component LOST $9,360 net on 58 trades,
  with $18,385 settlement-mark drawdown. This negative finding does not test the preferred ES hedge.
- Limits/next check: raw dated-price provenance, executable opening quotes, intraday variation margin, actual hedge
  contracts/rolls and native integer quantities remain necessary for a separate hedged implementation. Median smoothing
  delayed entry/exit and worsened source results; do not assume smoother indicators create better fills.
- Status: execution/accounting reference retained; naked component rejected, preferred hedge unverified. No execution
  saving, plan placement, trading, broker or live-policy change is claimed.

- FOMC-only follow-up, separate paper [SSRN2544445](results/fomc_vx_2544445_review.md): rendered source charts show an undefined`min-Maturity=5`which prose“nearest”does not capture. Printed Eq3 with negative3.5%leverage gives+18VXunder mathematical floor; screenshotpositive3.5gives intended−17. Preserve source sign/rounding and source-era monthly-contract universe before replication. Cboe legacy/current product documentation has a2018timestamp/schema transition; provider bar labels/timezones differ. A35-minute post-statement cover now crosses the usual press-conference start. Source0.7%sampleDDand zero triggered stops do not cap5%stop/gap risk. Product discovery and failed sample reads are recorded; no intraday panel or return test admitted. Retain a distinct conditional personal lead; the Calvados component failure does not falsify it.

ETP lifecycle/clock follow-up, 2026-10-30: Bordonado, Molnár and Samdal (2016),
[SSRN2753300](https://ssrn.com/abstract=2753300), [full uploaded-source review](results/vix_etp_2753300.md).
The front-VX/spot basis XIV/VXX switching example reports 69% annualized return, Sharpe2.11 and −24.5% DD in
2006–14, with explicit 0.20% fee plus 0.15% spread each side. Preserve those as unreplicated source claims:
prelaunch indicative histories, after-close futures settlement versus same-close ETP fills, and historical
product identities require separate audits. Common-factor price leadership is not verified arbitrage P&L.
Issuer SEC notices establish XIV's February2018 acceleration and SVXY's change from−1x to−0.5x afterFebruary27.
Do not splice a terminated product into a perpetual synthetic series or substitute SVXY/shortVIXY/SVIX without
a separately specified protocol. The termination event alone does not prove this switching rule held XIV then.
Next gate: one-day availability/fill/product-terms reconciliation plus source-era coverage; no new returns,
modern adaptation, purchase, current allocation or Apex eligibility is established by this review.
Acquisition follow-up: [actual intake](results/vix_etp_acquisition_2753300.md) restored240dated monthly VX files
and a partial364-row actual XIV public-table snapshot through2018-02-15. The source vendor's OHLC documentation
states its XIV OHL endsAugust2017 and warns futures opens became asynchronous with ETP opens. A purchased
synthetic-OHLC package alone would not establish a next-open termination replay. Early VX scale, zero-price
rows and original-versus-successor VXX identities remain unresolved; no raw reference file is a validated fill.

Available-data replay follow-up: [frozen XIV/VIXY proxy result](results/vix_etp_available_period_2753300.md)
now verifies next-open signals and retained overnight gaps over364sessions. It exited XIVJanuary30,2018,
then entered VIXYFebruary5; thus the rule did not hold XIV through that collapse in this sample.
Net+63.3%, DD−35.2%,29positions; one VIXY trade supplies75%of net. This is a secondary-price,
fractional-share historical proxy, not verified fill savings, source replication or a current allocation.

### E52 — Dynamic pair models are not self-financing contract ledgers

Source: Yang, Huang and Chen, unreviewed 38-page preprint SSRN 5017127, indexed posting 2024-11-11;
owned full PDF reviewed 2026-10-31. [Saved review](results/hierarchical_pairs_review_20261031.md).
Related: E09 cash/multiplier reconciliation, E19 information clocks, E38 return/NAV accounting.
- Use: changing an estimated hedge ratio changes the definition of a model spread. That movement is not
  necessarily P&L on the positions previously held. With constant prices 100/100, changing beta 1→0.9 moves
  `Y-beta*X` from 0→10 while held-book price P&L stays 0 before costs. Rebalancing requires actual signed quantities,
  executable leg prices, multipliers, margin/FX cash, fees and daily open-position marks.
- Evidence: source inspection and a constructed accounting identity, not a finding that the authors' unavailable
  implementation committed this error. Their validation Sharpe 4.19/return 13.318% remain unverified source claims.
  The paper acknowledges its continuous/weighted series cannot be directly traded; signals need identified
  contracts and an explicit roll/conversion ledger. Its stated uniform 0.1% commission is not a native all-in cost.
- Timing/coverage: a delayed entry crossing back through a threshold differs from the first outward breach.
  Freeze initialization, half-life fit, filtering versus smoothing, decision time and first executable fill.
  Interpolated prices cannot establish two executable legs; missing or suspended legs remain unknown.
- Limits: dynamic beta and cointegration do not guarantee neutrality or convergence; shared contracts across
  many pairs must be netted without removing actual gross turnover/leg costs. Printed SD/covariance errors and
  unspecified source settings cannot be silently repaired and called exact replication.
- Prerequisites/next check for an independently justified future project: one dated-contract trade/rebalance/roll
  example reconciled from signal through fills and cash/NAV, with causal model fitting and both-leg cost records.
  Do not restart failed CME index-pair variants from this method citation alone.
- Status: methodology/execution reference; no new return test, measured saving, portfolio place or trading change.

### E53 — Commodity skew ranks require clean returns, native sizing and delivery-safe rolls

Source: Vojtko and Padyšák, [SSRN 3507947](https://ssrn.com/abstract=3507947), PDF pp. 4–9;
[full review](results/ssrn_3507947_review_20261030.md), retained 2026-10-30.
- Use: a monthly long-four/short-four commodity ranking needs the full universe and a specified return construction;
  splice jumps can distort measured skew, while reduced-universe ranks define a different strategy.
- Evidence: source/model inspection only. Author cost assumptions and 6.67% modeled annual return are not measured
  native costs, executable micro performance or a replication. No new returns were run.
- Limits: the text combines most-liquid-contract holding with a first-day-of-delivery-month roll. Actual notice,
  delivery and broker deadlines require instrument-specific checks before execution. $1m/$5m capital figures are
  modeling assumptions, not universal account minimums; smaller native contracts do not cover every exposure automatically.
- Next check: identified full panel, formation/fill clocks, contract-specific rolls, native integer positions and
  fees under a frozen replication plan. A bootstrap percentile is not a maximum-loss guarantee.
- Status: retained personal-account research lead, NEEDS DATA/details; ineligible for current Apex intraday use as written.
- [Code build](results/commodity_skew_build_20261030.md): offline rank/whole-contract planner and generated fixture;
  29 constructed checks plus CLI pass. Same-contract returns, 100% gross reference sizing and native cost/deadline
  checks are explicit adaptations. No historical return, held-book ledger, live execution or source-parity claim.

### E54 — Unexpected activity is not automatically a forecast or executable depth

Source/review + date: Sakthivel & Kamaiah, [SSRN1589962](https://ssrn.com/abstract=1589962),
user full-text upload; [review](results/nifty_activity_volatility_ssrn1589962.md), 2026-10-30.
Execution question and useful lesson: separate activity known before an order
from same-day activity explained afterward. Daily futures OI is outstanding
contracts, not signed pressure or available bid/ask depth. A volatility relation
does not establish lower spread, fill costs, directional alpha or a useful filter.
Evidence: author Nifty spot/futures variance regressions, 2000–08, with ARMA(5,5)
expected/unexpected daily activity. Unexpected coefficients positive, expected
negative. No future forecast or execution test. Printed GJR feedback arithmetic
is 1.1235 under symmetric innovations; the source's 0.75 comparison omits its
gamma term. Retained arithmetic script is not an empirical re-estimation.
Market/platform limits: old Indian near-month daily series, not NQ/ES intraday
quotes/fills; OI publication timing and model fitting clocks are unverified.
Data/prerequisites: dated contract-level volume/OI and availability clocks,
roll/expiry mapping, past-only estimation, variance-validity checks, lagged
price-only forecast baseline, then paired net strategy/account outcomes.
Smallest justified next check: apply these clock/model checks if independently
undertaking activity-risk research; this source does not earn a new return test.
Status: methodological reference only; no demonstrated executable edge, zero
return trials, no promising-candidate queue entry or plan/live change.

### E54 follow-up — Post-news activity predicts later volume, not execution costs

Source: uploaded anonymized preprint *Trading Intensity, Forecast Disagreement, and Post-Announcement Volume
Persistence in European Index Futures*, [SSRN 7446599](https://ssrn.com/abstract=7446599),
[review / diagnostic-kernel scope](results/volume_persistence_7446599.md), 2026-10-30.
- Useful lesson: distinguish elevated volume, normalized one-sidedness, price direction and executable liquidity.
  Initial activity explains later excess volume in the reported FTSE/DAX/CAC sample; the R² rise 0.130 -> 0.395
  is historical fit for a volume outcome, not a return forecast. Directional concentration adds about 0.06 pp.
- Evidence: source historical associations, not independently re-estimated. NFP forecast dispersion is negatively
  associated with later volume. Matched non-announcement windows also show activity persistence. No uniform
  quote/book history, native fills, execution savings or trading profits are supplied.
- Timing: primary same-day contract selection uses end-of-day volume; next-day activation is the causal alternative
  tested by the author. Full-sample average-path boundaries require past-only fitting for a forecast. Initial activity
  arrives after the observation interval; AUC120, fitted decay and confirmed baseline duration are later labels.
- Code: a fixed-five-minute numeric measurement kernel plus synthetic arithmetic checks is retained in
  `analysis/codex_volume_persistence_7446599.py`; it does not validate upstream event clocks/contracts, fit a forecast,
  classify trade directions, route orders or measure costs. It reports baseline onset separately from confirmation.
- Next check only for a justified execution study: reconcile one dated event using prior seasonal days and actual
  quotes/fills, then test incremental spread/depth/markout/cost evidence at native size. Tick-rule concentration is
  not participant identity, and high activity can coexist with improving liquidity.
- Status: supporting measurement reference; no source-defined directional strategy or new economic return trial.

### E55 — Strategic futures demand, welfare and executable basis

Source: Hugues Dastarac, *Strategic Trading, Welfare and Prices with Futures Contracts*, Banque de France WP 841,
October 2021, SSRN 3947960, supplied 82-page PDF. [Review](results/strategic_futures_3947960_20261030.md),
[evidence](evidence/strategic_futures_3947960_20261030.md). Related: E07 slicing risk/impact, E11 information
clocks, E46 spot market power, E47 replenishing depth and E50 Treasury contract/liquidity measurement.
- Use: distinguish an individual incentive to affect settlement from net equilibrium price pressure. Under the source's
  symmetric-information/identical-risk-preference setup, opposing traders' effects cancel, despite changed execution
  timing and worse certainty-equivalent welfare. Slicing impact against future-price exposure is a trade-off, not alpha.
- Evidence: theoretical source inspection, no return replication. The negative hedge ratio is defined against expected
  future spot transactions net of the customer shock, not simply current holdings. The welfare result is conditional on
  its modeled equilibrium; the counterfactual non-influenceable contract improves welfare. No universal claim that
  futures or hedging lose money follows.
- Basis lesson: the model's spread depends on the expectation of future customer flow, not a later observed shock.
  Outside arbitrageurs and their endogenous price effects are left unmodeled. A displayed spread does not establish
  that both legs can execute at those prices/quantities or that a cash-and-carry trade earns the apparent spread.
- Limits: CARA preferences, Gaussian shocks, linear demand-schedule equilibrium, zero interest/storage costs and
  ignored margins. No tested contemporary futures strategy, estimated execution savings or calibrated source dataset.
- Next check only for a separately justified proposal: predecision flow/inventory availability, matched cash/futures
  instruments and payoffs, synchronized bid/ask, financing/borrow/carry, both-leg quantities, fees, fills and settlement;
  Treasury implementations also require deliverables, CTD, conversion factors and accrued-interest/repo accounting.
  Futures OHLCV, COT and auction dates alone do not supply these states.
- Status: market-structure/execution reference; zero return trials, portfolio comparisons, queue entries or live changes.

### E09 follow-up — Bank Nifty close marks versus protective execution

Source: Panigrahi, Vachhani and Sisodia, SSRN4013524,2021;
[full article review](results/bank_nifty_4013524_review_20261031.md), retained2026-10-31.
- Use: a close-to-close index-point ledger does not demonstrate a stated gap-down exit, intraday stop or target.
  Final daily candle color is unknown five minutes before its close; freeze the actual observation/fill clock.
- Evidence: our audit confirms the136 printed rows equal20 times index-close changes, totaling₹358,346.40 gross.
  This verifies source-table arithmetic only, not signal completeness, executable derivative P&L or net edge.
- Limits: futures need basis, dated contracts, historical lot sizes, fills and costs; ITM calls additionally need
  strike/expiry/premium paths. Excel forecasts and ANOVA against generated groups are not out-of-sample validation.
- Next check only for separately justified research: reconcile a real signal through native entry, gap/stop/target
  paths, exit and fees. No adaptation or protective-order change is warranted from this paper.
- Status: accounting/timing reference; no return trial, execution saving or portfolio placement.

### E10 follow-up — Bubble detection frequency and cost compounding

Source: Liu, Chuang and Xu, SSRN4494963, uploaded15-page preprint;
[review](results/bubble_riding_4494963_review_20261031.md),2026-10-31.
- Use: gross signal performance can disappear as decision frequency and turnover increase. Authors' daily
  DPSYI wealth7.90 before costs falls to1.37 after their assumed costs; these are unverified Chinese index results.
- Evidence: printed-table audit only. Multiplying gross wealth by0.995 for each reported trading period roughly
  reconciles daily endpoints. This does not verify that actual turnover or round-trip fees were charged correctly.
- Clock lesson: Tuesday detection followed by Wednesday execution separates measurement from trading. Historical
  bubble labels, bootstrapped critical values and interpolated CPI still require independent availability audits.
- Limits/next check: for a separately justified strategy, freeze causal inputs, tradable vehicles, position changes,
  dividend/FX cash, per-leg fees and fill clocks. Do not import the paper's ambiguous Sharpe-percent row or cost rate
  as current CME evidence. No new backtest, measured saving or portfolio allocation.

### E56 — Algorithmic-activity proxies and signed spread/markout accounting

Source: Viljoen, Westerholm and Zheng, [SSRN 1913693](https://ssrn.com/abstract=1913693),
[full-PDF review](results/ssrn_1913693_review_20261030.md), retained 2026-10-30; printed pp. 4–8, 11–19, Table 2.
- Use: distinguish negative dollar-volume/message intensity from algorithm identities or a directional forecast.
  Decompose trade-signed effective half-spread into realized half-spread plus five-minute signed midpoint impact.
- Evidence: source inspection only, SPI 200 day-session nearest contracts, January–December 2009. No replicated
  strategy returns, execution savings or modern CME transfer. Relates to E01/E04 and prior failed order-flow alpha E25.
- Source caveat: rendered Equation 5 omits trade side D; Equations 3–4 and Table 2's signed definition require it
  for the accounting identity. Resolve explicitly; this is not proof the author's unavailable code was wrong.
- Limits: five-minute midpoint is a posttrade label; aggressor side differs from a passive parent's side. Half versus
  full spreads, basis points versus native dollars, stale quotes and fees must not be mixed. Realized spread is not net P&L.
- Next check when relevant native data arrive: one verified buy and sell with pretrade and five-minute same-contract
  midpoints, event/receipt and quote-age records, side and fee reconciliation; preserve missing horizons as unknown.
- Status: execution diagnostic reference. No new alpha trial, plan placement, order-timing change or live logger.

### E09/E11 follow-up — ANANTA rate/FX snapshots, signal direction and netted exposure

Source: Nicolas Georges, April 2014, SSRN2419243;
[full-source review](results/ananta_2419243_review.md), retained October 30, 2026.
- Use: separate rate observation, availability, decision and executable FX fill clocks. London 18:00 and
  New York 17:00 are distinct snapshots; London/US DST mismatch changes their spacing. Same-fix execution
  cannot be assumed from a historical closing observation.
- Evidence: source review and deterministic synthetic checks only. Literal pair attribution sells the
  currency whose relative rate rises, opposite the prose. Under declared global-median/ten-leg normalization,
  a synthetic score panel assigns 10/36 = 27.78% to one currency, exceeding the stated 20% bound.
  Missing sign/normalization rules do not establish the behavior of unavailable author code.
- Accounting: bp per dollar traded uses gross turnover, not account NAV. Netted xxxUSD exposures can retain
  residual USD risk; constant gross requires explicit normalization, and zero mean differentials are undefined.
  Full/half spreads, financing, benchmark eras, spot/futures basis and integer quantities remain unresolved.
- Limits/next check: author 3.5/5 bp net claims are unreplicated OTC-FX backtests, not current CME savings.
  Need matching two-clock swap/FX quotes and source clarification; reconcile one day before returns.
  Public daily UK curves and swap transaction tapes do not supply the exact eleven-currency panel.
- Status: execution/accounting reference and separate data-blocked personal lead; zero return trials or live changes.

### E57 — Autocorrelated order flow can coexist with unforecastable price changes

Source/review + date: Gounas, *Information in Noise*, 2021-03-15,
[SSRN3692479](https://ssrn.com/abstract=3692479); user upload,
[review](results/autocorrelated_orders_ssrn3692479.md), retained 2026-10-30.
Execution question/useful lesson: distinguish raw signed flow from its innovation
relative to information already public. Lemma 1/equation (7), p.11 prices the
innovation, not the expected quantity. Knowing future buying is not by itself a
demonstrated after-cost return or cheaper execution policy.
Evidence: theoretical Gaussian, risk-neutral batch-auction equilibrium and author
numerical comparative statics; not a CME forecast, historical backtest or measured
execution saving. Private-signal agents' model profits are not public-data alpha.
Market/platform limits: current aggregate flow is observed by the maker before
the clearing price is set, then becomes public. No pre-update fill is implied.
Only market orders; no limit queue, partial fills or cancellation-latency model.
Symmetry restrictions/common-knowledge distributions limit transfer; autocorrelation
alone cannot identify actual orders as informed or uninformed.
Data/prerequisites: dated decision/order/quote/fill clocks, past-only flow
expectations, fixed parent opportunities/quantities, native costs, original-timing
and price-only/raw-flow controls, retained no-fill and missed-order outcomes.
Smallest justified next check: preserve these controls if separately conducting
an authorized flow/execution comparison. Do not relaunch failed NQ flow alpha
tests or change trading from the theoretical impact result alone.
Status: reference only, zero return trials, no execution policy or plan/live change.
Related: E04 opportunity-complete diagnostics, E25 raw-flow negative evidence,
E40 short-horizon price impact and E54 activity-availability clocks.

### E58 — RL stock simulators: observation/fill clocks, cash and reported fee counters

Source: Yang, Liu, Zhong and Walid, *Deep Reinforcement Learning for Automated Stock Trading: An Ensemble Strategy*,
ICAIF 2020, SSRN 3690996; [paper/code review](results/rl_ensemble_3690996_20261030.md),
[pretest plan](plans/rl_ensemble_3690996_mechanics_20261030.md). Pinned public FinRL-Trading source at
5b9290ed706efa34aaff96e10761af428a154076, with original Git blobs verified. Related: E09 cash/cost reconciliation,
E11 information clocks, E18 research/platform fill conventions and E43 accounting-to-account effects.
- Use: a close-derived state followed by a fill at the same close needs an actual causal order/auction protocol.
  Value and reward calculations cannot establish availability of that fill. Distinguish the actual cash charged from
  a separately reported fee counter; a counter error alone does not prove costs were omitted from net cash.
- Evidence: five predeclared synthetic groups executed original source class methods/function bodies via AST, not
  trained agents. All three environments can spend $1,001 from $1,000 cash on 100 shares at $10 with a 0.1% fee,
  retain 12.345 shares from a continuous action, and report $0 in the cost counter on a fully closed $100 sale even
  though cash correctly receives $99.90. Same observation close is used as fill before advancing to the next close.
- Specification lesson: source turbulence uses price levels instead of paper-defined returns; backward filling needs
  fold/ticker availability checks. A common positive Sharpe annualization scale does not alter model ranking.
  README/paper/code windows and end dates differ; a paper-era snapshot is not proof of the exact published run.
- Limits: synthetic incidence is not a measured historical failure rate or Sharpe inflation. Public data acquisition
  and panel shape were verified, but trained policy checkpoints, point-in-time universe/adjustment identity and
  portfolio attribution remain unverified. Source daily cash-equity fees do not translate to native futures.
- Next check only with clarified source/protocol: one causal observation/order/fill/cash/share trace, then verified
  universe, corporate actions, fold-local features, turbulence, seeds and benchmarks before economic replication.
- Status at the original source-only review: original engine fails reproduction admission; broader personal-allocation method is a low-priority queue
  lead. Zero historical agent training, strategy-return trials, portfolio comparisons, native savings or live changes.
- Related upload [SSRN 7013523 review](results/ssrn_7013523_review_20261030.md): all 30 performance-table cells
  match the archived original; do not count the 2026 upload as independent confirmation. A separate constructed
  check of its printed reward expansion disagrees with NAV accounting for a buy from zero holdings. This is a
  source-equation finding, not a claim that an unavailable runtime used it; no new economic trial or method queue entry.

- Follow-up2026-10-30: the user explicitly requested new corrected stock and intraday MNQ protocols. Both Python
  engines are now built and tested;12 synthetic mechanics groups pass. Independent CSV replay reconciles integer
  stock cash/shares/NAV and native-MNQ fill/roundtrip/daily fees, slippage and P&L for all declared policies.
  [Frozen build plan](plans/rl3690996_build_20261030.md), [results](results/rl3690996_build_20261030.md),
  [guide](code/rl3690996/README.md). These are adaptations, not repaired-source TableII reproductions.
- Economic outcome: stock selector-$120 on$10,000 in2018–2019 (equal-weight+$1,790); fixed1MNQ selector+$2,090
  in2018–2022 (long control+$5,404), doubled-cost selector-$5,188. Both fail design advancement. Stock turnover
  costs exceed its executed-path gross gain. Correct accounting does not establish an RL edge or savings.
- Remaining boundary: dividends/point-in-time stock lineage, opening-auction execution and actual MNQ contract quotes
  remain uncertified; incomplete futures sessions are enumerated. The$250 session loss budget is not an Apex floor.
  No dependent holdout/seeds/account contribution, live changes or measured execution savings; retain this negative
  result instead of reopening the same definition. Any materially different project needs its own source/evidence gate.

### E09/E11 follow-up — Duration, signed price impact and constructed event clocks

Source: Bowe, Hyde and McFarlane, October 2007, SSRN1025241;
[full-source review](results/bowe_duration_1025241_review.md), retained October 30, 2026.
- Use: distinguish raw intertrade duration from the paper's thinned price-changing event process. Equal-price
  trades/volumes and simultaneous timestamps are combined; overnight time is removed. Event construction
  changes the modeled process and must be frozen before claiming transfer to native CME events.
- Evidence: author regressions on 69,981 TIIE28 information ticks, 2000–2006, not independently replicated.
  Longer expected duration has larger signed effects in main models; the information parameter changes sign
  after augmentation. Nearby duration/volume t-statistics are only 1.35/−1.27; robust generality is unproven.
- Accounting check: Table6's 2.1014 spread and 73.74% liquidity share match absolute Table4A coefficient
  magnitudes, not the displayed signed sum. This flags a convention/presentation ambiguity, not verified
  author-code failure. Structural cost shares are not observed commissions, spreads or execution savings.
- Clock/sign limits: current direction multiplies duration/volume; coefficients do not justify a buy-after-silence
  or sell-high-volume rule. Completed durations and posttrade marks are not automatically predecision features.
- Next check only for a separately justified native execution project: timestamped same-contract trades/quotes,
  initiator side, quote age, raw/filtered events, pretrade midpoint and posttrade fee-adjusted markout; then
  past-only seasonality/model fits versus simple spread/volume/time-of-day baselines. Minute OHLCV cannot supply this.
- Status: execution-method reference; no market-return replication, alpha trial, strategy queue entry or live change.

### E18 follow-up — Future-extreme buffers and partly observed targets

Source: González-Maiz-Jiménez, López-Herrera and Reyes-Santiago, SSRN6401038, uploaded March2026 preprint;
[review and mathematical audit](results/straddle_buffer_6401038_review_20261031.md).
- Use: an order priced from the execution day's final high/low needs a causal estimator or as-of update policy.
  A daily bar touching a hindsight level does not show that the order existed then; wider buffers and slippage
  stress do not remove that information problem. Retain non-fills, cancellations, queue and trade-through evidence.
- Evidence: source inspection and constructed identical-prefix/different-continuation counterexample only.
  Paper's claimed Sharpe7.26–14.86 is not independently reproduced or demonstrated executable alpha.
- Accounting: equal static long/short entries cancel before costs. Combined UP profit is close minus short-cover
  price; DOWN profit is long-exit minus close. Inventory held before prediction creates no automatic advantage.
- Target clock: predicting tomorrow's close relative to yesterday's open includes already-observed price movement.
  In an explicit IID equal-variance Gaussian thought experiment, known-component sign predicts the combined sign
  with75% accuracy while predicting the future component stays50%. High old-anchor accuracy is not tradable edge.
- Next check only for separately evidenced research: prefix-only order levels, prediction/label maturity clocks,
  genuine forward-return baseline, native net positions/cash/margin and executable fills. No current strategy,
  sizing, protective-order or account-policy change; no new return trial or measured execution saving.

### E09 follow-up — WTI genetic optimization still needs native contract and cost units

Source: Aragón, Mejía & Zapata(2018), [SSRN3387570](https://ssrn.com/abstract=3387570);
[source review](results/wti_genetic_ma_ssrn3387570.md), retained2026-10-30.
- Lesson: optimizer fitness only measures the ledger it is given. A printed
  quantity-times-price-change formula is not native futures dollar P&L without
  specified signed units/multiplier, fills, turnover costs and roll cashflows.
- Evidence: source/Table2 and deterministic rounded-table/unit audit, no price
  replication. Article calls its example2,000WTI contracts on$2m while its equation
  does not show the CL1,000-barrel multiplier. Literal-contract interpretation
  changes dollar P&L by1,000×; this does not prove unavailable code used that error.
- Limits: generic Bloomberg15-minute closes,2017–18; no disclosed all-in costs,
  native fill ledger, complete intraday losses or session/roll convention. Ten
  test months are not an account-risk limit. GA search cannot fix missing units.
- Smallest next check if reopened: one identified contract trade reconciled from
  signal time through signed fill quantities, cash P&L, fees and roll before
  optimizing or mapping percentage returns into CL/MCL account sizes.
- Status: accounting caution, NEEDS SOURCE SPECIFICATION; zero return trials,
  no new optimizer/execution policy, promising-queue or plan/live change.

### E09/E43 follow-up — Current-book native fees, source coverage and account-preset identity (2026-10-31)

Source: [five-home portfolio audit](results/portfolio_audit_20261031.md),
[frozen protocol](plans/portfolio_audit_20261031.md), [code guide](code/portfolio_audit_20261031/README.md).
- Evidence: existing recorded-ledger historical diagnostics, native integer-lot costs, seven synthetic groups,
  independent ledger reconciliation and24 exact account-engine parity comparisons. User reports MNQ0.99–1.08RT,
  use1.04; MES/MCL1.04 remain assumptions. Source order-flow ends July7; later missing signals stay unknown.
- Use: a recorded closed trade can reconcile cash while its missing held minute still blocks adverse-path certainty.
  Requiring all minutes for every cash diagnostic removes85/87 CL trades here; that subset cannot represent the book.
  Keep separate cash/size and minute-risk admission. Source-style sparse-bar model outputs are conditional, not live odds.
- Netting: opposite NQ positions occur on70/390 days in50K/150K funded full-size recorded paths. Adding each strategy's
  separate high/low adverse marks can invent simultaneous losses. A low daily correlation does not resolve order or
  shared-price chronology. Broker netting, rejects and source StopPts/ATR/actual quantities need independent traces.
- Preset identity: the audit runner's initial suffix check treated funded_150 as ending in50, selecting50K rules.
  Canonical-engine parity alone passed against that wrong preset. Independent start/cumulative-cap checks caught it;
  archived invalid runs remain, and the explicit account mapping now verifies13000/20500 six-payout ladders.
- Sizing: fractional full-size intentions1.5 followed by cushion-flooring differ from an actual integer input1 followed
  by flooring. Current150K input identity must be resolved before claiming installed-sizing parity. No allocation
  selected from historical attribution; no shared/live/broker/VPS change or measured execution saving.
- Next check: dated exact-version research exports with native fills/fees, StopPts/ATR/qty and missing-minute capture
  semantics; then shared-price chronological account replay and independent review before allocation/safety claims.

### E09/E43 latest-source qualification — Claude's audit updates

[Follow-up review](results/portfolio_audit_claude_updates_20261030.md), source `d654fda13d43f3b481441168336586bb89bd9d9e`.
- Addressed:150K intended integer inputs now explicitly round three1.5 intentions to1; refreshed personal ladder
  uses19 labels and keeps four forward-only sleeves separate. No further duplicate request to define those inputs.
- Qualification: the overlap diagnostic uses the older50K RS-long roster, excludes OT and multiplies raw risk
  bases without executable lot flooring. It measures a potential exposure bias, not corrected account failures.
- Synthetic canonical-account evidence: applying the same$20 adverse bias to two hypothetical plans can cause
  one to fail and the other to survive. Thus conservatism alone does not establish unchanged relative decisions.
  This does not show that an actual allocation should change. Missing input paths can still understate risk.
- Personal ladder:120 cleared-subset plus10 forward-subset comparisons use the same historical reporting sample;
  new ranking is exploratory, with the inherited Twin/Kusho/OT/margin limits. No new historical returns were run
  in this source/settings/synthetic follow-up, no measured execution savings, live action or allocation change.

### E09/E43 closure — Integer-aware overlap replay and chronological ladder check

[Final follow-up](results/portfolio_audit_final_followup_20261030.md), Claude source88b5e95; frozen plan c83a9e9,
implementation d90aca1. Native-cost reference and constant-position shared-price sensitivity use exact reachable
integer q vectors, excluding entry/exit and missing-price minutes.53/615 daily quantity-state minima change but
0/500 paired histories change any account output or first-year payout on50K/150K. Current allocations retained
for this bounded model concern; no claim of actual fills, universally unchanged outcomes or certified floor safety.
The auxiliary100-lot CREDIT approximation can pay when both intended1-lot legs floor to0, so its wiring check alone
is insufficient; proper integer checks independently support the no-change result here. Eight canonical account
parity comparisons and54 production NumPy state checks pass. Current150K intended inputs and refreshed19-label
ladder are specified. New chronological subset results disclose small-row instability and shift personal planning
to the documented12-piece row; the underlying source/marking/margin and historical-selection limits remain.
Do not request these same implementation/checks again. No new alpha, allocation selection, live or broker change.

### E04/E47 follow-up — Literature Atlas: event paths, reactive fills and attribution

Source: Bandyopadhyay, SSRN7630598 (October18,2026), [focused review](results/literature_atlas_7630598_review.md), reviewed November7,2026.
- Use: distinguish trade-sign estimates from observed aggressor labels, prediction error from executable net P&L,
  and realistic-looking synthetic paths from an environment that responds to our orders. Reconcile differences through
  data, signal, sizing and execution (§12.1–12.3, B6/B12, §18.8).
- Evidence: title/abstract-based literature synthesis and untested author proposals, not new native fill evidence,
  measured execution savings or a verified NQ/ES strategy. Aggregate metadata arithmetic does not validate cited studies.
- Limits/data: event signatures require synchronized order/depth/trade paths; minute summaries cannot recover their
  ordering or queues. Reactive simulator claims need held-out native evidence. Own-impact relevance must be measured
  at actual integer size; opportunity/noncompletion costs can exceed a spread saving. Never delay protective exits.
- Next check: within an already-authorized offline verification, reconcile one complete decision/order/fill lifecycle
  and its cost ledger. Existing [data requirements D42–D45](DATA_NEEDED.md) apply; no new dataset request or live change.
- Status: reference only; no return trial, simulator build, monitoring policy, allocation or claim of lower costs.

### Research-method follow-up — Conditional factors versus pooled portfolio risk (2026-11-07)

Source: Chernov, Kelly, Malamud and Schwab, SSRN7596842, October11,2026 version.
[Focused review](results/infinite_factor_7596842_review_20261107.md),
[source receipt and finite algebra illustration](../../analysis/outputs/codex_infinite_factor_7596842/source_audit.json).
- Use: a small unconditional covariance eigenvalue does not by itself imply diversifiable noise. State-dependent
  managed exposures can add systematic directions under the paper's assumptions. Distinguish explanatory variance,
  expected-return spanning, sample estimation error and executable portfolio value.
- Evidence: focused theoretical-source inspection plus a two-state zero-mean covariance illustration; no exhaustive
  proof audit, empirical replication, native fill evidence or demonstrated savings. More risk directions need not
  mean positive expected returns. This supplements the Hidden Sharpe frontier caution above.
- Limits: infinite/growing menus and stock panels are not our finite integer futures book. Regularization can be
  biased; retaining every noisy component is not proved optimal after costs. No allocation, factor gate or strategy
  revival follows. Existing observed equity-index concentration findings remain intact.
- Next check only within a separately justified frozen estimator comparison: causal features, common opportunity
  set, chronological fitting, feasible weights, actual costs and account paths. No new data request or return trial.

### E11/E12 follow-up — Assemblage VAR: economic shock versus available trading input

Source: Barrette/Goulet Coulombe/Reinicke, SSRN7508198, [review and pinned source audit](results/assemblage_var_7508198_review.md), November7,2026.
- Use: distinguish a retrospective, jointly fitted macro index and its recursively identified innovation from a
  public input known before an order. Changing an index changes the shock; larger macro responses are not trading returns.
- Evidence: paper/code inspection and synthetic normalization check. Sorting zero-mean inputs does not preserve
  rank means; actual replication code imposes a mean constraint. No empirical execution saving or strategy result.
- Limits: monthly revised climate/macro histories, full-history seasonal adjustment/weights, in-block VAR-refit CV,
  different printed/code penalty conventions and benchmark/assembled gap-dummy handling. No native futures fill model.
- Prerequisites/next check: only within an independently justified future study, reconcile one original release/vintage,
  fold-local feature/weight fit and later executable fill; compare identical calendars and actual net units. Free
  transformed panels were obtained, so this is not a new missing-data alpha lead. No need to repeat acquisition.
- Status: methods/clock reference, no return trial, new queue entry, allocation, logger or live-system change.

### Research-method follow-up — Match forecasting targets before comparing accuracy (2026-11-08 UTC)

Source: Alqahtani, SSRN7511639, user-uploaded undated manuscript.
[Review](results/forex_ml_7511639_review_20261108.md),
[source/arithmetic receipt](../../analysis/outputs/codex_forex_ml_7511639/source_audit.json).
- Use: volume-class accuracy, risk-error reduction and price forecasting are distinct outcomes. Neither volume
  accuracy nor MSE reduction establishes directional returns, executable liquidity or account drawdown improvement.
  Require identical future targets, observations, clocks and baselines before inferring comparative superiority.
- Evidence: all extracted narrative/tables read; claims not reproduced. RF's reported78–85% is volume-class
  accuracy. RF/GBM/ARIMA have unmatched tasks, risk labels and volume provenance are incomplete, and an Open/26-day
  correlation versus univariate R² needs reconciliation. No model fit, return test or execution saving verified.
- Limits: daily spot-FX volume is not consolidated exchange activity; substitute futures volume changes the source
  target. Full-sample class boundaries/interpolation need causal checks. No NQ/ES fill or strategy evidence follows.
- Next check only if new source material arrives: exact labels/horizons, volume field, code/fold dates and same-target
  paired predictions. Existing causal controls already apply; no new data request, monitor, allocation or trial.

### E10/E56 follow-up — Dealer concentration, spread rents and censored persistence

Source: Kim/Mehrotra, SSRN486642, September2003, [review and arithmetic audit](results/nasdaq_dealer_486642_review.md), November7,2026.
- Use: distinguish nominal dealer counts from actual order-flow concentration. HHI and measured full effective
  spreads describe historical stock-dealer structure; neither an attributed spread component nor a realized spread is net P&L.
- Evidence: source reports8.76cents/0.5434%of price and20.3months to halving, the latter only for79.4%with
  observed crossings. These are not replicated profits, an exponential decay model or modern CME costs.
- Verified arithmetic: HHI units and the paper's spread-change example; printed Equation5 lacks quote-count
  normalization (constant quotes give nonzero “variance”). No claim that unavailable original code made that error.
- Limits/data: old Nasdaq stock dealers, concentration/spread endogeneity, fixed-count HHI lower bound, incomplete
  halving observations and contradictory group labels. Need actual dealer shares and same-contract trade/quote/receipt
  clocks. The historical five-second quote lag must not become a modern futures default; completed monthly HHI is not
  an earlier intramonth feature. Anonymous OHLCV/order-flow summaries do not supply dealer identities.
- Next check: within an already-authorized execution review, reconcile full versus half spread, actual fills/fees
  and quote freshness before any concentration/cost claim. Existing DATA_NEEDED D42–D45 apply; no new alpha/data request.
- Status: historical execution reference; zero trading-return trials, measured savings, allocation or live changes.

### E01/E56 follow-up — Island/Nasdaq: fine-grid priority and conditional maker markouts

Source: Biais/Bisière/Spatt, SSRN302398, November26,2003, [review/audit](results/island_nasdaq_302398_review.md), November7,2026.
- Use: unrounded competing quotes and synchronized receipt clocks matter. A fine-grid improvement can disappear
  in coarse displayed data; price priority on one venue is not guaranteed access to another venue's order flow.
- Evidence: historical seven-stock/two-five-session study, not independently reproduced. Authors infer predecimal
  rents and weaker simple-model evidence afterward; richer instrument tests still reject restrictions in2001.
- Profit boundary: marginal executed-book markouts use a thirty-minute midpoint. This is a future label, not an
  attainable exit or net order-policy P&L. Account for nonfills, partials, cancellations, closing costs and inventory.
- Identification: spread/markout moments identify handling cost plus rent, not both separately without additional
  assumptions. Synthetic checks reproduce that nonuniqueness and rounding mechanism, not a profitable strategy.
- Limits/next check: only for an already-justified execution audit, verify same-contract quotes, source precision,
  event/receipt/order/fill clocks, actual queue rules, native fees and side-signed markouts. Historical Island stock
  tick/rebate terms do not transfer to CME futures. Existing D42–D45 data requirements apply.
- Status: execution reference; no new alpha/data request, return trial, measured saving, allocation or live change.

### E03 follow-up — Venue fragmentation, delay units and cancellation denominators (2026-11-07)

Source: Battalio/Egginton/Van Ness/Van Ness, SSRN1941956, October5,2011 draft.
[Review](results/nasdaq_fragmentation_1941956_review_20261107.md),
[source/sign audit](../../analysis/outputs/codex_nasdaq_fragmentation_1941956/source_audit.json).
- Use: distinguish number of venues from actual flow allocation and reporting facilities from matching venues.
  Historical cost trends, within-year conditional relationships and causal execution savings are separate claims.
- Evidence: source narrative/key tables reviewed, Tables10/12 visually checked; no original regression replication.
  Table10 defines delay in seconds: negative fragmentation coefficients in2002–06 mean shorter delay, positive
  coefficients in2007–10 mean longer delay. The prose reverses the speed interpretation. Spread associations
  also vary by year; do not carry an unconditional faster/cheaper claim into execution assumptions.
- Cancellations: reported2010 percentages include NASDAQ16.3%, ARCA92.1%, ISE97.0%. These reporting averages
  are not quote-message rates, proof of spoofing/false liquidity or our probability of missing a fill. Reconcile
  order population, denominator, reporting coverage, time priority, partials and lifecycle before reuse.
- Limits: historical fragmented US stocks, not a native NQ/ES matching-book study; receipt-to-fill report averages
  are not broker/network latency. No trading rule, native fill benefit or measured saving follows.
- Smallest next check only with a separately justified execution task: validate matching report/order populations
  and clock units against observed lifecycle records. No new data request, allocation, monitor or return trial.

### E09/E11/E19 follow-up — Replication conventions, overlay caps and valid samples

Source: Delgado, *“Beat the Market” Revisited*, SSRN7323419, August20,2026;
[review](results/delgado_7323419_review.md), [input/free-data receipt](inputs/delgado_7323419/free_data_gate.md).
- Use: match typical-price volume-weighted VWAP and entry confirmation before comparing results. Keep
  price/dividend conventions, minimum commission, early closes and actual post-overlay leverage separate
  from an earlier engine's results. Cap final marked exposure after every sizing factor, not merely base sizing.
  A performance overlay's lagged **overlay-free shadow** returns are a separate state from actual scaled P&L.
- Evidence: author independent historical replication and disclosed engine fixes; not our verified fills/savings.
  The selected candidate changes several engine/risk conventions after an adaptive search; its seen recent
  period is not new validation. No new trading code or returns here; previous native futures findings retained.
- Research limit: retain all80observed SPY alternatives despite10missing reconstructions and preserve actual
  warmup-valid starts. The38–41%PBO applies to the25-point pre-fix grid, not the final80-trial adaptive search.
  Near-100%DSR does not establish future profit. Shared mechanism does not make SPY overlays transferable:
  all three reported QQQ adaptations have lower Sharpe than QQQ base.
- Missing/next: native SPY minute/dividend/calendar/fill/cash inputs; authenticate one complete interval before
  replay. Full trial series needed for independent statistical audit only. A new strategy test can instead freeze
  explicit interpretations on admitted free data. No ETF-cost or IEX-only volume substitution into futures.
- Status: methods/execution reference and low-priority D55data watch; zero new financial trials, no allocation.
- Subsequent user-authorized [ES historical test](results/delgado_es_20261108.md): three definitions fail
  candidate design advancement; no allocation. Twelve pre-return synthetic checks and gross/net ledger
  reconciliation pass. Freeze whole-lot quantity at the known decision close, never future fill-open; record
  fill/marked leverage breaches rather than retrospectively resizing. Unknown requested fills/held paths remain
  unknown calendar days. Source-like4xrequested exposure is not a broker-margin or gap-loss guarantee.
- [Unchanged baseline validation](results/delgado_es_baseline_20261108.md) under the user's later nomination
  verifies2018–22daily/trade CSVs byte-for-byte before inspecting2023+summaries. Preserve exact shared
  prefixes to distinguish later outcomes from silent implementation changes. Recent strength fails; no measured
  execution savings, native account promotion or reopening of the rejected modifications.

### E09/E12 follow-up — Slow trend signals, actual-position turnover and no-trade bands

Source: Tzotchev, SSRN4677166, February6,2018, [review/source audit](results/delta_straddle_4677166_review.md), November8,2026.
- Use: execution cost scales with changes in actual held positions; running cost with absolute exposure.
  Signal-only changes miss turnover from inverse volatility, risk targeting, contract rolls and integer rounding.
  Preserve last executed holdings and cumulative target drift when applying a no-trade band.
- Evidence: author simulations show fast4/8/16-day gross gains become losses after modeled costs;0.25band
  improves reported Sharpe over no band, but was chosen after historical comparison. No native savings reproduced.
- Limits: bounded CDF signal does not bound inverse-vol leverage; straddle-like geometry is not option protection
  or a timely account offset. Gross/carry/fees/collateral and native roll cash must reconcile. Printed AR(1)t-stat
  correction is reversed under marginal volatility; source DD below−100%needs NAV convention clarification.
- Next check on genuinely new matching inputs: one causal native formation/rebalance/roll/cash interval and cost
  bridge, preserving full universe, source selection and prior negative trend evidence. D54 records missing data.
- Status: conditional personal lead and cost-reference only; zero new financial trials, measured savings or live changes.
- User-requested build follow-up: [offline code/test report](results/delta_straddle_4677166_build.md),34synthetic
  mechanical checks pass for actual-held bands, whole lots, roll close/open costs and budget overrides.
  No fills/cash ledger or realized savings verified; modeled final-position budgets do not ensure a safe legged
  roll path. Personal profitability still needs D54inputs and a separately admitted native replay.

### Research-method follow-up — Strategy-relative regimes require predictive state and native switching

Source: Bilokon, *Strategy-Relative Market Regimes as Filtration Compressions*, SSRN6504227, April1,2026;
[full review](results/bilokon_6504227_review.md), [finite mathematical audit](../../analysis/outputs/codex_bilokon_6504227/source_audit.json).
- Use: define a regime's usefulness for a fixed strategy's future net reward, keep prior activation/holdings and
  include the cost of switching. A sufficient-state Bellman model implies hysteresis: turn on above+lambda,
  stay on above−lambda, for pre-switch dynamic advantage. It does not supply the forecast or its estimation.
- Evidence:4page theory note, no empirical strategy or profitability. Exact constructed example gives history-
  adapted objective1.25versus1.05for the stated reduced feedback state: MarkovZalone does not make
  history-dependent strategy rewards Markov. Need explicit reward-state sufficiency. A second fixture has
  optimal always-on action carrying0bits while observedZcarries1bit aboutX; full-distribution predictive
  sufficiency/minimality is not established by utility optimization. Independent formal review pending.
- Execution limits: utility penalty is not a native dollar cost bridge. Preserve shadow baseline outcomes while
  inactive; a switch with existing positions/orders can change later PnL, so use flat boundaries or replay actual
  order/position/cash paths. A binary mode need not encode that state. No measured execution savings.
- Next/status: method only, no trading/data-queue nomination. An actual causal predictor/fit/clock/utility/
  penalty and native replay must be independently specified before a bounded preregistered return test. Do not
  invent an ESregime filter after seeing recent baseline losses, reset multiplicity or add monitoring/schedules.

### Research-method follow-up — Indicator significance, selection and switching costs (2026-11-08)

Source: Fang/Qin/Jacobsen, *Technical Market Indicators: An Overview*, SSRN2449344, user-uploaded manuscript.
[Review](results/market_indicators_2449344_review_20261108.md),
[source/unit receipt](../../analysis/outputs/codex_market_indicators_2449344/source_audit.json).
- Use: distinguish regression significance, stable signs and economic value after switching. Main author screen
  goes93→30→10→8→0 economic outperformers; selected regime/robust exceptions exist but do not establish a new edge.
- Evidence: main narrative/selected tables, visual Table13 check, no empirical reproduction. Table13's short-sales
  Sharpe2.47 is multiplied by10^-2, yielding0.0247 per week; not annual Sharpe2.47. Switching cost0.10% is an
  author assumption for market/cash timing, not our native futures spread/fee/slippage ledger or measured savings.
- Clocks: NBER retrospective labels are not contemporaneous inputs; a real-time CFNAI release still requires
  original vintages and availability. Lagged indicator dates and full-sample-selected candidates do not establish
  independent tradable validation. Weekly NYSE short-sales data ending2008 cannot be silently replaced by modern
  daily short volume, short interest or futures volume.
- Next check only on materially stronger independent evidence: actual data/source clocks, precise forecast/refit
  conventions and same-opportunity costed holdings. No new data acquisition, return trial, filter, allocation or
  rejection of existing independently tested strategies follows. Supporting negative/method evidence only.

### E04 follow-up — Winner dependence, reselection and warm-up cash (2026-11-08)

Source: Malan, *One Ticker Deep*, SSRN7073258, July2026 draft.
[Review](results/one_ticker_7073258_review_20261108.md),
[source/arithmetic receipt](../../analysis/outputs/codex_one_ticker_7073258/source_audit.json).
- Use: chronological validation still needs constituent/concentration attribution. Excluding the largest winner
  and refitting measures a counterfactual portfolio, not that name's realized contribution to original holdings.
  Label both separately; a retrospective removal is not a forward exclusion rule or proof all trend profits are luck.
- Evidence: all extracted text/tables/appendices read and code statically inspected; no market-return replication.
  Author99-name OOS Sharpe1.53 falls to1.05 withoutNVDA versusSPY1.30. Full-sample volatility buckets are diagnostic
  only. Approximate membership still omits delistings; the full99-name list/companion engine are absent here.
- Risk/clock limits: AppendixA starts targets at index[window], leaving earlier rows in cash; source acknowledges
  warm-up helped miss COVID. Match pre-sample warm-up/common evaluation dates before attributing protection.
  Some reported grid/bucket drawdowns exceed SPY, so protection is not universal. A one-row signal lag alone
  does not establish an executable close fill; preserve actual price basis, next-trade clocks and cash/turnover.
- Next check within a separately justified portfolio study: frozen realized contribution ledger, separately
  labeled exclusion/reselection and matched cash/universe/risk benchmarks. No new test, winner-based filter,
  acquisition, monitoring process, guaranteed hedge or allocation follows from this source review.

### E04 follow-up — Crossover metrics, day win rates and cash attribution (2026-11-08)

Source: Arnold, SSRN6684499, April27,2026 capstone study.
[Review](results/crossover_6684499_review_20261108.md),
[source/arithmetic receipt](../../analysis/outputs/codex_crossover_6684499/source_audit.json).
- Evidence: primary text/tables and visual Table3 check, no empirical replication. Author50/200 stock portfolio
  annualized return12.04% versus17.27%, Sharpe0.779 versus0.849, drawdown−25.79% versus−35.23%. Negative
  daily benchmark-difference t−2.169 is not a risk-adjusted-alpha or Sharpe-difference test.
- Units: `(1 + mean daily return)^252 − 1` is not path CAGR; the printed Sharpe daily/annual conventions need
  code reconciliation. The52.10% win rate is positive days, not winning trades. Cash return and actual timing
  need matching; lower drawdown alone does not identify diversification or superior payout/account outcomes.
- Limits: same five-stock basket in both benchmarks; crossover exposure, warm-up and weight maintenance can
  differ. Constant20% return slots require a reconciled rebalance/cost ledger, beyond charging10bp only on
  crossover changes. No original code/input histories or native fill evidence supplied; no savings verified.
- Use only when a separate comparison is justified: freeze metric definitions, cash/benchmark dates and clocks,
  then reconcile trade-to-portfolio returns. No new data acquisition, MA/ML/regime search, filter or allocation.

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


### E11/E18 follow-up — Event-day selection and missing-bar exits in an automated lab

[Claude source audit](results/claude_system_audit_20261101.md), frozen source3ad0b16, reviewed2026-11-01.
- Use: an event selector must be known at the trade's decision, even if it reads only volume. Do not infer a completed holding path or scheduled exit from the last available earlier print.
- Verified: disconnected fixtures show Q009 uses09:31 volume after its08:00–09:29 trade; Q007's Wednesday membership can change with future Thursday volume. A Q007 trade with no bars after09:37 still receives a return despite its scheduled10:30 exit.
- Evidence: synthetic mechanics and exact-source review, not a historical re-estimation or measured execution loss. The affected saved design candidates failed; no allocation or profitable alternative follows.
- Limits/next check: dated official event calendars and complete observed holding/exit paths are prerequisites. Retain failed protocols, missing-data counts and amended universes; any justified rerun must preserve trials and existing admission gates. Otherwise record the gap and move on.
- Supporting process reference: [Jane Street interview assessment](results/jane_street_interview_review_20261101.md) motivates artifact-backed tests, explicit permissions and reproducible setup, with no verified trading or execution savings.


### E20/E22/E23 follow-up — Routing identity, ACCT schema and kill acceptance

[November1 formal review](results/REVIEW_2026-11-01.md), baseline dff44f1 plus latest29416b9.
- Use: separate the monitor's typed balance-query account from GetAccountID's chart auto-trading account, and both from native order/fill evidence. Adding a route field requires exact-column tests for every equity reader.
- Verified: invented rows reproduce lost #4 trades through inherited150 tags and a pending-version mute; a source wildcard can misattribute typed#2 equity to route#4 in the PowerShell floor reader. Latest Python equity readers use the exact typed field; #4's missing max_stop was supplied and its fixture passes.
- Kill evidence: source/control-flow checks show shared local/remote stop ownership and unknown remote reads can enable resume. Source presence, file creation or alert delivery does not establish working-order cancellation, broker flattening or installed acceptance.
- Limits: no PowerLanguage compilation, PowerShell runtime, VPS access or real orders. GetAccountID semantics checked against the official MultiCharts reference; installed/off-automation behavior remains unverified.
- Next check: responsible disconnected/paper-account acceptance of explicit account IDs, source/input version, stop ownership, failure paths, entry cancellation and broker/strategy position reconciliation. No live change is authorized by retention.


### E20/E22 follow-up — Two-latch fixes and effective-flag acceptance

[November2 follow-up](results/REVIEW_claude_followup_20261102.md), Claude cf4cc1e.
- Prior exact-column equity parser, date-effective150 tags, status-worktree boundary, removed version mute and unknown-edge fixes are supplied. Do not reopen their first implementation.
- Actual isolated PowerShell7.6.9/Linux tests with temporary -Dir and -NoAlert confirm the normal script-created local/remote latch sequence, but show direct KILL-file manual instructions can be overridden and failed effective-flag reconstruction on resume can return success with a local latch still active.
- Windows GetFileAttributesA's failure sentinel is not uniquely a missing file; GetLastError distinguishes reasons. Current signals treat any failure as flag absent. API/source evidence only, not an observed Windows read failure.
- Claude reports installation and remote file/phone tests; no independent VPS, phone delivery, cancellation, broker flatten or native Windows/MC acceptance is established here.
- Next check: supported manual interface, effective flag equals OR of latches under failures, and explicit unknown-read handling; retain separate broker/strategy/order-clock checks. No live modification or strategy-return trial.


### E20/E22 reply — Hand-made flag and rebuild-error fixes verified

[Kill-control reply review](results/REVIEW_kill_reply_20261102.md), Claude2a99380.
- Actual PowerShell7.6.9/Linux temporary-folder/-NoAlert cases now pass: hand-made flag adoption survives remote resume, deleted effective flag is restored by Check, independent resumes work, and injected reconstruction failure returns error instead of false success. Close the two reproduced prior defects.
- The new six-signal parent-folder guard blocks directory-query failure, with normal exits retained. It does not distinguish a file-specific attribute error from verified absence when parent attributes succeed. API/source truth-table evidence, not an installed Windows error incident.
- Claude reports16 VPS latch checks and eight2026-11-02 chart versions installed. No independent VPS/Windows/MC/broker cancellation or phone-delivery claim here; no live change or return trial.
- Smallest remaining check: actual file-query error classification/tri-state under the installed process identity. Do not repeat already completed source fixes or treat a parent attribute check as full file-read acceptance.


### E10/E12 follow-up — Handwritten AI-basket regime/liquidity checklist

[Image review](results/ai_trade_regime_checklist_review_20261102.md), user upload2026-11-02; author/calibration unidentified.
- Use: distinguish spread, depth, volatility, correlated exposure and executable cost; preserve data clocks and missing states before a regime-based risk decision. Counting related stress features does not give independent confirmations.
- Source-only: four regime labels and risk multipliers, skew/correlation/NAV thresholds, futures/put hedges and kill criteria. No tested edge, execution savings or incremental account benefit supplied.
- Specific issues: the apparent spread z-score < -2 means narrowing under standard normalization; parent definitions/units missing. An unindexed probability-weighted constant risk budget stays constant. Nominal-account percent losses do not replace actual trailing-floor cushion.
- Limits/next check: specify basket, past-only normalization, hedge/quote/NAV clocks, permissions and complete position/fill/cost ledger before any separately justified gated test. OHLCV is not inferred order-book depth or option skew. No new monitor, backtest, TODO strategy entry or live change.

### E11/E12 follow-up — Time-varying estimates and available-at forecasts

[November2 scout source check](results/scout_owned_source_followon_20261102.md), Malinska IES7/2020,
method/data/result sections of the university manuscript; not a full-paper review or return test.
- Use: lagged predictors alone do not make a coefficient available at the historical entry. Record the estimator's
  training endpoint, kernel support, bandwidth selection, controls' release clocks and missing-value treatment.
- Source check: Equation7 sums over the sample throughT; no past-only endpoint forecasting protocol was established
  in the inspected sections. Source controls include linear interpolation of missing observations. Using future
  observations in an entry forecast or interpolating across a later value can contaminate a tradable interpretation.
- Limit: a descriptive smooth is not inherently a defective descriptive analysis. It does not supply a costed
  historical trading rule. No measured forecast advantage, fill improvement or economic verification is claimed.
- Next check for any separately justified future hypothesis: freeze causal estimation and native clocks/costs before
  returns; do not use plots, full-sample signs or missing-data interpolation as historical entry information.

### E09/E11/E19 follow-up — Revised15-minute Globex noise-band code

[Completed design review](results/noise15_20261103.md), user upload2026-11-03. Two frozen candidates fail design;
no validation/account advancement or live/platform change.
- Verified source arithmetic: SetStopContract and actual BigPointValue preserve50/25point distances on NQ/MNQ.
  This supersedes the older CODE.txt's unchanged-input micro-conversion concern for this revised source only.
  Default2NQstill risks$2,000nominally before costs/gaps; the counter is not an account loss cap.
- User confirms full Globex. Calendar-date reset therefore uses the midnight-area chart bar, rather than an
  explicit08:30or17:00open. EMA and historical slot inputs also depend on complete chart-session observations.
  Fifteen-minute alignment supplies one update per slot/date; the older five-minute sampling concern is not
  asserted for this supplied configuration. Slot23at14:30does not disable the separate flat branch.
- Reproduction evidence: prearmed fill-anchored brackets, next-chart-bar orders, stop gaps and target trade-through
  modeled with repository execution helpers. Literal has3cross-date and5combined late/cross-date closed-trade flags;
  protected has0. Holding gaps and partial feature histories remain explicit, not repaired or treated as certain fills.
- Accounting: two reconciliation stops preserved; complete-trade/date aggregation and repeated-date handling fixed
  before same-rule reruns. Original literal trade fields match all attempts. Six synthetic checks and trade/day/cost
  conservation pass; this is not independent native-platform verification or measured execution savings.
- Next check only for a separately justified later task: complete matching source chart/report and dated native
  quote/roll/fill evidence. Current statistical/data gates already reject advancement; do not turn gaps into a
  recurring data request, optimization or automatic rerun. No allocation follows from this reference.

### E11/E44 follow-up — Public positioning, revisions and forecast vintages

[November3 scout checkpoint](results/scout_owned_source_20261103.md); selected primary sections/metadata only,
not a full-paper or return reproduction. Related sources: Kang/Rouwenhorst/Tang SSRN2449315, Maréchal3881922,
Gilbert et al.1108050 and Höllmann4882538. Merge with existing COT/event-clock references; no execution policy changes.
- Use: keep position observation, public release, revision, local receipt and first executable fill separate.
  Source2449315's days1–4and5–40distinction does not make all Tuesday-based regressions tradable at Tuesday close.
  Its post-publication portfolio remains an unverified26-market construction, not a three-market outright return.
- Owned-input check:783CL/GC/NG position-date rows across five legacy annual ZIPs, no duplicate dates or invalid
  selected numerical cells; stable market codes preserve2022name changes. Schema coverage is not released-vintage
  or native futures roll/quote evidence. Legacy aggregates do not identify operational/swap-dealer groups or orders.
- Free source check: [CFTC historical notices](https://www.cftc.gov/MarketReports/CommitmentsofTraders/HistoricalSpecialAnnouncements/index.htm)
  and [2019catch-up notice](https://www.cftc.gov/PressRoom/PressReleases/7864-19) show holiday Monday observations
  and shutdown delays. The latter planned February1publication of December24,2018positions; this is a schedule,
  not a verified receipt for the whole design panel. A universal Tuesday+3days rule would expose future data.
- LEI input check: public February22,2018forecasts differ (MetaTrader0.5%; contemporary Regions/ActionEconomics0.6%).
  A vendor forecast field is not automatically the Bloomberg median used in SSRN1108050. Do not infer survey identity,
  original-release vintage or pre-release knowledge from a current historical page.
- Limits/next check: only for a separately justified, fully gated proposal, reconcile one original observation,
  actual release/revision/receipt, same-contract executable entry and native cash/roll ledger. Missing fields stay
  unknown. No measured slippage saving, new return test, account improvement or deployment follows.

### E12 follow-up — Abnormal-day labels and forecasting targets

Caporale/Plastun2021 [primary methods](https://link.springer.com/article/10.1007/s11408-021-00380-w),
selected sections only; [scout record](research/scout/records/doi_s11408_2021_00380_w.json).
- A completed day's abnormal-return label and calibrated hourly average are not necessarily available when the
  proposed trade starts. Freeze a past-only trigger and its exact formation period before any justified return work.
  Do not silently repair the printed negative-threshold sign or import MetaQuotes GMT+3session boundaries into GC/CL.
- Costs omitted from a source simulation remain omitted; do not adopt the assertion that commissions disappeared
  as a native futures fee model. Höllmann's hedging-position target also does not establish a return forecast.
- Status: source/clock/model caution only. No full appendix review, synthetic/economic check, execution saving,
  strategy grade or automatic follow-up test is claimed.

### E09/E12 follow-up — Tick reversal is not minute-bar alpha

[November4 scout checkpoint](results/scout_owned_source_20261104.md), Cusatis/Kulkarni/Thomas2009,
[selected primary pp35–42](https://musabe.org/bfr20092020/40-260-1-PB.pdf); not a full-paper review or return test.
- Use: distinguish tick price changes, minute returns and executable bid/ask prices. Transaction-price negative
  correlation may reflect alternating sides of the spread; it does not promise a marketable fill at a recorded extreme.
- Source rule uses tick-order daily highs/lows,1/2-tick brackets and lagged tick autocorrelation. Owned ZN minute
  OHLC cannot recover event order, quote side, available depth or all eligible channel events.
- Limits: original cost/profitability sections not reviewed; no net loss, edge, fill saving or contemporary failure
  independently established. No OHLC scalping adaptation, new trial, allocation or live change follows.
- Smallest check only if genuinely new matching tick data and a separately justified proposal arrive: full source
  fill/cost rules, historical tick/quote clocks, sequential order replay and native fee/latency reconciliation.

### E09/E11/E19 follow-up — Ricochet hindsight exclusions and early-close carry

[Ricochet S1144 review](results/ricochet1144_20261104.md), complete user-uploaded November4note/PL;
two fixed causal design replays fail advancement. No MC compilation, native trade matching or execution saving proved.
- Default SaltaSenza830=1uses six2020dates selected for a later missing08:30bar. At the prior evening17:05entry,
  that future feed/session state is unavailable. Price-prefix equality alone would not expose a shared hardcoded
  future exclusion mask. Both bounded replay profiles disable it before outcomes; original bytes remain archived.
- Source15:00exit does not occur on a half-day without that bar. Observed-path source-style replay has3daily-flat
  crossings; a predeclared11:30known-half-day exit has0. This is model/code evidence, not installed-platform acceptance.
- Midnight crossing alone is within the current17→16account day; the funded plan explicitly permits such overnight
  sessions. Check actual daily flat deadlines and native joint paths rather than rejecting a calendar-date change.
- Same-close entries require clock/fill assumptions. Stops begin after a close-filled entry, not at an earlier low;
  one-minute chronology and1point target-through differ from the supplied5-minute BarMagnifierOFF setup.
- Exact-completeness flags preserve partial bars, unknown held paths and persistent Wilder-history uncertainty.
  A partial bar is not automatically a bad closing fill; a profitable flagged stream is not certified executable alpha.
  No outcome-selected deletion, fill interpolation or after-result gate relaxation was used.
- Next check only under a separately justified new task: original MC settings/trade ledger and matched native
  contract/roll/quote clocks. This failed candidate earns no automatic re-test, data chase, allocation or live change.

### Evaluation audit — Remaining cushion, account rules and broker evidence

New-data clock follow-up, November9,2026Pacific: [funding/fear tests](results/new_data_strategies_20261110.md)
and [primary source notes](inputs/new_data_strategies_20261110/sources/clock_evidence.md). A reference rate's
effective date precedes its next-day release; final core percentRate after the afternoon revision window differs
from summary percentiles that can be updated later. Delayed core-rate research is now supported by explicit
policy clocks, not actual receipt logs. For index features retain UNKNOWN separately: NaN==1 is false and would
otherwise silently put unavailable observations in the OFF group. All three new candidate arms fail design;
no measured execution saving, account improvement or new strategy admission follows from these clock lessons.

Direct-VB follow-up2026-11-10: [loss-side split-stop screen](results/vb_loss_split_20261110.md), one new
fixed proposal/four controls and candidate definitions. Retaining Twin2/DT2/finish mode, a7/8split at37.5/75points
lowers nominal15MNQ stop exposure2250→1725 but reduces design passes38.27%→35.75% (adverse DLL35.04%→33.78%).
Saved full-stop losses are outweighed by foregone recoveries. REJECT; no2023+variant outcomes or threshold rescue.
Model caveats include nonsimultaneous sleeve extrema, inherited held-path gaps and NQ-as-MNQ pricing; no
native/UNKNOWN-aware replay or live protection proved. The user explicitly allows changing/replacing the book.

Follow-up2026-11-10: [VB/ONB terminal-loss evidence reconciliation](results/vb_onb_tail_review_20261110.md)
preserves latest Claude management outputs. The user's later correction supersedes the original live89%
attribution:89% is a backtest figure;4/4 recent live accounts reportedly ended on a large VB/ONB loss.
The saved backtest defines89% as one component contributing over70% of failure-day loss; that is not
a verified count of avoidable full-stop failures. Exact-threshold liquidation and fractional portfolio scaling cannot certify
an executable account guard. The saved150K near-target half-size lead improves passes38.9%→40.6% on
its VB15/DT2 book; tighter daily stops reduce passes. This is reviewed legacy-model evidence, not a fresh
test or a result for the separate VB20 book. Next check: frozen integer sizing/native costs/calendar expiry,
common-price floor checks and adverse fills on the intended book; no new threshold search or live change.

[November4 loss forensics](inputs/eval_audit_20261104/loss_forensics.md),
[rule audit](inputs/eval_audit_20261104/engine_audit.md) and
[dated calendar evidence](inputs/eval_audit_20261104/calendar_audit.md).
- A strategy stop can sit beyond the account liquidation floor. On November4 the recorded50K/150K remaining
  cushions were931.34/1939.60, versus nominal ONB stop risks1062/2478 before costs. A fixed dollar-risk budget
  must not be confused with remaining loss capacity. A prospective cushion governor still needs account testing.
- Chart strategy logs can continue after broker rejection, DLL lock or account failure. Reconcile broker fills,
  equity, floor and account status before treating later virtual chart trades as executable account P&L.
- Current EOD evaluation floor rules differ from the funded PA starting-balance+100 lock. Model DLL liquidation
  at observed prices with costs,30calendar-day expiration and realized target balance after closing costs.
- The index15:15–15:30CT pause ended with trade-date2021-06-28. Use dated schedules; do not label every historical
  missing quote a closure. Source-chart compression/timezone also changes daily ATR risk inputs, notably CLS's
  Eastern calendar reset. Incomplete required sizing inputs remain unknown, not a finite estimated risk budget.
- These are forensic/model lessons. They establish no independently verified replacement strategy, live setting,
  execution saving or allocation. Exact account outcome comparisons are a separate preregistered study.
- The follow-up [source diagnosis](inputs/eval_audit_20261104/postexecution_source_diagnosis.md) separates actual
  missing expected-open ATR inputs from an adapter error:390 DT time exits were wrongly checked against CLOSE,
  although the existing source exits at OPEN. A separately committed overlay fixes all401 such clocks uniformly;
  it preserves prices, original outcomes and unrelated events. Factual source-clock repairs require their own
  provenance and pre-outcome code commitment; favorable-touch searches would change the execution claim.

Weekly source/accounting follow-up (week ending 2026-11-06):
[independent review](../cross_review/2026-11-06_codex.md) and
[post-read checks/proposed correction](../cross_review/2026-11-06_codex_response.md).
- Explicitly label fixed charges per side versus round trip. Two daily research helpers subtract twice their
  documented RT charge: an extra $7.25 per NQ or $5 per ES round trip. A two-line proposal passes eight invented
  flat/stop cases; it has not been applied to historical results or trading code and does not rescue an edge.
- Finite entry/exit marks do not establish a known held path. The actual green-day helper emits a finite trade
  despite an almost entirely unknown held path in a fixture. Require expected-session coverage and retain UNKNOWN;
  do not silently skip missing minutes or substitute an earlier close for an unavailable required exit mark.
- The legacy evaluation helpers and Claude's later cushion-cap bench retain a premature PA-like floor lock and
  21-session expiration. Invented first-passage counterexamples establish model defects, not corrected historical
  pass rates. Unknown ATR becoming zero size can turn unavailable risk inputs into apparent no-trade outcomes.
- Combined exposure caps depend on allocation order as well as stop budgets, fees, gaps and simultaneous exposure.
  The new cap source uses VB before ONB despite declaring ONB first. Freeze the actual ordering and data contract
  before a registered economic comparison; source checks alone do not certify survival or optimal sizing.
- Keep PA and evaluation floor contracts distinct. The later funded cap source has a legitimate PA floor lock,
  but its 50K, CLS-excluded bootstrap improvement (8.1% to 2.3% failures at VB=2) is not a full-book or 150K result.
  Its chronological two-year starts show 1.5% failures either way. Dependent scenarios and a source-plan adoption
  statement do not certify execution, causal live cushion inputs, account dominance or deployment readiness.
- Repeated chart-log rows are not independent broker trades: the cited November 5–6 logs have 102 CLOSE rows but
  four distinct complete rows. Preserve raw records and reconcile account/broker evidence before inferring fills.

### Source follow-up — Reaction windows, units and continuous risk weights (2026-11-06)

[Checkpoint](results/scout_owned_source_20261106.md); selected-source scope, no return tests or execution savings.
- [Auction6447502](research/scout/records/6447502.json): distinguish cash yields, native futures cash P&L,
  auction cutoff and actual results publication. Realized post-event order flow cannot predict its own payoff window.
  Preserve the existing failed auction tests; these cautions authorize no new clock/side variant.
- [NG attention](research/scout/records/doi_fut_70104.json): observing an announcement response does not earn
  the already-completed response interval. Authenticate surprises and receipt clocks before any later payoff.
- [Volume-conditioned risk](research/scout/records/5795584.json): a model weight is not an integer fill.
  Predeclare available-at transforms, observed-path missingness, rounding, turnover/costs and account constraints.
  Supporting analysis is not source replication, native account benefit or permission to impute missing returns.

### E11/E12 follow-up — Same-window shocks and completed-day states (2026-11-05)

[Source checkpoint](results/scout_owned_source_20261105.md); selected sections only, no new return tests.
- [Demand-driven risk premia5095671](research/scout/records/5095671.json), Paris2025 manuscript Eq1/pp6–9:
  Treasury shock and FX response both span auction−10/+10minutes. A signal using the window's closing price
  cannot earn that same window's response. This is a descriptive identification boundary, not a criticism of
  using contemporaneous responses to study transmission. A later tradable payoff must start after observation
  and execution latency; its edge has not been established by this source check.
- [Stock-bond correlation4346625](research/scout/records/4346625.json), December2024 AEA manuscript Eq1/pp8–9
  and Table9/pp44–45: daily correlation uses the day's full regular-session five-minute returns; the intraday
  lead-lag comparison conditions on that daily state. Do not use final-day correlation or full-sample percentile
  membership as an entry-time filter earlier that day. A separately justified past-only state needs frozen
  formation/estimation clocks and economic evidence before returns; no risk-reduction or P&L gain is measured.
- [Financialization4231994](research/scout/records/4231994.json), related Utrecht22-07 working paper footnote7:
  monthly reference periods are used without actual publication dates for descriptive linkage tests. Reference
  month-end is not release/receipt time. Pin the exact version and original vintages before treating a macro
  series as an available trading input; parity with the2026article remains unconfirmed.
- [Bond jumps1716759](research/scout/records/1716759.json), related Tilburg thesis event/investment sections:
  event plots exclude overnight returns and costs, while longer-horizon investment returns use a bond index per
  unit duration. Those charts are not a continuous native futures cash ledger or integer-contract sizing rule.
  Retain rolls, all held overnight changes, cash/fees and causal warm-up before any personal/account inference.
- Status: supporting clock/accounting cautions from selected primary text, not complete source reviews,
  independently reproduced returns, execution savings, account-stage passes or new allocations. Consult only
  when a relevant new hypothesis/input arrives; no rescue of closed flow/news/overnight definitions.


### E11/E12 follow-up — Position-report clocks, venue units and utility metrics (2026-11-07)

[Source checkpoint](results/scout_owned_source_20261107.md); selected sections/metadata only, no new return tests.
- [Baur/Smales2022](research/scout/records/doi_fut_22332.json): Tuesday snapshot dates do not establish Tuesday public availability. Source combines CME5BTC and CBOE1BTC positioning after size adjustment; raw counts or CME-only signals are not equivalent. Owned snapshots have no actual publication timestamp column. Audit original releases/holiday backlogs before any later source replication; no universal three-day shift.
- [Taylor2017](research/scout/records/doi_eneco_2017_07019.json): certainty-equivalent utility is not realized cash return or payout. Interval cost parameters, removed overnight differences and1000-day estimation warm-up need native execution reconciliation; do not shorten history or convert utility tables to account outcomes.
- [JPM2015](research/scout/records/jpm_momentum_2015.json): keep separate component definitions and their reported performance. Footnote88's three-day expiry rule is not Table41's weekly rule. No combined-index result, in-sample calendar selection or same-settlement mark establishes an executable component fill.
- [Maciejewski2026, arXiv2609.18019v1](research/scout/records/arxiv_2609_18019.json), abstract only: passive order shadowing follows exchange-order identifiers through add/cancel/trade events. Minute aggregates cannot reproduce order lifecycle, queue placement, latency or slippage. Retain as an offline execution benchmark watch only; no fill saving or directional edge verified.

### Research-method follow-up — Estimated frontiers are not executable Sharpe (2026-11-07)

Source: Chernov, Kelly, Malamud and Schwab, *The Hidden Sharpe Ratio*, SSRN7679420, October28,2026 upload.
[Review](results/hidden_sharpe_7679420_review_20261107.md), [source/code audit](inputs/hidden_sharpe_7679420_20261107/source_audit.json).
- Use: distinguish a statistical population-frontier estimate from identified tradable weights, net fills and account performance. The source's approximate7.4/5.0 Sharpe values are gross equity estimates, not futures backtests; low-variance covariance directions can also be noisy, illiquid and expensive.
- Evidence: main text and implementation appendices reviewed, public MIT implementation pinned and selected files inspected statically; algebra/units checks only. No empirical/economic replication or independent proof audit. In97% of broad-universe rolling windows the upper point is pinned to the lower by the corner rule; agreement is not independent upper-bound evidence.
- Implementation: author output tables annualize squared Sharpe and also multiply diagnostic columns by the annualizer. Preserve raw derivative/grid units; reconcile order1/corner-adjusted outputs with the paper rather than copying order2 examples. No upstream code was executed or installed.
- Limits: original source assumes a high-dimensional managed-stock/bond universe and statistical conditions including within-window stability/iid innovations. Native integer futures and intraday account floors are a different application. Source prose/figure bond numbers and HJ notation need reconciliation before reuse.
- Next check only if a later methods task justifies it: validate source/code parity, exact vintages, serial dependence, selection and net executable costs on the actual frozen universe. No new strategy queue item, live change, demonstrated saving or allocation follows.


### E09/E11 follow-up — Return-space hedges and ETF primary-flow clocks

Sources: [Joo/Park SSRN4355765](results/bitcoin_commodity_hedges_4355765.md) and
[Barahhou/Abitbol SSRN7517178](results/etf_flows_7517178.md), uploaded full PDFs.
- A covariance/variance hedge coefficient on returns is a notional ratio, not a native contract count. Convert with
  signed exposure/contract multiplier, preserve actual paired rolls, cash, fees and margin; CL is not Brent.
  HE is fractional variance reduction, not return, drawdown or account-breach protection. Gold's short-window
  positive HE turns negative over every displayed500–2000 evaluation; no verified hedge benefit for our account.
- ETF primary creation/redemption flow is not secondary volume or necessarily fresh cash buying: AP inventory,
  in-kind baskets and netting matter. Historical beginning-month stock weights, classifications and NAV/share
  publication vintages must precede a signal/fill. A future market-return regression control is not an observable feature.
- Evidence: source text/table-image inspection and reproducible source arithmetic/filename census only; zero
  new empirical strategy trials, execution savings or portfolio changes. Public vendor/SEC checks proxy403.
- Next check only with new matching free inputs: one native hedge/cash interval or ETF monthly flow/weight/receipt
  reconstruction as appropriate, then its own evidence/preregistration gate. No cross-market price proxy, paid
  data request, live/logger change, automatic collector or paused-scout restart is implied.


### E09/E11/E19 follow-up — KRX gold's explained opening gap is not a pre-entry return

Source: Yeom/Baek, [SSRN2903671 full review](results/krx_gold_2903671_review.md), uploaded17-page paper;
[evidence](evidence/krx_gold_2903671.md). Prior CME gold returns explain KRX close-to-open gaps (source beta0.414),
but the previous KRX close precedes completion of the futures signal. Do not backdate an entry or equate a predicted
auction price with a fill at the old close. A post-open strategy targets a different, untested return interval.
A close field must identify settlement/last/session-close, holiday mapping, DST and KRX historical hour eras.
KRX is KRW/gram, GC is USD/troy ounce; USD/KRW and local basis/delivery are needed, not an ICE dollar-index proxy.
Source Table2's9.6% hypothetical net return is about9.34% under its printed buy/sell fees; neither is a realized edge.
Evidence: source/table images, rounded-moment regression consistency, conditional fee arithmetic and source-assumed
winter/summer clock checks only. No independent market-data return or verified execution saving. Next check only
for a separately specified auction/valuation question: synchronized predecision GC/FX/auction quotes and actual native
order/fill/cash rules; no new collector, proxy trade, paid-data request, account or live/policy change.


### E11/E46/E57 follow-up — Analyst-affiliated quotes are not observed inventory or a future-event detector

Source: Mizrach, *Analyst Recommendations and Nasdaq Market Making Activity*, December2003 revision,
[SSRN499103 review](results/analyst_market_makers_499103_review.md),
[evidence](evidence/analyst_market_makers_499103.md). Historical1999–2000 pre-upgrade bid-appearance pattern
weakens in2001. The event-week63.61% rate is not prediction accuracy or a fill share. Headline75.0492% and
$592.077mn are summed/model-attributed event/firm estimates, not portfolio CAGR or observed dealer cash P&L.
Dealer quotes may be agency or principal; displayed depth/appearance and buyer-initiated trade imputation do not
identify passive counterparty, filled inventory, reserve depth or queue position. In particular, the source's equal
allocation of aggressive buys among inside-bid participants is a proxy, not a verified dealer-purchase matching rule.
Only a public, predecision detector evaluated on all eligible days could address tradability; do not select only
future upgrades or treat days−1 to+4 abnormal returns as fully post-release. Historical top-quote Nastraq is not
modern multi-level depth. Need release/receipt clocks, as-of MPID/affiliation, real quote/trade linkage and native costs
before a separately justified study. Evidence: source/table-image and source-arithmetic/schema checks only; no new
returns, verified execution savings, strategy queue entry, allocation, paid collection or live/policy change.


### E20/E22 follow-up — Nasdaq expansion/pilots are implementation narratives, not measured execution gains

Source: Lennon/Folkinshteyn2017, *From Bit Valley to Bitcoin: The NASDAQ Odyssey*,
[SSRN3025751 review](results/nasdaq_odyssey_3025751_review.md), supplied19-page journal article.
The small-sample historical case study proposes management lessons about capabilities, information, conflicting roles
and reliance on unfinished technology. Its blockchain cost-reduction language has no controlled before/after execution
or recordkeeping cost dataset. Licensing, an announced pilot, auditable records, operational deployment and verified
net savings are distinct evidence states; clearing/settlement is not quote-to-fill latency or improved strategy P&L.
Retain contextual support for existing product/version/acceptance checks only. No causal trading/operational benefit,
current Nasdaq/Bitcoin infrastructure fact, new return trial or execution saving is independently verified. If a concrete
implementation comparison is later authorized, require actual transaction/latency/cost records and the same-workflow
baseline. No blockchain build, new monitor, workflow/policy change, candidate/data queue or live action follows.


### E09/E11/E12 follow-up — Decade valuation labels mature; GDP quarter-end is not publication

Source: Swinkels/Umlauft, *The Buffett Indicator: International Evidence*, March30,2022,
[SSRN4071039 review](results/buffett_international_4071039_review.md),
[evidence](evidence/buffett_international_4071039.md). Source explicitly waits for ten-year return labels before
fitting; credit this rather than diagnosing leakage from long horizons alone. Its GDP footnote acknowledges
quarter-end unavailability but supplies no actual vintage/nowcast release bridge. Mature targets and available
features are separate gates. Raw country ratios are not directly comparable; forecast from within-country histories.
Nominal annualized GDP, total-market capitalization, local total-return and FX/native cashflow conventions matter.
Twenty annualized cost bps for maximum two-way turnover is an illustration, not verified FX/fee execution. Source
composite10.5%/Sharpe0.57 and52.1%drawdown are unreplicated; high ten-year R² is not intraday or crash-timing skill.
Evidence: source/table-image checks, source cost arithmetic and synthetic availability fixtures only; public free
probes proxy403. Next with new matching inputs: one country/formation/vintage/mature-label/currency ledger before
a bounded performance study. No new return trial, execution saving, current placement or live/policy change.

### E09/E10/E12 follow-up — Transaction taxes, participation and volatility are not alpha

Source: Velmurugan/Champramary, [SSRN2849388 uploaded-paper review](results/ctt_gold_2849388_review.md),
retained November 7, 2026. Historical MCX gold study, 2011–16, tax start July 1, 2013.
- Use: express charges in notional units and distinguish activity, dispersion and executable return prediction.
  The source's 0.01% seller tax is 1bp of notional, not margin; it is not a CME/MGC fee setting. Reported
  trading-value declines recompute to 43.95–57.08%; this does not identify a trade sign or a causal tax effect.
- Evidence: full-source/table-image inspection and published arithmetic only. Table 6's post-tax persistence
  sums to 0.974387 rather than 0.99; alpha5 p=0.3176 contradicts claimed significance. No raw MCX/GARCH replication,
  measured savings, risk reduction or strategy profit. Greater volatility need not mean exploitable inefficiency.
- Next use only for a separately justified cost/participation study: authenticate tax/event/sample clocks,
  market/contract/roll identity and controls. No new alpha queue/data-shopping item, automatic collector or return
  test; missing data alone is not merit. No allocation or live change.

### E01/E10/E56 follow-up — Listing transfers, spread components and urgency

Source: Bonini et al., [SSRN3985691 full review](results/listing_switch_3985691_review.md), December 15, 2021
preliminary draft, retained November 7, 2026; NYSE/Nasdaq stock switches 2009–17, not Nasdaq-100 futures.
- Use: distinguish quoted from effective/realized spread, and interaction coefficients from total subgroup effects.
  With aggressor side D, trade price P and same-contract midpoints M0/M5, the paper's full relative spreads satisfy
  `2*D*(P-M0)/P = 2*D*(P-M5)/P + 2*D*(M5-M0)/P`. Five-minute M5 is a posttrade label, not an available signal.
  Half-spreads, percentage points/basis points and native cash fees require explicit conversion. Realized spread
  excludes inventory, hedging and fees and is not net dealer profit; a passive parent's side differs from aggressor side.
- Evidence: full text/appendix, key table/figure images, source arithmetic and two invented algebra examples only.
  Large-firm dark effective spread changes +0.068−0.037=+0.031 percentage points, not a decline. Pooled lit effective
  spread changes −0.019; wider quoted spreads do not imply deterioration of every effective-spread measure.
  Coefficient-sum significance requires unavailable covariance. Announcement CAR is not significant.
- Limits/next check when separately warranted: actual fills and order/quote receipt clocks, side, quote age,
  classified venue, future midpoint coverage, native fees and missed-fill opportunity cost. Off-exchange is not
  automatically a specifically identified dark pool. No original TAQ replication, trading signal, measured saving,
  TODO strategy/data-shopping entry, order-routing installation, portfolio change or external message.


### E09/E19/E30 follow-up — Cross-venue leveraged products need native units and clocks

SSRN7065278, reviewed 2026-11-08: [source review and registered audit](results/pair7065278_20261108.md).
The literal author parser converts declared same-unit GBX prices 499/501 into 49900/501. This is a synthetic
counterexample, not measured historical inflation: fix units from source metadata and corporate-action records,
never from a price threshold. Even granting its UTC claim, 16:00 UTC is 17:00 London in summer, outside ordinary
continuous trading, and not a constant 11:00 New York. A date join and lagged position do not certify
simultaneous executable quotes or later fills. TQQQ and LQQ3 are different issuer/products, not fungible listings.

The paper's multiplicative cost equation reduces losing-trade losses; the actual code/workbook instead
subtracts costs. Preserve that distinction. Its alpha spreadsheet references the wrong sheet/cells. Define
NAV, gross exposure, collateral, borrow, FX and native leg costs before interpreting a pair-return difference.
Fifteen engineering assertions across nine groups reproduced the registered findings; source admission failed.
No historical return series, execution savings, portfolio result or live recommendation was established.
Smallest next check only with new matching evidence: one native two-leg timestamp/unit/quantity/cash ledger,
then a separate corrected protocol. The same accounting lessons apply broadly; its equity/ETP holds are not
evidence for our Apex futures plans. No live/VPS/broker change.

### E09/E11/E12 follow-up — RSI ratios need domain, sizing and confirmation clocks

Source: Tamele/Khoong/Bhattacharyya, [COR SSRN7164538 review](results/cor_dip_7164538_review.md),
[evidence](evidence/cor_dip_7164538.md), supplied21-page paper. Printed Eq12's absolute before/after asset–market RSI-gap
ratio can equal20 for valid RSI inputs and is undefined at a zero denominator, contradicting claimed0–1 boundedness.
A physics analogy does not define a probability, causal flow or fill. Printed Eq10 is not native share sizing if ATR
has price units; this is not a confirmed code bug because actual notebooks were LFS pointers and materialization hit proxy403.
“After dip” requires a causal confirmation/available-at ledger; it is not by itself proof of look-ahead.
Source hourly TSLL COR+ATR reports41.56%,7 trades,85.71% wins, versus43.77%,9 trades,77.78% withoutCOR: higher win rate
need not improve total profit. Separately optimized results need same-window matched ledgers/removed trades/random-drop controls.
Source uses zero trading costs/fractional shares; seven trades do not establish future execution or account benefit.
Evidence: PDF/table images, formula counterexample, unit illustration and pinned CSV/source receipts only. Some stock CSV
outputs differ from paper; no author code or market-path return executed. Source holdings do not establish Apex intraday fit.
Next only with genuinely new evidence: resolve denominator policy, indicator/position units, exact causal dip/exit/fill clocks
and code/output versions before any eligible preregistered test. No measured savings, strategy/data-shopping entry or live change.

### E09/E11/E12 follow-up — Donchian Pine activation, protection and risk sizing

Source: Poluri February2026, [SSRN6272239 review](results/donchian_btc_6272239_review.md),
[evidence](evidence/donchian_btc_6272239.md); MIT Pine pinned b58e642e97bd06bcce804d0ee0e2b513b517a78a.
Check native trailing units/offset, fill/recalculation settings and first protective-order activation; ATR stop distance
alone is not risk sizing. Compare current-ATR stops with frozen/ratcheted risk before porting. Never silently repair code
and call its returns replication. Figure is weekly despite daily methods; profit$41,023.96 is not ending equity on$10,000.
Source31 trades/PF7.076/90.32% wins also shows51.65% drawdown, not account survival or verified savings.
Evidence: source screenshot, pinned static code, official Pine-v5 documentation and synthetic stop arithmetic only;
12 checks pass, zero market-return trials, no Pine runtime verification. BTC venue, tester overrides, sizing and trade ledger
remain unresolved. Next only with new exact settings/code/trades: reconcile one entry/protective-exit lifecycle before an
eligible preregistered return study. No new alpha/data-shopping queue, port, allocation, paid collection or live action.


E09/E19/E30 reconstruction follow-up (2026-11-08): user-authorized corrected
[research components](results/pair7065278_reconstruction_20261108.md) pass28synthetic unit, quote-clock,
causal-indicator and state-transition assertions. Explicit GBX/GBP replaces the price-level heuristic;
15:00UTC is a provisional ordinary-session overlap, still requiring authenticated calendars and later fills.
This is not a complete execution/cash engine, measured saving, profitable strategy or reversal of the source
rejection. New free history probes hit proxy403. Missing native history/borrow/cash keeps returns blocked.

### E09/E19 follow-up — Locked arbitrage cashflow versus future convergence

Aktaş, *The Two Primitives of Spot Market Strategy*, SSRN6736280, May 2026;
[full review](results/spot_primitives_6736280_review.md),
[constructed audit](../../analysis/outputs/codex_spot_primitives_6736280/audit.json).
The source's §5.3 describes pure simultaneous arbitrage as depending on future convergence and bearing widening
risk before closure. Distinguish a locked executable spread in identical fungible deliverable units from a
position held for risky convergence. With both legs and delivery assured by assumption, buy ask 99/sell bid 101
less assumed total cost 0.20 yields 1.80 immediately; no later convergence is required. This is a mathematical
example, not observed quotes or an available opportunity. The source's narrow single-market premise itself
excludes this cross-venue case, but its later taxonomy explicitly includes it.
Practical replication still needs synchronized executable bid/ask, legging/settlement/financing/delivery risks,
native units and cash/borrow ledgers; correlation or a strategy label supplies none. Source §3.6 already
acknowledges dividends/coupons: retain income separately from price gain instead of omitting it from accounting.
Evidence: source reading and constructed checks only; no market-return trial, measured execution savings,
new data-shopping entry, policy change, arbitrage bot or live change. Existing clock/cashflow controls remain.

### E09/E19 follow-up — Weekly close exits, equity reconstruction and low-beta claims

[SSRN5630830 source/audit](results/weekly_nq_5630830_20261108.md), retained2026-11-08. Screenshot
shows a5%loss exit checked **after candle closes**, not an intrabar price-loss ceiling. Invented entry100,
low90,close96 loses10%intraweek without triggering the5%close condition. Native contract multiplier and
capital basis matter: price percentages are not account percentages. Weekly holds are not Apex intraday fit.

Source says its weekly returns were reconstructed from trade logs/rescaled to platform total, while retaining
a separately reported platform drawdown. Equal terminal values do not establish equal drawdowns or margin
paths. Need actual per-period marked positions/cash/costs, not assumed interpolation; the source does not
provide its reconstruction algorithm. Lowbeta0.1coexists with reported correlation~0.7; scale/exposure cannot
be presented as uncorrelated alpha. Final full-span CAGR/alpha arithmetic is consistent, though the earlier
five-year-alpha input explanation is not. Keep source versions and horizons distinct.

Evidence: full PDF/page18image,6registered arithmetic/synthetic-risk groups and10assertions. No native
strategy replication, measured execution saving, hedge benefit, portfolio test or live change. Missing custom
indicator formulas and fill/roll/capital clocks stop dependent returns. Next only with genuinely new matching
evidence: one source indicator/entry/exit and native mark-to-market cash reconciliation before any strategy trial.


SSRN5630830 user-authorized adaptation outcome (2026-11-08):
[actual weekly design test](results/weekly_nq_adapt_20261108.md) filled formulas explicitly, then stopped on
failed registered gates. At1MNQ,2018–22fullrule16trades/$4686net/t0.92/Sharpe0.54vsbaseline27trades/
$7029net/Sharpe0.50. Dailycash/costs reconcile; customindicator replication and source performance remain
unverified. Calendarroll quarantine avoids knownwindowspans but does not authenticate datedcontracts;
RTHdailyDD is not full overnightadversepath risk. A pre-return missing08:01bar check led to a committed
first-observed-bar delay amendment; do not invent prices during missing/halted intervals. No2023+NQreturn
test, portfolio stage or live change followed failure. This outcome is not evidence of execution savings.


E09 cross-instrument path follow-up (2026-11-08):
[Claude ingredient/ES review](results/claude_ingredients_review_20261108.md) confirmed literal inheritedNQ
$20/point in a pathhelper called withES$50/point trades. A synthetic ESentry100,exit110,net470,low99
produces+$250adversemarkinstead of−$80while terminalnetstillmatches. Realizedcashreconciliation alone
cannot certify intratrade pathunits. Parameterize nativepointvalue and verify adverse/realized marks before
accountsimulations. Also confirmed the purported stop-onlyablation changes a coupled target; holdother
exitsettings fixed or label the jointintervention. Sourcecode/static/synthetic evidence only, no new market
returns, observed execution savings or plan/live changes. Proposed fixes remain for review.


### E09/E19 follow-up — Ingredients, exit windows and native micro cost bridges

[Three-strategy diagnostic](results/ingredients_three_20261108.md), user-authorized2026-11-08,13frozen
DT/RS/LDFcases,2018–22then already-seen2023–2026-10-09. No promotion or livechange. DT's fixedtarget
clips historical totalprofit but improves recentDD; RS's magnitude threshold concentrates exposure and
removed profitable early trades; LDF14:30vs15:00exit is strongly period-dependent. These are conditional
source-port comparisons, not measured forcedflow or universally optimal execution.

Nestedfilter attribution was checked on common-date side/entry/exit/net and compared with1000within-year
randomdrops. Per-trade mean alone is insufficient. Keep target unchanged in a stop-only intervention; all
13cases preserve specified nonablated exits. LDFsource embeds ticks in prices, so expose its gross/commission/
slippage bridge before nativeMNQ conversion. $7.25NQcommission divided by10 is not the modeled$1.25MNQfee.

Source-like missingminute policies and differing target-fill rules remain: unknown nominalheldcloses are
counted, not futurefilled; RSretains within-rowforwardfill, DTobservednextbar and LDFskippedmissingbars.
Rerunning a port is not fresh MC/nativefill parity or a risk guarantee. Before any proposed newrule: separate
preregistration, native path/parity checks, then current-book comparison at integer size. No measured execution
savings, accountpayout improvement, funding recommendation or new source-data purchase established here.


Late-dayRS execution/design follow-up (2026-11-08):
[registered comparison](results/ldf_rs_20261108.md) replayed14:00residual entries with filled-entry ATRstops,
entrybar/gap handling and14:30flatten. Independent baselinewalker matches all492sourceLDFdesign trades
on side/net. Five synthetic fixturegroups cover long/shortstops,entrybar,gap,flatten/nativefeesandmissing
path rejection. No unknownheldOHLCin admitted1242sessions; common-calendarzeros alter Sharpe denominator,
not profit. Do not label that denominatorchange alpha. Next-bar fills remain modeled;1minute-delay replay
is a sensitivity, not measuredlatency. Fixedorderextra-tickcostview does not reanchor a newstop path.

StandaloneLateRSdesign244trades,$40163perNQ/t3.72/PF2.19lookspromisingbutfails the registered paired
incrementconfidence gate versusLDF. Combinedfilter removes350profitable-in-aggregate LDFtrades andfails.
No2023+,portfolio,payout,MultiChartsorlive result. Frozen standalone lead retained for independentreview,
not automatic gate reopening or execution-savings claim. No plan or strategy settings changed.


FC/ONB/T ingredient follow-up (2026-11-08):
[18-case frozen diagnostic](results/ingredients_fc_onb_t_20261108.md) conditions FC 2B v2 and active
T_ONESIDE fade-only v2 admission on retained MultiCharts event dates/sides because their native up-tick
Volume is absent from total-tick exports. Original realized entry/gross replay matches all 770 FC and 358 T
parent trades through 2026-10-09. This establishes conditional exit parity, not a reconstructed up-tick signal
or native intrabar path. Four early T all-night control directions differ from the MC parent; do not call that
comparison a pure volume-filter deletion. Exact common-date side/entry/exit/net identity is required first.

T's 08:30-labelled entry is the 08:29 civil CT bar open, before the cash bell; delaying to 08:31-labelled open
reduces net by $8,695 in 2018–22 and $9,905 in already-seen 2023–2026-10-09, with positive paired annual
5th–95th intervals. This is historical OHLC timing sensitivity, not measured live fill savings. A later timing
proposal needs a separate registered test and native bid/ask/path evidence. No live logger or entry change.
FC no-BE uses the v2 BER>0 guard; stopping it genuinely disables BE. Hold other exit settings fixed.

Both ONBs share an opening-range core; ML adds frozen calendar/price/volatility terms with ADX20/0.30ATR,
so ADX30/0.25ATR is not its no-ML parent. Full-history-fitted coefficients cannot yield a fresh historical
ML holdout through a calendar split. Fixed-block deletion changes score level/admission; it is not additive
causal feature attribution. No account payout or risk improvement, promotion, plan/VPS/broker change claimed.


Opening-handoff combination follow-up (2026-11-08):
[Two-candidate design screen](results/opening_handoff_20261108.md) uses price-only overnight direction,
ONB location/first-range/ADX confirmation and FCv2 fixed-stop/trailing exits. Native up-tick volume and fitted
ML are omitted explicitly. Both combinations fail2018–22 (60 trades,t1.62;58,t0.61), so no later-return,
account or live stage follows. A larger selected-trade mean does not establish a useful execution/entry filter.

A source-adapter mistake requiring an exact17:01 bar admitted only35 sessions; T's rule actually uses the
first observed reopening bar. Retain the aborted receipt/partial look history, amend before corrected returns,
and distinguish a source/data-universe correction from an optimized new opening anchor. Never silently treat
missing reopen bars as price evidence. Nine synthetic stop/gap/trail/fallback/delay/fee groups passed; they
verify replay logic only. Restore skipped trading dates as zeros for final annualized reporting, rather than
shortening time; preserve original conditional gate calculations separately. No measured execution savings,
new independent native parity, trade-plan change or account benefit established.

### E09/E11/E12 follow-up — Risk forecasts, cash-futures legs and news-sign clocks (2026-11-08)

[Scout checkpoint](results/scout_owned_source_20261108.md); selected sections/metadata only,
not full-paper reviews or independent economic verification. No return tests or execution savings.

- **Risk Everywhere, SSRN2722591 / DOI10.1093/rfs/hhy041:** selected final-published introduction
  evaluates risk models with a constant-Sharpe/mean-variance utility framework. Its48bp illustration
  is modeled willingness-to-pay, not measured cash alpha. A future sizing comparison needs past-only
  fit/centering, actual integer transitions/turnover and account paths against the same base.
  Source58-market estimation is not reproduced by substituting one owned future. No new trial now.
- **OFR21-01, Barth/Kahn:** selected CTD/convergence sections require the deliverable security,
  coupon cashflows, conversion/financing conventions and repo conditions. Cheapest-to-deliver status
  can change; continuous ZN is not a complete cash-futures hedge or cash ledger. A later basis test
  needs identified dated legs and funding constraints before any return/correlation interpretation.
  The paper interprets March2020unwinds mainly as a consequence of stress; do not assert they caused it.
- **Earlier SSRN1920401 draft:** SectionVI trades actual-minus-consensus surprise sign after a minute,
  not first-minute price direction. Simultaneous releases must agree. Descriptive full-day jump labels
  are not automatically the strategy's live filter: the draft explicitly uses all trading days for its
  trading analysis. One tick each way is not proof of modern all-in fees/latency. Need original receipt/
  release vintages, published-version parity and first executable native transactions; no live change.
- **Pradkhan, fut.21755:** publisher abstract and related thesis summary discuss regime-dependent
  activity/returns. A retrospective bull/bear state is not an available-at filter. Full journal methods,
  filtered-versus-smoothed state convention, position publication clocks and native costs precede code
  claiming a predictive benefit; volume-only bars cannot silently replace source OI/position inputs.

The TOPIX reconstruction and FX subminute-activity records are metadata cautions only. Authenticate
native mark/index construction and event resolution before using apparent reversals or minute-boundary
activity as an ES/6E predictor. Neither an abstract nor a file with minute labels verifies a fill.
Park absent source/data; continue distinct strategy discovery. No automatic gate reopening or allocation.


Pre-open signed-volume follow-up (2026-11-08):
[Native absorption screen](results/preopen_absorption_20261108.md) independently verifies the transported
2018–22gzip/original hashes, ET close→CT clocks, finite quantities and native total=buyer+seller. Native
aggressor fields are distinct from ordinary PowerLanguage up-tick Volume. The1,755,357bars are not a verified
raw-contract/tape or historical receipt archive. Preserve original source/build/roll and missing-stress limits.

Features end08:28CT; modeled normal entry08:30-labelledOPEN is08:29civilCT, leaving one minute of assumed
processing. A delay to08:31OPEN enters at the cash bell. Receipt delay is an assumption, not a measured saving.
Scheduled08:45OPEN exit preempts that bar's intrabar stop. Ten synthetic fixture groups cover clock/entry/gap/
rounding/flatten/delay/fees; held paths have no imputed bars. Gross/native-fee/daily ledgers reconcile.

The registered34-event absorption candidate loses$6,386.50perNQ,PF0.55, and fails; no later/account/live stage.
The contextual [Farmer etal2006 source](https://arxiv.org/html/physics/0602015) concerns adaptive liquidity,
not demonstrated NQ reversal profits. Keep that evidence distinction. Heavy-total-volume comparison repeats
known T-style conditioning; its positive design result is not new native parity, a selected strategy or a payout
improvement. No follow-direction or new clock is tested as a post-result rescue.

### E11 follow-up — UGL/GLL valuation, publication and reset clocks (2026-11-08)

[Historical primary-source audit](results/gold_clocks_20261108.md),
[preserved documents and evidence matrix](inputs/gold_clocks_20261108/README.md), data needD15.
Before January4,2019 gold NAV follows15:00London, usually10:00ET with US/UK DST mismatch variation.
January4normal NAV moves to13:30ET and AP cutoff13:00; both funds first strike BCOMGC NAV January7.
Annual2021/22tables corroborate normal policy. Do not back-map today's futures benchmark or clock to2018.
The2018 printed sponsor AP cutoff09:30 conflicts with an older-rule09:00 citation; retain uncertainty.

Source evidence supports daily mandates and typical/variable rebalancing around valuation, not exact
executed reset times or simultaneous counterparty GC hedges. IOPV dissemination is not finalized NAV
publication. NAV/AUM/shares date labels and current HTTP metadata do not establish historical available_at.
AP order cutoff, NAV basis, cash/futures settlement, share recognition and hedge timing are distinct;
historical T+1/T+2 provisions are not a universal lag for daily share changes. Actual daily contracts,
weights, exception notices, first receipts/revisions and execution records remain missing.

Next useful check: one authenticated original/revised field capture and matching order/settlement/reset
record, then a DST-mismatch/transition/early-close comparison. Separate2,518policy rows retain blank
publication/execution clocks and unchanged original data. Evidence is source-policy QA, not measured
execution savings, historical profitability, strategy admission or authorization for live/broker changes.

### E11/E19 follow-up — Treasury result documents retain earlier announcement times (2026-11-08)

Source: [local primary-data intake](results/new_data_local_20261108.md),
[independent cloud review](results/primary_data_review_20261108.md) and original TreasuryDirect XMLs in the
hash-verified transport package. This is direct source-field verification, not a trading or execution-return test.

- **Useful lesson:** retain announcement, operation start/close, result-content publication, download receipt and
  settlement clocks separately. All 520 audited operation XMLs carry a pre-operation `announcementDTM`, including
  172 `Results` and 206 `Released` documents; none supplies the parsed result-publication field. Do not make accepted
  amounts/prices available at the old announcement time just because they share a result document.
- Original operation-start offsets are 376 `-04:00` and 144 `-05:00`; a fixed year-round EST conversion would be wrong.
  Filenames encode another source clock and are not announcement times. Current download/Last-Modified times are not
  historical first public receipt. NYFed result `releaseTime`/`lastUpdated` labels likewise need semantic verification.
- **Next check and limits:** authenticate the actual historical release/receipt and revisions for one event before
  any separately preregistered strategy/execution replay. Keep current/future tentative schedules separate from
  completed outcomes and historical programs/tests separate from regular modern buybacks. No inferred result clock,
  automatic gate reopening, execution saving, deployment or live-system change follows.

### E09/E15/E18 follow-up — Event ingredients, source clocks and hidden intratrade risk (2026-11-08)

Source: [EOS/NFP/CL ingredient round](results/ingredients_events_20261108.md), frozen plan `fa2be26`;
15 diagnostic definitions, design first and unchanged historical recent replay. No changed rule selected.

- A CL no-stop trade attributed to Monday 2026-03-09 closes at about+$3,813 perCL after an observed source adverse
  mark of−$16,007. The recent no-stop daily DD is unchanged even though its intratrade mark is much worse.
  Booked profit/daily DD cannot substitute for an account-floor replay. One held source bar is missing on this event;
  its true worst path is not certified. Do not remove protection because the final cash ledger looks better.
- Preserve close-stamped bar labels versus civil open times: EOS08:31OPEN is08:30CT; NFP07:46OPEN is07:45CT;
  CL17:06OPEN is17:05CT, with the actual source exit09:00CT/10:00ET. The older CL10:00CT study is a different horizon.
  A first observed Sunday open after the five-minute decision cannot be used retrospectively for its gap signal.
- Source NFP/EOS stops anchor to raw entry, CL to slipped entry. Standard-contract and native-micro commissions
  are distinct; the sensitivity fee here is assumed$1.25RT perMNQ/MCL, not a verified broker quote. Extra cost on
  fixed orders is not a latency/stop re-anchoring replay or a demonstrated execution saving.
- The replay explicitly exposes skipped missing held bars and last-close fallback exits. Source-price agreement
  and five synthetic fixtures do not certify native fills, dated rolls or actual bar/receipt latency. Next use only
  for a separately preregistered changed strategy/account test after those prerequisites; no live/VPS/broker change.

### E09/E15 follow-up — Monday entry clocks, Sunday targets and Bridge path risk (2026-11-08)

Source: [Monday/Bridge/MOC ingredient round](results/ingredients_monday_moc_20261108.md), frozen plan `30b53e7`;
15 definitions, design checkpoint `756d29d` before unchanged recent replay. This is component attribution,
not a selected execution change or new account-survival estimate.

- Preserve the actual Sunday target timestamp when attributing a Bridge trade to Monday. The retained source's
  Monday `j1=0` marker for a Sunday fill is not the execution time. Four design and seven recent original trades
  complete on Sunday. Start adverse-path inspection after the Sunday 19:00 CLOSE entry, including the path
  before midnight; an old source next-morning `ovn` mark is not realized overnight P&L after an earlier target.
- Original Bridge's 2025-01-27 trade shows an observed adverse mark of −$16,427 per NQ before a −$5,757 exit.
  No held bars are missing on that source event. At the assumed native micro fee this mark is about −$1,643
  per MNQ. Elsewhere source gaps remain, and neither daily DD nor one observed mark certifies the worst native
  path or whether other book positions offset it before a breach. A profit target does not cap losing exposure.
- Bridge's target retains source touch fills and favorable-gap improvement. This is not a queue/trade-through
  certification or a waiver of future candidate fill controls. Target-bar high/low order remains flagged.
  Source Monday 08:30 CLOSE differs from Monday Long's 08:31-labelled OPEN at 08:30 civil CT. ES MOC's
  14:51-labelled OPEN is 14:50 civil CT; preserve its ES $50 multiplier and $12.50 tick separately from NQ.
- MON's last-close fallbacks and Bridge's retrospective Monday 14:55 coverage check are retained and reported.
  Source agreement alone cannot validate live-known availability. Keep costs, missing paths, early closes,
  actual labels/receipts and dated rolls explicit before a separate native/account replay. No live changes follow.

### E04/E09 follow-up — S30 daily clocks and Kusho unprotected fill bars (2026-11-08)

Source: [S30/S47/Kusho ingredient round](results/ingredients_s30_s47_kusho_20261108.md), frozen plan `f43c459`,
design checkpoint `324f5c1`;20 market/rule combinations, unchanged recent replay. Source attribution only.

- **Marked risk and accounting clock:** S30 NQ whole-history marked DD is$59,548 versus$37,656 booked only at
  exits; ES$50,003 versus$24,040. This round uses weekday23:59CT last-observed marks, unlike earlier15:00 cash
  marks. The final trade/daily totals reconcile, but the clocks can produce different DD without an accounting
  error. Neither is a prop-floor replay. Keep fees, actual fills, crossed roll removal, stale-mark ages and the
  clock definition with every risk figure. No capital/portfolio sizing update was performed.
- **A profitable closed trade can hide risk:** S30 ES's2025-04-03→04-09 trade closes+$2,633 after an observed
  adverse source mark−$30,243 perES. The NQ2024-07-23→08-08 trade shows−$51,492 before a−$28,137 exit.
  Absent-calendar-minute counts include scheduled closures; they are not all proven missing feed bars or a
  certified continuous native path. Offsets elsewhere in a book must arrive before a breach, not merely later.
- **Fill-bar lifecycle:** Kusho's2026-06-17 entry shows−$6,482 before a−$2,782 stop exit; its15-minute fill bar
  is unprotected. Full-bar high/low used for BE can also precede the actual limit fill.50/27 original trades in
  the two eras have nonpositive accepted swing risk. Retaining source mechanics for attribution is not native
  verification or approval to deploy them. S47 likewise retains a one-minute entry protection gap, distinct
  from the separate fixed MC backstop. Preserve both actual fill time and protection-activation time.
- **Grouping is not marginal contribution:** about43% of original Kusho profit lies in weekend-held trades,
  whereas original minus15:45 flattening is$51,095 across the whole history and changes weekday paths too.
  Neither grouped trade profits nor that broader timing comparison identifies an exact weekend-only premium.
  State-changing filters also cannot be assessed as pure deletions of original trades.
- **Next justified use:** verify native contract/roll identifiers, quote/fill and stop-activation clocks, partial
  fill/queue behavior and intrabar paths before a separately frozen implementation/account comparison.
  Current roll repair is retrospective price-jump identification, not executable rolling. No measured live
  execution saving, new strategy promotion, account survival estimate or live/VPS/broker change follows.

### E04/E09 follow-up — Causal fades, early-close guards and average-trade traps (2026-11-08)

Source: [Anson/R2Vault/S03 ingredient grids](results/ingredients_anson_r2_s03_20261108.md), plan `7320764`,
syntax-only amendment `65de599`, design checkpoint `70e5d0a`. Fifteen definitions; no changed strategy selected.

- **Keep the execution cursor:** fading R2's upward break means shorting only after the original trigger crossing,
  then applying the mirrored bracket to the remaining path. An earlier Low is not a short target. S03's fade keeps
  virtual follow-side band decisions while mirroring actual position and stop. Incompatible follow exits on a fade
  would test a different rule. Source OHLC sequencing and immediate processing are model conventions, not tick/
  order-receipt parity. Synthetic causal-cursor/gate checks precede market returns.
- **A weak average-profit effect does not make a guard decorative:** Anson's early adapter has little profit effect,
  but removing it produces6/5 late fills across the eras versus0/0 originally, including one recent cross-date
  trade. Unknown-held-minute labels grow to1,140 recently; closure classification is a proxy. Preserve actual
  next-observed-chart-open fills and phase timestamps instead of supplying a nonexistent14:55/early close.
- **Average trade is not total contribution or survival:** removing S03's sigma stop raises recent average$132→$174,
  yet total net is$132,191→$133,309 while daily DD rises$21,951→$41,219 and count falls1,004→765. Reentries and
  occupancy change. R2 without its stop has recent DD$76,687 versus$23,569, worst realized loss−$24,147 perNQ,
  and an observed−$26,952 mark on2025-04-08 before a−$22,007 close. No missing held minutes are flagged on
  that event. These observations are not native-tape extrema or an account-floor simulation.
- **No false deletion controls:** entry-gate changes in all three families fail exact event-level nested identity.
  Multiple trades on a date must match entry time/side/exit, not date alone. Keep whole-policy effects separate
  from a fixed-trade overlay and baseline side contributions separate from executable side-only reruns.
- Next justified use is a separately frozen native implementation/quote-path comparison with real clock, contract,
  fee, closure and floor semantics. The retained standard-NQ fee differs from older micro-equivalent tables;
  never splice means across units/universes. No live execution saving, admission, allocation or VPS/broker change.

### E09/E11/E19 follow-up — Reweighting inputs, causal jumps and price-discovery claims (2026-11-09)

- **Annual net demand differs from a monthly roll.** Selected Section2 of Yan/Irwin/Sanders2019
  ([author draft](https://scotthirwin.com/wp-content/uploads/2019/08/yan_irwin_sanders_supply_curve_slope_public.pdf),
  [record3360787](research/scout/records/3360787.json)) distinguishes announced production weights from
  market dollar weights. Its latter calculation uses the full index price denominator and designated contracts;
  annual reweighting overlaps a monthly roll, whose two legs have different demand effects. A generic January
  outright trade or current index weights cannot reproduce that event study. Settlement-time trading is an
  assumption in the inspected discussion, not an observed fill receipt. Full draft/appendix not reviewed.
- **Jump removal must match the causal source method.** Selected AppendixA.1 of
  [Aleti/Bollerslev/Siggaard2025](https://public.econ.duke.edu/~boller/Papers/MS_2025.pdf)
  ([record4388560](research/scout/records/4388560.json)) uses a rolling ex-ante jump threshold with time-of-day
  adjustment. Do not misdescribe it as a full-day hindsight classifier. Complete initialization/settings still
  require full reading, and its stock-factor return panel is absent from futures-only data. Forecast target,
  tradable ETF and native futures are distinct objects; their costs/rolls cannot be silently interchanged.
- **Efficient price discovery is not a signed subsequent-return rule.** The inspected
  [bond-futures opening abstract](https://onlinelibrary.wiley.com/doi/abs/10.1002/fut.22015) and historical
  [opening-consolidation metadata](research/scout/records/467120.json) describe information/market design.
  Neither supplies an admitted directional futures trade. Similarly, calendar-spread liquidity observations
  ([6087367](research/scout/records/6087367.json)) require simultaneous dated legs/books to model execution.
- **New files retain their own information clocks.** November9 identity checks match13 prior selected raw files,
  five macro snapshot files and five NQ gzip/original pairs. The NQ timestamp is minute close, not start;
  UpVol/DownVol are claimed buyer/seller aggregates, not native uptick Volume or trader IDs. The new macro
  catalog lacks the seven10:00ET release families needed by1920401, and historical forecast/actual receipt
  vintages remain unresolved. UGL/GLL policy clocks do not supply actual per-date publication/reset execution.
  [Inventory and exact mapping](inputs/scout_20261109/owned_input_inventory.json).
- **Status/next check:** supporting source/intake evidence only; zero new return definitions, execution savings
  or account comparisons. Park conditional watches until new matching inputs arrive. Then reconcile one
  source event/forecast/leg/clock before coverage, costs, power and preregistration. Continue distinct discovery.
  [Combined checkpoint](results/scout_owned_source_20261109.md). No live or allocation change.

### dot follow-up: shared account losses and source-review limits (2026-11-10)

Author/origin: **dot**, supplementing the existing evaluation-audit entry rather than a new strategy.
- [Loss-path map](results/dot_vb_onb_loss_map_20261110.md): documented ONB planned loss exceeded remaining cushion; the November 4 accounts were below reconstructed floors before later VB chart trades. Shared direction is one market event with separate account paths. Chart markers do not establish broker fills.
- The older 89% statistic spans any one of five components exceeding 70% of modeled failure-day loss; it is not VB/ONB-specific or a live failure-rate estimate.
- [Unbiased Trading review](results/dot_unbiased_trading_review_20261110.md): executable-cost and concentration lessons are methods, not verified alpha. The [Hyperliquid audit](results/hyperliquid_data_audit_20261110.md) distinguishes final settlements, forecasts, oracle prices and cash entitlement.
- Missing broker fills/floor history and historical funding receipt/payment evidence remain explicit. Smallest next check is evidence reconciliation, not an unregistered timing/size optimization. No measured execution savings, new return tests, allocation or program restart.

### dot follow-up: Whop broker/chart lifecycle anecdote (2026-11-10)

Source: user-supplied Whop export; [dot review](results/dot_whop_review_20261110.md). Extends E04 rather than introducing a new execution hypothesis.
- A Kusho community report describes asynchronous broker-fill/chart-state mismatch. This is an unverified third-party anecdote, not an inspected user setting or confirmed cause of the user's losses.
- Useful lesson: reconcile order IDs, submission/acknowledgement/fill/cancel clocks, position state and reconnect behavior against broker records; chart markers alone do not establish actual fills.
- Smallest next check, if matching evidence becomes available: one complete order lifecycle with timezone, contract and account mapping. No live inspection/change, measured saving, new logger or schedule follows from retention.
