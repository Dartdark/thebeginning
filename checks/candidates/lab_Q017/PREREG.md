# Lab Q017: trend-direction flow on turn-of-month days in CL, NG, GC, ZN, 6E (pre-registered 2026-11-02, before any return)

**Who pays / mechanism (structural).** Van Hemert (2014, 'MOM-TOM'): ~90% of the Newedge trend index return 2000-14 came on
the 3 turn-of-month days, partly reversed after, strongest in less liquid commodities. CTA subscriptions / rebalancing
arrive at month-end and are traded at the turn of the month in each market's trend direction: price pressure on known days.

**Days.** Per market, on its own weekday sessions: TOM = the last session of a month + the first 2 sessions of the next.
**Side.** sign(close[d-1] / close[d-64] - 1) on daily marks (last close at or before 16:00 CT); V3: d-253 instead of d-64.
**Trade.** Entry at the open of the first bar of the session (CL / NG stamp 0801, GC / ZN / 6E stamp 0721), exit at the
close of stamp 1325; stop 0.5 x `daily_atr(14)` from the entry, filled at the stop (or the bar open if it gaps) 1 tick worse.
**Specs.** CL $1,000/pt tick 0.01; NG $10,000 tick 0.001; GC $100 tick 0.1; ZN $1,000 tick 1/64; 6E $125,000 tick 0.00005;
$5 + 1 tick per fill.
**Pooling at equal ATR risk.** Each trade's net $ P&L is divided by its risk unit 0.5 x ATR x point value (R). Stage gates
are on the pooled R series; $ per 1 contract shown per market.
- V1 all 5 markets, 63-day trend. V2 CL + NG only. V3 all 5, 252-day trend.

**Gates.** Stage 1 (2018-22): best t >= 2.0, PF >= 1.15 (on R), >= 80 trades. Stage 2: (a) random-day placebo: the same
variant on random non-TOM sessions per market (same count per market, 500 draws), p < 0.05; (b) >= 4 of 5 years positive;
days 10-12 of each month reported as the paper's control. Stage 3 one look 2023-onward: same sign, t >= 1.5, PF >= 1.1.
t bar `lab_tools.bar()` 3.65 (N 380); pre-registered mechanism, 3 variants -> full-sample t >= 2.0 + clean placebo.
**Known risk.** Unadjusted continuous series: a roll inside the 63 / 252-day window can flip the trend sign (not corrected).
Apex: yes (micros, intraday).
