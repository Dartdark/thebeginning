# Summary
Personal bookkeeping and saved-output checks passed for both frozen raw interpretations.
All 14 baseline legs, 21 allocations per model, and phase-aware costs/marks were retained.
This is an independent review of the personal adapter; I authored the candidate replay.
The checks do not establish author MultiCharts parity, reliable stop acceptance, or live readiness.

## Scope and method

Reviewed `analysis/codex_r2vault_personal.py` and its reused `analysis/codex_anson_personal.py` allocation/MC helpers. No new candidate variant, price replay, Monte Carlo history, or parameter selection was run. I independently rebooked the saved ET and CT raw ledgers against the existing Grid24 observations, then recomputed statistics from the already saved daily portfolios, history indices, and paired MC arrays. Results are recorded in `analysis/outputs/codex_r2vault/personal/saved_output_checks.json`.

The baseline cache has 14 nonmissing legs. Its pinned source/input blobs are unchanged at the current context reference `172322e5151f45e2cbf1da4dbd9efb20ba12d1a9`, as recorded in `context_inventory.json`. The reproduced published full-baseline annual profit, historical drawdown, and paired MC quantiles agree to the published rounding. The reviewed allocation helper builds A/B/C/D/FULL, addition at 1/2 MNQ, and the frozen empty/replacement choices wherever VB exists: 21 configurations per model.

## Findings

No material implementation defect found in the reviewed personal adapter or saved numbers.

- `event_time`/`session_index` distinguish an open at close-stamp j961 (wall 16:00, old session) from an intraminute fill after that open (next session). The synthetic boundary fixture also checks that a 16:01 close cannot leak into a 16:00 mark.
- The full round-trip fee of $1.275 per MNQ and $0.50 entry slip are reserved in the entry session. Target exits pay zero exit slip; stops/other exits pay $0.50. These are monetary adjustments to raw entry/exit geometry, not altered target or stop trigger prices.
- Marks use the last finite Close on that date at or before 16:00, only if strictly after entry and before exit. No after-16:00 observation substitutes for an absent mark. Calendar/closure gaps can leave stale valuations, which are disclosed rather than converted to rescue fills.
- Both raw ledgers enter personal processing directly; the Apex `account_eligible` column does not filter them. All 3,037 ET and 2,760 CT trades were booked. Their one-MNQ net totals reconcile independently to $3,930.325 and $16,125.500 respectively, including fill-specific costs. There are no final open positions in these actual ledgers. The terminal-open synthetic fixture values an unclosed position without adding an executed exit or exit slip.
- For each model I checked all 42 MC summary rows, 72 paired-effect rows, and 294 historical rows. Every saved 5,000-by-252 paired history reproduces its saved profit/drawdown arrays. Daily portfolios equal their 14-leg baseline/allocation formulas; reported totals, drawdowns, quantiles, losing-year probabilities, paired deltas, and continuous equal-drawdown scales reconcile.
- The narrow paired-MC mean intervals measure simulation precision conditional on the observed history. The separate 20-day block intervals measure sampling uncertainty in historical annual mean differences. A positive narrow MC interval does not prove future edge. Continuous equal-risk scales are explicitly research ratios, not executable integer contract counts.

## Limits and interpretation

This checker did not redraw confidence intervals or certify the author implementation: the PDF supplies no source code. I am independent of the personal adapter, but not of the replay I authored. The deterministic one-minute causal path remains an assumed fill reconstruction, not tick data or MultiCharts parity.

Execution uncertainty is material: ET raw has 2,289 already-crossed signal-stop entries, 312 cross-date trades and 326 trades with an unknown observed held gap; CT raw has 2,093, 441 and 440 respectively. These fields remain in the source ledger. Some unknown spans may be calendar closures outside the verified mask; they are not automatically proof of feed failure. Broker treatment of an already-crossed buy-stop level needs direct platform/order validation before use.

The inherited personal baseline limitations remain: published day-based fee adjustments undercount some VB reentries, MOC uses a lower inherited fee, Twin uses the published v1 marking ledger, and daily drawdown omits intraday liquidation/margin exposure. Passing this bookkeeping review does not pass statistical promotion gates or authorize replacing any current-plan leg.
