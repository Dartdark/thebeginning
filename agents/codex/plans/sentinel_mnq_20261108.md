# Frozen experiment: Sentinel-inspired MNQ intraday, 2026-11-08

User chose our own version and MNQ intraday. This is **not** the withheld KSE Sentinel rule or a replication of
its PSX returns. [Evidence sheet](../evidence/sentinel_mnq_20261108.md): TEST with low prior confidence.
Candidate/family ID: `sentinel_mnq_20261108`, broad OHLCV intraday trend family; all earlier failures remain.
Implementation: `analysis/codex_sentinel_mnq_20261108.py`. Commit this plan, evidence, exact code and no-return
inventory/synthetic fixtures before the first return run. No fitting, labels, tuning, risk/sizing searches or live edits.

## Rule, version 1 (one fixed candidate)

1. Instrument/economics: one MNQ ($2/point, 0.25 tick), prices proxied by owned NQ one-minute OHLC. All historical
   2018–22 micro economics are hypothetical; MNQ launched May2019. No source PSX risk tiers/portfolio rules transferred.
2. Only normal cash sessions; skip known holidays/early closes using existing repo calendar. Require complete valid
   minute OHLC paths 08:31–14:55. Excluded/unknown days stay listed, not assigned zero returns. At least95% normal-day
   coverage is required. Grid input is isolated to the tested years; design never reads2023+ prices.
3. Five-minute RTH bars:08:31–08:35,08:36–08:40,…,14:51–14:55 CT. EMA9 and EMA21 each seed at the arithmetic mean of
   the first9/21 closes, then recursive alpha2/(n+1). Reset every session. ATR14 is simple mean of current/prior13
   five-minute true ranges; first bar TR=high−low, subsequent TR=max(range,abs(high−priorclose),abs(low−priorclose)).
   Overnight price moves, prior-session EMA/ATR and known overnight roll jumps never enter a feature.
4. Allowed decisions10:15–14:00 CT inclusive, five-minute marks. Earliest usable EMA21 slope is10:20. Long requires
   current and preceding candles each close>open and close>their own EMA9, current close>EMA21, EMA21>priorEMA21.
   Short is the strict mirrored inequalities. Dojis/ties do not satisfy a test. Take the **first** qualifying signal
   per day, one trade at most; enter at next minute open. No reentry, reversal, scaling or profit target.
5. Fixed protective stop distance =2×signal ATR14, rounded upward to0.25 point, measured from entry raw open.
   Active on the entry minute. Shared `grid.execute` performs minute stop replay, gaps filling at the adverse open.
6. At subsequent five-minute closes, master is aligned only if current close remains on the trade's side of EMA21
   and EMA21 slope remains strictly in the trade's direction. If aligned, exit after **two consecutive closes** on
   the wrong side of EMA9. If unaligned, exit after **one close** on the wrong side. Candle-body color is irrelevant
   for exits. An exact EMA tie is not a wrong-side close; a flat master slope is unaligned. Exit next minute open.
   This is a causal first-observed trigger, never the most favorable later trigger. Stop through the decision minute
   takes priority; at next open a gap-stop and pending market exit both fill at that open. Shared-engine adapter
   explicitly converts a non-stop decision-close result into this next-open market exit.
7. If no earlier exit, flatten at14:55 CT minute close, far before15:59. No orders or position outside RTH.

## Economic hypothesis, clocks, costs and controls

Predicted gradual trend persistence; no identified forced flow or dollar demand. Need to beat net costs, a simple
price-trend rule and random-entry controls. Source reported PF/Sharpe are not acceptance thresholds or reproduced facts.
Information event/available_at/decision_time: completed local five-minute close. First fill: following minute's open
(bar close label minus1minute); indicator exit likewise. Scheduled close14:55 is a precommitted time market exit.
Historical OHLC has no measured feed/order latency; main model assumes immediate next-minute execution plus slippage.
Session-local recursive features are past-only. No learned model or label-maturity pipeline applies.

