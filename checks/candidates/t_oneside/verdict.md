PASS WITH CONCERNS. The T leg holds up. The OS leg is weak. Formally the checker gives FAIL on G1 (DSR 0.926 < 0.95), although t 4.28 clears the CLAUDE.md alternative of t >= t_threshold(291) = 3.58.

**Replication** (`replica.py`, written from spec.md alone using the raw `data/NQ_1min_20*` and `NQ_1min_ON_20*` files, Dec-2017 warm-up). Every one of the maker's 874 trades is reproduced exactly: same date, leg, side, entry, exit, kind and net (P&L corr 1.0000, 0 mismatches). My replica also has 14 extra trades in January 2018, worth +$391 in total. They exist because the maker did not use the December 2017 nights as warm-up, which the spec asks for. This is immaterial. The replica trades, together with 8 neighbouring variants and a random-day placebo, are in `../t_oneside_replica/`.

**Gates** (maker trades / replica trades):
- G1 FAIL / FAIL. t 4.28 / 4.29, DSR(N=291) 0.926 / 0.928. Per leg: T has t 3.58 and DSR 0.76; OS has t 2.39 and DSR 0.30.
- G2 PASS. 2018-22: $135 a trade (t 3.66). 2023-26: $172 a trade (t 2.56).
- G3 PASS. 9 of 9 years are positive.
- G4 PASS, but only just. Without the best 5% of trades the total falls to $7.3k of $131k ($8.8 a trade).
- G5 PASS on both placebos:
  - The maker's placebo (20 runs of T with a random side) has a mean of -$29, and none of the 20 runs reaches the real mean. Its file was in wide format, so I converted it to the run,net layout the checker needs; the original is saved as `placebo_wide_maker.csv`.
  - My harder placebo (200 runs) takes the same trade counts on random valid nights or days. Its mean is $22 against the real $148, p 0.000. Per leg: T on random nights p 0.000; OS as an unconditional 10:00 long on random days p 0.005.
- G6 PASS. 2023+ P(Sharpe <= 0) 0.003.
- G7 PASS. 874 trades against a MinTRL of 120.
- G8 PASS. rho 0.82.
- G9 PBO (replica only, over 9 neighbouring variants) PASS. PBO 0.19.
- Metrics (all trades): Sharpe 1.42, Sortino 2.47, PF 1.51, Calmar 1.19, Ulcer 2.78, max DD $12.3k at 1 NQ.

**Leak and trap checks**
- **Night-volume median.** The night is banked only when the session opens, after the decision, so D's own night is excluded. Only valid nights go into the median. Heavy nights by weekday: Monday 14% (so Sunday nights are not inflated), Thursday 19.5%, Friday 18.6%; the heavy days are largely 07:30 CT data-release mornings. Four nights cut short by data gaps or the CME outage (2018-10-01, 2018-11-05, 2020-03-16, 2025-11-28; 139-257 bars) still count as valid and enter the median. This is minor. The Good Friday nights that run together (1,838 bars, 2021, 2023, 2026) are not heavy.
- **08:29 pre-bell fill.** Bars are stamped at their close: the volume spike sits in the bar stamped 08:31. So the T entry is at 08:29:00, one minute before the bell, decided on the 08:29 bar's close. This is not a leak, and the 08:30 bar has a median volume of 735 contracts. However, the edge is front-loaded. Entering at the 08:31 open instead gives $180 a trade (t 2.75) against $233; entering at 08:32 gives $161.
- **VWAP exit.** It uses the bar's close and a VWAP that includes that bar, and the exit fills at the next bar's open. No look-ahead.
- **Stop fills.** When the stop fill uses the bar's open if the bar opens beyond the stop, the result is identical: there are 0 such cases among the 60 stopped trades. The stop is not essential. Without it T makes $208 a trade, and moving to 0.3 / 0.5 ATRd gives $182 / $220.
- **Data seams and rolls.** The 07:59/08:00 and 15:15/15:16 seams are clean (worst gap 0.03%). The roll gaps fall on the first night bar, which the night return excludes. The exceptions are 2024-06-18 and 2024-12-16 (gap at 03:32 inside the night); neither night produced a T trade. Heavy nights are more common in the roll week, 12-20 days before expiry (25% against 17%), and T earns $520 a trade there against $173 in normal weeks. That is a volume artefact, but it is known in real time, and outside the roll week T still makes $194 a trade (n 329), so the result is not a roll effect.
- **Holidays.** There are 21 trades on half or holiday sessions (Memorial Day, Labor Day and similar), and their P&L is small.
- **Costs.** $17.25 is included in every trade.

**Robustness**
- **T leg.** It works only on heavy nights. The same fade on all nights makes $26 a trade (t 1.19); on light nights it makes -$15. The effect grows with the threshold: multiplier 1.2/1.3/1.4/1.5/1.6 gives $121/$147/$233/$258/$312 a trade. The exit time is not sensitive: 08:40 $247, 08:50 $222, 09:00 $206. Both sides are positive (longs t 2.5, shorts t 2.6).
- **OS leg.** Its returns depend on a handful of large winners: without its best 5% of trades (25) the leg loses -$8.9k, its median trade is -$27, and 2025 was -$3.2k.
- **The night switch does not help OS.** OS on every night makes $81 a trade (2023+: $131), against $87 on light nights only (2023+: $92). Run on heavy nights, OS makes $51 (2018-22: -$105). So the stated quiet-night mechanism is not supported for OS. OS is a long-only filter for one-sided morning momentum in a bull sample: an unconditional 10:00 long with the same exits makes $21.

**Practical concerns.** At 1 NQ the median stop in 2025-26 is $2.6-3.0k for T and $1.8-2.2k for OS. Sixteen trades lost more than $2,000 (13 of them in 2023+), and max DD is $12.3k. On an Apex 50K ($2,000 EOD trailing) this has to run on MNQ or at a fraction of the size.

**What would most change my mind**
1. A live or MultiCharts fill test of the 08:29:00 pre-bell entry. Every 1-minute delay costs about $50 a trade on T.
2. OS losing its top 25 trades' worth of luck out of sample. If 2026-27 OS looks like 2025, drop OS and run T alone.
3. The multiple-testing bar. T alone has t 3.58 (exactly the threshold) and DSR 0.76. A pre-registered forward period with T at t >= 2, or a lower TRIALS count, would clear G1. A rise in N, or a forward Sharpe near 0, would not.
