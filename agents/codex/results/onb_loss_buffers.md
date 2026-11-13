# ONB loss buffers: REJECT both additions; Overnight Tick is a limited historical lead

Summary: Tested two frozen reversal/overnight candidates against the current seven-piece evaluation book.
The heavy-night fade earns money alone but loses on recent ONB-loss dates and does not improve the book.
Overnight Tick earns +$3,709 at 1 MNQ on recent ONB-loss dates, but loses on the book's worst days.
Its recent fresh pass-rate gain is only +0.32 percentage points, band -0.11/+0.95; stressed gain +0.32, band -0.21/+0.85.
Neither clears the predeclared book gate. No new trading signal or allocation is justified by this run.

Plans: `agents/codex/plans/onb_heavy_night_fade.md` (0f467965), `onb_overnight_tick.md` (2e211db5).
Evidence sheets: matching filenames under `agents/codex/evidence/`.
Scripts: `analysis/codex_onb_heavy_night_fade.py`, `codex_onb_fade_book.py`,
`codex_onb_overnight_tick.py`, `codex_onb_buffer_checks.py`.
Outputs: `analysis/outputs/codex_onb_heavy_night_fade/`, `analysis/outputs/codex_onb_overnight_tick/`.

## Search and selection history

This is a targeted re-bench of existing frozen candidates, not a claim of two new discoveries.
Reviewed the registry before picking candidates. The recent active scan's `T_FADE` label actually loaded T_ONESIDE's
full T+OS trade list, so the early T-only fade was the first justified comparison. After it failed, checked existing
alternatives. Cash-session/Globex IBS holds across sessions; BB_MRM's MC evidence is weak in recent history;
NFP fade/CL Sunday fade are sparse and their old evaluation comparisons do not establish broad ONB protection;
FINRA already had little incremental gain after the latest NBL/LDF additions. None was silently revived or re-fit.

The second eligible candidate was Overnight Tick/VIX: existing A-grade MC confirmation and an already-seen stop-day
screen, with profits potentially realized before ONB. Earlier evaluation benches were near-neutral. That selection
history, the author's empirical interaction choice, old parameter searches and weak late-2026 trades remain part of
its evidence. Neither the conditional attribution nor 2023+ is a fresh out-of-sample discovery.

Return definitions run: T fade primary 1 MNQ, 2-MNQ size sensitivity, one-minute delay, all-night fade control;
OT primary 1 MNQ, 2-MNQ sensitivity, one-minute delay. Seven rule/size/control definitions across two existing families.
All original author and earlier repo trials remain counted. Book cases also include replacement and its empty slot;
no thresholds, sides or sizes were chosen on recent performance. No T or OT rule was retuned after failure.

## Rules and information clocks

**Heavy-night T fade:** known overnight move through the bar closing 08:29 CT, volume >1.4 times the median of
the prior 20 valid nights. Trade opposite that move, market at 08:29 wall clock; exit08:44. Stop 0.4 times the
previous 20 full-RTH-session mean range, active on entry bar, worse-open gap fills. Both sides. No OS momentum leg.
The one-minute-delay stress enters08:30 wall clock, keeps the exit/stop rule. Exact source timings, no clock search.

**Overnight Tick/VIX:** long after a down cash day if closing signed flow is negative with VIX>SMA25, or nonnegative
with VIX<=SMA25. Closing flow through15:15 CT and VIX close are known before entry17:05; exit03:00, no stop.
Friday signals enter Sunday. Uses frozen MC signals/report fill prices, not a newly fitted predictor.
One-minute delay uses the observed next minute open, same exit. All eligible nights, irrespective of ONB outcome.

Primary size1MNQ; both candidates pay **$2.275/MNQ round trip**, comprising assumed native commission/fees$1.275
plus one tick$0.50 on each market/stop fill. Tables of standalone results below are per MNQ; machine metrics use
per-NQ equivalents. Actual broker fees were not checked. Existing base cost conventions are retained; the prior
audit's Noise slippage omission and monitoring-size/uncapped-risk discrepancies remain review items, not silent changes.

## Standalone gates: both passed, neither alone establishes book protection

Common audit range2018-03-01 to2026-10-12. Design2018-22 first, then a single historical2023+ replication.

| Candidate | Design trades | Design net/trade/MNQ | Design t | Recent trades | Recent net/trade/MNQ | Recent t | Recent PF |
|---|---:|---:|---:|---:|---:|---:|---:|
| Heavy-night T fade |224|$18.51|2.76|129|$30.89|2.12|1.61|
| Overnight Tick/VIX |311|$26.68|3.48|238|$46.69|3.18|1.85|

