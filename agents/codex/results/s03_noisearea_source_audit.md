# S03 Noise Area v2: source audit, before reconstruction

Summary: The uploaded bulletin specifies a runnable NQ noise-band strategy but does not contain its cited PowerLanguage signal or Python engine.
The default is a 14-session band, half-hour checks, VWAP confirmation, and a fixed 0.4-sigma entry stop.
Its source-author results and parameter sweep are already-seen historical claims, not independently reproduced evidence.
Exact replication needs the original engine/data; a frozen reconstruction can state the small implementation choices listed below.
No repository market prices, signals, cached returns, or new backtest results were inspected for this audit.

## Artifact and extraction

- Upload: `S03_NoiseArea_v2_Bulletin.html`, 375,875 bytes; SHA-256 `05a176b0c4f6804d48d427ad484175076d125a61b62122736c34c6797c0d2b52`.
- Visible text: `agents/codex/inputs/s03_noisearea/source_extracted.txt`; extracted with Python's standard-library `HTMLParser`, omitting script/style content and image payloads. The HTML and its JavaScript were never executed.
- Three script elements: an inert `application/json` dashboard dataset, dashboard-rendering JavaScript, and a Cloudflare challenge script. There are no `pre`/`code` elements, downloadable signal/engine links, or embedded PowerLanguage/Pine/Python implementations. External links are font resources; navigation links are document anchors.
- The bulletin cites `s03_engine.py`, an author's PowerLanguage `SIGNAL`, and `ofb_bars_NQ.csv`; none is supplied as code/data by this HTML. Its embedded JSON contains author-generated trade/daily/curve arrays. Their structures were inventoried, but their individual values were not inspected or used for selection.
- JSON metadata, author summary/header claims, and author sweep/walk-forward claims were read as source assertions. Those claims are already-seen evidence and cannot create a new holdout.

## Rules explicitly stated by the source

Market: one NQ futures contract, $20/point, tick 0.25; one-minute OHLCV in New York time, close-stamped, unadjusted continuous. Source interval: 21 May 2017 18:01 through 7 July 2026 20:00 ET; 3,210,351 bars. It claims 2,354 RTH sessions, with 2,271 full sessions, 81 holiday/early-close exclusions, and two data-gap sessions. First trade is 12 June 2017 after 14-session warm-up.

For each RTH minute `t`, `sigma[t]` is the mean of `abs(close[d,t] / rth_open[d] - 1)` over the last 14 **full** sessions preceding today. `rth_open` is described as `open(09:30)`. Let `O` be today's RTH open and `PC` the prior close:

```
upper[t] = max(O, PC) * (1 + sigma[t])
lower[t] = min(O, PC) * (1 - sigma[t])
```

`BandMult=1.0`, `Lookback=14`, `CheckEvery=30`, `VwapConfirm=true`, `StopSigma=0.4`, `Qty=1`. Signal checks occur only at close-stamped 10:00, 10:30, ..., 15:30 ET (09:00, 09:30, ..., 14:30 CT). Strict inequalities:

- Long when `close > upper` and `close > VWAP`.
- Short when `close < lower` and `close < VWAP`.
- An opposite signal reverses the position.
- At those same checks, exit a long when `close < max(upper,VWAP)`; exit a short when `close > min(lower,VWAP)`.
- Orders decided at bar close fill at next bar open. The source describes its 16:00 ET flatten decision as filling at the 16:01 ET open (15:01 CT); for close-stamped minute data that is the bar covering 16:00–16:01 ET.
- The protective stop distance is `0.4 * raw_sigma[signal_time] * signal_close`, measured from the entry price, with the stop active on the fill bar. Long stop is entry minus distance; short stop is entry plus distance. It is an intrabar stop, not a check-time-only exit and not a moving sigma stop.
- Exact rounding wording: “Stops round to the tick nearest the entry (the conservative side).” A natural explicit implementation is `ceil(long_raw_stop / .25)*.25` and `floor(short_raw_stop / .25)*.25`, keeping the stop toward entry.
- Source costs are $5 round trip plus one tick per side: $15 total per NQ round trip. Repository-standard NQ costs are higher ($7.25 plus the same slippage); label both schedules if a source-cost comparison is shown.
- “Exchange holidays, early closes and two mourning days are skipped.” Two source data-gap dates, 28 February and 30 June 2020, use `SetExitOnClose` instead of the scheduled flatten.

## Minimum assumptions to freeze before any return calculation

These are omissions in the bulletin, not implementation facts established from its absent code. They can be resolved once in the preregistration, without optimizing them against outcomes.

