PASS WITH CONCERNS

# Verdict: Twin Continuation (NQ): checker

**Replication.** I wrote `replica.py` from `Twin_Continuation.txt` alone. It is a bar-by-bar MultiCharts port: IOG off, orders fill on the bar after the signal, exits sit idle on the entry bar, stop fills at the open on a gap, stop beats target on the same bar. Costs are $7.25 a round trip plus $5 per market or stop fill. My replica has 1,075 trades against the maker's 1,074. 1,073 trades match on entry date, time, setup and side (99.8%), and the P&L correlation on matched trades is 0.99995. Totals are $334,963 (mine) vs $335,578 (maker). All 3 unmatched trades and 2 of the P&L differences are holiday or early-close edge cases (2018-12-05, 2021-01-26, 2024-07-04/05, 2025-11-28). The spec is unambiguous.

**Gates on the replica** (`../twin_continuation_replica/checker_report.md`; the maker's own list gives the same results):
- G1: t 5.46, DSR(N=193) 0.995.
- G2: mean $185 a trade 2018-22 (t 2.63) and $470 a trade 2023-26 (t 5.05).
- G3: 8 of 9 years positive (2019 -$4.7k).
- G4: without the best 5% of trades, $85k is left.
- G5: in my own 200-run per-trade random-side placebo, the mean is $45 a trade (p95 $112, max $152) vs $312 real, p = 0.000. The maker's 10-run placebo agrees.
- G6: 2023+ P(Sharpe ≤ 0) = 0.000.
- **6/6 PASS.**

**Standard metrics.**

| | Sharpe | Sortino | PF | Calmar | Ulcer | Max DD (1 NQ) |
|---|---|---|---|---|---|---|
| All | 1.75 | 2.71 | 1.61 | 2.24 | 6.78 | $16.1k |
| Longs | 1.31 | 1.89 | 1.65 | 0.93 | | |
| Shorts | 1.19 | 1.92 | 1.59 | 1.06 | | |
| 2023+ Sharpe, all (p5–p95) | 2.48 (1.67–3.28) | | | | | |

The 2023+ drawdown permutation puts the actual drawdown at the 5th percentile.

**Leak and trap checks**
1. **10-minute oscillator.** A bucket is computed at the close of its last minute (:x0), and the MO entry is a market order at the next bar's open (:x1). Entry times are 841, 851, 901, 911, 921 and 931 only. There is no look-ahead. A missing last minute delays both the bucket and the entry by one bar. One quirk is in the code itself: the 00:00 bar starts a new date, so it forms a 1-bar bucket.
2. **6h swing confirmation.** A swing is a 7-candle fractal on completed 6h candles (17-23, 23-05, 05-11, 11-16). Its level becomes usable only at the 15-min close where the 3rd later candle completes, which is at least about 16h after the swing candle ends. `SwHOpen` uses only the current bar. There is no leak.
3. **Stop-entry gaps.** 0 of 726 BO entries filled at a gapped open, and the two entry stops never triggered on the same bar (0 cases). A 1-tick trade-through requirement on targets costs only $7.8k.
4. **Price level.** In percent of price the edge is stable. The yearly sums are: 2018 +3.5%, 2019 -1.4%, 2020 +17.9%, 2021 +14.4%, 2022 +16.1%, 2023 +15.7%, 2024 +11.6%, 2025 +11.1%, 2026 +16.5%. Per trade it is t 4.84. 2018-19 are flat, so most of the edge comes from 2020 on.
   - By setup and side (percent per trade, t-stat):
     - MO longs: 0.160% (t 3.2).
     - MO shorts: 0.193% (t 3.0).
     - BO longs: 0.067% (t 2.6).
     - BO shorts: 0.052% (t 1.3), weak, and only 0.007% a trade in 2018-22.
   - Concentration is high. The top 5% of trades make 74% of the dollars, and the top 8 are all MO trend days (2022-05-05 alone is +$11.1k). Without the best 5%, 25.9% of the 105.5% total is still left in percent terms.
5. **Sensitivity.** None of these changes makes it a knife-edge. Every variant has 8–9 positive years, and both setups stay positive in both periods. Totals and t-stats for each variant:

| Variant | Total | t |
|---|---|---|
| Base | $335k | 5.46 |
| MO_Trigger 80 | $290k | 4.25 |
| MO_Trigger 120 | $290k | 5.22 |
| Window end 9:20 | $334k | 5.52 |
| Window end 9:40 | $330k | 5.33 |
| BO_TargetMult 1.5 | $298k | 5.15 |
| BO_TargetMult 2.5 | $289k | 4.25 |
| MO stop 50 | $317k | 5.35 |
| MO stop 100 | $380k | 5.84 |
| Pivot timeframe 240 | $315k | 4.40 |
| Pivot timeframe 300 | $309k | 4.47 |
| VolCap off | $335k | 5.27 |
| Window start 9:00 | $264k | 4.78 |
| SignalLen 5 | $307k | 5.41 |
| BasisLen 30 | $305k | 4.81 |
| MO exit 13:00 | $329k | 5.54 |

6. **Rolls.** The series is an unadjusted continuous contract. Roll gaps are +1.0–1.4% at the 17:01 open in 2023+, plus two 03:32 splices in 2024. No position spans a roll gap. The 41 trades entered within 4 days after a roll average $393 a trade, vs $308 for the rest, so rolls are not the source of the edge.
7. **Holidays.** 4 trades are held across a session break, all on early-close days: 2018-05-28, 2018-11-23, 2021-09-06 and 2024-07-04 (MO). Together they lose $5.6k. `SHalfDay` misses July 4 and the holiday Mondays. In live trading this breaks Apex's flat-by-15:59 rule.

**Concerns: the 1-3 things that would most change my mind**
1. **Apex sizing.** BO's stop is the last opposite 6h swing: median risk is $5,970 per NQ vs a median target of $882. Only 22 of 726 BO trades hit the stop; the 214 trades closed at 15:45 lose $220k in total. The worst trade is -$11.7k, 61 days lose more than $2k, and the max drawdown is $16.1k at 1 NQ. That makes 1 NQ impossible against the $2,000 trailing drawdown. At 1 MNQ the drawdown is about $1.6k, which is still tight. The edge is real, but the size in the spec is not tradable on Apex. A funded-bench run at MNQ size, with a hard dollar stop on BO, needs to pass before this is promoted.
2. **MO trend days carry the dollars.** On the same entries, MO is +$62 a trade whether always long or always short. So part of the gain comes from the trend-day structure (a 75-pt stop plus a hold to 14:50). That structure is less effective at today's price, where 75 pts is about 0.3% vs 1.2% in 2018. The direction signal still adds about $470 a trade over that.
3. **Weak spots.** BO shorts are weak (t 1.3), and 2018-19 are flat. If the next 6 months look like 2019 (-1.4%), I would downgrade.

**Files.** In `checks/candidates/twin_continuation/`:
- `replica.py`
- `trades_replica.csv`, plus `trades_replica_<variant>.csv` for each variant
- `checks_extra.py`
- `checker_report.md` (re-run)

In `checks/candidates/twin_continuation_replica/`:
- `trades.csv` (= `trades_replica.csv`)
- `meta.json`
- `placebo.csv`
- `checker_report.md`
