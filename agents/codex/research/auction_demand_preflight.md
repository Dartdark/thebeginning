# Auction demand study: pre-return feasibility and logic review

This is a design preflight, not an independent performance verdict or promotion check.
The two read-only reviewers saw research context. A passing strategy would still require a fresh spec-only
maker/checker reconstruction after returns, as required by DEVELOPMENT_PROCESS.md.

- Both reviewers found no existing bid-to-cover-conditioned NQ return test. Prior tests used auction calendars,
  maturities, offering-size subsets, unconditional bond direction or NQ's own initial price response.
- Metadata-only intake:368nominal13:00ET design auctions on368dates, positive BTC throughout, no ambiguous date.
- Same-tenor/reopening prior-last6,min4 reference leaves326design opportunities before price confirmation:
  2018/19/20/21/22 counts40/62/68/78/78. These are intake counts, NOT trades or performance.
- The code's source-defined intake reproduced those counts before any execution. Reproduce via
  codex_auction_demand_confirmation.load_results(Timestamp('2022-12-31'),'design').
- Review clarified stable duplicate key(CUSIP,date), comparison of result fields for conflicts, chronological
  date/CUSIP ordering, rejection of equidistant tenor ties, and NaN slots for invalid historical BTC.
  These changes were committed as3db3857 before return testing, amending originald03cdcb.
- BTC deviation is not a consensus surprise or WI-yield tail. Tenor/reopening normalization is essential;
  offering-denominator changes and strategic dealer bidding remain confounders.
- Public release policy supports an after-auction buffer, but no original receipt/revision timestamps exist
  in the local CSV. Primary15min/diagnostic5min availability assumptions remain explicit limitations.
- The earlier DON'T TEST dealer-award next-morning idea remains rejected. This study does not infer
  dealer inventory, forced next-day hedge orders or unobserved awards. It tests same-day result repricing.
- Conditional direction may already be priced before entry. Result-independent same-frame ZN controls,
  exact kept/removed totals, uniform and within-year/tenor/reopening random drops are the frozen falsifiers.

No reviewer ran forward returns, changed files, committed code or contacted external people.

Implementation preflight completed after the intake clarification: a read-only reviewer inspected the new code
and found no concrete mismatch in grouping/prior references, deadline/decision/delayed fill clocks, duplicate
handling, exact candidate/control sides/brackets/costs, or within-cell sampling. No returns/tests/edits were run
by that reviewer. This is code/spec agreement only; receipt/vintage assumptions and performance are unverified.

After the frozen design finished, the same read-only engineering reviewer reconciled the saved metrics,
entry/exit labels, native micro costs, exact control subsets and all 1,000 stratified paths. Every ledger had
zero unobserved held minutes. This was a completion audit with maker context, not independent promotion.
The reviewer noted a missing row-level structural-exclusion listing. The report script now reconstructs it
from the hash-verified design-period source using frozen eligibility rules, preserving all 152 excluded rows
and reasons. No signals, returns, original bindings or selection rules were changed.
