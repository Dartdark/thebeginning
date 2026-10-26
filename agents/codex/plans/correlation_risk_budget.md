# NQ Correlation Risk Budget: frozen standalone preregistration

Evidence: agents/codex/evidence/correlation_risk_budget.md. Commit BEFORE new returns.
Only 30-minute signals; native one-minute execution. Prior55 evaluations/54unique; five more =>60/59.
New ES–ZN covariance input; a stylized risk-budget model, not observed AUM/orders or an ECB replication.

## Calendar, reference prices and strictly prior covariance

Native CT minute-close labels. Build ES and ZN references from 2017 onward; NQ execution begins2018.
Cash-date sequence includes early closes, so an unavailable previous date is never silently stretched to an
older convenient close. Exact 15:00 closes, finite/positive valid OHLCV, normal cash dates only; skip all July3/
Dec24 and cash_open_repair.roll_guard dates. Also exclude the last12Monday–Friday dates of February/May/
August/November for Treasury-roll risk, based on CME's described typical roll window; this is a conservative
calendar buffer for holidays, not an exact CME trading calendar or verification of our source's contract switch.
ZN's2017source begins in December, not January; count actual warm-up and skip until60admissible observations.
A daily observation needs BOTH its immediately prior cash date
and current date normal/non-roll, exact ES/ZN close keys, simple returns |rES|<=0.05, |rZN|<=0.03.
Conflicting source duplicates block; count exact duplicates. Save daily observation/exclusion audit.

Covariance C is an uncentred daily second moment: initialize from the mean outer product of the first60
admissible joint simple returns, then C_new=0.94*C+0.06*r*r'. Missing/excluded daily returns do not update C.
Keep count and last included observation date. Covariance emitted for date d includes only dates<d, never
today's15:00 close. Calendar gaps are not stretched into multi-day returns. Do not retrospectively erase
otherwise valid decision features if today's later close is absent. No fitted prediction or future completeness.

