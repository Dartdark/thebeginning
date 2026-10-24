# GC_COMBO_v2 evidence sheet: NEEDS DATA

Source-only review. Sources: uploaded research note pp. 1–5, community source and synthetic daily input, archived
unchanged under `agents/codex/inputs/gc_combo_v2/`. Audit: `analysis/codex_gc_combo_v2_review.py`; no new returns.

## 1. Who trades, and what causes the trade?

Author proposes a five-vote 10:00 ET gold blend (price continuation, tick-rule flow fade, prior GLD holdings change,
large prior CL move, extra price vote in a dollar-decoupled regime) plus a below-VWAP short. ETF hedging/liquidation
are hypotheses, not observed forced orders. Price A and the conditional E repeat the same direction. Tick-rule B
does not identify actual market-order aggressors. The note itself leaves the mechanism open (p. 1).

## 2. Direction, size and timing known before entry?

Source specifies clocks and signs, but not an executable estimate of forced dollar demand. The supplied Data3 file
encodes dates/flags, not raw GLD changes, dollar observations, construction rules or publication timing. Its artificial
05:00 bar is not a publication timestamp. Need dated input definitions and generator, including what “yesterday” means;
unrecoverable historic vintages should be disclosed, with lag stress reserved for a separately registered exploratory
replication. No future-information leak is demonstrated by this review.

## 3. Does the order reach the traded market?

GC is the research signal market. GLD creations involve bullion and possible futures hedges, but the package does not
measure what reaches GC or when. CL/dollar signals are proxies. Moving Data1 from GC to MGC also changes the UpTicks/
DownTicks and VWAP input, so executing smaller contracts is not automatically the same signal rule. State the signal
instrument and execution instrument separately before claiming parity.

## 4. Data that distinguishes flow from momentum/reversal

GCCOMBO contains 2,605 weekday flags from 2016-10-03 through 2026-09-25; formulas/provenance are absent. GC tick-rule
split and CL minute data are required. The checked repo GC CSV has only date/time/OHLC/total volume, so it cannot
faithfully reproduce vote B. The supplied daily flags are available for research, but their maintenance/source cost and
availability after September 25 are unknown. Do not fill missing votes with zero and call it the five-vote strategy.

## 5. Costs and an actual portfolio gap

Author reports $2.30 per GC side plus a tick per side; two such ticks plus commission total $24.60 for one GC round
trip. Net means are author-reported, not reconstructed. Main blend decides at 09:00 CT and enters next bar to 12:30 CT, overlapping the plan's
morning risk; Stretch can trade 07:20–14:00 CT and normally exits 15:00 CT. A gold position might diversify NQ, but its
joint losses and timing relative to an account breach are unmeasured. The note's Lucid Flex result and other NQ strategy
are not our paired Apex benchmark. Verify on all eligible events before measuring overlap, not just currently flat hours.

## 6. Power and selection

The note's 2018–22 annual counts sum to 670 trades, but net-return variance is not supplied: a t=2 test needs net mean
at least `2 * sd / sqrt(670)` under the elementary iid calculation; a credible numerical hurdle cannot be completed yet.
The author discloses 10,831 programme trials and a failed DSR, with claimed sealed 2025–26 evidence of 230 trades,
$288.98 average and only t=0.9 in gross bp. The original frozen marks/ledger are missing. A positive reported mean does
not clear our independent selection/promotion gates. Its seen 2023+ history is not a fresh holdout for a new variant.

## 7. Already tested, and what differs?

No exact GC_COMBO/GCCOMBO/five-vote entry was found in the latest pinned TIER_LIST/WATCHLIST. Gold Asian breakout is
C/parked; ordinary GC VWAP/LBMA/settlement and other flows have prior weak results. Those findings do not decide this
different composite. Its daily flags and tick-rule blend are the material differences; they need source verification.

## Failure/risk and decision

Blend defaults to no stop. Optional historical-move sizing is not a guaranteed loss cap. Exact-clock exits lack early-close
handling, and stale Data3 silently drops C/E instead of stopping. Main reported drawdown scales arithmetically to about
$4,375 at the same 1–2 MGC counts, before actual micro fees; this is not an Apex hit probability or measured MGC replay.
Gold may share macro shocks with current NQ/ES positions, so no timely protective offset is established.

**NEEDS DATA.** Obtain the Data3 generator/dated inputs, GC up/down-volume history and exact-source MC export/settings,
plus the original freeze/selection evidence. Keep the current plan unchanged. No silver test, stop change, vote removal,
sizing selection, new backtest or funded bench is authorized or run by this review.
