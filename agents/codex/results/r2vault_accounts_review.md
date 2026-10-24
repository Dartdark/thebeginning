# R2Vault Apex comparison: independent review PASS WITH CONCERNS

Summary: I reviewed the account path construction and independently reconciled its saved numerical outputs.
All180 funded rows,180 evaluation rows and460 recorded original-simulator parity checks pass.
The20 excluded days and inherited baseline closure marks remain limitations of the comparison.
No material account implementation defect was found; this is not original-author or tick-fill certification.

Scope: independent diagnostics-agent inspection of `analysis/codex_r2vault_accounts.py`, its reused Anson
account machinery, and saved files in `analysis/outputs/codex_r2vault/accounts/`. The execution agent prepared
`analysis/codex_r2vault_accounts_check.py`; I inspected and ran that separate reconciliation tool.
Preregistration:`a973f077`; pre-return calendar clarification:`dab01a8`.

## What was checked

- Intraminute entries use only the replay's post-entry adverse boundary, not an earlier low. Open exits exclude
  later prices in that minute. Intraminute exits retain only the traversed boundary extrema and actual exit cost.
- Every reentry reserves one round-trip commission plus$0.50/MNQ entry slip. Target exits have no exit slip;
  stops/market exits pay$0.50. Source geometry remains75/40points and cash scales to actual integer quantities.
- Missing prices are carried at a prior observable Close only within the declared known-closure mask.
  Unknown held spans and cross-date/late positions are excluded from Apex's shared comparison universe.
- Both clock interpretations, all allocations and both fees use the same2242 eligible days;20 dates are excluded.
  Funded histories respect those dates and each cohort. Evaluation keeps real21-day windows and requires the
  entire window to remain inside the stated cohort, with no compression of missing sessions.
- All180 funded summary rows match their saved1000x5 simulation arrays, including both payout horizons,
  payout quantiles, blown share, all-six share and median six-payout time. All1440 paired funded deltas reconcile.
- All180 evaluation summary rows and1080 paired deltas reconcile with saved chronological outcomes and masks.
  Daily candidate fill/cost totals reconcile independently in both funded-account files for each clock.
- Every360 production five-output comparison and100 synthetic comparison matches the original simulator exactly.
  The synthetic checks include the separate50K/150K rule parameters, integer sizing and payout states.

Machine-readable reconciliation:`accounts/saved_output_checks.json`. It reuses saved histories/returns and generates
no additional candidate model or history draw. The only checker repair normalised parsed microsecond timestamps
to nanoseconds before equality testing; all actual dates already matched, and no research output changed.

## Concerns and limits

1. The PDF has no code or verified execution settings. Causal OHLC order, persistent vaults, timezone alternatives,
   one-NQ monetary geometry, target trade-through and Apex flattening are frozen reconstructions, not author parity.
2. Source OHLC paths approximate unknown tick ordering. Exact simulator parity verifies account arithmetic on those
   inputs, not executable same-tick interactions between every strategy. The50K evaluation preserves pass-first
   same-minute ties;150K preserves breach-first, as the current reference simulators specify.
3. The pre2021-06-28 pause is treated as a documented closure. Candidate marks carry the last observed Close;
   inherited baseline paths can substitute entry price for missing adverse OHLC. This difference is preserved and
   audited, not silently repaired. The50K baseline contains285 known-closure contract-minutes for Monday Long and
   945 for Bridge Monday; it is an exercised limitation, not merely a theoretical one.
4. The prepared50K baseline has a small previously disclosed difference from the published reference. Shared-day
   results use their own matched baseline and must not be presented as exact reproduction of that published number.
5. Funded circular blocks join eligible days after exclusion, including omitted stress days. Payout intervals are
   conditional on this historical sample and simulator; they do not establish future profitability or full tail coverage.
6. A favourable account difference cannot bypass the failed strategy evidence: every frozen model is below the
   conservative multiple-testing t3.597/DSR.95 gates. Independent review of diagnostics and original-source validation
   remain separate from this account review.

No live, broker, infrastructure, ranking or plan change is authorised by this review. Claude reviews/ranks; the user decides.
