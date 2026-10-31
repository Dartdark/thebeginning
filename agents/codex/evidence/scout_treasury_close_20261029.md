# Clock-aligned Treasury month-end demand: TEST

Summary: Test a new, source-motivated correction to a previously rejected ZN calendar family.
The prior intraday test ended at 14:00 CT even after Bloomberg moved its strike to 15:00 CT in2021.
No new returns observed;175/180final-three-business-date windows have usable owned minutes.
One long rule plus matched-calendar and execution-cost controls; no parameter search.
This is an intraday adaptation of a multi-day paper, not an exact replication or verified edge.

## Source questions

About: Hartley/Schwarz, *Predictable End-of-Month Treasury Returns*, November22 2019, SSRN3440417,
study monthly timing of bond returns and insurer purchases. Full41-page extracted primary text retained
locally; figures' captions available, original plot pixels not independently audited.
Findings: Table8 reports10-year futures gaining0.17% over final3trading days in1990–2018,
standard error0.02%; these are source returns, not our dollars or intraday results.
Why: insurers buy duration and index additions at month-end, potentially creating predictable pressure.
Build on it: a single clock-aligned intraday ZN screen using owned minutes. The paper does not establish
that its multi-day effect falls in this final-hour window. That is the testable adaptation.
[Primary paper](https://rodneywhitecenter.wharton.upenn.edu/wp-content/uploads/2019/12/17-19.Schwarz.pdf).

Independent timing evidence: Dyer/Fleming/Shachar, NYFed September22 2026,
[Treasury Trading at the Close](https://libertystreeteconomics.newyorkfed.org/2026/09/treasury-trading-at-the-close/),
documents Bloomberg's January14 2021shift from15:00ET to16:00ET and a shift in volume concentration.
Volume concentration demonstrates a clock, not a directional edge or the sign of net hedges.

## 1. Actor and obligation

Index trackers and liability-matching insurers rebalance holdings/duration near benchmark pricing dates.
The original flow evidence concerns actual cash Treasuries, especially newly added securities. It does not
prove every index tracker buys, or that every ZN delivery basket inherits the full demand. This is a conditional
pressure hypothesis based on source evidence, not a promise of mandatory aggregate net purchases.

## 2. Information clock and direction

Calendar dates and benchmark-change date are public facts available before entry; no surprise or future volume
feature. Long only during the final hour before the prevailing benchmark strike on each of the month's
final3cash-bond business dates. From2018 through January13 2021, buy13:01-labelled open (13:00CT), exit14:00close;
from January14 2021, buy14:01-labelled open, exit15:00close. One protective1ATR15stop rounded outward to1/64point,
known before that calendar date, no target/reentry. No shorts or multi-day holds.

## 3. Direct contract/hedge transmission

Trade1ZN, the direct duration hedge for Treasury demand. The source explicitly documents Treasury-futures
spillovers. Intraday-only avoids holding continuous-contract splice jumps across calendar sessions; no
profit from a roll gap is claimed. Deliverable-basket and hedge-basis changes can still weaken transmission.

## 4. Inputs and feasibility

Six exact owned ZN files2017–22, hashed in inventory;2017ATR warm-up only. No2023+file opened. Public
US federal-holiday plus GoodFriday calendar, excluding2018national-mourning closure; Juneteenth begins2021.
The calendar is an explicit operational convention, not reconstructed historical index-constituent data.
Early-close windows lacking the benchmark endpoint are excluded and reported; no forward-filling endpoints.
175/180events pass timestamps-only checks: both endpoints,>=98%of60minutes and max1missing minute.
At least150events and90%coverage required before design. No return-informed exclusions.

Pre-return engineering detail: a provisional99%check implicitly required every one of60minutes and retained158.
Before evidence/preregistration or returns, it was replaced with the explicit one-missing-minute convention;
both provisional and final timestamp inventories are retained. No financial result was used. The eventual
frozen gate is not to be changed after outcomes. Gap-aware stops fill at the next observed open if crossed.

## 5. Costs and portfolio fit

Native ZN=$1,000/point, tick1/64=$15.625. Fees$7.25perfill+$15.625slippageperfill=$45.75RT;
stress2ticks/fill=$77RT. No proportional micro scaling: a small-notional Treasury future has a different
underlying/duration and is not a fungible microZN. First screen at1ZN; do not optimize size.
Potential home: existing equity-heavy personal portfolio, and intraday evaluation/funded only if executable
integer size and chronology permit. There is no claim of hedging equity losses before a breach. Current book
must be refreshed if the candidate earns account tests. Test all events regardless of existing occupancy.

## 6. Power

175events, assumed$200eventSD: t2.5requires about$37.80net/$83.55gross per ZN. Assumption, not observedSD.
Prior intraday ZN tests have weak or negative results, and native costs are large. This is a cheap exploratory
screen for a large effect, not confirmation that the multi-day historical effect is implementable intraday.

## 7. Prior evidence and falsification

TIER_LIST's month-end ZN row and `analysis/zn_month_end_test.py` already reject7:21–13:59 and12:00–13:59
on the last or preceding day. They remain negative evidence; no reset of multiplicity. The genuinely new
information is the documented2021benchmark-clock change; final3dates follow the paper's preferred horizon.
This is a new economic look in an existing broad family, not a newly invented discovery of bond month-end.
No selection between historical vs current clock or among lookbacks/windows/stops after the test.
Reject if any of: native net<=0,t<2.5,<4positiveyears, year-bootstrap lower<=0, matched-calendarp>.05,
stressmean<=0. A rejection ends this definition; do not rescue with2/5days or a side flip.

## 8. Failure, liquidity and shared losses

Market orders consume liquidity; neither source demonstrates savings from passive execution.
Rates repricing, macro releases, delivery-basket shifts and competing anticipatory trades can overwhelm
month-end demand. Stocks and bonds can fall together; this is not a tail hedge. Missing-bar stop traversal
and adverse gaps are material limitations. Before portfolio claims, replay simultaneous positions, drawdown
and daily limits at integer sizes; later equity recoveries cannot repair an earlier breach.
Independent verification, MultiCharts parity and forward evidence remain pending. No live or plan changes.
