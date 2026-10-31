# H09 preregistration: one affordable extra MES on the accepted closing-flow leg

Mechanism/source sheet BEFORE new inputs: `research/hunt_v2_mes_moc_affordability_nomination.md`.
Source isd14dc9a153df128aafd3f48d4fea2aa78b88bb28, `funded_strategies/ES_MOC_Follow.txt`,
blob33e4a6a1c57dc0867d6ee9b26c310879ebd08f18. H08 is closed without returns. This is explicitly
the SAME affordability family continued on a different accepted parent, not independent alpha or a
rescue of measured CL losses. The250USD allowance and100parent/50extra minima preceded this nomination.
Commit this plan before inputs; commit reviewed implementation before actual execution.

## Mechanism, selection and five definitions

The accepted ES parent follows a late move into the cash close, attributed to benchmark/index execution
and hedging. It measures price, not actual auction imbalance, participant identity or forced dollar
size. The new question is causal allocation of a second MES using already-known planned dollar stop
risk. A constant contract exposes different dollars across range states. It can fail because calm
past ranges precede jumps, costs consume the ten-minute effect, or its extra equity exposure worsens
joint book losses. No pre-breach hedge, low correlation or beneficial volatility premium is assumed.

LetA be the literal parent's prior15 stored weekday CT-chart-date ATR. Native MES point value5USD,
tick.25=1.25USD. D=ceil((.25*A)/.25)*.25. R1=D*5+3.74, where3.74=1.24RTcommission+1.25per market/stop fill.
**EXTRA=1 iff2*R1<=250, otherwise0; POLICY=1+EXTRA.** Equality admits2. Use exact rational tick arithmetic:
stopTicks=ceil(A), and2*(125*stopTicks+374)<=25000 in cents. No float boundary jitter. Minimumq1 remains
even when its planned risk exceeds250; this is not a hard cap, user account balance or gap-loss bound.
The slice is a fixed .5%-of-50K research normalization, not optimized against this leg.

Five counted definitions if actually run after gross PASS:

1. BASE_Q1: causal protected parent,1MES.
2. CONST_Q2:2MES every parent, unselectable constant-exposure control.
3. EXTRA: sole candidate piece, the additional1MES on affordable events only.
4. POLICY: executable1/2MES allocation, algebraicallyBASE_Q1+EXTRA; its statistic cannot qualifyEXTRA.
5. STRESS_PARENT: unselectable parent with four adverse ticks per market/stop fill, same1.24commission.
   Masks summarize this common stress parent using the PRIMARY frozen quantity, not reselected stress sizing.

Quantity2 is one ticket, not two independent observations. Noq0 baseline, reentry, fractional scaling,
new signal/window/budget/ATR/stop/side search. Generic PLRiskPerTrade(default0), earlier constant-size
tests, volatility targeting and `s_rank_moc_round2_test.World.legs` fractional ATR-dollar pooling are
related selected ancestry. Prior199MC/202Python full-history source comments, parent parameter search,
future-year source comments and65t6evaluations remain selection history, not a new clean universe.

## Literal parent, clocks and calendar port

CT close-labelled five-minute chart, midnight-aligned. A midnight-stamped bar belongs to the new date
although its first four minute components belong to the previous civil date. Process OBSERVED bars
chronologically: on observed date change, if priorDayClose>0, score the completed weekday date's
TR=max(DayHi,PrevDayClose)-min(DayLo,PrevDayClose) whenPrevDayClose>0, elseHi-Lo; insert15-slot ring.
TheDayClose>0 guard also wrapsPrevDayClose updates, including Sunday. Preserve every source/bar/TR
reference and partial observed bucket; no ideal full-day reconstruction, current-day range, forward
fill, CT one-minute daily_atr substitution or future full-session membership. Partial past observations
are explicit SOURCE_LIMITED history, not proven complete feed or MC parity.

Reference=C1400 (j840); decision=C1450(j890), ordinary completed-bar availability. IfRefPx>0,A>0 and
abs(C1450-C1400)>=.30*A, follow sign. Exact next-market reference nativeOPEN1451(j891), wall14:50.
One ticket/date. Active entry-bar stop D, no target. Exact nativeC1500(j900) time exit. No last-close
fallback. Source MC confirmation says BarMagnifierOFF; it does not certify native one-minute stops.

