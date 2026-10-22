# Review: Antigravity's "Vault Break Combined" (HYP-025) and the Time & Price campaign

Claude, 2026-10-21. Reviewed: `tasks/CLAUDE_COMPREHENSIVE_REVIEW_DOSSIER.md` on `antigravity/jesse` (commit 6f6ed54).
Independent rebuild: `analysis/anti_vb_combined_test.py` (output `analysis/outputs/anti_vb_combined_test_output.txt`),
on our Vault Break rebuild (`candidates24.vault_break24`, 1,742 trades 2018-26, vs MultiCharts' 1,743 and the dossier's 1,744).

**Verdict: don't adopt.** The two filters don't improve Vault Break once they leave the window they were chosen on.
Live VB stays unchanged. TIER_LIST: D.

## 1. Parameter stability and overfitting (the main question)

| Per NQ, our costs | 2018-26 t | 2018-22 t (design) | 2023+ t (holdout) | 2023+ $/yr | 2023+ max DD |
|---|---|---|---|---|---|
| Base VB | 3.78 | 2.71 | **2.66** | **$19,794** | $13,906 |
| Window (decisions <= 12:30) | 3.71 | 2.90 | 2.41 | $16,669 | $14,280 |
| Stretch <= 0.50 ATR | 3.89 | 2.88 | 2.66 | $19,097 | $13,462 |
| Combined | 3.95 | **3.21** | 2.46 | $16,370 | $13,550 |

- **Better on the design years, worse on the holdout.** The 2023+ Sharpe, profit and t are all below the base. The dossier's
  holdout gate checked only that the combined version's t stayed >= 2.5. It never compared it with the base on the same
  years.
- **The removed trades make money.** Decisions after 12:30: 351 trades, +$36 each (t 0.9). Stretch > 0.5 ATR: 186 trades,
  +$63 each (t 1.0). Both filters together remove 481 trades worth +$20k. The dossier says these groups lost money
  (−$551 and −$2,354). That isn't reproduced.
- **The drawdown cut is no better than chance.** Dropping the same number of base trades at random gives a median max DD
  of $13,571. The filtered max DD is $13,550 (P = 0.50). The paired bootstrap of combined minus base gives a DD
  difference of −$1.7k, but the 90% range is −$8.3k to +$3.7k, and the annual P&L difference is −$962
  (−$3.9k to +$1.9k).
- **Cliff, not plateau.** On 2023+ (grid B) the t rises steadily the later the cutoff, so the runway cut hurts. Stretch
  caps of 0.25 and 0.35 drop the t sharply (3.95 to 3.49 to 2.89), and the max DD jumps around between neighbouring cells
  (13.6k / 15.2k / 10.9k). That is what a single-path statistic looks like, not a structure.
- With the dossier's own costs the DD reduction is **5%** ($14,686 to $13,950), not 26.7% ($17,204 to $12,609).
- **Search count.** HYP-023, 024 and 025 each touched the holdout, and the combined version was built after both single
  versions had been seen. With ~28 logged hypotheses (and their variants) the multiple-testing bar for the CHANGE is
  t >= 2.9 to 3.3. The removed trades' t is +1.1 in the wrong direction.
- **Arithmetic error in the dossier.** $12,609 per NQ at 2 MNQ ($4 a point = 1/5 of NQ) is **$2,522**, not $1,260.90
  (that is 1 MNQ). That is above the $2,000 trailing limit. Monte Carlo on 2023+ at 3 MNQ: P(hit the $2,000 EOD trailing
  within a year) is 49% for the base and 46% for the combined version. Neither is "well below" the limit.
- Our own earlier test (TIER_LIST 'Time clusters', ~170 cells, 2026-10) also found no entry half-hour worth cutting.

## 2. Execution friction

- $17.25 commission + 1 tick a fill is more conservative than our $7.25 + 1 tick. For MNQ, check the real per-micro
  commission x 10: per NQ-equivalent it can sit nearer the dossier's figure than ours. It changes the level, not the
  ranking (section A of the output prints both).
- What matters more than the commission is the **target fill model**. A +40 limit should fill only when price trades
  through it (we require 1 point beyond). Touch fills overstate a high-win-rate system. The dossier doesn't say which it
  uses.
- 1 tick on the 75-point stop is fine on average, but stops cluster in fast markets. Our live log on 2026-10-20 and 10-21
  shows 8-MNQ stop-outs at exactly −75.00. Keep comparing live fills (`live_vs_backtest.py`).
- Next-bar market entries at 10:00-14:00 CT on NQ: 1 tick is realistic. Our limit-entry test (TIER_LIST) showed market
  entries are the right choice.