For any positive-definite C: sigmaE=sqrt(C00),sigmaB=sqrt(C11),wE=sigmaB/(sigmaE+sigmaB),wB=1-wE.
v=sqrt(252*w'Cw), leverage L=min(2,0.08/v), E=L*wE,B=L*wB. Equal risk in a two-asset positive-weight model.
Reject nonfinite/nonpositive variances/determinant rather than clip correlations or repair model outputs.

## Decision, attribution and five configurations

At 14:30 CT require the full 14:01–14:30 native OHLCV window in NQ/ES/ZN, exact prior cash-date ES/ZN15:00
closes, all positive/valid OHLC and nonnegative volume, normal/non-roll current+prior dates, and >=60 prior
joint observations. Today's partial simple returns from those exact prior closes must meet the same fixed
5%ES/3%ZN input-jump limits. Prior covariance is C0; C1=.94*C0+.06*r*r'.

Let rho0=C0[0,1]/sqrt(C0[0,0]*C0[1,1]); counterfactual CF has C1's diagonal but off-diagonal
rho0*sqrt(C1[0,0]*C1[1,1]). Compute old targets E0,B0 from C0, new E1 from C1 and EV from CF.
Model NAV after the partial return =1+E0*rES+B0*rZN; require positive finite NAV.
Drifted equity Ed=E0*(1+rES)/NAV. Full rebalance F=E1-Ed; frozen-correlation rebalance V=EV-Ed;
covariance contribution K=F-V=E1-EV. No model portfolio P&L becomes a strategy return.

Shared base eligibility: abs(F)>=0.01 NAV, V!=0, finite values, prior NQ15weekdayATR>0. Direction sign(F).
Candidate additionally sign(K)==sign(F), abs(K)>=0.5*abs(F), abs(K)>=threshold:
1. CRB005: threshold0.005, PRIMARY.
2. CRB0025: threshold0.0025.
3. CRB010: threshold0.01.
4. RP30: unrestricted full-rebalance base, omits all K gates, otherwise same event/side/exits/costs.
5. VOL30: unselectable counterfactual, same eligible base dates, side sign(V); V==0 fails shared eligibility.
Controls unselectable. Candidate order is CRB005,CRB0025,CRB010, never max return.

Entry at native open14:32 (j=872, one extra whole minute beyond14:30 decision). Missing scheduled open=>skip,
no hunting later fill. OneNQ/date, stop0.10prior15weekdayATR,target0.20,ceilto0.25,entry-bar active; flat15:00CT.
No reentry/BE/trail/overnight/position scaling. Shared grid._walk via F.replay; target1point through,
worse-open stop gaps. NQ$7.25RT+1tick($5)/market-stop fill. NativeMNQ$1.24RT+$0.50/fill independently;
fixed4tickfill stress nonselectable. Retain missing-held-minute tickets; no ex-post deletion.

## Frozen cheap design gate and controls

2018–22 only first. All five ledgers, both sides and every year; shared standard metrics incl cost/gross,
daily cash zeros, initial-zeroDD, trade t, NW5/NW20, native micro and stress. Preserve hashes, exact features,
calendar/prior/decision clocks, valid-return counts, all exclusions, missing fills and held paths.

Candidate basic gate: >=100tickets,net>0,t_trade>=2,NW5>=1.5,PF>=1.20,>=4positiveyears,MNQnet>0,
four-tickstressnet>0. Actual candidate ledgers must be exact RP30 subsets on entry/side/exit/brackets/net.
Filter gate: removedmean<0,kepttotal>=basetotal,p(randomnet>=kept)<=.10 and jointprofit/DD beating>=90%
of1,000uniform matched-size subsets. Save totals/DD arrays and seed, reconcile shared helper summaries.

Also1,000matched subsets preserving keptcount in each(year,sign(rES),abs(rES)/sqrt(C0[0,0])bin,
sign(V))cell; equity magnitude bins[0,1),[1,2),[2,infinity). Include zero-sign as its own cell; no cell repair.
Require same pnet<=.10 and joint>=.90 gates. This controls some own-equity/marginal-volatility dependence,
not all possible confounding. Save all arrays/cellcounts. Compare actual candidate total against VOL30 tickets
on identical candidate dates (same contract count, bracket distances, time-exit limit and cost MODEL, different
side allowed; actual stop/target exit times and fill costs may differ); require candidate>=matched
counterfactual total. Label a side-changing comparison as a whole-rule control, not removed-trade accounting.

Select first passing ALL gates. Commit selection and design evidence BEFORE testing only selected+RP30 on
2023--2026-10-09 once; call previously seen historical validation, never fresh holdout. VOL30's2023returns
remain closed because only the selected rule and matched base may advance. No pass=>no2023/accounts;
continue DISTINCT research. No inverted side/control nomination or failed-family tuning.

## Conditional completion and notifications

After pass only: random-side/time matched exits5,000 (times13:30--14:45, same30min window semantics and
entrydelay, flat15:00),5,000day-block bootstrap/permutations,10,000tradeMC,5,000one-year dailyMC at1MNQ;
dependence/selection/DSR at>=253 lower-bound trials (193older+60program), including unknown larger searches.
Fresh independent raw-spec checker before promotion, then current whole-contract personal19A-D/FULL
1MNQ BASE/ADD/replaceLDF/EMPTY with valid joint mark-to-adverse paths. Missing50K/150K joint data=>LIMITS,
no invented pass/payout improvement. Actual fund clocks, calibrations and contract continuity require review.

Record first full-history t4.5/5 crossings only if BOTH net trade/NW5 reach threshold, design/validation positive,
realistic native costs and no known fatal issue. Lower events are research progress, not t6 or trading approval.
Final t6 also needs dependence/selection/placebo and independent review, then account comparisons and limits.
No failure alert or automation pause. No watcher changes. No PowerLanguage on a failed gate.

Deliver analysis/codex_correlation_risk_budget*.py, analysis/outputs/codex_correlation_risk_budget/,
agents/codex/results/correlation_risk_budget.md, Summary<=5lines; update/push program on codex/work only.
Only allowedresearchpaths; no ranks/sharedplans/rootTODO/live/VPS/broker/API/PR2/purchases/accounts/messages.