LiteralUseHolidayTimes predicate: Jan1weekday/Jan2Monday; thirdMondayJan/Feb; lastMondayMay;
Juneteenth from2022(Jun19weekday,Jun18Friday,Jun20Monday); July3/4weekday orJuly5Monday; firstMondaySep;
ThanksgivingThursdayNov22..28 andFridayNov23..29; Dec24/25weekday orDec26Monday. Preserve its trace.
Additionally, this frozen conservative RESEARCH port permits only normal cash-session weekdays from
`codex_s03_calendar.calendar_status` and bound `replica.is_early_close`/pandas calendar definitions.
Thus known cash-closed/early days, including GoodFriday/mourning, cannot invent a closing auction.
This extra calendar guard is disclosed, not exact PL/MC parity or a price-selected change. Generate the
fixed2018–22 schedule only after this commit. Retain all calendar/literal disagreements and any observed
late bars on cash-closed/early dates. Never useg.trading, futurelast_j or existence of later prices for
earlier eligibility. Ordinary next-open availability, upstream timestamp/roll and ES-to-MES liquidity
are research assumptions; missing authentication remains LIMITATION rather than certified fills.

## Source/count admission before terminal returns

Only explicit owned `data/ES_1min_2017.csv` through2022;2017 warmup only. Bind all six names/bytes/SHA
before OHLCV interpretation; no2023+, old makers/pickles/broad caches or other instruments. Validate
declared year, date/HHMM, close labels, finite positive ES OHLC/order, volume>=0, native quarter ticks
with1e-7tick representation tolerance, duplicates/conflicts. Identical duplicates are retained in audit
and deduplicated once; conflicts/global invalid rows block before outcome calculations. No schema guess
silently accepted: source-only explicit parsing must be reviewed before execution. Grid24 may read only
six bound symlinks under the Codex output cache,night_pattern="". Ignore its future membership fields.

Every expected normal eligible2018–22 cash date must have complete exact five-minute C1400 andC1450
source bars (j836..840 and886..890), valid causal ATR and a recorded decision, including nonsignals.
Missing potentially eligible dates/references are unresolved and block the whole family, never presumed
no-trade. Every provisional parent additionally requires all native891..900 rows, exactO891/C900 and
valid held protection path. No return-based deletion or endpoint substitution. Source phase may check
row integrity/presence and pre-entry features but cannot subtract terminalC900 fromO891, run stops,
price null paths or compute financial results before its support marker.

Support gate: >=100 parent design opportunities,>=50 affordable EXTRA across>=3years,>=10EXTRA each
side,>=95% known affordability, all critical parent/execution paths resolved, and>=1000 distinct matched
quantity masks with a variable cell. Unknown extra state keepsq1 on an otherwise admitted parent;
unknown parent/path blocks. Retain all such records. These minima are not adjusted to actual counts.

Fixed null cells: designyear ×parentside ×abs(move)/A bins[.30,.50),[.50,.75),[.75,infinity). UnknownEXTRA
fixed0. Uniformly choose the actual number of extra lots within each cell without replacement. Count
exact combinatorial support before returns; saturated/sparse support stops, no pooling. If later needed,
save1000 unique masks with seed2026102709,max100000draws, selected eventIDs and full daily paths.
Diagnostic allocations are not causal strategies or valid funded paths. Do not match the exact ATR
affordability condition, which would saturate the policy by construction.

## Gross, native stopped designs and allocation test

Only after SOURCE/support PASS: raw gross=side*(nativeC900-nativeO891)*5, no stop/cost, both sides/year,
all/kept/omitted extra-opportunity count,total,mean,SD,SE,t. **EXTRA mean must be>=7.48USD**, twice3.74RT.
Raw failure adds1gross/0economic and closes the question; parent/POLICY/selected t cannot rescue it.

After gross PASS only, use private adapter to sharedgrid.execute/_walk, exact source paths, one tick
adverse primary fill. Entry=rawOPEN+side*.25; stop anchored on executed entry±D. If already through
stop at entry, use worse RAW entryOPEN, then adverse exit slip, never favorable nominal stop or modified
executed OPEN. Later gaps fill at worse observed OPEN. At time exit use exactC900 then adverse tick.
Direct native cash difference*5 minus1.24commission; no entry-slip double charge or extra3.74deduction.
Stress uses1.00point per fill and its own executed-entry stop anchor,11.24RT planningcost. No target;
target-through N/A. All exits15:00<15:59CT; holiday/half-day predicate and missing-path audits retained.

