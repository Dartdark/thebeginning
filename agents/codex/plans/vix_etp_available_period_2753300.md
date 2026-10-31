# Frozen limited XIV/VIXY test, user: “test w wat u have”

Committed before strategy signals, trade returns or performance. User explicitly requests testing the available
sample after the incomplete-input findings. This authorizes a clearly labeled proxy/limited implementation;
it does not establish source reproduction, source-period coverage or a current tradeable XIV strategy.

## Mechanism and exact scope

Volatility-insurance premium/basis persistence, not forced orders or guaranteed convergence. Use actual XIV
snapshot and owned VIXY (long-vol proxy instead of VXX), owned spot VIX and archived monthly VX settlements.
Use only the common available date range 2016-09-07–2018-02-15, starting flat; no future performance inspected.
This is a short post-paper historical illustration, not 2018–22 design or a fresh holdout. Source sample and
known February2018 termination are already public. No parameter/period/hedge search, new product splice or rescue.

## Information and order clocks

- Stock-session dates come from the owned VIXY file. Require every XIV row on every stock date in the sample;
  absent XIV dates are data failures, not zero returns. Native monthly VX filenames encode exact expiry dates.
- At the end of session d, wait for confirmed spot VIX close and VX settlement. Front contract = earliest
  ISO-dated monthly expiry strictly after d; exclude expiry-day final settlement. No weekly or legacy-name files.
- Basis = (front settle − spot close) / spot close. Require positive finite inputs, unique date/contract pair.
  The next regular stock-session Open is the first reference fill; no same-close execution or futures Open proxy.
- From flat: basis>0.08 selects XIV, basis<−0.08 selects VIXY, otherwise cash. Held XIV: keep while basis>=0.06;
  exit below0.06, with direct switch to VIXY only below−0.08. Held VIXY: keep while basis<=−0.06; exit above−0.06,
  with direct switch to XIV only above0.08. At exact thresholds, retain/keep cash according to these strict guards.
- Signal at d changes holdings at next session Open. All overnight gaps remain with the prior holding.
  No protective stop, hedge, leverage, stale fill, new entry on the final date or terminal signal execution.
  Final-date liquidation at its recorded Close, costed; no invented XIV continuation or redemption afterward.

## Exposure and costs

One unlevered account, $100,000 reference cash, all available cash invested at entry and held in shares until
exit/switch. Fractional split-adjusted share units are research accounting, not a native broker/integer account
simulation. This avoids falsely treating future split-adjusted VIXY prices as historical share denominations.
No daily rebalance; zero interest/dividend cash unless already reflected in input adjustment, no borrow fee for
long ETP positions. VIXY open/close must use a consistent split-adjusted scale; verify close/adjclose relationship.
XIV prices are secondary reported market O/H/L/C; quality and provenance limitations remain explicit.

Source costs each side: buy Open*(1+0.0015)*(1+0.002); sell price*(1−0.0015)*(1−0.002).
Record commissions and spread separately without double counting. Stress doubles both terms to0.003/0.004.
Compute gross zero-cost bridge on the same causal signal/exposure rules; no result-driven accounting changes.

## Bounded definitions and controls

1. Fixed causal XIV/VIXY/cash switching at source thresholds.
2. Same-period buy-and-hold XIV, entry first executable date Open, final Close, same costs.
3. Same-period buy-and-hold VIXY, same clocks/costs.
4. Same switching rule, doubled costs. Cash is a zero-return reference, not a searched definition.

Four economic definitions maximum, plus gross accounting counterpart. Do not add thresholds, delays, hedges,
stops or substitute another product after results. Preserve all failures. A minimum100trades is not waived for
admission: this short user-requested test is descriptive and cannot promote the strategy whatever the result.

## Outputs and decision rule

Save code/input/plan SHA, exact date/contract inputs, signals and decision→fill ledger, daily gross/net NAV,
per-position trade P&L and attribution for inverse/long-vol legs, by-year results and standard metrics using
analysis/metrics.py (daily dollar marks at reference NAV). Show whole/legs, sample sizes and costs.
Check closed-trade net totals equal daily marked net changes including all entry/exit costs and gaps.
Use existing resampling and daily Monte Carlo helpers only for labeled descriptive uncertainty when applicable;
short sample cannot establish tails or a current-account breach probability. No fake2023+ sample or Apex odds.

Net<=0 or stress<=0 means this limited implementation fails its basic profit/cost screen. Positive results mean
only “positive on this short proxy sample”; no adoption or account-stage advancement. Report timing/exposure
around February2018 from the frozen ledger, without assuming it held XIV during the collapse.
Closest overlap is existing personal VIX sleeve / equity-crash exposure. Current portfolio ADD/REPLACE/EMPTY
and Apex account sims remain unopened: terminated XIV and this short proxy series cannot support a current placement.

Script: analysis/codex_vix_etp_available_period_2753300.py.
Outputs: analysis/outputs/codex_vix_etp_available_period_2753300/.
