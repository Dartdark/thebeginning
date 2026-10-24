# S03 Noise Area v2: TEST the declared OHLC reconstruction

Summary: Test whether the supplied fixed 0.4-sigma stop improves this already-known noise-band family.
Owned NQ minute prices and volume support a bounded reconstruction; no independent tick/source parity is claimed.
The bulletin reports positive selected history, but the stop sweep, walk-forward and recent decay are already seen.
Commit four fixed profiles and a design gate, then run 2018-22 before recent/account tests.

Sources: archived `inputs/s03_noisearea/source.html` (SHA256
`05a176b0c4f6804d48d427ad484175076d125a61b62122736c34c6797c0d2b52`), extracted text and source/prior reviews;
`TIER_LIST.md` noise-area/Chuk rows; `analysis/intraday_research.py`; latest builder/workflow/template.
Local return trials before this sheet: **zero**. Author reports at least12 StopSigma values and other prior work;
their supplied full-sample/2019-26 claims are not independent unseen validation.

## 1. Who trades, and what forces or causes the trade?

Price continuation beyond a time-of-day historical mean absolute displacement, confirmed by VWAP. The source
attributes profit to trend days; no measured forced order, mandate or dollar imbalance exists. The incremental
hypothesis is risk control: a fixed protective stop may cut failed breaks before trend days recover the losses.
It must be tested with a matched stop-off replay, including changed re-entries, not attributed to new flow data.

## 2. Direction, size and timing known before entry

Use only the previous14 completed full cash sessions' absolute close/open return at the same minute. Upper and
lower use max/min(today open, previous cash close); entry confirmations and trailing exits occur every30 minutes
from10:00 through15:30ET. Orders fill the next observed minute open. Stop distance is0.4*raw sigma*signal close,
rounded toward entry and active on the fill minute. Flatten from16:00ET (15:00CT), next-bar fill normally15:01CT.
All rules/one-NQ research size are known before returns. No forced-dollar-demand estimate is available.

## 3. Direct contract

NQ prices and total volume directly supply the signal; actual account results use MNQ at one tenth the NQ point
value while preserving price geometry. The header's LucidFlex assumptions are not the user's Apex account rules.

## 4. New information and data feasibility

| Input | Owned source | Feasibility / limits |
|---|---|---|
| Minute OHLCV | Existing `scratch_data/g24.pkl`, Dec2017-Oct2026 | Reuse; no cache rebuild; native missing bars stay missing |
| Noise features | Prior14 full cash days at each clock | Shift before today; past completeness can be checked only after past close |
| Calendar | Existing early-close logic plus deterministic cash holidays/mourning | Preknown calendar; never skip current day using its future missing prices |
| Author source | HTML only, references unavailable PL signal/engine/OFB prices | Freeze reconstruction choices explicitly; cannot certify exact author parity |
| Stop path | Shared one-minute OHLC executor | No tick data; source itself says stops lack tick validation |

Primary uses actual09:30 cash-open price from the09:31 end-stamped minute, minute typical-price/total-volume VWAP,
previous cash-session close including legitimate half-day close, and14 past complete normal sessions. A single
09:30-bar-inclusive anchor sensitivity is registered; no selecting the better clock. Inputs cost$0.

## 5. Costs and occupancy

Source reports about$112/NQ/trade at$15 total costs; our fixed standard is$7.25 commission plus one tick at each
market/stop fill, normally$17.25. This difference alone does not settle a selected historical edge. Both sides
overlap morning/afternoon NQ; Vault Break is the prespecified replacement slot. Exact minute overlap and joint
losses belong to account-stage tests, never selection of flat-plan days. Protective stops can occur in the fill
minute and market gaps can exceed planned risk; average exposure is not an offset before a trailing breach.

## 6. Power

Author's roughly275 positions/year suggests1,000-1,500 design trades, not independently counted yet. If net trade
SD is$1,000, t2 requires around$52-$63 mean; at$1,500 SD it requires$77-$95. These are explicit assumptions.
Clustering/tail dependence reduces effective evidence. A cheap gross-versus-cost screen can pass in principle;
no parameter sweep is needed to find out. Report realized side/year counts and uncertainty without retuning.

## 7. Prior tests and falsifiers

The family was tested as long-only "Beat the Market" and Chuk noise bands. Their commissions, entry confirmations,
trailing exits and clocks differ, so historical quoted averages are not matched controls. Reconstruct the new
rule once, then switch only StopSigma0.4 to0. If net/Sharpe/DD, recent replication, placebos or portfolio marginal
contribution fail, reject the corresponding claim; do not choose a new stop, clock, direction or weekday.

## 8. Failure and diversification

| Question | Prediction before results | Evidence needed |
|---|---|---|
| Mechanism fails | Choppy sessions stop repeatedly; a few missed trend days erase gains | Year/side results, tail concentration and fixed stress |
| Liquidity role | Marketable entry/exit and stop orders, no passive edge asserted | Fill/gap timing and executable fees |
| Loss clustering | Low win rate and repeat breakouts consume the trail before a trend winner | Chronological paths, stop sequences and paired account bootstrap |
| Shared losses | Long NQ overlaps VB/RS; shorts may diversify or fail on rallies | Minute occupancy and conditional joint losses |
| Offset timing | Future trend wins cannot repair an earlier breach | Realized adverse path and account-state simulation |

One position at a time, fixed entry stop, no profit target, daily time exit. Data gaps and unclosed holds are
audited; no synthetic prices, silent trade removal or future-data current-session filtering. At account stage
compare BASE, ADD, REPLACE_VB and EMPTY_VB in all four Apex destinations plus the current personal ladder.

**TEST** the clearly labelled reconstruction. Exact source/tick parity remains open and blocks live promotion;
it does not prevent this authorized research test on owned data.