Random-side tests, 1,000 draws with each side's own stop for T, same fixed holding times for OT:
T p0.002 design/p0.012 recent; OT p0.001 in each period (add-one empirical estimate).
T's all-valid-night control is weak: recent $2.22/MNQ, t0.54, so a blanket fade is not a substitute.
Recent delayed T is only $22.93/MNQ, t1.54; delayed OT $48.09, t3.27. Execution timing is a material T caveat.

Recent T longs72/$22.65/t1.10; shorts57/$41.30/t2.02. No side selected from this split.
OT is long only; the short sample is empty, not an unreported positive result.
Full win/PF/Sharpe/Sortino/Calmar/Ulcer/DD, costs, side splits, yearly totals, block bootstrap, DD permutation and MC
are saved in each output directory. Recent standalone Sharpe T1.06 (90% block band0.32-1.74), OT1.59 (0.97-2.35).

The T recent MC comparison has126 matching date/side entries of129 Python trades and130 MC fades;
all126 entry prices match,124 exits match. This is substantial but imperfect parity, not 100% verification.
OT uses the MC list directly; all549 retained design+recent entry and exit prices exactly match minute-grid opens.
No feature reconstruction beyond the owned OF data endpoint2026-07-07 is claimed for OT; later signals come from
the saved MC report. Neither strategy has new independent checker approval from this run.

## Does either help specifically when ONB loses?

Report conditional outcomes only after evaluating all signals; no candidate entry was selected by an eventual loss.

| At1MNQ, realized contribution | T fade2018-22 | T fade2023+ | OT2018-22 | OT2023+ |
|---|---:|---:|---:|---:|
| On ONB losing dates |+$178|**-$804**|-$205|**+$3,709**|
| Number of active candidate dates in that subset |37|23|48|41|
| Per ONB losing date (including inactive candidate dates) |+$1.02|-$5.25|-$1.18|+$24.24|
| On the base book's fixed worst5% dates |-$77|+$332|-$255|**-$832**|

For the168 recent dates where the base first crosses a close-marked -$2,000:

- T has a realized gain before the crossing on13 dates, loss on16, no completed trade on139; net **-$524**.
- OT has a realized gain before the crossing on25 dates, loss on18, none on125; net **+$2,717**.

OT is therefore the better limited historical loss-buffer lead. But it does not offset the worst-loss state, and its
ONB-loss contribution flips sign between design and recent periods. Do not label it a reliable ONB hedge.

## Does it improve the actual whole-book evaluation objective?

Frozen current roster: ONB risk$3,500, Monday Bridge5, Twin2, DT2, JF1, Noise longs3, LDF risk$1,000.
Same normalized base ledger as the prior joint-loss audit, source book a5aeffec. EOS/VB excluded.

Fresh account150000/floor146000/target159050,21sessions; stressed scenario147998.08/floor146000/target159050,
20sessions. The stressed balance is historical, **not a verified current balance**. DLL2000; EOD trail4000 with no
funded-account floor lock. Replays classify starts through2026-09-01;945 recent and1,247 design start dates.
Start-year labels describe account start dates; a21-session path can span a year boundary. Every case uses identical starts.

Recent results under source-compatible adverse paths with the Sunday cash correction described below:

| Case | Fresh pass | Difference vs base (90% paired band, percentage points) | Stressed pass | Difference vs base (band) |
|---|---:|---|---:|---|
| Base |42.96%|—|24.66%|—|
| +T fade1MNQ |42.86%|-0.11 [-0.32,0.00]|24.66%|0.00 [-0.32,+0.32]|
| +T fade2MNQ |41.80%|-1.16 [-2.86,+0.11]|24.13%|-0.53 [-1.16,+0.11]|
| +OT1MNQ |43.28%|+0.32 [-0.11,+0.95]|24.97%|+0.32 [-0.21,+0.85]|
| +OT2MNQ |43.39%|+0.42 [-1.48,+1.91]|24.66%|0.00 [-2.01,+1.69]|

Design changes for primary1MNQ: T fresh+0.08pt/stress+0.40pt; OT fresh0.00pt/stress-0.08pt.
OT fails both the no-negative-design-stress condition and the strictly-positive recent bands. T fails recent improvement.
Increasing size does not rescue either. Bands use2,000 paired60-day block draws, retaining clustered start outcomes.

Recent base failures55.87% fresh /73.76% stressed. +OT1 gives55.56% /73.76%; median days to pass8 /7.5 vs base8 /7.
These are conditional empirical simulations, not guaranteed probabilities or current-state forecasts.

