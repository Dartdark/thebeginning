# Anson personal adapter: arithmetic PASS WITH CONCERNS

Summary: Independent code and saved-output checks found no material personal-adapter arithmetic error.
Eight representative cohort/allocation profit and drawdown arrays exactly reproduce the saved results.
All 2,059 raw trades reconcile to $18,951.775 after the declared personal costs.
This check does not certify execution across the eight unknown-gap trades or authorize promotion.

Scope: `analysis/codex_anson_personal.py` and its saved outputs under
`analysis/outputs/codex_anson/personal/`; preregistration `928c0ea`, plan pin `e34d71c`.

- Read the current 14-piece loader, pinned Twin helper use, source-session mapping,
  mark selection, cost allocation, frozen 21 allocations and paired block simulation.
  The reconstructed full baseline matches the latest published rounded statistics.
- Independently recomputed profit and maximum drawdown arrays from saved daily
  portfolios and 5,000 × 252 histories for A_ADD1, FULL_BASE, FULL_ADD1 and
  FULL_REPLACE_VB1 in both 2018+ and 2025+ cohorts: exact to 1e-8. Independently
  checked their medians, p95 drawdown and capital = p95 drawdown / 0.20.
- FULL_BASE, FULL_ADD1 and FULL_REPLACE_VB1 daily allocations reconcile to the
  baseline 14 columns, candidate series and removed VaultBreak column.
- The complete candidate daily book sums to the raw source ledger gross less
  $2.275 per MNQ round trip, with entry slippage in the entry session and fee plus
  exit slippage in the exit session. Marks select the same-date last observed
  close at/before 16:00 rather than a later fill. The actual cross-date source trade
  enters 2025-12-24 and exits 2025-12-25 after 17:00, booked into the next plan session.

Concerns retained: raw source gaps and stale marks, EOD rather than intraday margin
risk, the published Twin v1 ledger rather than an unavailable exact v2.1 ledger,
and the inherited approximate personal fee convention. No source setting or
allocation was selected by this check. Claude retains the independent ranking role.
