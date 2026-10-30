# QuantJourney stop-limit protection: REJECT as a plan candidate; retain execution reference

Summary: This is an educational daily-ETF order example, not demonstrated futures alpha.
Published CAGR 1.99%, Sharpe 0.02, DD -14.18% are author results, not our backtest.
Eight executed synthetic scenarios reproduced delayed protection, a lost bearish exit and stale protection state after rejection.
A stop-limit can remain unfilled through a large gap; its sell-price floor does not cap the position's loss.
No new return trial or account comparison passed the evidence gate; no place earned in any of the five homes.

Evidence: [pretest sheet](../evidence/qj_stop_limit_20261030.md). Plan:
[execution-only diagnostic](../plans/qj_stop_limit_mechanics_20261030.md), pretest commit `7ae772d845a100f203ae5d352a99ec9361383cf6`.
Code: [mechanics harness](../../../analysis/codex_qj_stop_limit.py), [report](../../../analysis/codex_qj_stop_limit_report.py).
Outputs: [scenario traces](../../../analysis/outputs/codex_qj_stop_limit_20261030/synthetic_results.json),
[run receipt](../../../analysis/outputs/codex_qj_stop_limit_20261030/run_receipt.json),
[zero-return-trial ledger](../../../analysis/outputs/codex_qj_stop_limit_20261030/trial_ledger.json).

## Four source questions

1. **What is it about?** A QuantJourney daily-bar educational example for SPY, QQQ and IWM shares. Enter when
   SMA20 crosses above SMA50, allocate 15% of NAV per new position, then submit a sell stop-limit with trigger 4%
   and limit 4.5% below the average entry. A bearish crossing submits a market exit when its branch is reached.
   This is code/documentation, not an academic paper; the author explicitly does not present it as optimized alpha.
2. **What does it find?** The screenshot and public packet report +63.64% over January 2001–December 2025,
   CAGR 1.99%, excess-return Sharpe 0.02 and -14.18% DD. Those figures were
   checked against the published packet, not independently reproduced from market data. Our own evidence is
   eight synthetic order tests, including three implementation hazards, not a new profitable backtest.
3. **Why could it make money?** Long US equity exposure during SMA uptrends can participate in market gains.
   No forced participant, independent flow input or incremental alpha is identified. A stop-limit changes which
   prices can execute, at the expense of sometimes failing to execute; it does not create a positive edge or a
   bounded loss. Positive nominal dollars over 25 years are insufficient evidence of useful excess return.
4. **Can we build on it?** Retain the execution lessons, but **do not pursue a new strategy or add it to a plan**.
   Four intraday futures homes do not accept this daily ETF-share strategy as written. A personal ETF sleeve is
   possible in principle, but useful incremental contribution is unverified and this source does not earn that stage.
   No SMA optimization, futures substitution or stop-market rescue is justified by this example.

## Published results: source evidence, not independent replication

| Published statistic, 2001–2025 | Value | Evidence |
|---|---|---|
| Total return | +63.64% | Author packet/screenshot |
| CAGR | 1.99% | Author packet/screenshot |
| Sharpe / Sortino | 0.02 / 0.03 | Author packet; configured risk-free rate 2% |
| Maximum drawdown | -14.18% | Author packet/screenshot |
| Trade events / closed long round trips | 379 / 188 | 379 is not the independent closed-trade count |
| Average closed holding period | 77.2 days | Author packet |
| SPY total return | +693.52% | Full exposure; not a risk-matched comparison |
| Average gross exposure | 25.35% | Author packet |
| Configured costs | 5 bps one-way; $0.005/share, minimum $1/order | Source settings, equity units |

The reported 379 trade events comprise 191 buys and 188 sells; the closed sample is 188 long round trips and zero shorts.
Selling a long is an exit, not evidence of a short strategy. The average holding period is 77.2 days, so this is
not an intraday candidate. Full SPY exposure and average 25.35% strategy exposure are unequal; underperforming SPY
alone is not a fair risk-matched alpha test. Nevertheless Sharpe 0.02 relative to the packet's 2% risk-free rate
is weak positive evidence. No current-portfolio benefit can be inferred from these statistics.

