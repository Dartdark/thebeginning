# Summary
Independent review found no material defect in the diagnostics adapter or saved arithmetic.
The positive CT raw recent result and nominal null passes do not pass the frozen promotion gates.
Full CT raw t=2.919716 and DSR311=0.504848 fall below 3.597295 and 0.95.
I authored the replay; this review is independent of the diagnostics implementation, not author-source certification.

## Scope and method

Reviewed `analysis/codex_r2vault_diagnostics.py`, its standard metric helpers, the fixed-entry causal walker interface, and the committed R2Vault design. Independently recomputed saved statistics using `analysis/codex_r2vault_diagnostics_check.py`; results are in `analysis/outputs/codex_r2vault/diagnostics/saved_output_checks.json`. No new strategy interpretation, price replay, Monte Carlo history or null draw was run.

The checker reconciles all 624 standard-stat rows, 84 placebo-summary rows, 13 staged-design rows and eight saved draw files, each with 1,000 iterations per period. It independently recomputes fill-specific net returns, t statistics, DSR306/311, daily/trade totals, profit factors, wins, initial-equity-aware marked drawdowns, and null tail fractions/counts. Bootstrap and standalone Monte Carlo generation were inspected but not redrawn.

## Findings

No material implementation defect found in this scope.

- Costs are applied to raw fill geometry once. Each MNQ pays the declared fee plus $0.50 entry slip; targets have no exit slip, while stop/market exits pay $0.50. NQ-dollar diagnostics are ten times the MNQ cost-normalized returns, not an assertion of the actual commission for one NQ contract. The raw personal fee of $1.275 is also reported separately.
- Trade periods are selected by entry date and contain closed trades; daily periods use marked session dates. Those totals can differ near a boundary. CT raw has one 2022-entry trade closed during 2023. The staged design result correctly excludes its unknown-at-cutoff exit; the full entry-cohort table discloses exits after period end.
- Fixed-entry long branches are asserted against 11,801 actual closed events across all four main models: exit address, price, kind, path segment and gross return. This is a strong consistency check between source chronology and the reusable exit walker, although both share the same declared causal-path primitives.
- The random-side control preserves actual entry price/time/path cursor, mirrors 75/40 protection, and skips a later source event while a previous null position is still held. Intraminute overlap checks compare the actual target-through event price, TP plus/minus one point, rather than the more favorable limit accounting fill. This avoids entering another event before the prior target actually qualifies.
- The random-time control uses an independent coverage-only daily calendar, one uniformly sampled fixed five-minute decision slot per date, the same model clock/flat rules, and a single position. It requires flatness at the decision close. Missing decision bars or next-minute opens skip that planned opportunity; they are not advanced to a later quote. Known historical closures may therefore create sampled skips, as preregistered. It is a falsification control with a different event count, not an optimized tradable alternative.
- Both controls preserve unclosed terminal positions separately; no terminal executed exit is invented. Their drawdown column is explicitly chronological closed-trade equity. It must not be substituted for marked drawdown, intraday account loss or breach probability.
- The trial ledger uses 306 as the preregistered lower bound and 311 after counting five distinct known concurrent NQDB2 profiles once. Design/recent windows are not extra model trials. Unknown author search remains a limitation; it does not justify reducing the count. No PBO or untouched future holdout result is claimed.

## Interpretation and limits

CT raw is positive recently and passes the nominal frozen controls. Its 2023+ random-time total tail fraction is **0.004995** against all source closed entries and **0.005994** against actual entry dates inside the control calendar. These are distinct references; the report must identify which is quoted. They do not override the full-history gates: CT raw at fee $1.04 per MNQ has t **2.919716 < 3.597295**, DSR311 **0.504848 < 0.95**. The lower-cost and timezone variants cannot be selected after inspecting their results.

The reconstruction is based on a PDF without author code and a deterministic one-minute path. Already-crossed stop acceptance, actual chart/session settings, stop residency and tick sequence remain unverified. Raw holds can traverse unknown observation gaps; controls retain analogous gap counts, rather than silently pretending every span is observed. The account adapter removes a shared set of incomplete dates, including material March 2020 stress dates; its probabilities remain conditional on that coverage universe.

This pass verifies diagnostics bookkeeping and declared control logic. It does not establish author MultiCharts parity, reliable live execution, a complete search registry, or permission to change the plan. Mixed CT account/personal benefits should be reported faithfully alongside the failed statistical qualification gates.
