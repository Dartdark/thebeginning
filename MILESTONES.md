# Milestones: how this started and what's been built

A record of the beginnings and the progress, in order. Dates are from the repo's history (all 2026). Details of every
test are in `TIER_LIST.md`; the current state is in `NEW_CHAT_BRIEF.md`. Add new milestones at the bottom.

## Week 1: from one strategy to a tested plan (Oct 9-12)

- **Oct 9: day one.** A single NQ VWAP-momentum strategy written in MultiCharts PowerLanguage, first backtests exported
  by hand ("Add files via upload"), CME Central-time conventions and the first reserved-word fix (`NumContracts`).
- **Oct 10: the research engine starts.** Bar exporter to get 1-minute data out of MultiCharts, a Python replica of the
  strategy, a prop-firm simulator (Topstep first, then the **Apex 50K EOD** preset that became the standard).
  First multi-strategy Apex plan; **Vault Break** and **Overnight Bias** found and **MultiCharts-confirmed**; first Monte
  Carlo.
- **Oct 11: two phases, two folders.** The funded (payout) phase planned with a PA payout simulator; strategies split
  into `apex_strategies/` (evaluation) and `funded_strategies/` (payouts); ES data added; the funded test bench built.
- **Oct 12: first live account and a big research day.**
  - **Account #1 (Apex 50K EOD) goes live** (the first days turned out to be on Paper Trader; see Oct 16).
  - **Expiration Open Short** (dealer hedging on options-expiration Fridays) confirmed, 105/105 trades.
  - **Overnight Bias ML**: a walk-forward ridge "skip today" filter (Kelly & Xiu paper), MultiCharts-confirmed, the
    plan's first **S-tier** strategy.
  - **Monday Long** and **Late-Day Flow** (leveraged-ETF / last-hour flow) found and MultiCharts-confirmed (450 and 895
    trades matching Python).
  - **The testing standard is born:** S-F **tier list**, random-entry placebos, longs and shorts analysed separately,
    Sharpe / Sortino / PF / Calmar / Ulcer, bootstrap and permutation tests, parameter clusters, fold stability.

## Week 2: a full funded plan, hardened (Oct 13-16)

- **Oct 13:** **NFP Fade** confirmed; **The Bridge's Monday Long** ported and confirmed 217/217 (added next to ours);
  combine add-ons lift the evaluation pass rate 46.9% -> 50.5%; order flow, dealer gamma and COT from The Bridge exported
  and tested (no edge: an important negative result).
- **Oct 14:** **S-rank program** (one top strategy per market). **CL Sunday Gap Fade** found and MultiCharts-confirmed
  (96/97, PF 3.02, 9/9 years): first non-NQ strategy in the plan. Account-pipeline study; live-vs-backtest tracker.
  First live order rejection (Overnight Bias stop above the market): every strategy now enters at market when the price
  is already through the level.
- **Oct 15: rigor upgrade.**
  - **Multiple-testing control** (trials log, deflated Sharpe, the t-bar) and the **independent checker** (maker-checker
    split with a fresh agent that rebuilds every candidate from its spec).
  - **Single-print day filter** for Vault Break (confirmed, adopted for funded).
  - **Twin Continuation** (your strategy): real edge, t 5.3, MultiCharts-confirmed, **A tier**: kept for a personal
    account. Your preference recorded: big, frequent edges.
  - **150K accounts** studied (+55% per slot); **strategy lifecycle** written: backtest -> MultiCharts + checker -> Apex
    incubation -> personal account. **Drift alarm** for live tracking.
- **Oct 16:**
  - **Business plan** (`reports/Trading_Business_Plan.pdf`): account choice, projections, roadmap, risks.
  - **Found that nothing had really traded yet:** every Rithmic order had been rejected because Symbol Mapping sent
    `@MNQ`. Fixed (`@MNQ -> MNQZ6`).
  - **Apex Target Guard** (evaluation finish line).

## Week 3: going live for real (Oct 17-21)

- **Oct 17:**
  - **Stop guard** on every live strategy (Rithmic rejects stops already through the market).
  - **Jesse + Antigravity integrated** on your PC: a second engine and a second AI lab. All 8 plan strategies
    cross-checked 97-100% trade-by-trade.
  - **Bootstrapped funded bench** (1,000 resampled histories) replaces the single history for plan decisions.
  - **ES MOC Follow** confirmed 199/199 and added (MES). Journal in Obsidian set up.
- **Oct 18:**
  - **First real Apex fill** (test order) and the **Bridge Monday first live run**.
  - Replacement sweep: no candidate beats the plan.
  - `LESSONS.md` started.
- **Oct 19:**
  - **Live trading moves to a VPS** (QuantVPS, Chicago); its backtest matches the PC 75/77.
  - **Trade logger** on every live chart, with an automatic daily push to GitHub and an automatic journal entry at 16:40 CT.
  - **Cowork** (local Claude) for chores; repo made private.
  - **First Apex daily-loss-limit day**, handled and documented.
- **Oct 20:**
  - **Account #2** set up on the VPS.
  - **Relative Strength NQ / ES** (your strategy, built from a lead-lag probe and two papers):
    - rebuilt (t 4.0, 9/9 years);
    - independent checker PASS WITH CONCERNS;
    - **MultiCharts-confirmed 1,157 days, P&L corr 1.000**;
    - optimisation found nothing better than your settings;
    - **added to both funded plans** (50K longs, 150K both sides) and the personal plan.
  - **Building-blocks program** tested (catalog blocks: no standalone edge, intraday or as swing trades).
  - **Antigravity becomes a strategy builder:** it learns the rules one mistake at a time (full data, costs, flat by the
    close, random entries, in-sample gate, honest fills) and starts rejecting its own failures.
  - **Performance Report Guide** PDF (how to read a backtest: bad / good / great).
- **Oct 21: running on its own.**
  - **Repo reorganised** (README map, one place per kind of file).
  - **Pre-flight checklist.**
  - **Automatic health checks:** the logger compares chart and broker positions, writes heartbeats, and the journal gets
    a 'Health (auto)' section.
  - **Live phone alarm** (ntfy): every 5 minutes it checks MultiCharts up, connection, frozen charts, position
    mismatches and new rejected orders (with a Symbol Mapping hint).

## Where it stands (Oct 21)

- About **300 ideas tested** and graded; a handful kept. The plan's edges are mostly forced flows (expirations, payroll,
  auctions, weekend gaps), breakouts, and relative strength.
- **Live:** two Apex 50K evaluations on a VPS, logged and monitored automatically; account #3 (150K) around Oct 27.
- **Next milestone:** the **mid-December gate**: 40-70 live trades at >= 75% of the backtest and no drift alarm, then
  scaling toward 20 accounts and a personal account from the first payouts.
