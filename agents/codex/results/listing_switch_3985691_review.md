# Switching to Nasdaq: useful execution measurements; no futures alpha

Summary: The paper studies stock listing transfers, dark/lit trading and execution costs, not Nasdaq-100 futures.
Authors report wider quoted spreads and migration to dark trading; announcement CAR is not significant.
Table 5's large-firm dark effective-spread change is +0.031 percentage points, contradicting the claimed improvement.
Retain signed spread/markout diagnostics; DON'T TEST as a trading strategy. No independently verified returns or allocation.

Source: S. Bonini, E. Gousgounis, F. Pavesi and A. Taatian, *Trade-off Between Trade Efficiency and Immediacy:
Evidence from Switching to NASDAQ*, [SSRN3985691](https://ssrn.com/abstract=3985691), December 15, 2021,
**preliminary and incomplete** user-uploaded draft. 45 PDF pages: two front pages plus printed pp.1–43.
Reviewed November 7, 2026 (America/Los_Angeles). No parity with a later publication/version established.
[PDF](../inputs/listing_switch_3985691/source.pdf) · [complete text](../inputs/listing_switch_3985691/source.txt) ·
[source receipt](../inputs/listing_switch_3985691/access.json) · [eligibility sheet](../evidence/listing_switch_3985691.md).

Scope: full extracted text including references/tables/appendix; Figure 2 and Tables 3–6 visually inspected.
Original TAQ/CRSP/switch-event data and regressions were not independently reproduced.
[Arithmetic/identity script](../../../analysis/codex_two_uploads_2849388_3985691_audit.py) ·
[executed audit](../../../analysis/outputs/codex_two_uploads_2849388_3985691/source_audit.json).

## Five questions

1. **What is it about?** How a US company's transfer between NYSE and Nasdaq affects execution costs, dark/lit venue
   choice and information-related spreads. The 2009–17 sample has **110 transfers to Nasdaq and 72 to NYSE**, excluding
   ETFs/ETNs. Data include exchange-supplied transfer dates, TAQ, CRSP and accounting/ownership/analyst databases.
2. **What does it find?** Authors report wider quoted spreads after moving to Nasdaq, more dark trading, improved lit
   price discovery and weaker lit liquidity. The quoted-spread DiD interaction is **+0.136 percentage points** under
   Table 3's units, not a demonstrated 13% relative increase. Table 4's pooled dark-volume change is about **113,324
   shares/day**. The announcement event study is not significant. Their broad dark/liquidity narrative is not consistently
   supported by the effective-spread tables, as checked below. These are source claims/estimates, not our replication.
3. **Why does it make money, if it does?** No executable investor profit is shown. Preferencing/dealer arrangements may
   weaken price competition; cost-sensitive traders may seek cheaper but less certain execution elsewhere. A dealer's
   spread revenue must pay adverse selection, inventory, fees and missed-fill risks. This does not give us a trade direction
   or access to dealer rents. Greater price discovery is not equivalent to higher trading profits.
4. **Can we build on it?** Yes for execution diagnostics: separate quoted/effective/realized spread, signed future impact,
   latency, urgency and fill probability. Original replication would require dated stock transfers, matched controls and
   correctly synchronized native trade/NBBO/venue records. Owned NQ OHLCV/order-flow aggregates do not supply them.
   No new futures hypothesis, data acquisition priority or deeper alpha investigation is justified here.
5. **Can a strategy code be made?** **A research/execution-analysis tool: yes; a paper-derived directional strategy: no.**
   Given real fills, side, trade-time midpoint, later midpoint, fees and quote clocks, code can measure execution quality.
   An actual order-routing policy additionally needs venue eligibility, queue/fill models and an urgency objective; this
   paper specifies no profitable routing algorithm or CME strategy. Our audit demonstrates the accounting identity with
   two invented observations only. It is not a market-making or trading backtest.

## Checked coefficients and interpretation

| Printed result | What can actually be concluded |
|---|---|
| Table 3 quoted-spread interaction +0.136, all dependent variables in percent | **+0.136 percentage points = 13.6 basis points** under the caption. It is not +13% relative growth without an appropriate baseline. Appendix A3 prints fraction-scale rounded coefficients; establish scaling before a raw-data replication. |
| Table 4 large-firm dark-volume interaction +418.316 thousand shares/day | This is the **increment versus small firms**. Its large-firm total post-change point estimate adds −83.663, giving **334.653 thousand**, not 418.316 thousand. Similarly, dark-share total change is −0.002 + 0.021 = **0.019**, or **1.9 percentage points**. No significance of coefficient sums inferred without covariance. |
| Table 5 “liquidity increases for large firms” | Effective-spread change = **+0.068 − 0.037 = +0.031 percentage points**. It stays positive: a smaller increase than for small firms, not a decline/improvement under their spread metric. The pooled change is +0.048. |
| Table 6 lit liquidity deterioration | Its pooled effective-spread change is **−0.019 percentage points**, while the size model has +0.018 − 0.072 = **−0.054** for large firms. These do not support a blanket effective-spread deterioration; quoted and effective spreads are distinct measures. Joint-sum significance is unknown. |
| Lower lit realized spread | Table 6 prints a pooled −0.085 percentage-point change. Lower liquidity-provider realized revenue is compatible with more adverse selection; it does not, alone, measure causal information efficiency or a profitable price forecast. Effective-spread changes must be reconciled too. |
| Matching/endogeneity | Only **42/110** transfers to Nasdaq and **52/72** to NYSE receive matched controls. Matching on observables does not by itself resolve endogenous switching, guarantee parallel trends or identify unobserved trader information. Dark-market regressions are not all the same matched DiD design. |
| Event study | Text describes roughly 180 estimation days at (−210,−30); Figure 2 says 100 days with a 50-day gap. Its chart labels **51 nonmissing-return events**, not all 110 transfers to Nasdaq. The post-event confidence bands include zero; it supplies no verified announcement-trading edge. |

The draft's causal story says uninformed flow departs lit trading, but participant information/urgency is inferred rather
than observed directly. A switch to Nasdaq listing is not necessarily Nasdaq-100 index inclusion, nor a mandate for NQ
futures buying. Off-exchange reporting must also be distinguished from specifically identified ATS/dark-pool activity;
the upload does not supply a reproducible record-level venue-classification procedure.

## Retained execution identity and its clock

The paper uses trade-price denominator `P` and aggressor side `D` (+1 buy, −1 sell):

```text
full effective spread = 2*D*(P - M0)/P
full realized spread  = 2*D*(P - M5)/P
signed price impact   = 2*D*(M5 - M0)/P
effective = realized + impact
```

These are **full** relative spreads; the one-way midpoint distance is half the corresponding full-spread measure.
`M5` is a posttrade outcome, unavailable at entry. Negative realized spread is not a negative bid–ask quote; it can
indicate adverse selection for the liquidity supplier. Aggressor sign differs from a passive parent's order side.
Quote age, order receipt, exchange event time, classification, contemporaneous prices and missing future midpoints
must be explicit. Commissions and inventory/hedging costs are separate: realized spread is not net dealer P&L.

The invented buy/sell examples in the audit verify this algebra only. They establish no execution saving or market alpha.
Merge the lesson into [E56 / execution references](../EXECUTION_REFERENCES.md) and existing quote/clock prerequisites.

## Eligibility and next action

Checked exact ID/title against TIER_LIST, WATCHLIST, TODO, results/evidence/scout records and Claude's tier/watch/queue
files; no previous full review found. The older [dealer-concentration review](nasdaq_dealer_486642_review.md), E01/E10/E56
and related execution records already cover much of the supporting measurement family. This source is not a new trial.

Bounded owned-file/header inspection found no certified original TAQ/NBBO/switch panel. No strategy is being parked
merely for missing data: neither the paper's statistically insignificant announcement response nor its spread regressions
establish a specific prospective opportunity. No acquisition chase, TODO strategy entry or new data-register request.

**DON'T TEST as standalone alpha.** No direction/entry/stop/exit/size invented; no return preregistration, reservation,
gross/design/historical-validation/placebo or BASE/ADD/REPLACE/EMPTY account stage. New economic definitions: **zero**.
Strategy Sharpe, PF, payouts and portfolio improvement are **not tested**, not zero. Independent empirical verification
remains pending. Existing scout continuation and trial budgets stay intact; no code installation, allocation or live action.
The cover's circulation notice is source content, not an instruction to this assistant; no author contact or external message.

For Claude: `agents/codex/results/listing_switch_3985691_review.md` — execution-reference only; interaction/sign/units
and event-study limitations; zero new economic definitions.
