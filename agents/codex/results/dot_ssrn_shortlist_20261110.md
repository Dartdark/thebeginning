# SSRN strategy foundations: one new conditional lead, no test-ready promotion

Summary: Basis-Momentum is the strongest new foundation found in this pass, for a personal-account commodity book.
Annual commodity-index rebalancing remains a worthwhile existing data-blocked lead, not a new discovery.
Rates/FX candidates mostly duplicate prior rejections; the full papers reinforce execution-cost concerns.
No paper establishes an improvement to the user's current account survival or payouts.
Source review only: zero return tests, economic definitions, purchases, live changes or schedule changes.

Author: dot. Date: 2026-11-10.
Repository: Dartdark/thebeginning, codex/work. This is a one-off request, not a restart of paused programs.

## 1. New conditional foundation: Basis-Momentum

Boons and Porras Prado, [SSRN2587784](https://ssrn.com/abstract=2587784), subsequently Journal of Finance 74 (2019), 239–279.
[Primary manuscript inspected](https://conference.nber.org/confer/2016/CEMf16/Boons_Prado.pdf): 2016 conference version, 74 pages including appendix. Publication-version parity is not established.

**What is it about?** Monthly commodity-curve predictability. Signal: compounded prior-12-month first-nearby return minus second-nearby return. Rank monthly; buy top four, sell bottom four, using outright contracts or calendar spreads.

**What does it find?** 1960–2014 historical high-minus-low annual returns: 18.38% outright (t6.73), 4.08% spreads (t6.43). These are author results, not current net returns. Cost illustration assumes 4.4bp half-spread and 211.2bp yearly turnover cost. Cross-currency evidence supports portability, not prospective validation.

**Why might it pay?** Maturity-specific pressure and compensation for volatility risk; not demonstrated compulsory orders.

**Can we build on it?** Conditional personal research, not intraday Apex. Main universe: crude, gasoline, heating oil, rice, corn, oats, wheat, cotton, lumber, feeder/live cattle, lean hogs, gold, silver, copper, soybean oil/meal/beans, coffee, orange juice, cocoa. Expanded sample has32 commodities.

**Can code be made?** Yes with identified contracts, monthly prices, twelve-month warm-up, rolls and costs. Source rolls before expiry-month proximity; follow its exact rule. References: sections2–3, Table1, Table8, AppendixA.1.

### dot's implementation assessment

Verdict: **NEEDS DATA / source-version reconciliation**, not TEST or a trading recommendation.

- This differs from D06 weekly basis reversal, D08 double-sorted momentum/carry and D09 skewness. It nevertheless shares their expensive maturity-panel prerequisites. Do not build a second acquisition pipeline or claim it is independent merely because its name differs.
- No exact2587784 or “basis-momentum” hit in repository search; its ID was absent from the retrieved codex/work scout progress. Connector search is not a proof of exhaustive branch coverage.
- Existing CL/GC/NG continuous series cannot reproduce a cross-sectional paired-contract strategy. Do not silently reduce the universe, replace deferred prices with continuous-front proxies or use back-adjustment changes as tradable P&L.
- First permitted next step: reconcile publication-version definitions and one complete source-sized month, including actual roll cashflows, information availability and whole-contract quantities. Then a no-return coverage census. No return test was run here.
- An eventual protocol must fix signal/weight/roll rules before returns, charge both legs and native micro commissions, model collateral/margin and marked open losses, and separately label any altered universe.
- For account survival, compare loss timing with the existing equity book. Calendar spreads can gap, become illiquid or face margin changes. Different underlying markets do not prove protection when capital is most needed.
- The accessible manuscript is free to read. Original CRB/Futures Industry Institute data are not verified as free or licensed for redistribution. No complete lawful free matching panel was obtained. Publication repository access returned an explicit access denial; it was not bypassed.
- Code feasibility is stronger than deployment readiness. Python research is plausible; production PowerLanguage would need synchronized multi-contract instruments, order lifecycle and integer sizing, independently verified later.

## 2. Existing conditional foundation: annual commodity-index rebalancing

Yan, Irwin and Sanders, [SSRN3360787](https://ssrn.com/abstract=3360787), “Is the Supply Curve for Commodity Futures Contracts Upward Sloping?”
[Author's58-page February2019 manuscript](https://scotthirwin.com/wp-content/uploads/2019/08/yan_irwin_sanders_supply_curve_slope_public.pdf). Methods, event definitions and results inspected.

**About:** annual GSCI demand changes, distinct from monthly maturity rolls.
**Findings:** 24 commodities,2004–2017; signed-weight long-short cumulative abnormal returns peak59bp at event day7 and decline to10bp by day15. This is not costed strategy profit.
**Mechanism:** announced index demand meets temporarily inelastic supply.
**Build on it:** conditional personal-account research, already parked. Fourteen annual event clusters give much less independent evidence than a commodity-by-day count implies. Selecting the observed peak as an exit is hindsight.
**Code:** conditional on historical contract-production weights, designated contracts, announcements, calendars and settlements. Signal normalization uses old/new production weights with the same pre-rebalancing prices; raw year-over-year index-weight changes are not equivalent. Implementation occurs January business days5–9. See sections2.2,3,4.2.

### Dedup and next action

Current record `agents/codex/research/scout/records/3360787.json` already reviewed this source on November9; S01 in DATA_NEEDED records its prerequisites. This pass confirms an existing foundation, not new alpha or a solved data gate. Do not create a duplicate queue item. Recover one original announced weight change and its full-universe denominator/contract mapping before proposing a test. No complete free matching historical input set or rights were verified. Multi-day exposure is incompatible with the ordinary prop flattening requirement.

## 3. Strong papers that should NOT become new tests

### FX fixings: reject recycled gross seasonality

Krohn, Mueller and Whelan, [SSRN3521370](https://ssrn.com/abstract=3521370), [published Journal of Finance full text](https://onlinelibrary.wiley.com/doi/full/10.1111/jofi.13306).

**About:** recurring currency moves around benchmark fixing.
**Findings:** spot1999–2019 and futures2006–2019; published TableX shows negative unconditional liquidity-demanding customer returns after spreads, unlike liquidity providers.
**Why:** benchmark-related order flow; knowing a pattern is different from earning its spread.
**Build:** no revival of the already rejected European pre-fix design.
**Code:** clocks can be coded, but a faithful execution/conditional-flow study needs executable quotes and source-matched flow. Refinitiv FX Matching is not replaced by CME order flow. No verified free full input set. Published evidence does not establish present net profitability.
Existing evidence: `agents/codex/results/scout_3521370_20261029.md`.

### Treasury month-end: existing failed family

Hartley and Schwarz, [SSRN3440417](https://ssrn.com/abstract=3440417), [full manuscript](https://rodneywhitecenter.wharton.upenn.edu/wp-content/uploads/2019/12/17-19.Schwarz.pdf).

**About:** predictable month-end bond demand.
**Findings:**1990–2018 study reports around0.25% monthly ten-year excess return over final three trading days and annualized Sharpe around1; source uses yield/financing construction with futures robustness checks.
**Why:** benchmark and investor rebalancing.
**Build:** background only; do not override rejected modern unconditional ZN protocols.
**Code:** calendar rule possible, but original multi-day exposure is personal-only; executable native contracts, financing/rolls and current costs remain necessary. An intraday flattening adaptation is a different hypothesis.

### Treasury auction cycle: not an auction-day futures scalp

Lou, Yan and Zhang, [SSRN1659239](https://ssrn.com/abstract=1659239), [author manuscript](https://personal.lse.ac.uk/loud/Shocks.pdf).

**About:** predictable auction-cycle dealer inventory pressure.
**Findings:**1998–2008 cost analysis makes holdings of six days or fewer unprofitable; ten-day version net annualized Sharpe0.84.
**Why:** temporary intermediation constraints and subsequent inventory absorption.
**Build:** mechanism reference only; existing auction-family failures remain binding.
**Code:** original trades two-year cash notes with duration-matched bill/ten-year hedges and reverses around auctions. A ZT/ZN implementation changes instruments, financing and hedge. Needs a separate justified protocol, not a relabelled retry.

### Goldman roll: retain rejection, not a fresh recommendation

Mou, [SSRN1716841](https://ssrn.com/abstract=1716841), [CFTC-hosted July2011 manuscript](https://www.cftc.gov/sites/default/files/idc/groups/public/@swaps/documents/file/plstudy_33_yu.pdf).

**About:** short index-held maturity and buy destination maturity before scheduled rolls.
**Findings:** historical19-commodity2000–March2010 Strategy1 calendar-year Sharpe2.75; headline4.39 uses capital-deployment-day annualization. Transaction costs excluded.
**Why:** anticipated index roll demand and limited arbitrage.
**Build:** no. Repository full-source review already says DON'T TEST, retaining post2006 decay and negative livestock results from2008.
**Code:** paired-contract calendar rule possible, but overnight exposure, costs and obsolete sample prevent a current recommendation. Do not revive failed outright CL proxies.
Existing evidence: `agents/codex/results/scout_1716841_20261029.md`.

## 4. Source-blocked or duplicate leads not elevated

- SSRN2682698, Liquidity Timing: abstract accessible, full manuscript not obtained. Keep S09 parked; no abstract-only promotion.
- SSRN3357455, soft-commodity curve effects: abstract accessible; no new full-source review or executable rule established.
- SSRN3792028, trading-time seasonality: accessible Glasgow paper begins with monthly-averaged prices across many maturities; already recorded, no newly solved executable-price or panel gap.
- SSRN5250499 weekly basis reversal,2942340 roll spreads,2614241 carry/momentum and3507947 skewness already have distinct DATA_NEEDED entries. None was retested or relabelled.
- SSRN4761614 volatility-managed volatility selling was only screened at metadata/abstract level. Do not treat it as full-text-qualified or sell-vol protection for an equity-heavy book.

## 5. Portfolio decision and research gates

**Priority1:** investigate the Basis-Momentum input/version gap, sharing the existing broad commodity-panel work. This is the only newly shortlisted source.
**Priority2:** retain annual GSCI reweighting in its existing queue; proceed only when genuinely new matching inputs arrive.
**Prop-account shortlist:** none from this pass. Do not manufacture an intraday strategy by trimming the original holding period.
**Ready-to-code production strategy:** none. A research selector is feasible, but missing native inputs prevent an admitted economic test.

For a future admitted candidate: preregister bounded definitions, use the repository's design/cost gate, then only earned validation and BASE/ADD/REPLACE/EMPTY account comparisons. Historical2023+ data are already seen, not pristine holdout. Promotion requires independent review, native parity, frozen forward evidence and user approval. No existing ranks, book memberships, sizing or operational files changed.

## Audit

Read AGENTS, complete BUILDER_BRIEF, handoff, TIER_LIST, DATA_NEEDED, scout progress and relevant per-paper records, SCOUT_LOG and personal PORTFOLIO at codex/work. Plan prose contains older statuses; no live/current-sizing inference made. Exact-ID/title searches supplemented, not replaced, branch-specific records. Secondary summaries were used for discovery, not adopted as verified performance.

Research scope: targeted SSRN search, not an exhaustive catalog census. Primary manuscripts were inspected for key methods/results/costs; no claim every page or every referenced dataset was independently replicated. All paper performance figures are author-reported. No return tests or trial-budget reservations; paused programs remain paused.

Tell Claude: review `agents/codex/results/dot_ssrn_shortlist_20261110.md`, especially2587784's distinctness, manuscript-version parity and shared data gate; no promotion requested.
