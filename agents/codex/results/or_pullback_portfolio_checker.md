# ORPullback portfolio: WATCH - targeted account and baseline audit

Summary: The paired account results support keeping the current plan on the tested complete sessions.
Exact lookup/reference simulator checks pass, and the frozen RS baseline matches its committed ledger.
The full-calendar funded baseline is close to, but not identical to, Claude's saved reference; its small difference remains unresolved.
Sixteen excluded sessions include March 2020 stress dates, so these are conditional comparisons, not a full-history risk certification.
This memo is not a blind maker-checker reconstruction or a promotion PASS; I authored the plan-loader adapter under review.

Preregistration: `agents/codex/plans/or_pullback_portfolio.md`, commit `1ad4306`.
Source pin: Claude `a67035be4189b493098c80f1def979348520fd5d`.
Scope: static account-code inspection, saved-output arithmetic, baseline fee counts and source/reference reconciliation.
No candidate returns or portfolio allocations were rerun for this audit.

## Checks and their limits

- `analysis/outputs/codex_or_pullback_portfolio/independent_output_audit.json` records 160 exact five-output
  comparisons of the quantity-state lookup with the pinned `funded_sim`, plus reconciliation of 32 funded-summary
  rows and 48 evaluation rows. This verifies the acceleration on the declared histories; it does not independently
  verify the source-to-trade replay or certify every possible account path.
- `analysis/outputs/codex_or_pullback/baseline/baseline_rs_audit.json` reconciles all 1,161 reconstructed frozen RS
  rows with the committed reference: date, side, kind, entry, exit and net match within 1e-7; no exceptions were accepted.
  The loader used the original fixed RS functions, not a new signal variant or substituted MC ledger.
- Account candidate paths exclude the entry minute's pre-close OHLC, charge entry slippage/fees while exposure is
  open, and use executable stop/gap or time-exit prices. The saved synthetic path fixture checks the most material
  timing boundary. Both timing modes, both fee schedules and all frozen allocations are reported rather than selected.
- The full-calendar evaluation BASE is 49.8449% at the $1.04 fee, consistent with the saved 49.8% after rounding
  (`evaluation_baseline_reference.json`). The primary paired comparison uses the common complete-window cohort;
  it is not the same denominator as the full-calendar reference.

## Funded baseline discrepancy: unresolved, not silently attributed to fees

`baseline_reference.json` reports the unrestricted local BASE as $9,193.50 / $11,976.00 for one/two-year expected
payouts, 7.7% blown, 91.0% all-six and median 263 days. Claude's saved reference is $9,180 / $11,982, 7.6%, 90.8%
and 263 days. Differences are +$13.50 / -$6.00, +0.1 percentage point blown and +0.2 point all-six. They are small,
but exact equality has not been demonstrated. Matching the reference simulator does not resolve different input paths.

The original local `lab.pkl` predates fee-count metadata. The adapter recovers counts from the same MC ledgers:
VB 1,743 round trips, split 1,209 normal / 534 flagged; ONB ML 343, Monday 450, EOS 105, LDF 895, NFP 78,
Bridge 217 and RS longs 598. These are ledger counts, not the number of nonzero daily P&L observations.
They are reproducible from the pinned loader and the fee totals in `current_plan_manifest.json`.

In particular, VB's nonzero-day fallback counts are only 668 normal / 274 flagged. Using that fallback would lose
fees on repeated entries. The adapter therefore retains exact round-trip counts, as intended by the latest
`real_fee_bench.py`; it does not reduce VB to one fee per traded day. Single-trade/day components have matching
trade/day counts. This rules out treating fallback counts as a proven explanation for the small reference gap.

The saved fee output's dollars-per-year are rounded and divided by `len(lab.tr)/252`, including whatever warm-up
calendar existed in that original lab. The local cache has 2,262 trading rows from 2018-01-02 through 2026-10-09.
Consequently, comparing rounded annual fee figures alone does not establish different per-trade fees or counts.
The original serialized reference lab is unavailable here; cache-calendar, path and floating-point reconciliation
remains open. No parameter, fee or calendar was tuned to force the saved aggregate to match.

## Coverage and inherited model concerns

`account_calendar.json` excludes 16 incomplete candidate sessions before replay. They include 2020-03-09,
2020-03-12, 2020-03-16 and 2020-03-18. Missing prices can coincide with actual halts and stress, rather than random
data loss. Omitting these days can alter both the loss distribution and apparent diversification.

All funded allocations use the same 2,246 complete sessions, and all evaluation allocations use the same 1,972
complete 21-day start windows. This is a fair paired **conditional** comparison. It does not establish the strategy's
performance on the excluded sessions or an unconditional Apex breach rate. Funded resampling compresses the common
complete-session calendar; the evaluation retains chronological trading-day windows and omits incomplete windows.

The initial descriptive overlap routine also treated unknown candidate days as zero. That was corrected to restrict
daily correlation and joint-loss outputs to the eligible sessions; refreshed `daily_joint_pnl.csv` has 2,246 rows.
This correction changes descriptive coverage, without requiring new strategy returns or allocation selection.

The pinned baseline retains its CL whole-Monday adverse-path approximation and ES MOC close-based path approximation.
The inherited `combine_levers_test.challenge` checks an exact same-minute target/breach tie as a pass (the target
branch is checked first). That differs from `portfolio.py`'s more conservative prose. The comparison preserves the
same reference behavior for every allocation; it must not claim a breach-first tie policy or live fill parity.

## Interpretation

The negative plan decision is supported on the declared sample: the primary one-MNQ addition lowers two-year payouts
and increases blown accounts, while larger additions/replacements are worse; replacing VB must also beat EMPTY_VB.
The complete-session and reference-gap concerns prohibit stronger claims of full validation. They do not justify
changing the source, selecting a different size or reclassifying the historical test as a fresh holdout.

Claude should independently review the candidate replay and these account qualifications before ranking it. The user
decides what trades. No live plan, broker/VPS settings or mailbox PR was changed.
