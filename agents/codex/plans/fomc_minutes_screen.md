# FOMC minutes reaction continuation — preregistration

Date: 2026-10-22. Branch: `codex/work`. One return trial, not yet executed.

## Mechanism and novelty

The Fed publishes its meeting minutes at 14:00 Eastern / 13:00 Central, normally three weeks after the decision.
Policy-sensitive investors and their dealers may adjust equity exposure as the text is processed; NQ is a direct
execution instrument for that adjustment. Hypothesis: the first five minutes identify pressure that continues for
the next 25 minutes. This is **scheduled information flow, not a mandated directional order**. The release schedule
is established; persistence and the identity/size of trading participants are unverified hypotheses.

Checked TIER_LIST, WATCHLIST and the scripts through Claude `7bb539a`. Statement / press-conference reactions
are already F; the high-liquidity statement-day short is WATCHLIST 23. Those are different events. No dedicated
minutes-release reaction test was found. Gao's paper mentions minutes days, but the repo tested decision days.
Do not retest Friday expiry, covered-call selling, close-to-close LETF momentum (Chan, already F), VIX-ETP proxy
momentum, or roll-week directional shorts. The calendar spread needs separate delivery-month data, absent here.
ADP was considered for the 07:15 gap but not tested; its verified historical release calendar is not in the repo.

## Calendar and data

Use every distinct minutes release during calendar 2018–22, including January releases for December meetings,
and the April 2020 release covering the emergency March meetings. Exclude notation votes without a distinct
minutes release. Commit a 40-date snapshot and its official Fed source URLs with this plan. Do not infer dates
from volatility or simply add 21 days. Include holiday-shifted releases.

Sources: [2017](https://www.federalreserve.gov/monetarypolicy/fomchistorical2017.htm),
[2018](https://www.federalreserve.gov/monetarypolicy/fomchistorical2018.htm),
[2019](https://www.federalreserve.gov/monetarypolicy/fomchistorical2019.htm),
[2020](https://www.federalreserve.gov/monetarypolicy/fomchistorical2020.htm),
[2021–22 calendar](https://www.federalreserve.gov/monetarypolicy/fomccalendars.htm).
The [March 2021 meeting page](https://www.federalreserve.gov/monetarypolicy/fomcpresconf20210317.htm)
explicitly records the minutes' 14:00 ET release time.
Use existing `scratch_data/g24.pkl`; do not rebuild caches.

## One fixed rule

At the 13:05 CT minute close on a release date, follow the sign of NQ's change from the 13:00 close to 13:05.
Unchanged price means no trade. Enter the next minute's open (13:06 bar, as the repo stamps minute closes).
Stop: 0.25 × lagged 15-session daily ATR, rounded up to a 0.25-point tick. No target; exit at the 13:30 close.
Stops active on the entry bar, adverse gap stops at the open. Skip incomplete signal or holding-window bars;
never forward-fill a missing price. One trade maximum per event. No alternate direction, timing or threshold.
Costs: $7.25 commission + one NQ tick per market/stop fill = $17.25 per round trip, per full NQ.

Use the accepted actual-position occupancy builder from the SGE screen. Skip the event when **any** current
roster line is open at 13:05; do not net opposing positions or infer occupancy from daily P&L. Future occupancy
is measured after execution and never used to decide eligibility. The existing map shows Wednesday/Thursday
13:00 hours about 56–57% minute-flat; this is a partial gap, not an entirely empty hour. Exit before LDF starts.
Closest replacement comparator: LDF, because both trade afternoon directional pressure; existing entries unchanged.

## Cheap design gate and stop rule

Count this as **one trial even if it fails**. Execute candidate returns on 2018–22 only. Require all:

- At least 20 executed trades (the entire event population is only 40 releases).
- Mean gross >= 1.5 × $17.25 = $25.875 per NQ, positive net total, net trade t >= 2.
- Positive net in at least 3 of 5 calendar years.
- At least 95% of actual candidate position minutes have no existing roster position.

Report whole / longs / shorts standard metrics and annual results, gross vs costs, every skipped event and
actual overlap. On **any failure, REJECT and stop**: no candidate 2023+ signals/returns, placebos, Monte Carlo,
funded bench, parameter rescue or reversal test. The pre-existing roster map may use accepted historical trades;
that is not an unopened holdout claim about the overall portfolio.

## Only after design passes

Freeze this rule and calendar mapping before opening 2023+ once. Require positive holdout mean with a 90%
bootstrap lower bound > 0, t >= 2, and same-calendar random-side / ordinary-day matched-time controls with
p <= .05. Use repository resampling and account tools. At 1 MNQ, run Monte Carlo and paired funded bootstrap
as addition, replacement of LDF, and LDF empty-slot control, versus the accepted current roster (ES MOC 2 MES).
Promotion requires improved year-1 and year-2 payouts, a positive 90% paired interval on year-1 gain, blow-ups
no more than 1 percentage point higher, and no longer median time to six payouts. A design pass alone is not
a candidate for live use. Any changed rule is a separately registered trial.
