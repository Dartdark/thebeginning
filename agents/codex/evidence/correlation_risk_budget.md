# NQ Correlation Risk Budget: TEST

Summary: Test whether a covariance-driven change in a stylized stock–bond risk budget predicts late NQ adjustment.
ES–ZN correlation is the new input; hold individual volatilities fixed in a counterfactual to isolate it.
Published research supports the portfolio mechanics, not our US execution clock or a proven futures edge.
Commit five configurations, test 2018–22 first, and reject this family if its cost/filter gates fail.

Sources: [ECB, May 2020](https://www.ecb.europa.eu/press/financial-stability-publications/fsr/focus/2020/html/ecb.fsrbox202005_02~f6616db9be.en.html);
[MSCI, March 2019](https://www.msci.com/research-and-insights/blog-post/the-risk-in-risk-parity-strategies);
local ES/ZN/NQ minute files, analysis/cta_volcontrol_test.py, agents/codex/research/t6_program.md at 21f9ed8.
Return trials for this family: zero. Prior program: 55 counted evaluations / 54 unique rules; many older trials.

## 1. Participant and cause

Risk-targeted multi-asset managers adjust exposures when portfolio risk changes. ECB describes a daily
risk-parity model with an 8% volatility target; MSCI shows correlation's independent effect on portfolio risk.
Neither source identifies current aggregate positions, a mandatory 14:30 CT deadline or actual NQ orders.
The prediction here is that diversification changes can cause further broad-equity adjustment near the close.
This is a modelled-flow hypothesis. A US two-asset futures proxy is not a replication of the ECB's four-asset
European ETF model. Equal-risk mathematical mechanics remain meaningful, while current AUM/calibration
and the persistence of any exploitable execution delay are unverified.

## 2. Direction, scale and clock known before entry

At the completed 30-minute close 14:30 CT, update a frozen ES–ZN covariance model with returns since the
immediately preceding normal cash close. Compute equity exposure under updated correlation and under
unchanged prior correlation with the SAME updated marginal volatilities. Their difference isolates covariance.
Trade in the total modelled equity adjustment's direction only when covariance agrees and supplies at least
half its magnitude. Three fixed covariance magnitude hurdles: 0.005 primary, 0.0025 and 0.01 NAV.
This is not an observed order imbalance. A hypothetical $100bn pool makes 0.005 NAV $500m, roughly 1,250
NQ contracts at an assumed index of 20,000; neither pool size nor index value is a measured event flow.
No actual flow/contract-volume ratio is established. These numbers explain scale only, not expected impact.
Decision close -> wait one full additional native minute -> entry at close-labelled 14:32 open -> flat 15:00 CT.

## 3. Transmission

ES measures broad equity exposure; ZN supplies the bond covariance input. Broad equity allocation may reach
NQ through shared constituents and index arbitrage. NQ-specific transmission and unabsorbed demand are
predictions, not source facts. Only one NQ/MNQ is traded. No ES/ZN portfolio returns, existing trade ledgers,
strategy combinations, fitted return weights or return rescaling enter the tradable result.

## 4. Input feasibility and new information

| Input | Source and fields | Coverage/warm-up | Timing and limits | Cost |
|---|---|---|---|---|
| ES, ZN | Native OHLCV minute CSVs | 2017 reference year; 2018–22 design | Exact 15:00 prior closes and 14:01–14:30 decision window; no forward fill | Already local |
| NQ | Native OHLCV minute CSVs | 2018 onward | 30-minute signal window; one-minute execution; prior ATR | Already local |
| Calendar/roll guard | codex_s03_calendar and cash_open_repair.roll_guard | Historical cash dates | Skip early closes, July3/Dec24, predeclared quarterly roll windows and return endpoints | Local |

Use covariance and modelled exposure, not another price-follow trigger. Reject conflicting duplicates; preserve
exact duplicate counts, every eligibility exclusion and raw hashes. Continuous files are unadjusted. Calendar
roll guards reduce risk but do not establish actual contract switch dates; flag endpoint jumps above fixed
5% ES / 3% ZN as unavailable input, without repairing or selecting them from forward strategy P&L.
Historical receive timestamps and original-contract parity are absent. A one-minute buffer is an assumption.
The Treasury guard additionally excludes the last12Monday–Friday dates in February/May/August/November,
buffering holidays around the typically described ten-business-day roll. ZN2017 data starts in December;
it is not a full warm-up year. The actual 60-observation gate controls initial2018availability.
[CME's roll guide](https://www.cmegroup.com/trading/paceoftheroll/user-guide.html) describes typical Treasury
roll concentration in those weeks, while explicitly giving no universal exact roll date. The guard is conservative,
not proof that every vendor contract discontinuity is removed.

## 5. Costs, gaps and liquidity role

NQ $7.25 RT plus one tick ($5) per market/stop fill; MNQ independently $1.24 RT plus $0.50 per such fill.
Target needs one NQ point through, active entry-bar stops, worse-open gaps, fixed four-tick stress.
With two market fills, NQ cost is $17.25. At an assumed net SD $250 and n=250, t2 requires about $32 net,
or $49 gross. These are feasibility assumptions, not a measured edge. Late-day orders consume liquidity and
can coincide with existing Late-Day Flow, ES MOC Follow and Relative Strength. No empty slot is established;
do not select dates by plan occupancy. Exact joint account comparisons are conditional on a design pass.

## 6. Power before returns

About 1,250 cash dates exist in 2018–22 before calendar/data filters; 2017 prices provide model warm-up.
The retained fraction is unknown. At assumed n=250–600 and SD $250/NQ, t2 needs $20–32 net/trade; t6 needs
$61–95. Daily dependence, selection and tail concentration can raise these hurdles. Require >=100 executed
trades and at least four positive design years. A rare/weak result does not authorize threshold relaxation.

## 7. Prior work and falsifiers

cta_volcontrol_test.py already tests ES marginal-volatility exposure and drift, plus CTA triggers. Its controls
and failed variants remain relevant. It does not model stock–bond covariance. The failed implied-variance
breach family uses NQ realized variation against prior VXN; it has no bond input or portfolio-risk attribution.
Cross-asset lead/lag and price-pair tests are also prior trials, not erased by this plan.

New falsifiers: same-marginal-volatility frozen-correlation counterfactual; unrestricted two-asset rebalance base;
total kept/base/removed profits; 1,000 uniform and 1,000 year/equity-return/marginal-flow matched subsets.
Require positive net at native costs and stress; covariance must improve total profit rather than simply average
profit. If no candidate passes, no 2023+ test, direction flip, changed clock, new threshold or side nomination.

## 8. Failure and diversification

| Question | Prediction/limit before returns | Evidence needed |
|---|---|---|
| Why could it stop working? | Slow model is unrelated to actual allocations; managers smooth/hedge earlier; crowding or market absorption | Failed controls, weak replication or measured flow mismatch |
| Liquidity role | Market entry/stop consumes liquidity; target is a resting-limit approximation | Native fills and quote evidence before trading |
| Common losses | Inflation shocks, correlated sell-offs, late reversals and execution gaps | Both sides/year, dependence checks, chronological stress |
| Shared plan exposure | LDF/MOC/RS late equity exposure, currently unmeasured | BASE/ADD/replacement/EMPTY joint paths after pass |
| Offset before breach? | No guaranteed offset or tail hedge; stops can gap | Actual mark-to-adverse-minute account paths |

One contract, stop 0.10 prior 15-weekday ATR, target 0.20, exit 15:00, at most one ticket/date. Missing inputs
block entries; held gaps are retained and disclosed. TEST means eligible for the frozen cheap design study,
not independent approval, t6 qualification, account adoption or live trading.
