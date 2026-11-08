# Lab Q003: 6E into / out of the WM/Reuters 4 pm London fix (pre-registered 2026-10-31, before any return)

**Mechanism.** The WM/Reuters 4 pm London fix is the benchmark rate for asset managers' FX hedges and index-fund FX
trades; the volume is largest on month-end days, when foreign-asset hedges are rebalanced (Melvin & Prins 2015; Evans
2018). Dealers who sold fix orders pre-position, so 6E drifts into the fix in the direction of the pre-fix flow (V1, V3)
and partly reverses afterwards (V2). Overlap check: Codex's all-days post-fix fade (16:03 London, TIER_LIST F) found no
gross edge; V2 here is month-end only, V1 / V3 trade the drift before the fix, which nobody has tested.

**Clock.** fix = 16:00 Europe/London converted to CT for each date (10:00 CT normally, 11:00 CT in the DST-mismatch weeks).
Below, F = the fix in CT; bars are CT bar-end stamps (bar F covers F-1 .. F).
**Month-end day** = the last 6E weekday session of each calendar month.

**Rule (1 6E, $125,000 per point, tick 0.00005 = $6.25).**
- V1 month-end only: move = close(F-5) - close(F-30). Side = sign(move). Entry at the open of bar F-4, exit at the close
  of bar F (= the fix). No stop.
- V2 month-end only: move = close(F) - close(F-30). Side = -sign(move). Entry at the open of bar F+2 (F+1 .. F+2),
  exit at the close of bar F+30. No stop.
- V3 = V1 on every weekday session.
Flat trades (move = 0) are skipped.

**Costs.** $5 commission + 1 tick ($6.25) per fill = $17.50 a round trip.

**Gates (lab/README.md).** Stage 1 (2018-22): best variant t >= 2.0, PF >= 1.15, trades >= 40 (V1 / V2 event studies) or
>= 80 (V3). Stage 2 placebo (500 draws): V1 / V2 = the same rule at the same CT clock on random non-month-end days (same
count); V3 = the same rule with F replaced by a random whole hour 03:00-14:00 CT other than 10:00 / 11:00, all days; p < 0.05
and >= 4 of 5 years positive. Stage 3 one look on 2023-onward: same sign, t >= 1.5, PF >= 1.1.
t bar: `lab_tools.bar()` = 3.64 (N 361); pre-registered mechanism with 3 variants, so full-sample t >= 2.0 + clean placebo.
Best variant = highest stage-1 t. Apex: yes (6E / M6E).
