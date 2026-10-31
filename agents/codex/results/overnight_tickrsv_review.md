# Overnight TickRSV/VIX: WATCH; exact backtest needs source/data

Summary: The reported results are worth investigating, but the upload contains a description and screenshots only.
Screenshots report 547 longs, $211,405 net, PF 2.01 and $16,515 strategy drawdown; these are unverified claims.
Owned NQ prices and VIX exist; owned Bridge aggressor-volume fields are not established as the requested tick-direction input.
Obtain the PowerLanguage code, exact report/settings and original chart-field provenance before return testing.
No new strategy returns, account simulations, research caches, ranking or live changes occurred.

Plan: `agents/codex/plans/overnight_tickrsv_source_review.md` (source-review scope, not a return preregistration).
Evidence: `agents/codex/evidence/overnight_tickrsv.md` — NEEDS DATA.
Script: `analysis/codex_overnight_tickrsv_review.py`; output: `analysis/outputs/codex_overnight_tickrsv_review/summary.json`.
Return trials run: **0**. Screenshot arithmetic checks are not an independent backtest.

## Rule (as supplied, not tested)

The completed cash session is negative (09:30-16:00 ET close below open), and is not an early close. During
15:15-16:15 ET, accumulate chart UpTicks/DownTicks and compute `(up-down)/(up+down)`; invalid data blocks entry.
Long when negative TickRSV pairs with VIX above its completed daily SMA, or nonnegative TickRSV pairs with VIX
at/below SMA. Decision 18:00 ET, time exit 04:00 ET, fixed one NQ. No active stop or target. Optional disaster
stop and volatility sizing were disabled. The stated default SMA20 and selected SMA25 are distinct variants.

There is a plausible overnight long/reversal foundation, but neither a forced buyer nor a causal reason for
the selected interaction is demonstrated. Known overnight drift is already represented in prior OND research.

## Results supplied by the author

| Item | Screenshot claim / derived arithmetic |
|---|---:|
| Period shown | 2017-09-12 to 2026-07-07 |
| Trades, long / short | 547 / 0 |
| Net profit | $211,405 |
| Gross profit / gross loss | $420,280 / $208,875 |
| Profit factor | 2.01 |
| Winning trades | 59.96% |
| Mean net/trade, assuming described fixed 1 NQ | $386.48 |
| Max strategy drawdown | $16,515 |
| Max close-to-close drawdown | $12,820 |

Gross profit minus gross loss equals the reported net, and their ratio matches the rounded PF. This is an
internal consistency check only. The screenshots do not establish costs, bar fills, contract-roll treatment,
complete adverse excursions, exact inputs or reproducibility. Their $100,000 starting-equity curve differs
from the zero-start Monte Carlo P&L chart; do not conflate ending account balances with accumulated profit.
The displayed 1,649% return-on-account uses the platform's $12,820 required-account denominator, not the
$100,000 initial equity. These denominators do not establish a safe capital allocation.

The author explicitly reports "many tests," selecting SMA25, testing stop choices and volatility targeting,
and trying to improve the stagnant early period. This is extensively seen development history. A new test
cannot honestly call the author's 2023-2026 data untouched. The 2017-2019 stagnation could reflect a weak
underlying drift, few qualifying trades, interaction-regime mix, costs or later-period selection. The curve
alone cannot distinguish these explanations; annual trade lists and the four signal cells are necessary.

## Owned data and the actual replication blocker

- Local NQ minute day/overnight CSVs supply OHLC and total volume. The Claude branch additionally contains
  `data/NQ_1min_2017.csv` (remote blob metadata verified; no content replay here). Existing Grid24 is reusable.
- `data/VIX_daily.csv` supplies ample moving-average warm-up. Its dates alone do not certify the original
  Data2 completion and as-of alignment.
- Thirty-five `OF_1min_*.csv` files include upvol/downvol through 2026-07-07. Their exporter reads UpTicks and
  DownTicks from **The Bridge's synthetic bars**, documented as aggressive buy/sell volume. The uploaded
  description explicitly distinguishes its tick-direction proxy from true aggressor RSV. Matching field
  names are insufficient. Substituting these values would be a separately declared strategy, not replication.
