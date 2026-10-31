# Turn-of-the-month equity returns: WATCH as historical evidence; already tested locally
Summary: This upload combines a Q Group proposal with a completed historical turn-of-the-month return study.
For 1987–2005, value-weighted daily returns average 0.15% during the four-day window, near zero on other comparison days.
The attached study does not establish that payday cash flows cause the pattern; after-cost implementation is proposed.
Related local futures tests already exist and do not justify funded placement; no new return trial or duplicate queue entry.

Source: John J. McConnell and Wei Xu, *Equity Returns at the Turn of the Month: Trading Strategies and
Implications for Investors and Managers*, Q Group proposal plus attached *Equity Returns at the Turn-of-the-Month*,
[SSRN 925589](https://ssrn.com/abstract=925589), uploaded version.
SHA256: `83174e7606ea36a83fffe9e371a357e4b69feb384c31f286f2d04a0bd8e5dbb4`.
Review: 2026-10-29. New return trials: **0**. Source results not independently reproduced.
Repo context: codex/work `833f47ff11a4741845660c901651be0672b56c24`.

## 1. What is it about?

A calendar pattern: stocks earn unusually high returns on the last trading day of a month and first three
trading days of the next month. The attached completed study uses CRSP value/equal-weighted market returns
for 1926–2005, checks the post-earlier-study period 1987–2005, and examines characteristics and international markets.
The front proposal asks whether industry/sentiment splits and mutual-fund, ETF or index-futures implementations
can profit after costs. A proposal to investigate a strategy is not a completed net-profit result.

## 2. What does it find?

| Attached study result | Qualification |
|---|---|
| Table 1 Panel B: 1987–2005 value-weighted daily return 0.15% in the four-day window versus approximately −0.001% on other comparison days; difference t=3.78. | Historical gross stock-index return difference, not a net futures trade return. |
| Table 1 Panel C: 1926–2005 value-weighted daily return 0.16% in the window versus 0.01% otherwise; difference t=8.06. | A long historical sample; not proof that the effect persists today. |
| Effect reported in 30 of 34 international markets; not confined to small/low-price stocks, year ends or quarter ends. | Cross-market corroboration, not 34 fully independent modern strategy tests. |
| NYSE standardized daily volume is 0.98 in the turn window versus 1.02 otherwise; measured mutual-fund flows lack a sustained positive cluster. | Tests do not support the simple payday explanation, but cannot rule out every cash-flow or liquidity mechanism. |

Attached Table 1 defines day −1 as the last trading day and days +1/+2/+3 as the first three of the next month.
To capture all four daily close-to-close returns, entry is at the preceding trading day's close, not after
the last day has already returned. Its “other days” comparison is day −10 through −2 and +4 through +10.
Do not infer the cumulative four-day compounded return simply by quoting the daily mean as a trade return.

The statement that all positive returns occur around month turns concerns aggregate averages over long periods,
not a guarantee about individual months or lack of profitable days elsewhere.
The “109-year” comparison combines the earlier DJIA study with this CRSP evidence; it is not one uniform
CRSP series spanning 1897–2005. The proposal's abstract mentions 1926–2006, but the attached U.S. tables end in 2005.

## 3. Why does it make money, if it does?

The historical calendar return pattern is demonstrated in the source; its cause remains unresolved.
A popular hypothesis is that wages, dividends and retirement contributions generate scheduled purchases.
The authors explicitly test implications using volume and TrimTabs mutual-fund net flows and find no support.
They also note coverage/reporting limits; failure of these tests is not proof that all institutional flows are absent.

We should not label this a verified forced-flow strategy simply because a month-end story sounds plausible.
Any modern claim about pension rebalancing, index tracking, cash demand or institutional execution must identify
the actual obligation, signal availability and transmission separately. Those flows can even predict opposite directions.

The proposed implementations face spreads, commissions, financing, roll effects, taxes and holding risk.
This file does not establish a completed, implementable net-of-cost futures strategy, modern robustness,
or compatibility with a small trailing-drawdown account.

## 4. Can we build on it?

**It is worth knowing as a calendar benchmark, but it is not new to our research book.**
Existing pinned TIER_LIST findings, quoted as prior repository evidence rather than rerun results:

| Existing research | Recorded finding |
|---|---|
| Turn of the month | +$376 per trade, t=2.0 (t=3.7 with stop); weak 2018–22 and harms funded payouts at tested sizes. The short row does not specify every protocol/unit detail; consult its underlying source before using the dollar figure for sizing. |
| Personal overnight round, `analysis/overnight_round.py` | Day −2 close to +3 close: ES $426 per full contract, t=1.0; NQ $1,063, t=1.4; a 1-ATR stop worsens both. |
| Month-end close follow and rebalancing fades | Separate intraday hypotheses already examined; no basis here to reopen their parameter searches. |

The local overnight script explicitly buys the second-to-last trading day's 15:00 close and sells the third
trading day's 15:00 close. It is related to the paper's four-day daily-return window, but differences in cash versus
futures prices, session clock, dividends/carry and costs mean it is not an exact stock-index replication.

Apex cannot hold that ordinary multi-day position under our intraday rules. A personal account can, but the
available local evidence is weak and has not established portfolio benefit from a new allocation.
A future reopening needs materially new evidence: a clearly different observable mechanism, or sufficiently
new frozen forward results. Another lookback, stop or calendar sub-cut on already-seen data is not fresh confirmation.

Replication requires an exact exchange calendar, pre-close decision/fill clock, cash-versus-overnight decomposition,
costs and roll/carry treatment. Existing futures data can support a related test, but cannot reproduce CRSP
total returns or the original international/flow panels without their inputs. No new data availability audit was run.
No account occupancy, joint-loss timing or new payout comparison is inferred from this review.

## Decision

Retain as historical calendar evidence with an unresolved mechanism. **No new backtest now**: consult existing
tests before considering new trials. No duplicate promising-strategy queue entry for a previously tested family.
This paper is more relevant than a trader-preference survey, but the prior negative/weak local results still matter.
No code, plan allocation or live/VPS modifications; no newly calculated strategy performance.

For Claude: `agents/codex/results/turn_of_month_paper_review_20261029.md`.
