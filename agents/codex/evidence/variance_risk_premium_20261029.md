# Monthly equity VRP allocation: NEEDS DATA
Summary: Strong published monthly equity forecasting evidence merits source-parity checks.
The source supplies no frozen net allocation strategy, forced flow or intraday execution gap.
Verify monthly IV/RV construction and availability before preregistration; no return trial now.

Sources: [paper review](../results/variance_risk_premium_review_20261029.md), Zhou (2018), SSRN 1783624,
pp.4–6, Table 1 p.23, Figure 1 p.27. Repository snapshot `fd8a54f386752423aba0dfdb19ad2d4a4659b694`.
New return trials: 0. Source claims are not independently reproduced.

## 1. Who trades, and what causes the trade?
Insurance buyers and risk-bearing investors price variance/tail uncertainty. This is a conditional risk-premium
mechanism, not an identified mandatory trade. Participants, dollar demand and a scheduled futures imbalance are unmeasured.

## 2. Direction, size and timing before entry
Paper hypothesis: higher end-of-month equity IV minus trailing RV predicts higher subsequent equity excess return.
No size rule, threshold or executable fill is supplied. VIX/RV at month's end must finish and become available
before any decision/fill. No close-price entry using information first finalized at that close.
No dollar-flow/ES-volume comparison is defensible from this source.

## 3. Transmission to traded market
SPX equity risk connects economically to ES, but this does not identify incremental ES orders.
NQ/VXN and FX VRP would be different inputs/markets. No evidence for concentrating the monthly relation intraday.

## 4. Data and incremental information

| Input | Status / requirement |
|---|---|
| End-of-month VIX implied variance | data/VIX_daily.csv exists; coverage, vintage and availability not audited here. Paper uses VIX²/12 in percentage-squared monthly units. |
| Prior-month SPX five-minute RV including overnight | Exact data/code unverified; resolve sampling/session convention. Daily SPY or futures RV is an adaptation. |
| Author IV/RV/VRP series | Advertised homepage, not fetched; availability, licence, price and revision history unknown. |
| Equity excess returns, P/E and risk-free series | Definitions/scale and as-of valuation inputs need pinning; source S&P/CRSP inputs not verified owned. |
| Executable ETF/MES ledger | Contract/roll, integer quantity, costs, margin and monthly holding protocol not specified. |

Option prices add information beyond past returns. Require VIX-only, RV-only and constant-equity baselines.
Do not count a raw proxy as source parity or select estimator details on return results.

## 5. Costs and plan gaps
No costed rule or plausible net per-trade move is supplied. A monthly personal position spans many existing
equity holdings and cannot be restricted to the intraday occupancy gaps. Apex flat-by-15:59 CT conflicts with
an uninterrupted monthly holding period; a daily-flat version is a separate hypothesis.
Native MES/ETF fees, spread, financing/rolls and margin must be fixed before a later personal comparison.

## 6. Power
2018–22 has at most 60 monthly forecast origins before warm-up; overlapping quarterly outcomes are not 60
independent trades. A conservative nonoverlapping quarterly design offers about 20 observations.
For planning only, t=2 requires mean about 0.447 times per-quarter SD at n=20.
For an assumed 8% quarterly SD, that is about 3.58% net mean per quarter before a multiple-testing adjustment.
These are illustrative assumptions, not measured moments or an allocation hurdle selected on returns.
The original 1990–2016 regression has a much longer sample. A short personal-backtest window cannot be credited
with its statistical power. Dollar SD requires a specified instrument and integer size; neither is frozen yet.

## 7. Already tested and falsifiers
Prior VIX regime tilts, implied-volatility exit scaling, contrarian VRP ETF paper and failed intraday implied
variance breach are related but different. See links in the review.
Failure to reproduce the direction/measurement, loss of incremental forecasting versus VIX/RV baselines, or
poor net account contribution would refute the proposed use. No threshold rescue is authorized.

## 8. Failure and diversification

| Question | Prediction / missing evidence |
|---|---|
| Mechanism failure | Proxy may chiefly contain forecast error; relation may decay, depend on crisis observations or fail after publication. |
| Liquidity role | Unknown until instrument/order protocol is fixed; assume no passive improvement. |
| Clustered losses | High VRP may coexist with continuing equity selloffs, gaps and persistent uncertainty. |
| Shared losses | Existing personal equity exposure likely shares downside; joint losses unmeasured. |
| Offset before breach | No offset identified; a later equity premium cannot protect an earlier account breach. |

Stop/time exit, max exposure, missing-data treatment and margin controls are not specified by the source.
They must be frozen in a future plan rather than invented in a return run.

## Decision and next gate
**NEEDS DATA** — obtain and audit exact source-series construction/availability and define the implementable
personal exposure rule before preregistration. No return test, parameter search or account bench now.
A source-only diagnostic does not reset previous trial history or the stopped Hunt programs.
