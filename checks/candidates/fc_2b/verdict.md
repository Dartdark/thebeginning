PASS WITH CONCERNS (the formal checker says FAIL: 7/8 on the MC list, 7/9 on my replica. G1 fails on the DSR leg, but t clears the CLAUDE.md t-bar; G4 is borderline)

# FC 2B v2: checker verdict (2026-10-23)
Spec: `FC_2B_v2.txt` only. Reference trades: the MC v2 report (`trades.csv`, 773 trades 2018+, net = MC profit - $17.25).
My rebuild: `replica.py` (total-volume CSVs, bars stamped at the close, 08:31-15:00). Gates: `checker_report.md`, `../fc_2b_replica/`.
I read REVIEW.md only after the replica was finished.

## Replication
- **vs MC v2, 2018+:** 725 shared days out of a union of 812 (89.3%). On those 725 days the replica matches MC exactly:
  side, entry and exit are 100% equal and so is net (corr 1.000). Exit types also agree one-to-one (eod 397, stop 325,
  3 entry-bar "Stop Loss" backstops). 39 days are only in the replica, 48 only in MC. Of the 48, 3 are 2026-10-12..16
  (past the end of our data) and 5 are CME holidays (Presidents, Memorial and Labor Day; my |z| there is 0.25-0.92).
  The rest sit at the threshold: my |z| is 0.73-1.31 with a median of about 1.0. This is the
  Volume-definition caveat (MC up-tick Volume vs our total), not a logic error.
  Cost of the gap: MC-only trades average $423 (n 48) and replica-only trades $178 (n 39). Replica $199.2k vs MC $212.6k.
- **vs python_trades.csv (v1 exits):** my `--v1` mode reproduces it trade for trade (764/764, net identical).
- A crude up-volume proxy (volume on up bars only) keeps only 27% of the days but still makes $253 a trade. The trade
  set depends on the volume definition. The edge does not.

## Gates (MC list / replica; N = 282, t_threshold 3.57)
G1 significance **FAIL**: t 4.02 / 3.82, DSR 0.890 / 0.845 (< 0.95). t clears 3.57, and still clears 3.61 at N = 322
(282 + the author's ~40 builds), but only by 0.2-0.4. | G2 holdout PASS: 2018-22 $292 (t 3.68) / $290 (t 3.65);
2023-26 $252 (t 2.10) / $220 (t 1.84). | G3 years PASS: 9/9 on both, but 2023 is only $4.3k / $3.4k. | G4 concentration
PASS / **FAIL**: without the best 5%, +$1.6k / -$4.8k. | G5 placebo PASS: 100 random-side runs average $31 (95th
percentile $132), and 200 runs of random days drawn from the every-day opening-drive trades average $119 (95th
percentile $195). Real is $275 / $261; p < 0.003 for both. | G6 PASS: 2023+ P(Sharpe <= 0) 0.009 / 0.030. | G7 MinTRL
PASS: 773 trades vs 112. | G8 regime PASS: rho 0.81. | G9 PBO (replica, 16 neighbouring variants) PASS: 0.45.
Metrics (MC list): Sharpe 1.32, Sortino 2.58, PF 1.51, Calmar 1.53, Ulcer 2.68, max DD $15.3k per NQ. Longs $305
(Sharpe 1.07); shorts $246 (Sharpe 0.81). In 2023+ shorts drop to $161 (MC) / $109 (replica), bootstrap P(Sharpe <= 0) 0.16.

## Leak / trap checks
- **Look-ahead:** none found. The signal uses bars 08:31-09:00, which are complete at the 09:00 close. Entry is the
  09:01 open; 0 of the MC entries fall at another time, and all MC entry prices equal our 09:01 open. z uses only
  previous days (the buffer is appended after z is computed). Stops are set at the bar close for the next bar, so the
  backtest never has to guess the order of events inside a bar. Gaps fill at the open.
- **Holidays / overnight:** in v2, 0 trades are held overnight and 29 are flattened at 11:31. Roll: the ratio is
  dimensionless and everything is intraday.
- **Costs:** the MC report has none. I apply $17.25 per round trip.
- **Selection / exits:** the exits are not knife-edge. Across stop 80/120, trail 0/100/200, BE 0/0.5/1.0, lookback 40/100
  and exit 13:00, totals range from $163k to $223k. **This contradicts REVIEW.md:** a fixed 100-point stop with an EOD
  exit (no BE, no trail) makes $247 a trade (an independent loop gives $250, t 3.2), not $29, and trail-only makes $272,
  not $43. The edge sits in the entry signal, not in the BE step. REVIEW's ablation should be rechecked.
- **Filter value:** on its own, the opening-drive direction makes $118 a trade on all 2,259 days (t 3.0). The z filter
  lifts that to $261 a trade vs $45 on the skipped days (t of the difference 2.59). The lift is t 2.66 in 2018-22 but
  only **t 1.06 in 2023+**, and in 2023 the filter lost.
- **Point-scaled exits on a price that quadrupled:** full-stop rate by year is 8% / 3% in 2018-19 and 20-37% in 2022-26.
  EOD exits fall from 90% to 21%. 31 of the 39 top-5% trades are from 2022 onward. With the stop and trail scaled to the
  price, the edge holds (t 3.0-3.8 at reference levels of 10k / 14.3k / 20k), so this is drift, not a break.
- **Size:** at 1 NQ a single stop is -$2,017, which is the whole Apex trail, so this is an MNQ strategy. 2023+
  block-bootstrap probability of hitting the EOD trail within a year: 10% at 1 MNQ, 43% at 2 MNQ (assuming $3 per
  round trip per MNQ).

## What would change my mind
1. Forward / live fills where the up-tick `Volume` signal days diverge from the backtest. Lower the verdict to FAIL if
   the forward log's mean is below $0 over about 80 trades.
2. A clean holdout of the z filter itself. Its 2023+ lift over unfiltered drive days is only t 1.06. If the filter does
   not hold, the strategy degrades to the $118 base.
3. Concentration: if the best ~5% of trend days thin out (as in 2019 and 2023), the rest are net flat to negative.