1. **RTH bar anchor.** With close stamps, the 09:30 ET cash-open price ordinarily comes from the 09:31 ET bar's open. Use that explicit convention rather than a bar covering 09:29–09:30. The source's `open(09:30)` wording does not resolve this on its own.
2. **Prior close.** State whether this is the immediately preceding eligible/full RTH session's 16:00 ET close or the immediately preceding exchange session's RTH close even after an excluded holiday/half-day. Do not substitute the overnight/session-settlement price silently.
3. **VWAP.** Source gives no formula or anchor. Freeze session-reset VWAP from cash open through the current close using a named price input (for example `(high+low+close)/3`) and observed volume. State zero-volume behavior. Close-only and typical-price VWAP are different reconstructions, not a supplied author default.
4. **Full-session eligibility.** Freeze exchange holiday/early-close calendar, mourning dates, required coverage, exact-minute missing-data policy, and rolling-history eligibility. Do not interpolate a missing check bar or count an incomplete day among the 14 full-history sessions silently. Distinguish past-day completeness, known after its close, from current-day entry eligibility: do not erase a current day's earlier trades because a data gap is discovered later that day. Calendar exclusions can be known before the open; runtime gaps need explicit handling as encountered.
5. **Order priority and state.** State gap-through-stop fills at the worse open, stop versus pending next-open exit/reversal priority, no pyramiding, same-check reversal handling, and whether a position stopped intrabar can reenter from that bar's close check. A fixed entry stop applies to each new/reversed position.
6. **Entry basis and slippage.** Freeze whether the stop anchor is the clean next open or the actual slipped fill. Count slippage/commission per filled leg, including reversals, without double charging a separate shadow trade.
7. **Missing flatten bar.** Source's exceptional `SetExitOnClose` depends on its MultiCharts session template, which is absent. Freeze a conservative last-observed-tradable-bar fallback for incomplete sessions and record those dates. The two cited source dates must not be assumed to be the same gaps in another data vendor's history.

The absence of source code bars an exact bar-for-bar claim. It does not prevent an explicitly labeled reconstruction with these frozen choices. Missing original `ofb_bars_NQ.csv` also bars explaining the author's four-trade residual solely with rounding; source-vendor bars, roll treatment, calendar, VWAP and order semantics may all differ.

## Author claims and selection history, not independently verified

The bulletin's own engine claims 2,493 positions, net $278,225, daily Sharpe 1.33, Sortino 1.79, PF 1.35, 29.6% wins and max drawdown $22,295. It describes author-header v2 as 2,497 positions and $283,100 net and attributes the residual to stop rounding. Its no-stop v1 has 1,919 positions. Exact-price stops purportedly yield 2,476 positions and approximately $285.5K, versus the rounded result.

The embedded source sweep contains **at least 12 already-tested settings**: `StopSigma = 0, .2, .25, .3, .35, .4, .45, .5, .6, .7, .8, 1`. The bulletin calls .35–.6 a plateau; this is full-sample author evidence, not an independently preregistered local search. It separately describes anchored yearly maximum-daily-Sharpe selection using all preceding data. The displayed chosen settings are 2019 .4, 2020 .45, 2021 .4, 2022 .7, 2023 .45, 2024 .4, 2025 .4, 2026 .5. It claims stitched 2019–2026 net $225.6K / Sharpe 1.20 versus fixed .4 $237.0K / 1.27. The original reason for selecting .4 and the total author trial count are not supplied.

Other reported fragility is material: since July 2024 PF 1.22, or 1.11 without April 2025; top ten positions are 43.5% of total net; 56% of positions exit via stops, including 132 stops in the entry minute. Longs are reported at $167K / PF 1.49; shorts at $111K / PF 1.24 with crash-year dependence. The source's full-horizon trade-resampling conclusions and LucidFlex sizing examples do not establish repository Apex account fit or a future loss probability of zero.

## Data and execution limits to carry into the result

- One-minute OHLC can model an entry-bar fixed stop with adverse gap rules, but cannot establish tick path, queue/fill quality, latency or stop slippage on headline days. No tick validation is supplied.
- Unadjusted continuous prices can distort prior-close gaps at contract rolls. The source identifies this concern but supplies no contract/roll schedule, roll-adjusted sensitivity, or original raw contract identifiers.
- Historical source sample runs through July 2026 and its parameter sweep uses the full sample. Local 2023+ comparisons must be called historical replication, with a genuinely frozen forward log for any future decision.
- Source LucidFlex account terms are third-party summaries and differ from this repository's account assumptions. Do not copy source sizing, payout claims or recommendation into the Apex plan.
- The rule is price-based intraday trend following; its obvious overlap is Vault Break/noise-band momentum. The source supplies no forced-flow identification, new causal evidence or plan-level diversification calculation.
- Before promotion, use repository costs and tools, longs/shorts and year splits, matched-exit placebos, concentration checks, and the authorized account/overlap workflow. No strategy conclusion follows from this source audit alone.
