# Anson placement implementation review: PASS WITH CONCERNS

Summary: I independently reviewed diagnostics, 50K/150K Apex accounts and personal-plan implementations.
Saved statistics and portfolio outputs reconcile; 220 production and 100 synthetic simulator checks match exactly.
The frozen evidence supports no adoption: statistical gates fail, and added personal profit carries a larger risk budget.
Source parity, coverage, closure marks and the conditional random-time benchmark remain material limitations.

Preregistration: `928c0ea`. Current-plan pin: `e34d71cd3537a9f019d2521e280fc92f3ffdb4c6`.
Reviewed: `analysis/codex_anson_diagnostics.py`, `analysis/codex_anson_accounts.py`,
`analysis/codex_anson_personal.py`, their pinned adapters and saved outputs.
I authored the candidate replay; this review is not blind independent certification of its signals.
No new strategy return variant or price replay was run for these checks.

## Execution and account checks

- The user's intended 4.5 threshold/20-bar holding period is used in account placement. File defaults
  3.0/6 remain a standalone diagnostic. No better-looking version or account size was selected afterward.
- All 2,038 eligible Apex trades independently satisfy the contiguous-bar exit clock:
  `exit_j = min(entry_j + 100, 896 regular / 691 early)`. This verifies the direct timed-exit geometry
  used by the random-time control. It represents 20 completed five-minute position bars, then the next
  chart open; it does not add a false extra five-minute delay. Entries hold their opening minute;
  exits exclude that minute's later range. A full chart bar separates an exit fill from the next entry.
- Independently constructed synthetic account paths confirm that an entry-minute extreme remains
  exposed, and an open exit excludes subsequent extremes. No protective stop was invented. Entry
  slippage is charged at entry; round-trip commission and exit slippage are charged at exit, per the
  declared model. Baseline fee/path approximations remain distinct.
- The generic funded state machine uses each pinned account's start, trail, lock, safety, qualifying
  day and payout ladder. The 150K fixed DLL and 50K graduated DLL are preserved, with cushion references
  $3,000/$1,500 and integer flooring. All five original outputs match in 220 production comparisons
  and 100 synthetic comparisons covering sizing, payouts, trail, DLL and zero quantity.
- Latest RS-both and DualThrust pieces are added only to the declared 150K roster. The saved DT audit
  reconciles all 1,611 committed timed trades with zero mismatches; it does not reconstruct timestamps
  by price or rerun a strategy search. Evaluation risk quantities are floored after scaling dollar
  budgets, with the difference from the older fractional 150K convention disclosed.
- Funded configurations share common eligible-day block histories. Evaluation retains complete real
  21-day windows, with the reference's account-specific tie handling. Price histories and source
  features are not filtered by account eligibility before signal generation.

## Personal-account checks

The complete 14-piece baseline reproduces the published reference within its rounding. Candidate
daily money equals all 2,059 raw trade nets at the declared $2.275/MNQ round-trip cost. Raw late and
cross-date positions remain in the personal ledger. All ten saved marks are at or before 16:00;
code selects only that date's last available prior close and checks it lies within the position.
A separate synthetic test confirms stale prior marks, no later-price peek, next-session booking
for after-16:00 fills, and entry/exit-session cost allocation.

All 21 frozen starter/full configurations receive the same paired histories. Added absolute profits
are reported together with drawdown/capital burdens. The matched-DD95 comparison scales the complete
portfolio continuously and is explicitly labelled non-executable. Every tested ADD configuration
versus its BASE has lower median profit after that risk normalization in both reported cohorts.
This supports the risk-budget conclusion for these tested plans, not a claim about every possible
personal allocation.

Narrow paired Monte Carlo mean intervals measure simulation precision conditional on observed
history. The separate historical 20-day block intervals address finite-history uncertainty under
their resampling assumptions. Neither is a guarantee of future returns. EOD personal Monte Carlo
does not establish intraday margin or liquidation safety, and inherited Twin/fee conventions remain.

## Output reconciliation and controls

Independent arithmetic checks passed for:

- 252 standalone statistics rows: 1,260 count, mean, total, trade-t and DSR fields;
- eight placebo summaries against saved real totals, null draws and retained trade counts;
- 42 personal MC summaries in ten fields each, plus all 72 paired personal effects;
- 44 funded summaries in nine fields each, and 110 evaluation summaries in six fields each;
- all 220 production and 100 synthetic original-simulator parity records.

Random side is a valid conditional sign test here because no stop/target or direction-dependent
exit changes the frozen holding schedule. Random time is a weaker conditional falsification:
it retains observed event days and side order, and can place a side from a later actual momentum
signal at an earlier sampled clock. Thus its p=1 result is not a causal tradable benchmark and does
not prove momentum has no edge or establish a superior alternative. The main source replay remains
causal. No replacement control or model was chosen after observing this result.

The statistical gate fails independently: 2023+ trade t is about 1.930 raw / 1.929 Apex, below 2;
full-sample DSR is about 0.255 / 0.349, below 0.95. Positive means and narrow MC sampling intervals
cannot override those failures. The author's prior stop/target/size/side/WFO search burden remains
unknown; already-seen 2025+ is replication, not a fresh sealed holdout.

## Remaining concerns

Seventeen Apex dates are excluded, including March 2020 stress sessions. Their exclusion changes
funded block adjacency; evaluation instead excludes windows containing them. Raw personal source has
11 late trades and one cross-date trade. Eight raw trades have held gaps unexplained by the limited
closure proxy, including a Christmas span; these labels do not establish eight feed failures. No
rescue fill, interpolation or broad deletion of closure-spanning personal trades is justified.

The Default/Globex proxy, exact original chart settings, source compile and author trade-list parity
remain unverified. The data cannot reproduce the author's complete 2016-24 period. Source has no
protective stop, and the Apex early-close adapter is a disclosed different return model. Existing
CL/MOC adverse-path approximations, minute-level hedging ambiguity and personal fee undercounts stay
visible. Simulator parity is not proof of real execution or exact author replication.

Status is PASS WITH CONCERNS for this research implementation, not a clean promotion checker PASS.
The evidence supports keeping the current plans and moving on under the user's stated rule. Claude
reviews/ranks results; the user decides trades. No live source, account setting or infrastructure
change is authorized by this review.
