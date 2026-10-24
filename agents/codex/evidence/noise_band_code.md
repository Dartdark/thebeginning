# Uploaded noise-band / EMA / reversal code: NEEDS DATA

Summary: This price-based noise-band implementation belongs to an already-tested research family.
The exact source has no supplied instrument, timeframe/session settings, report, ledger or selection history.
Its default dollar stop consumes the nominal Apex trail, and several rules depend materially on the chart configuration.
Review the source only; do not treat related research as validation or begin another strategy test.

Source: unchanged `agents/codex/inputs/noise_band_code/source.txt` (user's CODE.txt).
Repo context: Claude `8f6b75cc1c6044f712c3ad5f1a774de60dd14859`; latest builder brief/development process apply.
New strategy-return trials: **0**; source author's trials: unknown.

## 1. Mechanism

Noise-band crossings with candle-direction gates imply an intraday momentum hypothesis. No participant mandate,
signed order flow or independent reason for sustained pressure is supplied. EMA exits and reversals are price rules.

## 2. Timing, direction and size known before order

Completed-bar closes determine signals and next-bar market orders. The intended decision cadence is unspecified.
Size is a fixed dollar budget divided by a nominal point stop and an input multiplier. No estimated flow dollars or
contract-volume share is supplied. The code anchors on calendar date change, not an explicitly named exchange session.

## 3. Transmission

The multiplier default suggests NQ, but the chart instrument is not declared. No proxy-flow connection establishes an
edge in NQ/MNQ or another contract. Changing instrument without reconciling its multiplier changes point distances.

## 4. Data and reproducibility

Need exact instrument, chart interval/timestamps, session/timezone, IOG/magnifier settings, inputs, costs, original
trade list and report. Existing repo caches are not rebuilt. No non-price input distinguishes this from ordinary momentum.
The historical array stores every eligible chart bar; a variable called LookbackDays does not guarantee daily sampling.

## 5. Costs and actual gap

No expected gross edge or actual fees/fills are supplied. The default stop budget exhausts the nominal initial trail
before transaction costs; the count of losing trades is not a cushion rule. Trading spans the same morning/afternoon
hours as several NQ plan legs, particularly Vault Break. That is potential overlap, not this code's measured correlation.
No candidate events are selected based on existing plan positions.

## 6. Power

Trade frequency, daily variance, sample coverage and within-day dependence are unknown. No t, DSR or numerical power
claim is invented. A later replication would need frozen rules and a declared opportunity-count/variance assumption.

## 7. Prior family and falsifiers

TIER_LIST already records noise-area momentum and the Chuk noise-band adaptation; prior paired account comparisons did
not establish improvement over the then-current plan. This code differs in anchors, history cadence, EMA rather than
VWAP, brackets and reversals. Earlier-family results cannot certify or refute it. Failed parity, unavailable chart provenance,
weak selection-adjusted evidence or no paired add/replace/empty-slot gain would prevent promotion.

## 8. Failure and diversification

| Issue | Concern | Evidence needed |
|---|---|---|
| Mechanism fails | Whipsaws and reversals instead of sustained momentum | Frozen exact-version results by period and side |
| Liquidity role | Market entries/exits pay spread; stops can gap | Timestamped fills and declared fees |
| Loss clustering | Several trades/stops can consume remaining cushion | Chronological integer-contract account paths |
| Shared loss | Possible same NQ momentum exposure as VB/ONB/RS | Joint losses measured on the exact source |
| Offset arrives in time | An annual correlation statistic does not prevent a breach | Netted account replay with intraday/daily limits |

## Decision

**NEEDS DATA**, with supplied default risk rejected for the current plan. Source comments/names and the attachment do
not authorize a live change or parameter repair. A future exact-source or corrected-source return test requires a separately
committed preregistration, trial counting, independent checking and current account gates; forward logging is discretionary.