Main fee $1.24/MNQ round trip plus one adverse tick($0.50) each entry and exit: **$2.24/trade**.
Stress doubles both: fee$2.48 plus two ticks($1)/fill = **$4.48/trade**. No target/passive fills.
Report gross, fees, slippage, net and breakeven additional round-trip cost separately. Stop distance uses raw modeled
entry; adverse tick offsets are charged as P&L costs, not altered trigger levels. Costs do not scale from NQ commission.
Also show descriptive NQ units at $20/point, fee$7.25RT plus$5/fill, without using them to select/promote this MNQ version.

One prespecified **price-only baseline**: first decision in the identical allowed window whose current close is
beyond EMA21 with aligned EMA21 slope, ignoring candle bodies/EMA9 at entry. Same signal-time ATR stop, exit rule,
one-trade cap, calendar, costs and flatten. This tests the complete construction against generic momentum; entry
times differ so it is not an isolated matched-trade candle-filter attribution. Count baseline as a second economic
definition; no attempt to select it if the candidate fails.

## Splits, budget and stopping rules

Design2018-01-01–2022-12-31, input hashes/inventory committed first. Historical2023+ through last owned2026 date
is only earned after design and placebos; it is previously seen repository history, **not fresh holdout**.
One candidate + one baseline = **two economic definitions**. Cost stress is fixed-ledger accounting, not another
signal variant. No search or separate side selection; side/year rows are diagnostics. Failed gate ends this family.

Cheap design advancement requires **all**:

- >=300 candidate trades; positive native net; daily t>=2; PF>=1.10.
- >=4of5 design years positive; positive stressed net.
- Candidate total net greater than price-only baseline on identical eligible sessions.

If any fail: save full/long/short/by-year ledgers/metrics and cost bridge, label **REJECT**, and stop before placebos,
2023+, bootstrap/Monte Carlo, account comparison or PowerLanguage. A side that looks better does not rescue the whole.
Only if cheap screen passes, run1,000 random-side draws and1,000 random-time draws (seed7102818+i), each with the
same eligible signal-day universe, daily cap, causal exits and stop policy. Random-side keeps original first entry
time, chooses equiprobable side; random-time keeps original day/side, chooses uniform five-minute decision10:15–14:00
(EMA/ATR are already valid, slope need not be). These are conditional nulls using the observed signal day/side,
not deployable alternative policies. Recompute stop distance from each randomized entry signal. Add-one one-sided
P(total>=candidate)<=.05 for **both** is required; no null-seed selection.

Passing design+nulls earns unchanged recent historical validation with the same cheap criteria except >=3positive
years, then recent block-bootstrap/permutation/Monte Carlo on whole/long/short using repository tools. Promotion
still needs repository-wide multiplicity criteria, stability, independent checker/MC confirmation, native-data limits
resolved and useful actual-book comparison; this plan waives none. Independent agent work must follow the user's
session restriction (no delegation requested); an unperformed check remains pending, never claimed complete.

## Account stage only if earned

Likely overlaps VB, DT/PT/RS and Swing Target intraday momentum. Freeze then-current five rosters/versions before
bench, compare personal,50K/150K funded and50K/150K evaluation BASE/ADD1MNQ/REPLACE/EMPTY, with chronological
symbol-netting, executable risk and shared loss times; use bootstrapped funded/evaluation rules, payout/risk/timing.
No future side/size/roster choices are preapproved here. A failed standalone gate means **no place earned in any
of five homes**, not a measured portfolio loss or an account simulation. No live/broker/VPS changes.

## Audit and delivery

Save no-return inventory/coverage/synthetic fixtures; committed code SHA and plan commit; input hashes and dependencies;
eligible/excluded counts; raw decisions/fills/stops, reason and clock fields; daily-vs-trade accounting; whole/side/year
standard metrics (Sharpe,Sortino,PF,Calmar,Ulcer,maxDD,trade/dailyt), all failures and definitions. Independently inspect
sample raw minute paths and feature prefixes with no new economic variant. Save report and reproducible commands,
update the KSE queue with the distinct custom experiment outcome, commit/pull/push `codex/work`, and hand user report
path for Claude. PowerLanguage only after gates pass, following `MULTICHARTS_PITFALLS.md`.
