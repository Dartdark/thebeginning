# Uploaded XAUSTBreakFree on gold futures: TEST — requested fixed-rule personal-account screen

Summary: User explicitly asks to test the supplied gold strategy first; RSI/Bollinger is queued separately.
Use the uploaded default parameters without optimization, on owned GC minute data with overnight holds.
This is a GC futures adaptation, not a replication of the author's XAU-USD dataset or reported returns.
First gate: 2018–22 only, realistic costs/latency and actual source timing; no 2023+ until a pass.
TEST authorizes a bounded diagnostic screen, not promotion or live trading.

Source: user upload preserved byte-for-byte at `agents/codex/inputs/xau_st_break_free/uploaded.py`.
Video transcript previously supplied in chat; official Jesse reference commit
`9a3ebe075d9d0af5f012f921f46c2286f234af68`; `jesse-rust==1.3.1` in the configured Python environment.

## 1. Participant / mechanism

The economic prediction is persistent gold trends after a long-window breakout. The source identifies no forced
flow or independent inventory information. This user-requested price-rule replication is separate from new
forced-flow research; no institutional rationale or already established edge is claimed.

## 2. Direction, size, timing

Hourly close versus the prior 85 session-hour high/low, with four-hour Supertrend 24/4, EMA 10 and ADX 10 long /
15 short. Original six other exit defaults are frozen in the accompanying plan. The source stores its stop before
entry; it does not contain the RSI strategy's `qty*5` discrepancy. Source risk is 3% with notional caps, not a
guarantee against gaps. Use fixed one-GC P&L to screen the signal before evaluating personal-account sizing.

## 3. Direct market

GC directly trades gold, but differs from XAU-USD and tokenized/perpetual gold. Contract rolls, basis, trading
calendar, point value, costs and margin differ. No return claim is portable merely because both track gold.

## 4. Data / timing

Owned GC files include 2017 warm-up and overnight observations; metadata inventory is already committed in
`analysis/outputs/codex_rsi_bollinger_source_audit/date_time_inventory.csv`. No purchase or API key is needed.
Use Grid24 restricted to 2017–22 files, actual CT → UTC conversion, observed minute bars, UTC hour/4h buckets and
the source's New York session filter. No price data from 2023+ is read before a design pass. Preserve source hashes.
Literal `anchor[:-1]` can discard a newly completed four-hour bar at a boundary; replay that behavior, don't fix it.

## 5. Costs / gap

Repository baseline is $7.25 commission plus two GC ticks ($20): $27.25 per one-GC round trip. Charge this
conservatively on target exits too. Exclude no event because the plan is occupied. Multi-day positions make this
personal-account research, not an Apex candidate. Existing gold breakout entries and NQ trend exposure are the
relevant comparison families; no funded addition/replacement or roster change is proposed here.

## 6. Power

No candidate event count or SD is known before replay. As planning sensitivities, n=50/100 and SD=$1,000/$2,000
need approximately $283/$566 or $200/$400 net per GC trade for t=2, plus costs. These are assumptions, not observed
signals or expected performance. The reproducible screen will write the formula calculations and actual support.
Low support is a reason to stop rather than optimize thresholds.

## 7. Prior tests and falsifiers

Catalogue context: GC morning/Asian-range breakouts, generic Bollinger reversals and the six-market personal
trend study have already been examined. This exact supplied default class is not established by those results.
Reject further work if the fixed rule has no net design edge, inadequate support, dependence on a few trades,
or fails the predeclared execution controls; do not tune the author's search ranges or drop the losing side.

## 8. Failure / diversification

Chop produces repeated breakout failures; prolonged reversals can overwhelm a slow regime signal. Market entries
consume liquidity and overnight stops can gap. Short-only profit targets and different trailing distances make
the sides structurally different. Neither gold's label nor trend following establishes a hedge for the plan.
Joint loss timing and actual micro sizing would be later work after a pass. No live risk is authorized.

## Decision

**TEST — bounded user-requested diagnostic only.** Commit the execution/design gate before returns; account sizing
and possible forward paper tracking come after the edge/data gates. Positive continuous-series results alone
cannot verify rollover execution or establish a live-ready strategy.
