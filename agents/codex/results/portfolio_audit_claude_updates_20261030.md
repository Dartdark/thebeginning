# Claude portfolio-audit updates: inputs and ladder refreshed; risk conclusions remain qualified

Summary: Reviewed Claude through `d654fda13d43f3b481441168336586bb89bd9d9e` after the user said the updates were complete.
The explicit 150K integer chart inputs and stale personal-ladder findings are addressed as plan-definition work.
The overlap diagnostic measures a useful potential bias, but uses the older 50K RS roster and unfloored risk sizes.
Its blanket inference that comparisons cannot change is unsupported; a canonical-account synthetic counterexample confirms this.
The refreshed ladder is historical selection, not independent confirmation of its capital thresholds. No allocation changed here.

Parent: [five-home portfolio audit](portfolio_audit_20261031.md).
Verification: `analysis/codex_portfolio_audit_claude_updates.py`;
output `analysis/outputs/codex_portfolio_audit_claude_updates_20261030/verification.json`.
New alpha definitions and independent historical return reruns: **zero**. Source/settings review and synthetic mechanics only.
Claude's saved performance figures below are attributed results, not independently reproduced in this follow-up.

## What is now addressed

| Original finding | Latest source change | Updated audit status |
| --- | --- | --- |
| Ambiguous 1.5-contract intentions on 150K funded | Commit `4855fea`: `plan150_integer_test.plans()['all 1.5 -> 1']` explicitly sets VB flagged, Monday Long and Bridge Monday to 1. All fixed inputs are integers; DT2 retained and ST not restored. `FUNDED_PLAN.md` now specifies these chart inputs. | **Intended chart inputs resolved.** Tested source function and cushion-factor fixtures pass. Actual installed-copy parity is a separate question. |
| Old personal ladder described a 16-piece core | Commit `d654fda`: `personal_ladder.py` assembles the current 19 labels and rebuilds the ordering; four forward-only sleeves remain excluded from the cleared tier. | **Stale table refreshed.** Treat the new ranking and capital figures as exploratory historical estimates. |
| Opposing NQ positions may exaggerate summed minute risk | Commit `85481dd`: a new occupancy/range diagnostic reports the potential overlap term. | **Measured, with scope limits.** No corrected shared-price account replay was supplied. |

Claude's 500 paired two-year histories report the all-integer 150K choice at $17,769 mean first-year payouts,
$20,182 second-year payouts, 1.6% failures and median sixth payout on day 208; fractional reference $17,870/$20,137,
1.8%, day 209. That supports a small difference **within that inherited bench**; it does not establish statistical
equivalence, native-fee execution parity or future stability. The explicit integer wrapper is the correct source
for future comparisons; historical `swing_target_bench.plans150()` still retains its fractional reference.

Updated ladder figures from Claude's saved output:

| Current tier | Conditional capital at DD-p95 / 20% | Median 252-session P&L | Daily-equity DD p95 |
| --- | ---: | ---: | ---: |
| OT + Twin + ONB ML + LDF, 4 pieces | $10,935 | $8,764 | $2,187 |
| Through PAPERTREND, 12 cleared pieces | $14,882 | $18,734 | $2,976 |
| All 15 cleared pieces | $24,285 | $26,330 | $4,857 |
| Full 19, after forward-only pieces qualify | $36,112 | $40,543 | $7,222 |

At $10,000, the four-piece row's modeled DD p95 is 21.87%, so the prose “$10–11k start at row2” is looser than
the same table's 20% threshold. Approximately $10.9k clears the stated rule in this historical model, before
margin feasibility and uncertainty about future edge. This is a numerical clarification, not a new sizing decision.

## Overlap measurement does not establish account-level neutrality

`analysis/opposing_overlap_check.py:16` selects `STB.plans50()['50K plan']`. That is the historical RS-long roster,
whereas today's documented 50K uses T_ONESIDE. The script excludes OT by design, and lines28–29 multiply by the
raw `lab._base` risk-sized values rather than flooring actual executable lots or applying each account's daily
cushion state. Its full sample also differs from the audit's common-coverage window. Consequently, the reported
88/416 days and approximately $20 mean per affected minute are not exact measurements of today's account paths.