## 3. The "4 governing microstructure laws"

I don't agree with treating them as laws. They are stories written after four results, three of which are "filter
failed in-sample". The simpler reading of the evidence is that time and stretch filters don't improve any of the four
strategies, VB included once it is tested on the holdout. Notes on each:
- LDF: leveraged-ETF rebalancing is proportional to the day's return (Cheng & Madhavan), not to the distance from VWAP.
  "Stretch caps remove the flow" is plausible but untested as stated.
- ONB: "delays cost the trend runners" fits the 09:00 result and is a reasonable prior. It is not a law.
- Monday "institutional dip-buyers" and VB "institutional supply zone above 0.5 ATR" are just-so labels. The VB one is
  contradicted by our data: stretch 0.5-0.75 ATR trades average +$106.
- Useful as priors for pre-registering future filters, not as conclusions.

## 4. PowerLanguage code review (the dossier's NQ Vault Break Combined)

Not ready to run. It does not implement the tested rule:
1. **`AvgTrueRange(15)` on a 30-minute chart is the ATR of the last 15 thirty-minute bars** (tens of points), not the
   15-day daily ATR (~300+ points). The noise band and the stretch cap would be ~10x tighter: a different strategy. Use
   the per-date true-range array in `apex_strategies/NQ_Vault_Break.txt` (or a daily Data2).
2. **No stop or target during the entry bar.** The exits are only sent while `MarketPosition > 0` at a bar close, so a
   position opened at the bar's open is unprotected for its first 30 minutes. That differs from the backtest and is a
   live risk on Apex. Use `SetStopLoss` / `SetProfitTarget` (with `SetStopContract`), plus our Rithmic stop guard
   (`VB SG`).
3. **The trade counter misses trades.** `MarketPosition <> 0 and MarketPosition[1] = 0` doesn't see a trade that opens
   and closes inside one bar (like the 12:30 trade on 2026-10-21), so `MaxEntriesPerDay` can be exceeded. Count with
   `TotalTrades` as our VB does.
4. **No holiday half-day handling.** On 12:00 CT closes a 12:30 entry or the 14:30 flatten can't happen, so a position
   could be carried into the halt. Use our `IsEarlyClose` list.
5. No ATR warm-up guard (entries before 15 days exist). Volume on tick-based charts should use `Ticks` (as ours does).
   The midnight reset fires twice (23:30 and 00:00) but ends up anchored the same as ours. That is harmless but
   untidy.
6. No `NumContracts` input and no Trade Logger tag.

Lookahead: entries are `next bar at market` on bar-close values and IOG is off, so the code itself has no intrabar
lookahead. The mismatch with the Jesse logic is the ATR definition and the entry-bar exits, not lookahead.

## What would change the verdict

A pre-registered forward test: from 2026-11, the trades the filter would have removed average below $0 over >= 150
trades (about a year), with the paired-bootstrap DD difference below 0 at 90%.

## Addendum: SundayReopenPush (HYP-018) and Vault Break Short (dossier commit 2a3df6a)

- **SundayReopenPush is our WATCHLIST #22** (the user's NQ_WKND_v2, rebuilt in `analysis/sunday_reopen_test.py` on 2026-10-18).
  The numbers match ours: $179 per NQ, t 2.5, 171 reopens. It is not a new discovery and not uncorrelated evidence.
- **The holdout gate means nothing here.** Only 9 of 167 trades fall in 2018-22 (the 17:00 minute is missing from those
  exports), so there is no design period to hold out from.
- **The core problem is the fill, not the statistics.** The gap direction is read from the first print, and the trade
  enters AT that first print. Any order sent after the open is seen is late. Our check (2 ticks + $14.50 a trade):
  enter at the 17:01 close and hold to 17:02 −$39 (t −1.5), to 17:15 +$10 (t 0.2), to 17:30 −$34; enter at 17:05 and
  hold to 17:15 +$25 (t 0.7). The dossier's "15-minute hold peaks at +$40,950" is the same first minute plus noise.
- The only way to get that price is an order in the pre-open auction, with the side taken from CME's indicative opening
  price. MultiCharts' bar-close signals can't do that; it would be a manual order. WATCHLIST #22 stands: log the
  indicative price, your fill and the first print for ~20 Sundays before any money goes on it.
- Their Jesse code's `go_long` buys at `self.price` (the bar's close in Jesse), so it may not even trade the first print.
  The ledger's prices are the bar open. Check which one the 167 trades actually used.
- **Vault Break Short (HYP-019/020): F.** We agree. Design t 3.11, then 2023+ −$13.4k with a $36k DD: a filter picked in
  sample. The "structural asymmetry" story is post hoc again.
