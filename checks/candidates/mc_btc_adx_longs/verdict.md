READY FOR THE USER'S BACKTEST (with 3 small fixes recommended; a roll procedure is required before live)

**File:** personal_strategies/BTC_ADX_Longs.txt + functions/PS_UTCOffsetCT.txt (2026-11-14, not compiled). Replica: replica.py (the PL state
machine bar by bar: spot 15m bars built on local close stamps, PS_UTCOffsetCT as written, the catch-up while loop with ScanMax 2900, first
calc at data1 bar 3000, MC order fills: market at the next open, resting stop min(open, stop)). compare.py vs the reference.

**Replication (entries from 2019-07-01)**
| | reference | replica as written | replica + DST fix |
|---|---|---|---|
| paper books, both sides (t, side, book) | 675 | 674; 98.4% matched | 99.6% matched |
| matched: same exit time / reason | | 99.5% / 100% | 100% / 100% |
| real MBT longs | 299, $1,505/yr | 282, $1,304/yr | 282, $1,306/yr |
| real matched by paper entry | | 93.0%, P&L corr 0.94 | 93.6% |

Paper mismatches all trace to DST days (2020-03-08, 2021-11-07, 2023-03-12, 2025-03-09 and EMA/ADX carry-over 1-4 weeks later).
Real-side gap (-$200/yr) explained: re-running the reference with MC timing gives $1,375/yr (entry at next open, -$130/yr; Python fills at
the signal close, incl. 10 signals on the 16:00 CT bar that MC fills after the break) and $1,364/yr with exits next open; the rest is the
"closed and reopened" case (MC keeps the contract: 19 reference trades merge into chains; sums agree within $5 a chain) plus fill noise
(e.g. 2024-05-15 b50: stop 0.07% from the low, -$770 swing).

**Compile risks** (none certain): `he = Mod(ok, 60) = 45;` (l.98) parenthesize; MaxBarsBack must be FIXED at 3000 (variable `Date[j] of data2`
up to 2900); compile the function first. Reserved-word / case clashes: none found.

**Logic findings / fixes**
1. PS_UTCOffsetCT l.16: `TimeVal >= 200` -> `TimeVal > 200` (close stamp 02:00 on the spring day is CST; as written it maps to 07:00 UTC, before
   the previous bar), and BTC l.93-95: process a spot bar only `if ck > LastKey` (duplicate / backward stamps). Lifts paper match 98.4% -> 99.6%.
2. l.210 `Ready` does not require ND >= 121, so the vol-ratio gate is OFF for the first ~4 months of a chart; header l.31-32 says no trade is
   taken before it is ready. Add `and ND >= 121` (or fix the comment).
3. Rolls: on an unadjusted @MBT/@BTC continuous the replica makes $10,507 vs $9,497 adjusted from 2019-07 (+$1,010, 4 more stops) - backtest on a
   back-adjusted series. Live: books last up to 240 h across MBT's last-Friday expiry; the code and setup have no roll procedure.

**Gates** (replica trades, checker_report.md): G1 FAIL (DSR 0.42, N 487), G2 PASS (2023+ t 2.65), G3 PASS 7/8, G4 PASS ($152 left without the
best 5%: thin), G5 FAIL (no placebo), G6 PASS, G7 PASS, G8 PASS, G13 CONCERN (years). G10/G11 not run: leak_checks has no BTC tick table.
**Leaks:** spot bar closing at T is used on the MBT bar closing at T, order next bar: none. Python's same-close fill is the optimistic side.

**Would change my mind:** the MC report differing from the replica by more than the 2% residual; MC stamping the spring 02:00 bar differently
(then fix 1 is moot); a live roll that cannot be handled.
