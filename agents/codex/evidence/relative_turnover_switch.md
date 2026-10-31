# NQ Relative Turnover Switch: TEST

Summary: A new standalone entry tests whether a sudden shift of futures turnover toward Nasdaq predicts
continued movement in the contemporaneous NQ candle direction. Independent quantity input: NQ/ES notional
turnover relative to their own same-clock history. This is not an NQ-minus-ES price residual or old signal filter.
Prior own-volume studies failed, so own-volume/time-matched controls must falsify a misleading quantity story.

Sources inspected: native data/NQ_1min_*.csv and data/ES_1min_*.csv; Grid24 CT stamp documentation;
analysis/abnormal_volume_test.py; TIER_LIST.md abnormal-volume, cross-asset lead/lag and RS rows;
analysis/codex_cash_open_repair.py calendar roll guard and native cost helpers. No new returns inspected.
Prior program45counted evaluations/44unique rules; much larger unknown earlier repository/author search.

## 1. Participant and mechanism

Nasdaq-focused execution, hedging and inventory transfer can concentrate activity in NQ without an equivalent
broad-index turnover increase. If demand is worked over several bars, the price direction during that shift
might persist. Actual participant identity, directional order imbalance and any compulsory mandate are not
observed. Every trade has a buyer and seller; volume is NOT net buying. This is an explicitly uncertain hypothesis.

## 2. Information before entry

At a completed5/15-minute close09:00--14:00CT, compare current and previous-bar NQ/ES notional turnover ratios
with each bar's prior20normal-session same-clock median. Require the previous normalized ratio<=1 and current
>=1.5or2, plus a directional strong-close NQ candle. NQ own relative volume>=1 and ES>=0.5 prevent a pure
low-ES-volume artifact. All constituent minutes/quantities are known at signal close; market entry waits one
whole additional minute. No current-day final volume or future completeness mask is used.

## 3. Transmission

Only NQ is traded. ES volume is a contemporaneous reference, not a hedge leg, portfolio component or price lead.
No old RS/Twin/VB/HSF/OPP entry or ticket can trigger a trade. Gross notional uses the repo contract multipliers
NQ$20/point and ES$50/point; it is a turnover proxy, not a measured dollar allocation or directional flow.

## 4. Input feasibility

Local native CT close-stamped NQ and ES OHLCV2018-2026. Align exact calendar dates and5/15-minute closes;
require every minute in current/previous bars valid and both aggregated volumes/prices positive. No forwardfill.
Conflicting duplicates block intake. Same-clock medians use exact prior20normal research dates,min15valid,
excluding today. Standard calendar roll-window dates are skipped and remain NaN places in history, because
front-contract volume shifts can mimic a participation change. Actual source contract-switch timing is unverified.
No paid data, account, API key, revised OF profile or new external source is required.

## 5. Costs and overlap

NQ$7.25RT plus1tick($5) each market/stop fill; target1point through. MNQ$1.24RT plus$0.50/fill independently.
Fixed4tickfill stress. Stop0.10priorATR,target0.20,45-minute limit,flat14:55,max4/day,one position. Current cash
momentum exposures RS/Twin/VB/HSF may share losses. No empty slot or hedge benefit established.

## 6. Power before returns

Approximately1,250design cash sessions before exclusions/warm-up. At0.5--1.5executed events/day there could
be600--1,800tickets. Assuming SD$500/NQ, netmean for t2 is$24--41/trade and for t6$71--122. Add fees/slippage
for the gross hurdle. These are feasibility assumptions; no observed count/profit is claimed. Count actual events
without relaxing after returns; overlapping opportunities and clustered days reduce effective information.

## 7. Prior work and falsifiers

Own abnormal-volume continuation failed; broad price lead/lag and decoupling failed; RS used a beta-adjusted
price residual. NQ Flow Absorption/Participation Resumption/Implied Variance Breach also failed and are not being
retuned. Here the trigger is a cross-market quantity-share switch; current bar direction only assigns the side.
Reject if basic net design fails, if removed signals are profitable, if it loses to matched random drops, or if
within-clock-hour/own-volume-stratum random drops perform as well. Do not flip direction or nominate controls.

## 8. Failure and diversification

Hedging/making turnover may indicate exhaustion, not persistent demand. Relative volume can reflect futures roll
migration, export conventions, an ES feed issue or different volatility rather than a new NQ allocation. Trends
can reverse and losses can cluster with other NQ momentum trades. Our market/stop orders consume liquidity;
no queue advantage is claimed. Missing inputs block entries, missing held minutes remain reported, never removed.
One active position/max4daily entries, entry-bar bracket and fixed time exit; worse gaps can exceed nominal stop.
No before-account-breach offset exists until valid joint chronology demonstrates it. Whole-contract account
addition/replacement/empty-slot work is conditional on a valid candidate, never inferred from point correlations.

TEST a frozen five-model2018-22 screen. A failure ends this mechanism only; later iterations continue distinctly.
