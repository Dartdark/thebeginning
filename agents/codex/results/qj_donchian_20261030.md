# QuantJourney 55-day Donchian: WATCH — data/accounting blocked; no plan admission

Summary: A daily cross-asset trend example, structurally incompatible with all four Apex plans as written.
Published results claim CAGR 4.67%, Sharpe 0.30,DD 16.70% on $2 million; these are not our backtest results.
Verified reporting issue: open-position market values omit contract multipliers; the packet fails its own sanity checks.
No personal admission: contract-aware reconciliation and executable roll data are missing; no independent return trial ran.

Evidence: [NEEDS DATA sheet](../evidence/qj_donchian_20261030.md).
Plan: no strategy preregistration admitted; source/data gate did not pass.
Scripts: [audit](../../../analysis/codex_qj_donchian_audit_20261030.py), [report](../../../analysis/codex_qj_donchian_report_20261030.py).
Output: [arithmetic](../../../analysis/outputs/codex_qj_donchian_20261030/arithmetic_audit.json),
[timestamp inventory](../../../analysis/outputs/codex_qj_donchian_20261030/inventory.json).
Own return trials: 0. No parameter search, source-strategy return run, own 2023+ return run, portfolio simulation or MC code.

## Rule (as supplied, not a return replication)

Markets MES/MNQ/**CL/GC**, daily. Close above the previous 55 rows' highest high goes long; below their lowest low
goes short; otherwise retain the sign of the existing position. The current row is excluded from the channel.
ATR is a 20-row simple mean of true ranges including today's bar. There is no ATR stop or other protective exit.
An existing position persists until opposite breakout or target-size reduction, potentially for months.

Every day, recompute whole contracts separately for each market:

```
min(floor(0.005 NAV / (ATR × multiplier)),
    floor(0.25 NAV / (price × multiplier)),
    floor(0.15 NAV / reference initial margin))
```

Submit target-current quantity as a market order, after the daily bar closes. The archived public engine describes
next-bar execution and the source packet says open. Do not backfill an order at its signal-day close.
A pending active order skips that symbol. No fresh breakout is necessary for daily resizing. When size reaches zero,
the implementation has no retained directional state; it stays flat inside the channel until another breakout.
Reversals must count both closing and opening contracts. The ATR sizing fraction is **not a maximum loss bound**.

Source cost model: 1 basis point adverse fill price plus $2.50/contract/side with $2.50 minimum/order. Not tick-rounded.
Reference margins MES $1,584 / MNQ $2,100 / CL $7,000 / GC $10,000 are constants from the public registry, not live broker requirements.
The example models full-notional cash and an additional reference-margin cap; it explicitly omits dated rolls,
variation margin and current buying-power enforcement. Those omissions matter for a real futures account.

## Results — author claims versus our checks

| Metric | Published packet, 2019-05-06→2025-12-31 | Independent return replication |
|---|---:|---|
|Starting capital|$2,000,000|Not run|
|Total return|35.50%|Not run|
|CAGR|4.67%|Not run|
|Sharpe / Sortino|0.30/0.43|Not run|
|Maximum DD / Calmar|16.70%/0.28|Not run|
|Reported win rate / PF|48.00%/1.34|Trade analytics require reconciliation|
|Fill events / matched FIFO lots|978/852|Not independent directional bets|
|Average / median lot holding days|100.5/68|Overnight/multiweek rule confirmed in code|

These modest risk-adjusted returns do not justify promoting the example. Low reported SPY beta could be useful
for diversification, but it does not measure correlation or incremental contribution to our 19-piece personal book.
The screenshot says its curve was traced from a published chart; pixel paths are not a reproducible daily ledger.
The source uses a 2% risk-free rate; our standard zero-rate Sharpe is not directly comparable without recalculation.

### Verified accounting problem, without overstating it

The hosted [JSON](https://backtester.quantjourney.cloud/strategies/example-orders-20-futures-donchian-contracts/performance_report.json)
uses quantity×price in its open-position market-value field; contract multipliers are missing:

| Contract | Reported signed market value | Quantity×price×multiplier | Missing factor |
|---|---|---|---|
| MES | $130,957.50 | $654,787.50 | 5× |
| MNQ | $330,937.75 | $661,875.50 | 2× |
| CL | $-574.20 | $-574,199.98 | 1000× |
| GC | $4,325.60 | $432,560.01 | 100× |

Its separate margin/exposure table correctly incorporates multipliers. Thus a reporting layer can be wrong while
another layer is contract-aware. **This does not establish that the headline NAV curve is wrong.** It does prevent
trusting unreconciled position/FIFO/profit-factor diagnostics. Open P&L fields show the same multiplier omission.
The [text report](https://backtester.quantjourney.cloud/strategies/example-orders-20-futures-donchian-contracts/performance_report.txt)
also flags volume consistency 0.19 and failed sanity checks. Daily resizing can legitimately produce a FIFO-count
mismatch; that warning alone is not proof of an economic error. Realized/NAV profit gaps need opening/closing cash,
fees and remaining positions reconciled, not an assumption that every gap is invalid.

## Sizing and account placement

At the packet's **2025-12-31 prices**, a single contract needs NAV≥4×price×multiplier solely because of the 25% cap:

| Contract | Min NAV from 25% notional cap | Max contracts at $50K | Max contracts at $150K |
|---|---|---|---|
| MES | $137,850.00 | 0 | 1 |
| MNQ | $203,654.00 | 0 | 0 |
| CL | $229,679.99 | 0 | 0 |
| GC | $1,730,240.04 | 0 | 0 |

These are necessary bounds and upper quantity ceilings, **not actual allocated positions**. ATR/margin/direction
can reduce quantity further. They describe those prices, not every historical day or today's market.
The source's $2 million return/DD cannot be divided proportionally into a $10K/$50K/$150K strategy. Replacing CL/GC
with MCL/MGC, relaxing the cap or forcing daily liquidation defines a new strategy; none was silently tested.

| Current home | Verdict | Basis and benchmark status |
|---|---|---|
|50K evaluation|No place as written|Multiweek holds violate intraday boundary; no account bench run|
|150K evaluation|No place as written|Same rule mismatch; no inferred pass rate|
|50K funded|No place as written|Same boundary; no payout/blow-up/timing claims|
|150K funded|No place as written|Same boundary; no 150K payout comparison|
|Personal A–D/core/full|Unverified/data-blocked; no addition earned|Needs contract-correct cashflows/rolls and actual-capital BASE/ADD/REPLACE/EMPTY tests|

No independent whole/long/short, yearly, design/recent, t-stat or portfolio-return table is available; filling these
with the hosted results or an unadjusted splice backtest would invent validation. Current rosters were checked
against the existing [six-plan snapshot](../inputs/greenorb/plan_snapshot/manifest.json); nothing is changed.

## Data feasibility and why a new economic screen stopped

Owned OHLC exists for every market. A timestamp-only inspection of 2017–22 files produced:

| Market | 2018–22 session labels | First 17:01 bar present | 16:00 close present |
|---|---|---|---|
| ES | 1292 | 29 | 1248 |
| NQ | 1292 | 54 | 1248 |
| CL | 1289 | 1278 | 1248 |
| GC | 1291 | 1284 | 1251 |

These counts use an **assumed** 17:01 previous date → 16:00 session date CT aggregation. Raw CSVs have no contract or
timezone fields; this is not proof of the author's provider session or exact daily-open clock. Late first observations
and partial/missing sessions cannot be treated as verified next-open fills or silently compressed 55-session history.
Examples: all four 2020-11-30 sessions end around 18:00 the previous evening; CL 2019-08-21/22 are absent.
Most ES/NQ observed session starts lack the 17:01 close-stamped minute; filling at the first observed bar is an approximation.

The decisive carry-data limit is [NEW_CHAT_BRIEF](../../../NEW_CHAT_BRIEF.md)'s explicit statement that these
continuous series are unadjusted. They omit dated-contract identity and roll cashflows. A multiweek position spanning
a splice can acquire fictitious price-change P&L. Removing one roll minute does not recover the missing roll transactions.
No valid as-written multiweek carry return replication is supported by these exports alone. An intracontract or
roll-excluded partial study would answer a narrower question; silently truncating the position changes this rule.

Warm-up clarification: the stale shared checkout and codex branch lack NQ daytime 2017, but the file **does exist**
on pinned Claude 7a42ea (2017-05-01→12-29); [remote receipt](../inputs/qj_donchian_20261030/nq2017_remote_receipt.json).
We checked that before calling it missing. Its existence does not supply the executable roll chain, full overnight
history or the source's daily-data payload. No blanket claim that the repository lacks 2017 daytime is made.

### Exact source-engine access

The public v0.10.0 [source contract](https://github.com/QuantJourneyOrg/quantjourney-bt/blob/v0.10.0/backtester/core.py#L898)
establishes next-bar timing. The [SDK data path](https://github.com/QuantJourneyOrg/quantjourney-bt/blob/v0.10.0/backtester/mixins/sdk_client.py#L177)
shows `source=yfinance` still uses authenticated QuantJourney preparation. Public code is not the full hosted reporting
build; original data hash/payload is absent. We inspected public sources and free packet artifacts; no account access,
API-key lookup, paid data or synthetic-sample substitution was attempted. The missing artifact is research data/code,
not permission to access live trading or credentials.

## Verification performed and retained lessons

**17 checks PASS**, using reviewed pure definitions on synthetic arrays/inert order stubs. They cover
ATR column alignment/simple averaging; invalid inputs and the three independent sizing caps; 55 prior-row channel
exclusion; daily carry/resizing; zero-position direction loss; reverse-order quantities; pending-order handling;
and all four published multiplier omissions. No `_credentials`, `main`, Backtester engine or authenticated API ran.
These checks validate specific mechanics/arithmetic, not profitability or an economic replication.

The [run manifest](../../../analysis/outputs/codex_qj_donchian_20261030/manifest.json) hashes original code,
selected source facts, archived public files, scripts and outputs. The source's 2019–25 results are already seen;
any subsequent test remains historical validation with family selection history, not a pristine holdout.

Prior family: TIER_LIST's weekly six-market momentum and Turtle review, plus the public-repositories Donchian baseline
review, already describe related approaches. A 55-day rule is not a new forced-flow mechanism. Missing inputs alone do
not establish a promising strategy, so this example is retained as an accounting/execution reference rather than a
duplicate promising-alpha queue entry. Any future economically warranted personal test must be preregistered after
the data gate; no scout reservation, trial history or automation was changed.

Smallest justified next check: reconcile a closed lot for each market and aggregate contract-weighted realized/open
P&L, fees and daily NAV; then obtain a dated-contract roll ledger. Only after that, freeze a single actual-capital
personal definition and perform the cheap design screen. Do not optimize a screenshot or scale its CAGR mechanically.
Execution lessons retained in [EXECUTION_REFERENCES.md,E09](../EXECUTION_REFERENCES.md).

## Differences between MultiCharts code and the test

No MultiCharts implementation or new historical return test was produced because the input gate failed.
No live/VPS/broker/plan settings, credentials, ranking or allocations were changed.

For Claude: review `agents/codex/results/qj_donchian_20261030.md`, especially multiplier diagnostics versus headline NAV.