The dashboard's 3.99% volatility is a rolling-window value; its run log reports 4.91% full-sample annual volatility.
Those are different statistics. We do not replace either with an independently calculated estimate.
The supplied configuration uses $100,000 initial capital, 5 bps one-way slippage and equity commissions of $0.005/share,
minimum $1/order. Do not translate percentage allocations or these fees directly to native MNQ/MES contracts.

Primary sources:
[public example packet](https://backtester.quantjourney.cloud/strategies/example-orders-08-stop-limit-protection),
[structured source report](https://backtester.quantjourney.cloud/strategies/example-orders-08-stop-limit-protection/performance_report.json),
[pinned strategy](https://github.com/QuantJourneyOrg/quantjourney-bt/blob/4f403d853833e1daa6de01c5b6c6cb3983dc0044/strategies/example_orders_08_stop_limit_protection.py).
The public report was generated 2026-07-11 and inspected 2026-10-30. Archived
[claims](../inputs/qj_stop_limit_20261030/published_claims.json) preserve attribution.

## What we actually executed

Pinned public source: QuantJourneyOrg/quantjourney-bt commit
`4f403d853833e1daa6de01c5b6c6cb3983dc0044`, current public version 0.12.5. The packet names 0.10.0+private;
we did **not** establish version parity with that historical engine. The canonical upstream strategy class matches
the pasted logic; source hashes and Apache license are archived. A disconnected base supplies feature tables and
average entry prices. AST extraction executes only the strategy class. The four reviewed pure execution modules
(orders, fill engine, slippage, commissions) run unchanged; the SDK/API package initializer, credential helper,
source main and simulator/core are not executed. Core/simulator source was inspected to confirm scheduling.

The reviewed public simulator fills prior pending orders before calling the strategy after each daily close.
An order submitted at that callback first becomes eligible on the next daily bar. There is no source entry-fill
hook to arm an attached protective child during the entry bar. Our delayed-protection result applies to this
explicit schedule; it is not a claim that every stop-limit implementation has this delay.

| Scenario | Actual synthetic behavior | Interpretation |
|---|---|---|
| Entry protection | Buy fills at $100.05; entry bar reaches $90 before protection is submitted | Separate daily callback leaves entry day unprotected |
| Bearish crossing while arming | Only stop-limit submitted; previous signal becomes 0; next bearish callback sends no market exit | The one-off bearish crossing can be lost |
| Gap below sell limit | Stop $96/limit $95.50 triggers; prices $90 then $80 leave 100 shares unfilled | Limit price is not a maximum-loss guarantee |
| Recovery after trigger | Later recovery fills 100 shares at $95.50, $1 commission | Gross price bound respected; net proceeds $95.49/share |
| Protective-order rejection | Rejected stop, no pending order; protection flag staysTrue; no next-callback retry | Boolean does not reconcile actual order state |
| Ordinary bearish exit | Existing stop is cancelled, market sell of 100 shares queued | Expected ordinary transition works |
| Partial protection | 10 shares fill, 90 remain; cancel stop remainder and queue market sell of 90 | Actual remaining quantity retained in this sequence |
| Stop-out above SMA | No immediate reentry; a new down/up crossing later queues a buy | This is the declared crossover rule |

All eight assertions reproduced their predeclared expectations. **That is a diagnostic success, not a safety PASS.**
Prices/dates in fixtures are invented, not observations of those dates. The rejected-order reason is injected;
no broker rejection frequency is estimated. Partial fills in scenario 7 use a 1% prior-volume participation cap
to expose the state transition; this is not the source's historical fill rate or a new strategy variant.

The bearish-exit issue is stronger than a one-bar delay: the `elif pos>0 and not has_stop` branch submits the
stop and then saves the new bearish signal. If the next signal remains bearish, `prev` is already 0, so the
market-exit branch does not fire. The normal bearish transition works after protection is already flagged.
Likewise, `_has_stop_limit=True` is set after submission without checking rejection status. In the forced
rejection fixture, no actual protective order remains, yet the next callback sees the flag and does not retry.
These are source/harness implementation findings; they do not quantify financial damage in the published run.

## Why no new historical return or portfolio test ran

The pretest evidence sheet is **DON'T TEST economic returns**: this is a generic SMA/order demonstration with
weak reported excess return, no new economic mechanism, direct account incompatibility and unresolved exact
historical engine/data provenance. The instruction to backtest uploads does not bypass that evidence gate.
The completed work here is source verification and executed execution-mechanics tests, **not a return backtest**.

A bounded owned/free check was still completed. No verified owned SPY/QQQ/IWM OHLC set was found. The existing
`data/SPY_daily.csv` is close-only with index/futures-scale numbers, so it was not treated as native ETF prices.
Yahoo's public SPY chart request returned a proxy-tunnel403; that endpoint was not retried or bypassed. A public
GetPriceData repository contained scripts but no archived CSV panel. QuantJourney's credential-free sample data
are deterministic generated prices, so they cannot validate historical profitability. No fictitious opens/highs/lows,
missing returns, guaranteed limit fills or futures proxies were manufactured. See the
[access receipt](../inputs/qj_stop_limit_20261030/access_receipt.json).

No 2018–22 design return series, 2023+ validation, confidence interval, random-return placebo, Monte Carlo return
simulation, native fill saving or independent raw-spec economic check exists for our work. Their values are
unavailable, not zero. A new future question would need a distinct justified hypothesis and its own complete
evidence/preregistration; this review is not an invitation to keep optimizing these SMA periods.

## Explicit placement in all five homes

Read-only plan sources refreshed at Claude `7ce07ece525fa16e95ac2221a27521d317b2b05c`:
[snapshot manifest](../inputs/qj_stop_limit_20261030/plan_snapshot/manifest.json).

| Home | Verdict | Measured account contribution |
|---|---|---|
| 50K evaluation | Ineligible as written: daily ETF shares and multiday holding | Not run |
| 150K evaluation | Ineligible as written: daily ETF shares and multiday holding | Not run |
| 50K funded | Ineligible as written: daily ETF shares and multiday holding | Not run |
| 150K funded | Ineligible as written: daily ETF shares and multiday holding | Not run |
| Personal portfolio | No eligible addition earned: weak source evidence and unsafe protection assumptions | Not run; no BASE/ADD/REPLACE/EMPTY claim |

No ADD/REPLACE/EMPTY benchmark was earned. Lack of admission is not measured harm to all five portfolios.
No baseline payouts, pass rates, blowup rates or personal-capital changes are inferred from ETF daily returns.
No shared plan, ranking, live strategy, account setting, key, VPS or automation was modified. No PowerLanguage
or platform installation was attempted. Independent verification remains pending.

## Retained reference and next action

Save the order lesson in [EXECUTION_REFERENCES E36](../EXECUTION_REFERENCES.md#e36--stop-limit-protection-price-control-is-not-a-loss-cap),
cross-linked to E03/E05/E18. A stop-limit exchanges execution certainty for a price constraint; protective-order
state must follow actual acknowledgements/status, and a fill-to-protection gap must be explicit. No new execution
policy was installed. No TODO promising-strategy entry: missing inputs and educational examples alone do not
establish merit for that queue. **Move on as a strategy candidate.**

Reproduce the finite mechanics and report from repository root:
```
/workspace/venvs/thebeginning/bin/python analysis/codex_qj_stop_limit.py
/workspace/venvs/thebeginning/bin/python analysis/codex_qj_stop_limit_report.py
```
For Claude: `agents/codex/results/qj_stop_limit_20261030.md` — source/order review; eight synthetic groups;
zero economic return trials or current-portfolio simulations. Do not describe it as independently backtested alpha.
