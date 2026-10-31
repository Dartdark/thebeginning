# VIX ETP basis switching: WATCH — positive limited historical proxy

Summary: Tested the available 364 sessions, September 7, 2016–February 15, 2018, with actual XIV and VIXY replacing VXX.
The frozen next-open rule earned +63.3% net on $100,000 reference cash, with −35.2% peak-NAV drawdown and 29 positions.
Doubling both source cost terms leaves +33.3%; buy-and-hold XIV and VIXY lose 85.2% and 69.3% respectively.
One February 2018 VIXY position supplies 75% of total net profit; the rule had exited XIV before the collapse.
Positive short proxy sample, not exact paper replication, a current strategy, independent verification or a portfolio admission.

Plan: [frozen protocol](../plans/vix_etp_available_period_2753300.md), committed `dd13fac` before returns.
Script: [replay](../../../analysis/codex_vix_etp_available_period_2753300.py), implementation committed `0fea48b` before returns.
Output: [summary and hashes](../../../analysis/outputs/codex_vix_etp_available_period_2753300/summary.json).
Trials: four registered economic definitions, plus one zero-cost accounting counterpart; all five reported below.
Final reporting-code commit `17c9dab`; year-boundary reporting correction `9769355` changed no trades or parameters.
Source, paper claims and acquisition receipts: [review](vix_etp_2753300.md), [intake](vix_etp_acquisition_2753300.md).

## Rule as tested

Front VX is the earliest monthly ISO-dated expiry strictly after each decision date, excluding expiry-day final settlement.
After confirmed daily settlement and spot VIX close, basis = (front settle − spot close) / spot close.
From cash, buy XIV above +8%, or VIXY below −8%; otherwise retain cash. Hold XIV while basis >=+6%;
hold VIXY while basis <=−6%. Exit outside the holding band; switch directly only if the opposing entry threshold is crossed.
Execute at the next regular ETF session Open. Old holdings bear the overnight gap. No hedge, leverage, stops or daily rebalance.
Start flat; first eligible fill September 8. Forbid new final-session entries and liquidate any remaining shares at the final Close.

Invest all available $100,000 reference cash using fractional split-adjusted research shares, not native integer broker quantities.
Both legs are long ETP shares: XIV is economically short volatility, VIXY long volatility. VIXY is a disclosed proxy for VXX,
not a continuation of the original note. XIV is not extended beyond the available actual history or into a synthetic modern product.
Each buy costs Open×1.0015×1.002; each sale receives price×0.9985×0.998. Fee 0.20% and spread 0.15% apply each side.
Stress doubles both terms. No borrowing, futures multipliers, NQ commissions or interest credit are inserted.

## Results

Returns are compounded NAV changes over this entire partial period, not annual returns. Drawdowns use running peak NAV.

| Registered definition | Net return | Max drawdown | Positions | Daily-return Sharpe |
|---|---:|---:|---:|---:|
| Fixed switching | +63.26% | −35.24% | 29 | 0.94 |
| Buy and hold XIV | −85.17% | −96.48% | 1 | See machine output |
| Buy and hold VIXY | −69.26% | −84.34% | 1 | See machine output |
| Switching, doubled costs | +33.27% | −37.02% | 29 | 0.64 |
| Zero-cost accounting counterpart | +100.01% | −33.40% | 29 | 1.22 |

Zero-cost and costed accounts buy different quantities as expenses reduce capital. The correct primary cash bridge is:
$83,149.47 gross trade P&L − $11,364.32 commissions − $8,523.43 spread = **$63,261.73 net**.
Do not subtract the primary expenses from the separately compounded zero-cost counterpart.

Standard repository metrics use daily dollar P&L, not percentage returns. Leg numbers attribute the actual shared account's
P&L to its held product; they are not separately capitalized replays. Dollar drawdown and percent drawdown differ once NAV changes.

| Metric | Whole | XIV / short volatility | VIXY / long volatility |
|---|---:|---:|---:|
| Positions | 29 | 26 | 3 |
| Win rate | 55.17% | 57.69% | 33.33% |
| Net P&L | $63,261.73 | $36,545.51 | $26,716.22 |
| Average net / position | $2,181.44 | $1,405.60 | $8,905.41 |
| Trade t statistic | 0.98 | 0.89 | 0.46 |
| Daily-dollar Sharpe | 0.80 | 0.79 | 0.42 |
| Sortino | 1.41 | 1.03 | 0.98 |
| Trade profit factor | 1.76 | 1.59 | 2.29 |
| Calmar | 1.24 | 1.11 | 0.75 |
| Ulcer index | 14.69 | 9.55 | 17.83 |
| Max dollar drawdown | $35,236.74 | $22,755.95 | $24,502.79 |

Per-NQ units do not apply to ETP shares. Whole daily-dollar t is 0.96. These are descriptive statistics without an independence claim.

