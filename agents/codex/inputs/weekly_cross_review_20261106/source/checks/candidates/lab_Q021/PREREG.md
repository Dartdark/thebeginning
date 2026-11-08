# Lab Q021: NG Sunday up-gap fade = the plan's CL rule ported unchanged (pre-registered 2026-11-04, before any return)

**Who pays / mechanism (structural / behavioral).** Weekend weather-model runs and news reprice NG at the thin Sunday
17:00 CT reopen, where few liquidity providers quote and demand a premium; the overshoot is given back as Monday's
liquidity arrives. Same mechanism that pays the plan's CL Sunday up-gap fade (rank A).

**Frame (copied from `analysis/s_rank_gap_round2_test.py` / `cl_sunday_fade_confirm.py`).** Sunday -> Monday weekends
with a full Monday session (holiday Mondays drop out). ref = last NG price before Sunday 17:00; gap = first open at /
after the 17:01 bar - ref; gA = gap / `daily_atr(15)` known on Monday. Weekends whose ref -> Monday 09:00 window
contains an NG roll bar are dropped. **NG roll bar** (lab Q011 lesson): our series switches contract at the first evening
bar of the session of the expiry day (expiry = 3 business days before the 1st of the delivery month, US federal holiday
calendar); that bar is marked as the roll.

**Trade (1 NG, $10,000 a point, tick 0.001 = $10).** Entry at the open of the 17:05 bar (stamp 1706) on Sunday, 1 tick
against us; stop 0.75 x ATR from the raw entry, filled at max(bar open, stop) + 1 tick (shorts; mirrored for longs); else
exit at the close of stamp 0900 Monday, 1 tick against us. $5 commission a round trip (+1 tick per fill as above).
- V1 (CL's exact form): short when gA >= +0.1. V2: both sides (long when gA <= -0.1). V3: short when gA >= +0.3.

**Gates.** Stage 1 (2018-22): best t >= 2.0, PF >= 1.15, >= 80 trades. Stage 2: placebo on Mon-Thu evening reopens (17:00
after the 16:00 break -> next day 09:00, same entry / stop / exit), gap threshold set at the quantile that keeps the same
share of evenings as the variant keeps of Sundays, same side rule; random draws of the same count, 500 draws, p < 0.05;
>= 4 of 5 years positive. Stage 3 one look 2023-onward: same sign, t >= 1.5, PF >= 1.1. t bar `lab_tools.bar()` 3.65
(N 384); pre-registered mechanism + rules copied (no new parameters), 3 variants -> full-sample t >= 2.0 + clean placebo.
Apex: yes (the Sunday 17:00 start is Monday's Apex day; flat 09:00 Monday).