Replacement chosen by2018-22 position-minute overlap, not P&L:
T overlaps JF most (238minutes vs DT227); replacing JF gives recent fresh42.01%/stress23.49%, below base and empty slot.
OT overlaps Monday Bridge most (8,046minutes); replacing Bridge gives40.42%/21.38%, materially below base despite
being better than an empty Bridge slot. That control prevents calling a replacement good just because it beats doing nothing.

## Common-price/clock sensitivities

Counter-direction positions must not be assigned different simultaneous NQ prices and called one portfolio mark.
Replayed a common-price high/low bound on actual17:00-16:00 sessions and a less conservative close-only model.

| Recent primary1MNQ difference (percentage points) | Canonical | Common-price session | Close-only session |
|---|---:|---:|---:|
| T fresh | -0.11 | -0.11 | -0.11 |
| T stress | 0.00 | +0.11 | +0.21 |
| OT fresh | +0.32 | +0.42 | +0.21 |
| OT stress | +0.32 | +0.42 | +0.11 |

No OT or T primary clears the required recent fresh-and-stress strictly-positive bands under these sensitivities.
Close-only OT stress risk even rises slightly; do not select a path convention because its point estimate is better.
Common-price intraminute lifecycle is still a bound; one-minute data cannot order every entry, exit, high and low.

## Accounting, checks and limits

- Rebuilding the base exposed12 Twin Sunday-evening exits left on Sunday by the shared grid and dropped when it
  selects weekdays. This research preserves them on Monday. All base daily totals reconcile to the audit ledger.
  The helper's original flat-exit marking was also corrected before the final replay to match the shared Twin method.
  No shared/live files were edited. These corrections are explicit, not presented as a new sizing benefit.
- All549 OT fills match minute opens. One design OT exit,2018-12-05 (US cash closure), is not in the audit's trading-date
  index: standalone sample311 vs310 in the account's design attribution. This difference is disclosed, not treated as a
  missing night or silently expanded account calendar. Source/no-stop overnight risk remains material.
- Standardized candidate fee assumption includes an extra$0.55/MNQ versus most historical base pieces. Gross, fees
  and slippage reconcile separately. No double-counted slippage or hypothetical stop-profit is used.
- T gaps through stops use the worse open; missing endpoint/intermediate bars are excluded/countable. OT exclusions
  are saved per period; there are no recent exclusions. Predeclared roll-screen heuristic is inherited, not fitted here.
- Validation independently recomputed gross/net, counts/t-statistics, ONB-loss attribution and every saved pass-rate
  difference from individual outcomes; both candidates have identical base outcomes. Validation is arithmetic/code
  checking by the maker, **not** the independent economic checker required before promotion.
- Historical parameter selection, reused recent years, incomplete MC parity for T, raw-volume field ambiguity,
  missing intraminute sequencing, prices after maintenance gaps and uncertain future edge remain limitations.
- Standalone Monte Carlo at1MNQ is not the combined book. Recent one-year EOD-only$2k-trail hit estimates:
  T0.2%,OT0.25%; at2MNQ T9.95%,OT17.8%. These omit intraday breaches and future regime changes, so they cannot
  replace the paired account replay or justify larger size. This library diagnostic uses its default capped-floor
  convention (lock at start+$100), not the continuously trailing150K evaluation rule used in the paired replay.

## Decision and work stopped at the failed gate

**T fade: reject for this ONB-buffer objective. OT: retain only as a limited historical lead; reject adoption as a proven
improvement to this evaluation book.** Neither passes the fixed book gate, so dependent funded-payout/implementation
tests and new forward-log promotion were not run. Underlying existing strategy grades and forward records remain unchanged.
No version was tuned to force an improvement; no live trading, VPS, account setting or plan allocation changed.

The search produced a concrete distinction: a strategy can earn money alone, and even earn money on ordinary ONB
loss dates, while still failing to protect the worst dates or materially change account success. No qualifying addition
was found in these two tests. Further discovery requires a separately supported hypothesis, not relaxing the gate.

## Reproduce

```
python analysis/codex_onb_heavy_night_fade.py design
python analysis/codex_onb_heavy_night_fade.py recent
python analysis/codex_onb_fade_book.py
python analysis/codex_onb_overnight_tick.py design
python analysis/codex_onb_overnight_tick.py recent
python analysis/codex_onb_overnight_tick.py book
python analysis/codex_onb_buffer_checks.py
```

Use Python3.11 with numpy,pandas,scipy,openpyxl,matplotlib. The supplied grid at
`C:/TradingVault/scratch_data/g24.pkl` is read only. Run manifests/gates record commits, input hashes, exclusions,
fees, seed20261113 and dependency versions. Full output grids are regenerated in RAM; no large caches are committed.
