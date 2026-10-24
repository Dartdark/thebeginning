# Merged OvernightBiasORB + OvernightAnomaly v4.1 (user's file, 2026-10-24)

File: `Overnight_Anomaly_BiaisORB.txt` (15-min NQ chart, Bar Magnifier 1-min, IOG off). Two blocks on one position:
- **Block A, OvernightBiasORB (08:30-14:30 CT):** close beyond the 08:30-08:45 range, in the direction of the overnight
  bias (08:30 open in the top / bottom third of the 00:00-08:30 range), ADX(16) >= 20, breakout bar <= 2.5 x the 20-bar
  average range, OR <= 2 x its EMA median; stop 0.30 x 15-day RTH ATR, target 3R, up to 4 trades a day.
  = OB v2 without its ATR15/ATR100 regime filter (Codex replay: OB v2 replacing ONB, evaluation 50.2% -> 43.4%).
- **Block B, OvernightAnomaly v4.1 (17:30 -> 02:30 CT):** long at the 17:30 bar close after an RTH session that closed below
  its open (not after a half day); time exit at the 02:30 close; disaster stop 4 x the EMA(20) of the window's range;
  vol-target size $2,200 / (stop x point value), 1-20 contracts. Inside one Apex trading day (17:00 -> 16:59 CT): legal.

User's report (01.2025-09.2026): NQ Block B $85,316 PF 1.55, Block A $67,829 PF 1.49, merged $153,145 PF 1.52, MSD -$29,830.

## Rebuild of Block B, 2018-2026 (`analysis/overnight_anomaly_test.py`, per NQ, $7.25 + 1 tick per fill)
Parity: 2025-01 -> 2026-09 205 trades, $409 a trade = ~$84k (report $85.3k). Disaster stop hit 3 times in 1,002 trades.

| per NQ | trades | avg | PF | t | years + | 2018-22 | 2023-26 |
|---|---|---|---|---|---|---|---|
| Block B (after down RTH) | 1,002 | $158 | 1.34 | 2.9 | 7/9 | $109 (t 2.0) | $224 (t 2.2) |
| every night long (control) | 2,182 | $90 | 1.20 | 2.7 | 7/9 | $56 | $135 |
| after up RTH days | 1,180 | $32 | 1.07 | 0.8 | 6/9 | $10 | $61 |

- Random nights, same count: Block B's mean beaten by 3.0% of 1,000 draws. Down-minus-up nights $126, t 1.85.
- Daily (zeros on flat days): Sharpe 0.98 / Sortino 1.43 / PF 1.34 / Calmar 0.88 / Ulcer 6.1 (every night long: 0.90 / 1.29 /
  1.20 / 0.80 / 7.7). 2023+: Sharpe 1.10 (bootstrap 5-95% 0.38-1.79, P(Sharpe <= 0) 1%), max DD $20,241 per NQ (rank 14%).
- Losing years 2018 (-$2.5k) and 2024 (-$4.7k). Long only (no short side to split).
- Monte Carlo at 1 MNQ: one-year block bootstrap p50 $1,621, P(loss) 12%, P(hit $2,000 EOD trail) 6.5%; at 2 MNQ 37%.
- Multiple testing: t 2.9 < bar 3.58; DSR 0.52. Same family as Overnight Drift / the 'premium after fear' result
  (Vojtko row): the condition is the known overnight long drift, concentrated after down days.

## Apex benches (`analysis/overnight_anomaly_bench.py`)
- Evaluation (combine set VB 8 + ONB ADX30 $1,100 + Bridge Monday 2 + EOS $500): pass 50.1% -> + Block B 1 MNQ 49.9%,
  2 MNQ 50.2%, 3 MNQ 47.6%; in place of Bridge Monday 49.1% / 48.7%. Median days to pass 6 in every case. No gain.
- Funded: see the bench output (added below when the bootstrap finishes).

## Block A at 9 MNQ (the user's challenge idea)
Stop = 0.30 x 15-day RTH ATR. At 9 MNQ one stop-out costs (median per year): 2018 $623, 2022 $1,743, 2024 $1,398,
2025 $1,858, **2026 $2,365** (max $4,437); every 2025-26 day above the $1,000 daily loss limit. One loss in 2026 is more
than the whole $2,000 trailing drawdown, and the block allows 4 trades a day. Fixed 9 MNQ is not viable; risk sizing (as ONB
ADX30 does at $1,100) is the minimum, and as an ONB replacement the OB v2 family already lost (50.2% -> 43.4%).

## Code notes
1. Block A: stop and target are set from the signal bar's close, not the fill (next bar open): slippage shifts the R:R.
2. Block A's overnight range resets at the first bar of the calendar date (00:00-08:30), not the 17:00 reopen.
3. Block B: `this bar on close` entries / exits are market orders at the bar close live (backtest fills at the close
   price exactly): 1 tick each way in our costs.
4. `Risk_Per_Trade_USD 2200`, `Max_Contracts 20`: on MNQ this sizes 1-2 contracts now but up to 20 when the overnight range
   was small (2018-19); cap `Max_Contracts` at the plan size.
5. `SetExitOnClose` on a 24-hour chart fires at the 16:00 session end, after both blocks are flat: harmless, not needed.
6. Shared position: the `MarketPosition = 0` / `OnrbPos` guards keep the blocks apart (no hedge possible).

## Verdict
Block B: a real but modest effect (the overnight drift, stronger after down days), t below the bar; C. It does not help
the evaluation and (pending the funded bootstrap) is not a plan change. Block A at 9 MNQ: no (a single stop can end the
account). Personal-account candidate for Block B at 1 MNQ; Apex use only if the funded bootstrap shows a gain.