EXTRA design requires>=50events,positive total,trade t>=2,dailyNW5>=1.5,PF>=1.20,>=3positive designyears,
positive excluding each individual year, positive under STRESS_PARENT. POLICY total positive. Report
Sharpe,Sortino,PF,Calmar,Ulcer,maxDD,winrate,t,NW5,byyear/side,costbridge,raw/stopped and breakevenfee.
Allq1 parent tickets remain inPOLICY. Report all/kept/omitted hypothetical additional-lot profits and
omitted-opportunity t even when positive; sizing is not a claim removed existing trades lose money.
EXTRA must strictly beat BOTH nettotal andmaxDD on at least951/1000 fixed matched allocations:
(1+#nullprofit>=actual OR nullDD<=actual)/1001<=.05, ties fail. Retain marginal ranks, IDs and paths.
No overlapping diagnostic portfolios may count as executable returns or independent observations.

## Immediate book gate, then only selected historical validation

Immediately after design PASS, before further robustness, use CURRENTpersonal19 and1MESMOC slot,
common design dates/native1.24fees and published1.04diagnostic, whole contracts. Reuse shared engine
5000paired252-day/20-day-block histories,seed2026102709. Freeze and disclose inherited booking,
reentry/fee/mark/coverage treatment before book values; full common evidence endsOT2026-07-07.

Rows BASEpublished; EMPTYentireMOCslot; ADD_EXTRA=BASE+causalEXTRA; REPLACE_POLICY=EMPTY+causalPOLICY.
Mandatory controls EMPTY+causalBASE_Q1, EMPTY+causalCONST_Q2, andBASE+causalBASE_Q1(unconditional extra).
Separate published-versus-causal parent implementation change from sizing alpha. Do not addPOLICY
andEXTRA twice or count identical account arithmetic as different evidence. An ADD/REPLACE candidate
must beatBASE,EMPTY and corresponding constant-size implementation controls in historical annual
profit/maxDD,medianMCannualprofit/medianmaxDD,medianannualprofit/DD95; paired medianprofit difference
positive. Report absoluteDD95 and intervals. Unsupported fee/mark/coverage envelopes remainLIMITED,
not a certified candidate. A failure stops this question before2023+/additional robustness. Funded
50K/150K and evaluation comparisons require actual joint intraday paths; daily proxies do not imply
pass/payout/liquidation improvements.

If design/book survive, commitEXTRA/POLICY and matchedBASE_Q1 selection BEFORE only selected rule
and matched control run2023+once, called previously seen historical validation. Freeze exact placebo/
dependence implementation BEFORE those returns; no result-dependent recipe choice. Randomside uses
same original causal entry/quantity/stop distance/fixedC1500exit, uniform independent signs. Randomtime
uses the NORMALcash-date pool in each design/validation year, chosen without any future14:50 signal,
EXTRA-event membership or side. Eligible pool affordability uses only the sampled date's causal priorATR
and this same fixed risk slice; a future signal or return cannot select dates. Match actualEXTRA counts
byyear, draw distinct dates uniformly without replacement, then decisionC1300..C1450 on5-minute steps
uniformly. Side follows that sampled decision's preceding50-minute signed close move (zero gets uniform
randomside), without a .30ATR threshold. Enter exactnextnativeOPEN (C1300decision->O1301); use that
date's .25ATR rounded stop, SAMEfixedC1500 endpoint and primary fill/fee rules. Holds vary because only
entry time is randomized. Source-complete priorreference/entry/held paths required; missingness blocks
the test, no price-based redraw. Save1000draws/IDs/paths,seed2026102719, empiricalp=(1+#nulltotalnet>=
actualtotalnet)/1001. These are diagnostic reference paths, not adopted executable positions.
Each randomtime/randomside p<=.05. Full2018–26 incrementalEXTRA itself must clear current326item
tbar3.609533 ORDSR>=.95, positive both periods, plus dependence/selection sensitivity retaining all
family/control/t6history and fresh independent raw-spec checker. No qualification borrowed fromPOLICY.
Pre-MESlisting ES-price-proxy results are counterfactual native-cost research, not historical MESfills.
No PowerLanguage draft until all gates pass; no deployment or new user notification for routine failure.

## Budget, reproducibility and scope

Before registration5/60economic,8/10hypotheses,4gross plus archived65t6. This plan registersH09as9.
Source/support failure0gross/0economic; raw1gross/0economic; five actually run stopped definitions
add5economic, validation selected/control each add1 if newly evaluated. Controls/failures/stress are
never erased. No next hypothesis untilH09closed. At60evaluations OR10hypotheses finish the bounded
evidence/summary, then pause6adea9fee9c88191a45399d233743746; no11thhypothesis. Do not pause for failure.

Code `analysis/codex_hunt_v2_mes_*.py`; output/cache `analysis/outputs/codex_hunt_v2_mes_affordability/`;
report `agents/codex/results/hunt_v2_mes_moc_affordability.md`. Exclusive lock, write-once attempts and
markers, bound prereg/code/source/dependency/inputSHA, no data on import or invented fixtures. Writes
onlyallowedCodex paths, branchcodex/work; no shared rankings/plans/rootTODO/other-branch/live/VPS/
broker/Rithmic/Apex/API/settings,PR2,purchases/paiddata/accounts/trials/external messages, stoppedweb/
403retry or submitted-template execution. `notification_event` staysnull for rejected/routine results.
