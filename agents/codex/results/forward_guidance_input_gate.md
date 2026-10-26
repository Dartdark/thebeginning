# Forward-guidance revision: NEEDS DATA; source census only

Summary: The distinct input would compare an issuer's new management guidance with its own earlier
guidance for the same future fiscal horizon. The local earnings files supply neither statement nor an
exact publication/receipt clock. A committed source-only census retained 310 report rows on 227 dates
in 2018–22; these are calendar metadata, not observed guidance revisions or trades. No return test ran.

Source plan: agents/codex/plans/forward_guidance_input_gate.md, commit **ac88ccd**.
Evidence: agents/codex/evidence/forward_guidance_revision.md.
Script: analysis/codex_forward_guidance_input_gate.py.
Output: analysis/outputs/codex_forward_guidance_input_gate/.
New economic configurations/return trials: **0**. Cumulative program: **65 evaluations / 63 unique rules**.

## Proposed information and novelty

An investor can revise expected cash flows after management changes guidance for a still-future period.
This is a possible information-repricing mechanism, not evidence of a compulsory order, delayed response,
known futures hedge or profitable direction. Guidance versus earlier issuer guidance differs from actual
quarterly EPS versus analyst estimates; a guidance increase can still disappoint market expectations.

analysis/megacap_earnings_nq_test.py already trades weighted EPS-surprise sign and earnings-night price
follow/fade rules. The intraday and YM studies cover additional earnings-calendar/price variations.
An EPS normalization, name subset, ticker port, reversal or shifted clock is not a new family. Definitions
and hashes are retained in agents/codex/research/distinct_evidence_candidate_20261026.md.

Comparable original guidance pairs need the same fiscal horizon, metric, interval, currency, share-count
and accounting basis. Interval width, overlap, withdrawal/reinstatement, acquisitions and changed horizons
cannot silently become midpoint changes or zero revisions. There is no selected symbol, direction,
threshold, entry clock, exit or signal timeframe. Any future timeframe must be 1, 5, 15 or 30 minutes.

## Actual source execution and census

The source-only plan was committed before this census. It is **not an economic preregistration**.
Execution completed at 2026-10-26T11:32:21.513915+00:00 using the authorized workspace and interpreter.
The script projected only ticker, fiscalDateEnding, reportedDate and reportTime metadata. No EPS or
surprise values entered the calculations; no futures price, strategy ledger or account path was used.
No entry dates were remapped, signals generated, financial paths replayed or network requests sent.

| Source | 2018 | 2019 | 2020 | 2021 | 2022 | Total metadata rows |
|---|---:|---:|---:|---:|---:|---:|
| NDX collected issuer file | 36 | 36 | 38 | 40 | 40 | 190 |
| Dow collected issuer file | 24 | 24 | 24 | 24 | 24 | 120 |

Combined: **310 rows, 227 distinct reported dates, 16 collected issuers, 58 dates with multiple issuers**.
The selected metadata have zero repeated same-source issuer/fiscal-period keys or recorded identity/clock
exceptions. This does not establish original-release identity, complete calendar coverage, historical index
membership, absence of revisions or an exact minute clock. Pre/post-market labels are coarse buckets.
The current collected issuer set can have selection/survivorship bias.

Both schemas lack all explicitly named guidance-pair, original-document, exact receipt/vintage and as-of
index-weight fields in the frozen census. This is a literal-field/local-source finding; aliases and other
external sources are not exhausted. No actual guidance pair has been identified. The 227 dates are a local
metadata opportunity ceiling, not eligible futures sessions, independent events or effective sample size.
No power or expected gross edge is inferred from these counts.

The manifest binds the script, source plan, both CSVs, old definition scripts and every output artifact.
All selected metadata, year/issuer counts, combined dates and exception/duplicate tables are retained.
Successful intake cannot be overwritten by rerunning the script. Do not repeat this gate on unchanged inputs.

## Previously unfinished mortgage-source gate

The committed MBS duration-state evidence gate was resumed first. The additional saved-PDF content audit
and its reproducer retained four source hashes and 79 term-match contexts, rather than any portfolio state
or return. See agents/codex/research/mbs_primary_input_gate_20261026.md and
analysis/outputs/codex_mbs_primary_input_gate/manifest.json; script analysis/codex_mbs_primary_input_gate.py.

The new content check of the other saved papers supplied no original risk/exposure series, before-entry
hedge clock or evidenced ZN allocation. The previously reviewed literature describes swap hedges.
Term counts only locate text; the bounded exact-phrase search can miss formatting variants and cannot
prove all relevant concepts absent. MBS remains NEEDS DATA. Do not repeat this audit against the same
hashes or substitute the existing ZN-price-momentum family.

## Costs, statistics and limits

Repository assumptions are NQ $7.25 round trip plus $5 per market/stop fill; MNQ $1.24 plus $0.50 per
such fill, separately calculated. Two market fills imply $17.25/$2.24. These are cost hurdles, not fresh
broker quotes, measured strategy costs or evidence of sufficient gross alpha. Native micro listing,
parity, fees and fills remain unverified; a scaled NQ series cannot prove them.

Trade t, daily Newey-West(5) t, net profit, stops, placebos, dependence checks, both-side/year returns,
2023+ historical validation and account comparisons are **not applicable: no economic rule ran**.
The independent check here reconciled source hashes and metadata; it was not a fresh raw-spec promotion
checker or a material independent strategy-review result. No trading approval or milestone follows.

The last economic result remains the rejected frozen Flow Innovation Relaxation design. Its family stays
closed, all failures are retained and the best completed standalone result remains Opening Path Persistence
at full-history trade t3.665 / NW5 t3.625, below every requested full-history threshold. No t4/4.5/5/6
milestone or notification record changes. The separate already-reported EIA access issue is preserved.

## Next gate

Acquire and audit actual comparable original guidance statements, original publication/receipt histories,
historical constituent exposure and evidence of index transmission before deciding TEST. No new access,
account, purchase or user action is requested by this result. Missing data for these hypotheses does not
mean the execution workspace or existing raw futures files are unavailable, and does not pause the program.

Continue genuinely distinct source research as new evidence permits. A future TEST sheet and committed
at-most-five-configuration economic preregistration must precede 2018–22 returns; freeze selection before
only the selected rule/control sees previously seen 2023+ validation. Dependence/selection/placebo checks,
a fresh independent raw-spec checker and valid whole-contract BASE/ADD/replacement/EMPTY paths remain
required. No PowerLanguage, deployment, proxy account improvement or new watcher alert is produced here.