| Calendar slice | Net P&L | Slice NAV return |
|---|---:|---:|
| 2016, September 7–December 30 | −$33,591.37 | −33.59% |
| 2017, full year | +$59,376.06 | +89.41% |
| 2018, January 2–February 15 | +$37,477.04 | +29.79% |

Annual returns use the previous year's last NAV as the starting base, including the first session's P&L.
2018–22 design and 2023+ validation: **not available/run**. The 2018 row above is only the early partial sample.
The source paper's June 2006–April 2014, 69% annualized result is **not reproduced** by this different period/product/fill protocol.

### February 2018 exposure and concentration

The January 29 basis was −2.276% (front settlement 13.525, spot 13.84), below the XIV holding threshold.
XIV exited at the January 30 Open, 125.21. No subsequent XIV entry occurred in this sample.
February 2 basis was −9.734% (15.625 versus 17.31), selecting VIXY at the February 5 Open.
That position exited February 13 and earned **$47,424.75 net**, **74.97% of the entire strategy's net profit**.
The other two VIXY positions lost $15,436.10 and $5,272.43. The ledger therefore shows this particular rule avoided
holding XIV during the February 5 collapse; it does not establish reliable crash anticipation or general tail protection.
VIXY fill prices are split-adjusted research units; interpreting them as contemporaneous per-share dollar prices would be wrong.

## Placebos and account level

Buy-and-hold controls and doubled costs are the registered comparisons, not randomized timing/side placebos.
No post-result placebo, parameter search or rescue variant was added. The sample is below the frozen 100-position
admission gate, and XIV is terminated: no promotion, forward claim, MultiCharts implementation or portfolio allocation follows.
Apex requires intraday flattening; this overnight ETP strategy does not fit. BASE/ADD/REPLACE/EMPTY and current-plan
account simulations are not supported by these inputs and were not run. Personal-plan placement remains unestablished.

Existing repository bootstrap: 5,000 resamples, 10-session blocks, seed 2753300. The 90% daily-dollar Sharpe interval
is **−0.25 to 2.06**, including zero. Daily-dollar Monte Carlo uses the same block/seed and 252-session horizon:
5th/median/95th P&L −$22,079 / +$42,456 / +$119,567; conditional loss frequency 14.06%.
These resample a short, changing-capital historical dollar series; they are neither a forecast nor independent validation.
They cannot establish crash probability, survival at another size or an Apex trailing-breach probability.

## What could make this wrong

- Only 364 sessions and 29 positions; one winner drives most profit, and there is no fresh holdout or independent review.
- XIV is a secondary public historical table, not audited exchange prints. Matching all VIXY session dates establishes
  coverage, not transaction-price accuracy. Exact VXX and the paper's prelaunch synthetic history remain missing.
- Native front-contract settlement and next-session ETF Open avoid same-close look-ahead, but daily Opens are price
  references, not guaranteed achievable fills, depth, halt or impact models. Settlement availability is assumed before next regular Open.
- Positive finite front settles were checked in this 2016–18 window; this does not resolve earlier archive anomalies.
- Fractional split-adjusted shares, no cash yield and a large reference account do not establish integer sizing or current capital needs.
- The endpoints follow available XIV coverage and include a known crisis. No claimed untouched selection, hedge optimization or multiplicity clearance.

Synthetic tests cover strict thresholds, signal/fill lag, overnight loss before exit, double-sided switches, costs and the final-entry guard.
All five actual panels pass trade-to-daily P&L, gross-minus-expenses, daily leg attribution, decision-before-fill and final cash-flow reconciliation.
A separate aggregate check reconstructed terminal cash from signed fills. Independent economic verification remains pending.

## Reproduction and saved evidence

Run `python3 analysis/codex_vix_etp_available_period_2753300.py selftest`, then `run` from the repository root.
The runner requires committed plan/code, preserves every panel, records exact input SHA256, plan/script hashes, code commit and dependency versions.
Raw acquired prices and the complete input snapshot remain local under `/workspace/vix2753300_acquisition/`; repository outputs
retain transformed basis/expiry signals and derived fill/trade/daily ledgers. Input hashes and intake sources permit source reconciliation;
a fresh checkout needs those acquired raw files, not just the script. There are no MultiCharts/live implementation differences to compare because none was written.

## Five paper-review answers after this test

1. **About:** switching long ETP holdings between short- and long-volatility exposure using front-futures/spot basis hysteresis.
2. **Finds:** this limited causal XIV/VIXY proxy earned +63.3% net, with −35.2% drawdown; original paper statistics remain source claims.
3. **Why money:** the proposed mechanism is short-volatility carry in contango with exposure switched during backwardation.
   Our measured gains come from both legs and are heavily concentrated in one VIXY trade; that does not prove the mechanism persists.
4. **Build on it:** retain as WATCH research only. A modern product needs a separately justified payoff/lifecycle protocol and longer matching data;
   these results earn no current plan placement or automatic substitution test.
5. **Can code be made:** yes, the frozen historical research implementation is committed and tested. A current executable strategy is not established.
