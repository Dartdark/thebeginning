# Whop strategy review

Author/origin: **dot**. Reviewed 2026-11-10. Source: user-supplied Whop export; community statistics below are attributed claims, not independently reproduced results. No private export or screenshots are included.

Summary: Source review only; no independently validated new edge.
MNQ two-bar compression merits a rule/parity check, not promotion; Turnaround Tuesday is low priority.
Existing Core3 weakness and failed NR7-family evidence remain intact.
Trials run: 0. No code, strategy test, account comparison, or schedule change.

## Decision

Keep existing rankings unchanged. The useful follow-up is a narrowly specified two-bar-compression comparison on MNQ, subject to confirming exact rules and prior repository coverage. It is a research lead, not a validated edge. Turnaround Tuesday remains low priority. No new tests, trading changes, or schedules were run or created for this review.

## Two-bar compression

An October 18 community commenter reports 110 MNQ trades, profit factor (PF) 1.59 versus baseline 1.11, and split-half PFs of 1.76 and 1.45. The commenter reports weaker ES results. These are unverified community results; costs, execution assumptions, sample selection, and out-of-sample validity remain to be established.

The repository already tests ES two-bar compression in `analysis/es_core3_test.py`. The failed NQ NR7 family is a different specification and does not, by itself, settle this two-bar MNQ idea. Conversely, repository-wide novelty has not been established, so this should not be described as an entirely new strategy. Existing independent weakness in Core3 remains relevant and is not overturned by this comment.

## Turnaround Tuesday

The described rule is: Monday close below Friday close; enter long Monday at 18:01 ET, exit Tuesday at 15:55 ET; no stop. The author claims PF 1.36 and maximum adverse excursion of approximately $10,600 per NQ contract. The author also reports worse trailing-drawdown behavior for the basket.

Selection among hundreds of variants raises a substantial selection-bias concern. An unbounded stop policy and large adverse excursions make this a poor priority for constrained drawdown accounts. Keep it low priority; the reported PF is not sufficient evidence to promote it.

## Broker/chart lifecycle

A Kusho community anecdote describes an asynchronous mismatch between broker fills and chart state. Treat it as a reason to check order lifecycle behavior, not a verified diagnosis of the user's settings. Relevant checks would reconcile order identifiers, acknowledgements, fills, cancellations and reconnect recovery against broker truth before relying on chart state. No settings were inspected or changed in this review.

## Remaining material

Most other strategy families in the export have already been researched. This review supplies no new independently validated results and does not justify reranking them.

## Five review questions

1. **What is it about?** Community strategy claims and one broker/chart execution anecdote from the supplied Whop export.
2. **What does it find?** The MNQ compression comment supplies the most useful specific research lead; Tuesday's source PF is modest relative to its adverse-path risk. These are author/commenter claims, not our returns. Existing ES Core3 results do not justify promotion.
3. **Why might it make money?** Compression followed by expansion and a calendar-conditioned rebound are hypotheses, not demonstrated causal mechanisms. This export does not establish a forced flow or explain a durable advantage after selection and executable costs.
4. **Can we build on it?** Only through a specification/parity check first: identify the exact MNQ two-bar definition, lookback, session, direction, trigger, exit, sizing, dates and cost model, then compare against the existing ES two-bar implementation and repository history. Do not rename or revive the failed NR7 family. Tuesday's unrestricted adverse path and the author's worse trailing-drawdown basket keep it low priority.
5. **Can a strategy code be made?** Conditionally. A two-bar directional strategy needs the missing exact rule inputs above. Tuesday's calendar filter and timed long can be coded, but the Friday/Monday close convention, holiday handling, session/timezone and execution/cost model must be frozen first. Monday 18:01–Tuesday 15:55 ET is Monday 17:01–Tuesday 14:55 CT; verify trading-session eligibility rather than classifying it from the calendar-date change alone. No-stop code feasibility is not evidence of safe sizing or profitability. The broker/chart anecdote supports a reconciliation check, not a new alpha strategy.

## Repository evidence and scope

Reviewed against `codex/work` at `cc168c49e30439634281a0eb11f0f2fb885e57bd`.
[Existing ranks](../../../TIER_LIST.md), [watchlist, especially NR7 #21](../../../WATCHLIST.md),
[ES Core3 test](../../../analysis/es_core3_test.py), and [execution references](../EXECUTION_REFERENCES.md).
The tier list reports ES two-bar NR at 119 trades, $151 per ES, t 1.4, with 2018–22 −$10 versus 2023+ $382 per trade; these are existing repository results, not rerun here. No full-repository novelty claim is made.
The private export remains outside the repository; only concise attributed claims and dot's analysis are retained.
