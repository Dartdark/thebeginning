# NQ Implied Variance Budget Breach: TEST

Summary: Test whether unexpectedly rapid realized variance, relative to a prior option-implied forecast,
identifies unfinished directional repricing. This is a new raw-data entry, not a volatility rescaling of old trades.
Independent input: lagged VXN, causally calibrated to cash-session variance and its time-of-day distribution.
No new forward returns inspected; five frozen models will receive a 2018-22 cheap screen first.

Sources inspected: data/VXN_daily.csv (DATE/CLOSE, begins2009-09-14); native NQ day/night minute files;
analysis/implied_vol_test.py; TIER_LIST.md implied-volatility unit and Headline Shock Follow;
WATCHLIST.md #24 RS/VXN sizing. Cboe methodology search result explicitly describes VXN as 30-day
expected volatility; it does not establish this proposed trading rule:
https://cdn.cboe.com/api/global/us_indices/governance/Volatility_Index_Methodology_Selected_Broad_Based_Index_Equity_and_ETF_Volatility_Indices.pdf
Historical methodology corroboration: https://www.sec.gov/rules/sro/cboe/34-48807.pdf
New return trials: zero. Existing program40evaluations/39unique plus much larger unknown earlier search.

## 1. Participant and proposed mechanism

A variance surprise may force risk-budget revisions and continued hedging/inventory transfer while new
information is absorbed. We do not observe mandates, dealer gamma or order quantities. Direction comes
from contemporaneous cash-price displacement, not from assuming that higher variance always means selling.
The hypothesis is continuation specifically when variance has exceeded what the pre-open option forecast,
calibrated only on past sessions, would have anticipated. An effect on volatility alone refutes the direction claim.

## 2. Information and clock

Use the prior US cash-market day's exact VXN closing observation, never today's VXN. At each completed
5/15-minute decision09:00--13:30CT, all native cash minutes through that close determine cumulative squared
one-minute log returns and running HLC3/volume VWAP. Expected variance uses only prior completed sessions.
Decision at j; one full extra minute for receipt/order delay; market at native open j+2. No future full-day
variance, high/low, volume or data-completeness mask may decide whether today's signal exists.

## 3. Transmission

NQ is a direct future on Nasdaq100; VXN reflects options on that benchmark. This is a defensible variance
reference, not evidence of incremental futures demand. Only one NQ/MNQ position is traded; no cross-asset
trade, portfolio sum, old entry list or fitted return predictor.

## 4. Input feasibility and controls

Native CT close-stamped OHLCV is local. Lagged VXN closes are local Cboe history. Point-in-time revision/
receive timestamps are unverified; a prior-day close is assumed available before today's cash open.
No accounts/keys/paid data needed. Conflicting duplicate price or VXN dates block intake. Missing exact
expected VXN prior date blocks new signals; no nearest-date substitution. Complete current prefix required.
Past full-session data enter calibration only after their dates, and missing past sessions keep their places
in the exact20/60-normal-date windows. Same history/quote mask applies to price-only controls.

## 5. Costs and overlap

NQ$7.25RT plus1tick($5) each market/stop fill; target needs1point through. Native MNQ$1.24RT plus$0.50/fill
modeled independently. Fixed4tickfill stress. Proposed stop0.15priorATR,target0.45,flat14:55,one/day.
Exposure can overlap cash-momentum RS/Twin/VB/HSF. No occupancy gap or hedge benefit is established.
Orders consume liquidity; stress-event spreads/gaps may exceed the models. Do not select events on book flatness.

## 6. Power before returns

There are approximately1,250design cash sessions before normal-calendar exclusions and60-session warm-up.
At300--600qualifying days and assumed SD$800/NQ, t2 requires net$65--92/trade; t6 requires$196--277.
These are feasibility assumptions, not measured opportunity counts or forecasts. Count actual signals without
relaxing after returns; daily clustering and all prior search further reduce apparent statistical evidence.

## 7. Prior work and falsifiers

Prior VXN exit/sizing studies were changes to existing entries and mostly failed account utility. HSF used
an isolated5-minute jump relative to historical bar sizes; this study uses a cumulative, time-adjusted variance
budget anchored in prior option prices. Neither old entry can trigger a trade here. This is not a rescue of
Opening Path Persistence: no path-efficiency condition, first30-minute decision or old trade ledger is used.
Falsify if basic design fails, if the shock gate only removes profitable price-control trades, or if conditional
matched random timing is just as good. A rejected candidate does not authorize threshold/direction/exit retuning.

## 8. Failure and diversification

Unobserved informed order flow may already be exhausted; variance may predict only future variance. Intraday
volatility seasonality, futures/spot basis and changing implied-variance premia may make the budget misleading.
Known-event gaps and whipsaws can cluster with existing NQ trend losses. No before-breach offset is established.
Keep one position/trade per day, active entry-minute stop and fixed time exit. Missing current prefix/quote/
calibration blocks entries; missing held minutes remain reported and are never dropped to improve metrics.
Only after valid evidence: whole-contract BASE/ADD/replacement/EMPTY account tests and joint chronology.

TEST the committed small screen. A failure ends this hypothesis's validation only; continue the t6 program.
