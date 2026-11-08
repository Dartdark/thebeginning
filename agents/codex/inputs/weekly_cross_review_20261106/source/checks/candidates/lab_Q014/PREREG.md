# Lab Q014: GC while Shanghai (SGE) is closed: Spring Festival and National Day (pre-registered 2026-11-02, before any return)

**Who pays / mechanism (structural).** Chinese physical buyers (SGE, the largest physical market) are absent while the
mainland is closed; the Asian bids that normally absorb London / US selling are missing, so gold drifts weaker on closure
days and recovers once Shanghai reopens.

**Days.** `data/sge_holidays.csv` (closure weekdays 2018-26 from the State Council schedule, entered before any return).
Reopen days = the first 2 GC weekday sessions after the last closure day of each holiday.

**Rule (1 GC, $100 a point, tick 0.1 = $10).** Entry at the open of stamp 0721 (07:20 CT), exit at the close of stamp 1225;
stop 0.3 x `daily_atr(14)` from the entry, filled at the stop (or the bar open if it gaps) 1 tick worse.
- V1 short on every closure weekday. V2 long on the 2 reopen sessions. V3 V1 on the first 3 closure weekdays of each holiday.

**Costs.** $5 + 1 tick per fill = $25 a round trip.

**Power check (lab lesson Q012).** ~10 closure weekdays a year: V1 ~53 trades in 2018-22 (needs mean >= ~0.28 sd for
t 2); V2 ~20 and V3 ~30 trades are below the 40-trade event bar, so only V1 can pass stage 1. Stated before the run.

**Gates.** Stage 1 (2018-22): best t >= 2.0, PF >= 1.15, >= 40 trades. Stage 2: the same variant on random non-holiday
weekdays (same count, 500 draws) p < 0.05; >= 4 of 5 years positive. Stage 3 one look 2023-onward: same sign, t >= 1.5,
PF >= 1.1. t bar `lab_tools.bar()` 3.65 (N 378); pre-registered mechanism, 3 variants -> full-sample t >= 2.0 + clean
placebo. Apex: yes (MGC).
