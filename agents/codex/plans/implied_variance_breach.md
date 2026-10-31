# NQ Implied Variance Budget Breach: frozen standalone preregistration

Evidence: agents/codex/evidence/implied_variance_breach.md. Commit before any new returns. No old trade inputs.
Only5/15-minute decisions with one-minute inputs/execution. Prior40evaluations/39unique; this adds5=>45/44.
Unknown older searches remain relevant. Raw grids start2018; no2017warm-up. Design2018-22 before2023+.

## Causal variance forecast

Normal US cash dates via shared calendar, conservatively skipJuly3/December24 as signal/calibration dates.
For each date d, identify its immediately preceding cash-market date (normal OR early-close calendar status,
excluding weekends/holidays); require its EXACT VXN DATE/CLOSE. No backfill, no today's VXN. VXN>0 finite.
At native close j, cumulative RV is sum squared log increments of [O08:31,C08:31,...,Cj]. All native OHLCV
minutes08:31..j must be valid/finite, nonnegative volume, prices>0. No future completeness test on today's signals.
Cash full-session RV ends15:00. Each completed past normal date records its full RV, cumulative/full share curve
and RV divided by that date's lagged-implied daily variance I=(VXNprior/100)^2/252. Missing complete past
session or prior VXN leaves a NaN record in its chronological place; do not stretch a window for good data.

Before date d:
- Require at least60 preceding normal dates in history, with>=45valid ratios among exact last60.
- Scale=median(last60 fullRV/I). Each fullRV belongs to a completed past date, never d.
- Shape(j)=median(cumulativeRV(j)/fullRV among exact last20 normal dates), >=15valid curves.
- ExpectedRV(j)=today's lagged I * Scale * Shape(j). Forecast must be positive finite.
BudgetRatio(j)=today cumulativeRV(j)/ExpectedRV(j). This is a variance ratio, not volatility ratio.
The252-day conversion and spot/futures/cash calibration are explicit modeling conventions, not a Cboe daily forecast.
Append today's calibration record only AFTER all today's signals have been generated.

## Entry, controls and exits

At completed5/15-minute closes09:00--13:30CT, let net=Cj-O08:31 and vwap=running nativeHLC3*volume/sumvolume.
Potential long if net>=0.20prior15-weekday calendar ATR AND Cj>vwap; potential short if net<=-0.20ATR AND Cj<vwap.
Same positive volume/valid forecast/history/ATR eligibility for ALL models. Candidate also needs BudgetRatio>=k.
Exactly five models in fixed candidate order:
1. IVB5_2:5-minute,k2,primary.
2. IVB5_3:5-minute,k3.
3. IVB15_2:15-minute,k2.
4. BASE5:5-minute potential price signals, no BudgetRatio threshold.
5. BASE15:corresponding15-minute price control. Controls unselectable; no post-result nomination or side fitting.

Take the first eligible signal each date only. Spend the day's opportunity even if its scheduled open is missing;
no later retry. Entry at native open j+2, one additional whole minute delay after decisionclose. Stop0.15priorATR,
target0.45priorATR, ceil to0.25point, active entryminute, time exit14:55CT. One position/trade/day, noBE/trail/
overnight/risk rescaling. Shared grid._walk via codex_flow_absorption replay adapter; first-signal selection
is an explicit one-trade adapter, not shared engine mutation. Target1point through; stop gaps worse nativeopen.
NQ$7.25RT plus1tick($5) permarket/stopfill. NativeMNQ$1.24RT plus$0.50/fill separately. Fixed4tickfill stress.

## Intake, diagnostics and staged decision

Audit raw NQ keys/OHLCV and VXN DATE/CLOSE before execution; conflicting duplicate keys=>NEEDS DATA.
Preserve hashes and prior-date/calibration-count features. Synthetic tests: shifted quote, missing exact prior
quote, future mutation cannot alter earlier forecasts, time-shape seasonality, variance vs sigma units,
protected entrybar/gaps/through, extra-minute delay and one/day. No actual returns before prereg commit.

Design cheap gate for each candidate:>=100executed tickets, net>0, trade t>=2,dailyNW5>=1.5,PF>=1.20,
>=4positive years, nativeMNQ net>0,4tickstressnet>0. Report missing held minutes; any fatal data issue blocks
qualification, never improve results by deleting incomplete trades.

Actual one/day candidate and BASE ledgers have DIFFERENT first-signal times; do NOT label them nested.
Report actual total net/DD difference and require candidate actual net>=base actual net before advancing.
Separate independent-per-window diagnostic: all eligible potential and budget-gated windows, with original
brackets/timeexit. These overlap and are NOT executable portfolios. Show kept/base/removed totalnet,
removedmean/t and1000matched-size random subsets. Require removedmean<0, kepttotal>=basetotal,
p(randomnet>=kept)<=.10 and jointlybetterprofit/DD than>=90%random subsets. This supports signal information
only, not a causal capped-account filter improvement.
Also1000conditional random-time paths: on the candidate's actual event dates select one independent price-only
eligible control window per date, retaining its stop/target/14:55exit and costs. Exactly one/day is executable
on those ex-post-conditioned dates; they are placebos, not deployable alternatives. Require randomnet p<=.10
and candidate jointlybetterprofit/DD in>=90%. Save all diagnostics/counts as additional return paths, no selections.

Choose first candidate passing ALL basic and diagnostic gates, not maximum return. Commit design before
chosen+its matching BASE historical2023--2026-10-09 run once. No pass=>reject this hypothesis only;
continue a distinctly preregistered mechanism, not 2023+ retuning. Previously seen2023+ is historical validation.
Full-history t4.5/t5 milestones require BOTH nettrade t and dailyNW5>=threshold, positive design/validation,
realistic native costs and no fatal issue; preserve milestone history and remaining checks. Goal remains>=6both.

All/long/short/year metrics fromshared tools, initialzeroDD,cashdayzeros,NW5/NW20,costs,nativefee/stress,
signals/rawwindows/first-selection/missingentry/missingheld/calibration counts. If it advances, then matched-exit
randomside/time5000,blockbootstrap/permutation5000,tradeMC10000,oneyeardailyMC5000 at1MNQ; DSR at>=238
reported-trial lowerbound, selection limitations and fixed sensitivities. Fresh spec-only checker beforepromotion.
Then personal19A-D/FULL BASE/ADD/replaceHSF-or-RS/EMPTY at1MNQ wholecontracts; valid50K/150Kjoint account
paths required for precise improvements, else LIMITS. Frozenforward evidence needed before tradingdecision.

Deliver analysis/codex_implied_variance_breach.py,analysis/outputs/codex_implied_variance_breach/,
agents/codex/results/implied_variance_breach.md Summary<=5lines. Onlycodex/work and allowedresearchpaths;
no watcher changes, sharedrank/plan/live/VPS/broker/API/purchases/accounts/messages or PLonfailedgate.
