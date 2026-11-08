# Lab Q016: ES / ZN drift before 09:00 CT macro releases predicts the post-release move (pre-registered 2026-11-01,
before any return)

**Mechanism.** Kurov, Sancetta, Strasser & Wolfe (JFQA 2019; ECB WP 1901): for 7 of 21 market-moving US releases, ES and
ZN start moving in the eventual direction ~30 minutes before the release, the pre-move is about half the total reaction
(leakage / proprietary early estimates). If informed traders only partly trade before the number, the pre-move sign
predicts the continuation after it.

**Release days (fixed calendar, no returns).** ISM Manufacturing = first business day of the month; Conference Board
consumer confidence = last Tuesday of the month; both 09:00 CT (10:00 ET). Keep a day only if the ES bar 09:00-09:01
(stamp 0901) has volume >= 3x the median of the stamps 0846-0900 (confirms the release), and drop it if the ES stamp 0731
has volume >= 3x the median of 0716-0730 (a 07:30 release the same morning, e.g. NFP).

**Signal.** move = close(stamp 0858) - close(stamp 0835) on the traded market; skip if |move| < 0.05 x `daily_atr(14)`.
Side = sign(move).
**Rule.** Entry at the open of stamp 0900 (08:59:00, before the release). Stop 0.3 ATR from the entry, checked on each bar
from stamp 0900 to the exit, filled at the stop (or the bar open if it gaps) 1 tick worse; else exit at the close of the
exit bar.
- V1: ES, exit at the close of stamp 0910. V2: ES, exit at the close of stamp 0930. V3: V1 on ZN.

**Costs.** ES $5 + 1 tick ($12.50) per fill = $30 a round trip per ES; ZN $5 + 1 tick ($15.625) = $36.25 per ZN.

**Gates.** Stage 1 (2018-22): best t >= 2.0, PF >= 1.15, >= 40 trades. Stage 2: the same variant at the same clock on random
non-release weekdays (same count, 500 draws) p < 0.05; >= 4 of 5 years positive. Stage 3 one look on 2023-onward: same
sign, t >= 1.5, PF >= 1.1. t bar `lab_tools.bar()` 3.64 (N 373); pre-registered mechanism with 3 variants -> full-sample
t >= 2.0 + clean placebo. Apex: yes (MES / ZN intraday).

## Amendment 1 (2026-11-01, after the first run; day selection only, not a variant)
The 0901 volume confirmation (>= 3x the 0846-0900 median) is unusable on ES: at 09:00 CT ES is 30 minutes into the cash
session, so the median ratio is 1.9 on ISM days and 1.3 on Conference Board days; only 18 / 60 ISM and 2 / 60 CB days
(2018-22) passed, leaving 10 trades. The release dates are fixed by the agencies' calendars, so the confirmation is dropped:
days = the calendar rule alone, still dropping days with an ES 0731 volume spike (>= 3x). Variants, exits, costs, gates
unchanged. First run kept in the record: V2 +$184 (t 1.49, 10 trades), V1 +$116 (t 0.81), V3 ZN -$83; placebo p 0.12.
