# Night-volume-switch account review: PASS WITH CONCERNS

Summary: The frozen source models were compared in joint current-plan account paths at actual micro fees.
I independently inspected the account runner and reconciled every funded summary field with its saved simulations.
All160 original-simulator parity records pass; no material account-code defect was found.
An early-payout benefit exists, but the two-year benefit is uncertain and promotion gates remain open.

Scope: independent diagnostics-agent review of `analysis/codex_night_volume_switch_portfolio.py`
and its account outputs. I authored the diagnostics module, which requires separate peer review.
Preregistration `affb482`; context `febc65f1573040abf9a697d1d3468e1bce48c4c0`.

## Verification

- Open-entry paths include the entry minute's range, including the primary source's unprotected entry bar.
- Open market/gap exits exclude that minute's later range; intrabar stops cap marks at the actual rounded fill.
- Costs include$1.04 micro round-trip fees plus$0.50 entry and$0.50 exit slippage perMNQ; sensitivity uses$1.24.
- Raw source features are formed before account eligibility filtering; every allocation uses the same eligible dates.
- The immutable baseline cache and27 unchanged dependencies are checked against the latest context.
- All32 funded summary rows and their9 payout/range/risk/timing fields independently match the savedNPZ data
  to1e-10. All160 five-output original-simulator checks are exact. All48 evaluation outcome rows sum to one.
- The separate arbitrary-event diagnostic walker matches all866 eligible actual exits per mode, including
  rounded stop prices, fill phase, exit minute, kind and gross points before it generates the null controls.

The reconciliation is reproduced by
`codex_night_volume_switch_diagnostics.verify_saved_accounts('analysis/outputs/codex_night_volume_switch/accounts')`;
machine-readable evidence is `accounts/independent_output_audit.json` beneath the output directory.

## Interpretation supported by the reviewed figures

At$1.04 fees on the common2018+ account calendar, adding1MNQ raises year-one expected payouts$345
(paired95% interval$221.50-$471.51) and moves median six payouts from269.5 to256days. Its two-year
change is only+$25 (−$124 to+$180), with an inconclusive−0.4percentage-point change in blown risk.
Adding2MNQ raises year-one payouts$727 but reduces two-year payouts$152.50; replacing ONB loses to BASE.
Thus the early-payout effect must be reported, while a durable overall-plan improvement remains unestablished.

## Concerns that remain open

1. Eight excluded sessions include March2020 stress dates. The account bootstrap is conditional on this coverage;
   circular blocks join eligible days. Evaluation excludes affected real21-day windows instead of compressing time.
2. Original author/MultiCharts signal and execution parity is not established. A stop-order syntax does not prove
   broker residency or disconnect behaviour; a delayed stop submitted behind the market may not be accepted as modeled.
3. Existing CL/MOC path approximations and per-leg adverse-minute aggregation are inherited baseline limitations.
   Exact funded-simulator arithmetic parity does not establish tick-by-tick executable hedging or future account outcomes.
4. The immediate-stop diagnostic happens to match the literal-delay ledger on this dataset; it does not remove
   the source's known unprotected-entry risk on an unseen bar.
5. Full-sample DSR atN294 is.946250, below the.95 gate despite t4.43775. Do not round that into a pass.
   Quiet removed fades have negative means, but recent t−.429 and a drawdown-null p=.250 show limited precision.
6. The source family has prior searches and already-seen2023+ history. Mask and side/time controls are frozen
   falsification tests, not fresh holdouts or permission to choose a profitable leg.

This review authorizes no live, plan, broker or infrastructure changes. Claude reviews/ranks; the user decides trades.