- Header/endpoints were checked; complete flow windows were not certified. In particular, the June 2020
  part ends on 2020-06-30 at 10:11 ET, before that day's required afternoon window. No 2017 OF file was found
  in either inspected remote data directory. Original chart/feed and volume-building settings are needed.

Smallest next input bundle: **the actual PowerLanguage code and full exact-version MultiCharts Excel export,
including Settings and trades**. Record feed, symbol, session template, timezone, bar size and "Build volume on"
setting. If these do not match owned OF semantics, obtain the original chart's historical Date, Time,
UpTicks and DownTicks for the signal window, with interval and units recorded. No OHLC approximation is used.

## Execution and look-ahead points to settle first

1. Freeze actual SMA input20 versus25; retain the original selection history. Do not select the better one on
   the already-seen full sample and present it as independent validation.
2. Confirm which completed RTH session feeds each evening, especially Sunday/Friday and holiday/reset logic.
   Define five-minute endpoint inclusion: a bar stamped15:15 can include trades before15:15.
3. VIX finalized after16:00 may legitimately be known by18:00. The issue is actual publication/receipt and
   completed Data2 indexing; an unfinished daily bar or date misjoin can leak information.
4. An18:05 bar label may mark the bar whose open was18:00. It does not prove a five-minute fill delay. Native
   order creation versus IOG-off next-bar fills needs source and exact timestamps.
5. The "last RTH bar before15:00" early-close heuristic can confuse missing data with a shortened cash
   session. Futures bars are not automatically the cash calendar. Verify completeness and real holidays.
6. Continuous futures roll handling must match actual fills. The03:32CT artifacts noted in the repo are
   outside the stated03:00 exit; the17:01CT entry vicinity can coincide with a roll. Check actual contract/fill
   prices and define roll handling before returns; do not award synthetic roll profit.

## Monte Carlo and account scope

The roughly100 displayed paths are conditional resamples of a selected historical strategy. They do not
remove selection bias or establish out-of-sample survival. With fixed size, simple reordering of the same
complete trade list produces identical final P&L; differing endpoints imply replacement, varying paths or
another procedure. Obtain those settings. Closed-trade resampling also omits the intratrade risk of an
unstopped ten-hour futures position, margin pressure, missed exits and chronological portfolio breaches.

| Destination | Current status |
|---|---|
| 50K evaluation | Not run: exact signal/source and historical tick-field parity unresolved |
| 150K evaluation | Not run: same inputs missing; no result inferred from 50K |
| 50K funded | Not run: no validated ledger/MTM path for an addition, replacement or empty-slot control |
| 150K funded | Not run: same source/path limitation; no 50K scaling inference |
| Personal ladder/full portfolio | Not run: a promising standalone screenshot does not establish marginal portfolio value |

Clock clarification:18:00-04:00ET equals17:00-03:00CT. The builder brief's broad "no overnight" phrase conflicts
with the funded README explicitly allowing overnight-session trades closing before15:59CT; TIER_LIST also
calls a17:00-reopen-to-morning strategy Apex-legal. This proposal does not cross the daily flat deadline. It
must not be rejected solely for crossing midnight or silently converted to Sunday-only. Resolve the account
policy interpretation against the current documented rules before its account gate; no broker/VPS settings
were accessed. No active stop means historical drawdown is not a maximum-loss bound at any account size.

## Next decision

**WATCH / NEEDS DATA, not an edge rejection and not a completed backtest.** The exact-code/data gate is
concrete: reproduce the original fields, freeze a return plan, then run the cheap 2018-2022 screen and compare
incremental value against same-clock overnight/down-day/VIX/tick controls. At most five variants total;
recent history is replication of seen data; advance to chronological account comparisons only after gates.
The brief's explicit instruction is: "Only TEST sheets advance; NEEDS DATA / DON'T TEST stop here."

Reproduce this no-return audit with:

```bash
/workspace/venvs/thebeginning/bin/python analysis/codex_overnight_tickrsv_review.py
```

No strategy code, alternative-flow backtest, plan, allocation, live file, VPS, broker setting or API key changed.
