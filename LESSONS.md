# Lessons (short rules learned the hard way)

For the user and for Claude. One line each, newest at the bottom of each section, with the date and where it came from.
Claude adds to this during the Friday review (and whenever a mistake is caught); the user can add or strike lines anytime.

## Trading and evidence
- One winning trade is not a strategy; being on the right side at the right time looks like skill. Judge rules over
  hundreds of trades, never by the last trade (user, 2026-10-18).
- Price patterns fail out of sample here again and again; edges that hold have a reason someone is forced to trade at a
  known time (index funds, rebalancing, payroll, weekend flows) (TIER_LIST, 2026-10).
- Stock-level effects ('abnormal returns', 'additions vs deletions') net out in NQ / ES; check that a flow pushes the whole
  index before testing it (Franz index-rebalance paper, 2026-10-18).
- A plan that beats every challenger on the same data is partly home advantage: it was picked on that data. Live results
  decide, by rules written in advance (drift alarm, mid-December gate) (2026-10-18).
- Expect live results below the backtest (published anomalies lose ~26% out of sample, ~58% after publication); the plan
  was sized to still work at 75% (2026-10-18).

## Testing
- The one-history funded bench overstates swaps: +$700 'gains' at 2 MNQ blew 17-22% on the bootstrapped bench. Decide plan
  changes only on the bootstrapped bench (replacement sweep, 2026-10-18).
- Always test a candidate against the slot left EMPTY, not only against the plan: cutting Vault Break looked like a noise-band
  win until the empty-slot control showed the same result (2026-10-18).
- A candidate can earn its place by replacing, not only by adding (user rule, CLAUDE.md, 2026-10-18).
- Count every variant you looked at; a sub-cut found after seeing results needs an untouched market or period to confirm it
  (the LETF push sub-cut failed on YM, 2026-10-18).

## Research sources
- Read the PDF before trusting a summary: Antigravity misread the FOMC paper's key number (2026-10-18).
- A paper with 'proposed', 'framework', 'may' and no 'we find' has no results (gamma expiration draft, 2026-10-18).
- Check `TIER_LIST.md` for a paper's title / SSRN id before testing: Treasury auctions came back as 'new' (2026-10-18).
- Never attach a finding, number or citation to a source that doesn't state it (Antigravity's invented citations, 2026-10).

## Live operations
- A dropped connection costs real trades (missed winner 2026-10-12): reliability (VPS, screen sleep off) beats speed.
- Rithmic rejects stops already through the market: every strategy needs the stop guard (ONB rejection 2026-10-14).
- A copier sends every account the same size; cushion sizing needs per-account groups or multipliers (2026-10-19).
- Copied evaluations pass or fail together; stagger new evaluations 5-10 trading days apart (2026-10-15).
- "Permission denied, contact the FCM" from Rithmic was a wrong password: check the simple things first, and set
  up / test a second machine only after the close (VPS move, 2026-10-19).
