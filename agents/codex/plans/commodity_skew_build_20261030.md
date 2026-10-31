# Commodity skewness: authorized offline code build

User request: build code based on the SSRN 3507947 review. Source and evidence boundary:
`agents/codex/results/ssrn_3507947_review_20261030.md`, execution reference E53.

This is an engineering plan, not an admitted return experiment. No historical market outcomes,
parameter searches, economic trials, scout reservations, trading orders or account changes.
The source lacks a verified 22-market input panel and exact price-series definitions. Those
prerequisites still block historical return and portfolio-comparison stages.

## Fixed build scope

- Offline Python module and CLI, complete input schema, runnable generated synthetic example,
  synthetic regression tests and build report. Only Codex research paths and the permitted
  research verification queue may change.
- Full exact named 22-commodity universe. Prior 12 calendar months of independently declared
  complete daily settlement observations; at least 200 return observations per commodity.
  Each daily simple return uses the same dated contract's prior close, including incoming
  contracts on roll dates. No outgoing-to-incoming price splice is a return. Prices must be
  strictly positive; unsupported nonpositive-price episodes remain blocked, not dropped.
- Adjusted Fisher-Pearson sample skewness (explicit local estimator choice). Long four lowest,
  short four highest. Reject zero variance and near-equal scores across either cutoff
  (absolute/relative tolerance 1e-12); do not resolve a ranking ambiguity using future returns.
- Full daily history and universe/calendar must be known before the declared decision. Every
  event/availability time has an offset. Declare a local calendar timezone. Formation is in
  the month after ranking, entries strictly follow the decision, and next actions are before
  contract-specific delivery/last-trade deadlines and within the holding month.
- Equal ideal absolute weight 1/8 NAV, 100% gross total (50% long, 50% short), consistent with
  the source's no-leverage assumption. Actual draft quantities floor to whole contracts and
  reject unaffordable selected legs. Emit reference gross/net exposures and weight shortfalls.
  Reference prices are not fills or a margin/buying-power guarantee.
- Separate explicit per-side fees and tick-slippage estimates for a from-flat entry and
  hypothetical unchanged-contract exit. Include units and separate components. These are not
  actual rebalancing/roll turnover, simulated P&L or costed performance.
- Emit target positions and action deadlines only. No order routing, assumed roll fills,
  held-book ledger, arbitrary backtest runner, guessed cash interest, stops or reported returns.

## Checks before handoff

Constructed checks must cover the known analytical skew value, exact rank direction, full-universe
and 12-month coverage, duplicate/missing/nonselected rows, same-contract and previous-session
alignment, future/naive clocks, invalid numbers, zero variance/cutoff ties, integer rounding,
cost components, unaffordable legs, expired/delivery-unsafe contracts, FX/spec availability,
next-month formation and fail-without-output CLI behavior. Run the synthetic CLI and retain
its hashes/check log. These checks establish code behavior, not historical source parity.

## Decision and next step

Build accepted only if the regression checks and CLI example pass and the documented limitations
match the output. Economic evidence remains NEEDS DATA. Later historical work requires matching
data, a reconciled native-contract cash/roll ledger and a separately committed bounded preregistration.
Monthly holds are personal-account research; all four Apex evaluation/funded homes remain
ineligible as written. Existing return gates and BASE/ADD/REPLACE/EMPTY requirements still apply.