For a fixed set of genuinely simultaneous open NQ positions, the range term is a useful description of possible
overstatement from separate long/short extremes. The diagnostic does not recalculate protected entry/exit minutes,
shared-price paths, liquidation times, payouts or BASE/ADD/REPLACE/EMPTY outcomes. Missing observations can also
understate risk. The whole-night-minimum proxy addresses one source of pessimism while retaining session timing
and coverage limits; it cannot establish that the **entire** model is “never optimistic.”

The claim in `FUNDED_PLAN.md` that the bias “hits every plan in a comparison alike, so no decision changes” does
not follow even if an equal error is assumed. The committed synthetic test uses canonical `funded_sim.run_pa`:
both hypothetical plans reach balance $50,500/floor $50,100, then have a final true low of -$390/-$370. Both
survive. Applying the same extra -$20 adverse bias to each makes the first fail and leaves the second alive.
This is a counterexample to cancellation, **not evidence that an actual adopted allocation should change**.
The saved fixture retains all five account outputs for both cases.

Suggested replacement for that conclusion:

> The measured overlap term can overstate risk for simultaneous opposing NQ positions under the stated price-path
> assumptions. Its account-level effect on current allocations has not been replayed. Retain current decisions
> pending independent review; qualify failure and payout estimates for missing data, timing and netting assumptions.

## New personal ranking is selected on its reporting history

`personal_ladder.py:20–29` greedily tests every remaining addition and selects the highest Monte Carlo
median-return/DD-p95 ratio. The 15 cleared sleeves require 120 subset comparisons; the four forward-only sleeves
add another 10. All use the same historical assembly and seed 1 resampling; the script contains no separate
chronological selection/validation split. Therefore “best ratio” means best encountered along that historical
greedy path, not a validated best portfolio or globally optimal subset.

Rebuilding this table is useful and addresses the outdated count. A bootstrap of the history used to choose
the subsets does not remove allocation-selection bias. Freeze any intended subset before evaluating separate
data or prospective observations, retain the existing forward requirements, and describe the printed capital
lines as conditional research estimates. No new subset is promoted by this review.

`personal_portfolio.py` is unchanged by these three commits: it still explicitly identifies the main Twin ledger
as v1 rather than literal v2.1, books Kusho on exit dates, and carries the original OT data cutoff. The old
`max(1, floor(...))` illustration is also unchanged. The new smaller-subset ladder reduces the practical temptation
to use that illustration, but does not fix its implementation or fill missing source/marked-position/margin inputs.

## Updated recommendation

Do not keep asking the user to specify the 150K intended integer inputs or rebuild the stale table; those actions
are complete. Continue using the explicit integer inputs and the refreshed ladder as the documented research
reference. Remaining work is qualified verification of the underlying current-version/session-marked account
paths and of any newly selected ladder row, rather than another pass over the same documentation.

The original concentration result remains a reason to seek independently evidenced different market exposure;
these updates do not add a new return source or establish that a particular portfolio change is beneficial.
No shared trading plan, live, VPS, broker setting or strategy was modified. Independent historical reruns of
Claude's new 500-history comparison and greedy ladder were not performed here.

For Claude: `agents/codex/results/portfolio_audit_claude_updates_20261030.md`.

## Completed latest-source follow-up

Claude `88b5e95f5d10f468a0865c693b302fb48cdb956b` now supplies the current-roster overlap replay and chronological
personal subset comparison. The [final follow-up](portfolio_audit_final_followup_20261030.md) independently checks
whole-contract overlap using the native-cost audit paths:0/500 account histories change for either funded size.
The ladder now acknowledges unstable small rows and favors its documented12-piece row at conditional capital
around$16.6–17.4k in historical validation. Mark the repeated input/table/replay/check implementation requests
complete. Original source/version/data/margin/future-stability limitations remain documented boundaries, not
requests to redo completed work. Prior tables above retain their original frozen source identity.
