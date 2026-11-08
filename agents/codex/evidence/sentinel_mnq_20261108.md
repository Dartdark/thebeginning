# Sentinel-inspired MNQ intraday adaptation: TEST, one bounded user-requested experiment

Summary: The user explicitly selected our own version and MNQ intraday after the source-rule review.
This is an exploratory price-trend hypothesis, not an exact KSE Sentinel reproduction or a verified forced flow.
Owned NQ minutes supply 1,238 complete normal design sessions, 99.12% of scheduled normal sessions.
Freeze one rule and a simple trend comparator; reject at the cheap design gate before dependent tests.
No historical returns were examined when this sheet was written.

Source: [full paper review](../results/kse_sentinel_7102818_review.md), uploaded SSRN7102818;
[PDF/hash](../inputs/kse_sentinel_7102818/manifest.json).
User direction in this chat: “Build and test our own version”; market: “MNQ intraday”.
Return trials at admission: zero for this adaptation. Prior broad EMA/candle/momentum failures remain relevant.

## 1. Who trades, and what causes the trade?

Proposed, unverified mechanism: gradual information incorporation and persistent intraday directional demand
may let a trend continue after two confirming candles, while asymmetric exits retain longer favorable moves.
There is no identified mandate, forced participant, known dollar flow or independent nonprice predictor here.
The PSX author's claimed returns do not establish a CME edge. This is eligible only as the specifically requested
bounded experiment, consistent with the process allowance for supported trend research; it is low prior confidence.

## 2. Direction, size and timing known before entry

Five-minute RTH candles and session-local EMA9/EMA21, with explicit SMA seeds. Earliest fully usable master slope
is 10:20 CT. Two same-body-direction closes beyond their own EMA9, aligned with EMA21 position/slope, set side.
All information is available at the completed bar close; first fill is next minute open. No paper API or labels.
Fixed one MNQ, one trade/day at most, fixed two-ATR stop, no target; causal regime-dependent exits; 14:55 flatten.
Clock: exchange America/Chicago, already-local historical labels with DST; one-minute CSVs are close-stamped.

## 3. Does the mechanism reach the contract?

We trade index trend directly, without claiming PSX stock flows transmit to Nasdaq. NQ price bars proxy MNQ
prices at $2/point. They do not verify micro liquidity, spreads or broker fills; pre-May2019 observations are
explicitly hypothetical micro economics because MNQ did not yet exist. No cross-market empirical replication claimed.

## 4. New information and data feasibility

|Input|Owned source|Coverage/clock|Limits|
|---|---|---|---|
|OHLCV|`data/NQ_1min_2018.csv` through `2022.csv`|Complete 08:31–14:55 paths on 1,238 normal design days|NQ continuous, not native MNQ quotes|
|Calendar|`analysis/codex_s03_calendar.py` and existing early-close rule|Known holidays/early closes, no future prices used for trading eligibility|Ten early closes skipped by rule|
|Signal features|Past/current completed five-minute bars|All indicators reset each RTH session; no overnight warm-up|No independent information beyond price|

[Inventory](../../../analysis/outputs/codex_sentinel_mnq_20261108/design_inventory.json) includes raw hashes.
Eleven normal days have unresolved minute paths and stay excluded/visible, never zero-P&L dates.
Complete-path research exclusion is retrospective data-quality selection, not a live skip oracle.
EMA reset eliminates cross-session/overnight vendor roll jumps at known 03:32/17:01 clocks; no overnight holdings.
Unknown contract identity and any undocumented intraday roll remain limits. No fitting or revised macro data.

## 5. Costs and actual intraday gaps

Main one-MNQ cost $1.24 round trip plus $0.50 on each market/stop fill = $2.24/trade (1.12 points).
Stress $2.48 plus $1/fill = $4.48/trade (2.24 points). These are fixed research assumptions, not measured fills.
Two-ATR moves could exceed these costs; whether their signed expectation does is the actual cheap test.
No plan vacancy is asserted: the late-morning/afternoon window can overlap VB, Relative Strength, PAPERTREND,
Dual Thrust/Swing Target and Late-Day Flow. Test all eligible days first, not only days the book is flat.
Only a passing standalone candidate earns current-roster occupancy, joint-loss and account comparisons.

## 6. Power before returns

At most 1,238 independent-day observations; assumed $100/day MNQ standard deviation implies approximately
$5.68/day net mean for t=2, or $7.92 gross including main costs if every day trades. At 600 trades and
$100/trade SD, the naive per-trade hurdle is $8.16 net/$10.40 gross. These are illustrative assumptions,
not measured P&L; dependence, missed signals and multiplicity can raise them. Several-point sustained moves
make a bounded falsification informative; no prior power guarantee or significance exception is claimed.

## 7. Already tested and falsifiers

`TIER_LIST.md`: 20/50 EMA pullback failed (11,627 trades, t−1.2; best confirmation t1.3); Glow Ribbon failed;
T5 EMA/ADX and the MNQ OHLCV falsification study supply further negative priors. Hourly two-bar CHoCH is a
different structure-break rule with prior failed filters, not the original of this design. Kusho/PAPERTREND are
distinct related trend exposures. None is revived, retuned or renamed here; all selection history remains.
The incremental disclosed construction is two candle bodies beyond EMA9 and master-dependent exit strictness.
A simpler EMA21 trend comparator checks whether this construction adds anything to generic momentum.
Nonpositive net, weak daily t, year concentration, failure under costs or inferior baseline total falsify advancement.
No side-only rescue, parameter search, alternative timeframe, risk optimization or entry-clock search.

## 8. Failure and diversification

|Question|Prediction before results|Required evidence|
|---|---|---|
|Mechanism failure|Fast efficient repricing/mean reversion removes continuation|Net design edge versus costs and price-only baseline|
|Liquidity role|Small marketable entry/exit, stop becomes marketable|Actual quote/fill study remains unavailable|
|Loss clusters|Sideways whipsaw, false continuations and gaps through stops|Daily/side/year results first; account paths only if earned|
|Shared losses|Likely same-direction momentum losses with VB/DT/PT/RS|Unmeasured until common-date replay|
|Timely offset|No hedge or tail protection inferred from the trend label|Chronological symbol-netted account risk if earned|

Fixed one-MNQ exposure, no pyramiding, one trade/session, no target; protective stop starts on entry minute.
Unknown minute paths block replay. Stops can gap; neither two ATR nor a time exit caps executable loss.
The five homes are personal, 50K/150K funded and 50K/150K evaluation. No place is earned before standalone gates.

## Decision and next gate

**TEST** — explicit user-requested custom experiment with owned inputs and a single definition, not a paper-profitability
endorsement. Commit exact plan and code before returns. Cheap 2018–22 screen first, then only earned placebo,
historical 2023+ validation, independent review and actual current-book ADD/REPLACE/EMPTY tests.
