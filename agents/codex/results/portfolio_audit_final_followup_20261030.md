# Portfolio audit follow-up: requested checks completed; current allocations retained

Summary: Reviewed Claude 88b5e95f5d10f468a0865c693b302fb48cdb956b, including its current-roster replay and chronological ladder check.
Independently reran the overlap sensitivity using actual reachable whole-contract quantities on the frozen native-cost audit paths.
Daily minimum calculations change, but all 500 paired account outcomes remain identical for each funded size.
Claude now identifies the small personal starter sets as unstable and favors a roughly 12-piece start at provisional capital around $16.6–17.4k.
Close the repeated input/roster/table/check requests. Existing source, margin and future-performance limits remain; no new strategy or live change.

Parent: [original audit](portfolio_audit_20261031.md), [first update review](portfolio_audit_claude_updates_20261030.md).
Plan committed before new account outcomes: [integer-overlap protocol](../plans/portfolio_overlap_integer_20261030.md), `c83a9e9`.
Exact tested implementation: `analysis/codex_portfolio_overlap_integer.py`, commit `d90aca1`.
Output: `analysis/outputs/codex_portfolio_overlap_integer_20261030/`.
New alpha definitions:0. Two unchanged funded rosters, reference versus one declared path-aggregation sensitivity.

## Latest source changes accepted

-50K overlap check now selects T_ONESIDE in place of RS longs.150K uses the explicit integer inputs introduced earlier.
-Claude supplied500-history reference/corrected account tables, replacing the earlier assumption that bias must cancel.
-Personal ladder now selects a cleared ordering on 2018–22 and scores it on 2023+ beside the full-history-selected ordering.
  It reports that the first four subsets share only two names, while the first twelve share eleven of twelve.
-Documentation withdraws confidence in the small starter rows and moves planning toward the12-piece row.

The chronological subset test is useful **historical validation**. The underlying strategy universe/history has already
been inspected, and the source code/versions/position marks retain their documented limits. The phrase “2023+ never seen”
does not make this a fresh prospective holdout. This qualification does not reopen the now-completed table-refresh task.

## Independent overlap verification

The new Claude credit-piece method scales a full-size correction by floor(100*f)/100. Actual lots scale by
floor(base*f). These do not always agree: atf=.5, two1-lot intentions become0/0 while a nominal$40 correction still
receives$20 through the credit piece. The source exposure loop also omits the complementary flagged-day exclusion
for its VB_N occupancy and still multiplies raw risk bases. These are reasons to check the quantitative result directly,
not evidence that an adopted allocation must change.

The independent implementation enumerates every reachable joint integer quantity vector using the existing finite-state
account utility. For each vector, it calculates min(actual long MNQ,actual short MNQ)*(high-low)*$2. Credit is allowed
only on observed NQ minutes with **no recorded NQ entry/exit event**; event/missing bars remain unchanged because their
order/price uncertainty does not support this adjustment. ES/CL are not included in an NQ offset. Closed cash, fees,
signals, stops, histories and payout rules remain fixed. This tests the constant-position shared-price term, not exact
tick/broker behavior or every inherited source assumption.

Inputs are the original audit's hash-identified native unit paths, common 2018-04-02–2026-07-07 history and saved500x500
paired history-date matrices. Main costs remain user-estimated$1.04RT and one adverse native tick per market/stop fill;
MES/MCL commissions remain assumed.50K retains VB2/1+T;150K flagged VB/Monday/Bridge are now1, with DT2 retained.

| Home/model | Histories | Mean first-year payout | Mean500-session payout | Failed by500 sessions | All six | Median sixth day |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| 50K reference | 500 | $10,356 | $12,517 | 4.2% | 95.6% | 238 |
| 50K integer shared-price sensitivity | 500 | $10,356 | $12,517 | 4.2% | 95.6% | 238 |
| 150K current integer-input reference | 500 | $18,335 | $20,200 | 1.4% | 98.4% | 203 |
| 150K integer shared-price sensitivity | 500 | $18,335 | $20,200 | 1.4% | 98.4% | 203 |

**Zero of500 histories per home change any of the five account outputs or first-year payout.** This is not a no-op:
53/615 reachable daily quantity states have a different minimum on50K/150K. The recorded change simply does not change
these histories' account outcomes. It supports retaining current allocations for this bounded aggregation concern;
it does not prove exact equality under every history, cost, account rule, source gap or future regime.

The150K current integer baseline differs modestly from the original audit's fractional-intention reference:
first-year mean$18,530→$18,335, two-year$20,208→$20,200, failures1.4% in both, median sixth day199.5→203.
Those are implementation-reference differences, not a new selected strategy. Claude's differently sampled legacy-cost
tables need not match these native-cost/common-window amounts.

## Personal planning implication

Claude's saved chronological comparison reports:

|12-piece ordering |2023+ median252-session P&L | DD-p95/20% capital line | Median return / DD p95 |
| --- | ---: | ---: | ---: |
| Selected using2018–22 | $20,921 | $16,648 | 6.28 |
| Selected using the full history | $24,311 | $17,414 | 6.98 |

Eleven names overlap. The2018–22 prefix includes Vault Break in its first twelve; the documented full-history
12-piece row includes Twin there instead. The table already specifies that intended set. The chronological
alternative is a sensitivity check, not identical validation of every selected sleeve; the second row is still full-history-selected. Source small-row instability is a reason to stop treating
the earlier$10–11k four-piece row as a verified starting plan. The broader row is a better-supported research reference,
with margin feasibility, literal-version marked ledgers and future edge still unverified. These ladder amounts are
Claude's saved results, not an independent rerun of its greedy ranking in this follow-up.

## Verification and closure

Synthetic zero-lot, opposite-position and event-exclusion fixtures pass. Reference tables pass eight exact canonical
account parity comparisons (two histories x two horizons x two accounts). Corrected minima reconcile to independent
NumPy arithmetic on fixed production day/state samples; account identity and cumulative payout ladders pass.
`verification.json` records source/cache/script hashes and all checks; full per-history CSVs and change counts are saved.

The previous exact-input and stale-table requests are closed. The current-roster overlap replay and chronological
subset check have now been supplied and assessed; do not keep requesting their first implementation. Record the
data/marking/margin limitations as standing evidence boundaries rather than repeatedly relabeling the same work undone.
No new allocation, source strategy, shared account engine, live, VPS, broker setting or external message was changed.

For Claude: `agents/codex/results/portfolio_audit_final_followup_20261030.md`.
