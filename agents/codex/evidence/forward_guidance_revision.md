# Issuer Forward-Guidance Revision: NEEDS DATA

Summary: A change in management's earlier guidance for the same future fiscal horizon supplies information
different from realized-quarter EPS surprise. The existing EPS fields are already used by an old NQ strategy.
No original paired guidance documents, exact observable clock or index transmission evidence is established.
Keep this at source feasibility; no signal time, threshold, entry direction or economic rule is selected.

Sources: local definition review and SHA256 bindings in
`agents/codex/research/distinct_evidence_candidate_20261026.md`; Alpha Vantage attribution appears in
`analysis/megacap_earnings_nq_test.py`, but this review did not retrieve provider/issuer documentation.
No primary guidance source has been acquired or audited. Return trials: **zero new configurations**.
This sheet precedes a strategy preregistration. No TEST decision, promotion or trading approval.
The separate source-only census plan is `agents/codex/plans/forward_guidance_input_gate.md`, committed
as `ac88ccd`; it is not an economic preregistration and cannot authorize a futures price test.

## 1. Who trades, and what forces or causes the trade?

An issuer may change its revenue/earnings outlook for a still-future fiscal horizon. Investors can revise
cash-flow expectations and target exposure when they read that information. This is an information
repricing hypothesis, not an observed order, compulsory hedge, obligation or deadline. It does not establish
that repricing is delayed long enough for an intraday futures entry, that a guidance increase is good news
relative to market expectations, or that an offsetting disclosure will not dominate it.

The guidance change must stand on its own. Neither an overnight index move nor a just-reported EPS beat
can be relabeled as evidence of changed future management guidance. The source gate needs real paired
announcements before an economic mechanism can be evaluated further.

## 2. Direction, size and timing known before entry

Required as-of state: old and new management forecast intervals (including units and accounting basis),
the exact fiscal horizon they concern, old and new original documents and their publication/receipt times.
Normalize only economically comparable same-horizon statements. Preserve fiscal-week differences,
acquisitions/disposals, changed currency assumptions, share-count/split adjustments, and GAAP/non-GAAP
changes. Interval width and overlap matter; midpoint subtraction alone can hide ambiguity. Withdrawal,
reinstatement, qualitative guidance, changed horizon and missing old guidance are separate explicit states;
none may be silently coded as zero or assigned a direction from subsequent prices.

This proposal compares issuer guidance with its **own earlier guidance**, not with analyst consensus and
not with realized quarterly EPS. A guidance revision and a consensus surprise may disagree. Any eventual
model must declare which statement is being tested before returns.

No direction or size is frozen here because these inputs have not been audited. There is no estimated
futures flow or hedge fraction. No rough exposure number can be inferred from the CSV's fixed old weights.
An eligible eventual signal frame is1/5/15/30minutes, still unselected. Publication → receipt → completed
signal → order → fill → exit must later be specified with timezone/DST and delayed dissemination conventions.
The CSV's pre-market/post-market label does not establish any of these minute clocks. Do not choose an
entry time from the earlier earnings strategy's outcomes.

## 3. Does the information reach the traded contract or its direct hedge?

NQ would be a possible index hedge for a relevant Nasdaq-100 constituent. Actual constituent membership,
as-of weights, other same-session announcements and netting across investors remain unresolved. A company
valuation change can stay idiosyncratic, be hedged through its stock/options, or be offset by another name.
No compulsory NQ/MNQ demand or incremental index-level continuation has been established. Symbol remains
conditional; this is not a ticker port of the old EPS strategy.

## 4. New information and data feasibility

| Input | Exact local evidence | Coverage and point-in-time status | Ownership/cost |
|---|---|---|---|
| Old/new issuer guidance for an identical fiscal horizon | Neither earnings CSV has a guidance field; bounded data/input filename search found no guidance/consensus/revenue/press-release product | No audited history or event count; original statements and revision lineage needed | Not established; no purchase, account or API work authorized by this sheet |
| Original issuer publication and receipt times | CSV fields are reportedDate and reportTime bucket | No exact original clock/receipt or revision provenance established | No source retrieved |
| Point-in-time index membership, weights and corporate-action normalization | Old NQ code uses fixed approximate name weights | Not a historical membership/weight input; cannot reuse it as exposure proof | Not established |
| Existing EPS/calendar fields | Headers of `data/ndx_megacap_earnings.csv` and `data/dow_heavy_earnings.csv` | Fields: ticker,fiscalDateEnding,reportedDate,reportedEPS,estimatedEPS,surprise,surprisePercentage,reportTime; original vintages not established by schema | Existing repository files; not a new guidance product |

The research note hashes both full CSV files and relevant old source scripts without calculating strategy
returns. The source-only census manifest completed2026-10-26T11:32:21.513915+00:00 under plan `ac88ccd`
at `analysis/outputs/codex_forward_guidance_input_gate/manifest.json` is the authority for the limited
metadata counts below. Both schemas lack every required literal guidance/document/receipt/weight field
named by that plan; no alias inference or external-source conclusion follows. A filename/header audit
proves only the bounded inputs inspected, not that no external free source exists. Retain original
documents, provenance and hashes if later acquired. No keys, paid feeds, accounts or new network requests
were used. No raw futures data or prior strategy ledgers were opened for this sheet.

## 5. Costs and actual intraday gaps

Repository research assumptions: NQ$7.25roundtrip plus$5for each market/stop fill; two market fills cost
$17.25. MNQ is separate at$1.24roundtrip plus$0.50per market/stop fill; two market fills cost$2.24. These
are assumptions, not newly verified broker quotes. A future target fill still needs the engine's NQ1point
trade-through; gaps and active entry-bar stops need conservative native-price execution. Event-time spread,
latency and smaller-contract listing/parity/history have not been verified.

No measured gross guidance edge exists to compare with those hurdles. No occupancy-map or joint-path
research was run; no free account window, diversification benefit, payout improvement or replacement claim
is established. Do not select event samples based on whether the existing book is flat. NQ cash-session
exposure could overlap VB/ONB/Twin and earnings-sensitive momentum; that is an unmeasured risk hypothesis.

## 6. Power before a return test

No2018–22 admissible same-horizon guidance pair count is known. Corporate quarters do not imply an
independent trade per ticker: firms do not always revise guidance, multiple names announce together and
sequential guidance comparisons are dependent. As-of membership, source coverage, missing old statements
and timing exclusions may remove much of the apparent calendar. An outcome-blind event census is required.

The completed outcome-blind **report-metadata** census retains310rows from16collected issuers on227
distinct reported dates during2018–22, including58multi-issuer dates. Selected metadata exceptions and
repeated identity rows/groups are zero. These are a collected report-date ceiling only: they are not
observed guidance revisions, original releases, futures sessions, independent samples or effective n.
No guidance pair, original guidance document or exact receipt timestamp was observed. Historical issuer
selection and survivorship are unresolved. Zero census exceptions does not validate original vintages
or authorize trading those dates. A separate comparable-guidance-pair census is still required.

If effective event count were n and per-contract trade standard deviation were s, t6 would require net
mean approximately6s/sqrt(n), before selection/dependence adjustments; the gross hurdle also adds costs.
Neither n, s nor a predicted mean is estimated here. Do not fabricate apparent power from the existing EPS
calendar or borrow a favorable old return statistic. No economic preregistration is justified yet.

## 7. Already tested and falsifiers

`analysis/megacap_earnings_nq_test.py` already trades weighted EPS-surprise sign, earnings-night price follow
and fade, subsets, a price-move threshold and a later entry. `analysis/megacap_earnings_intraday_test.py`
adds run-up, first30minute and gamma-conditioned signals. `analysis/ym_dow_events_test.py` conditions on
earnings dates and YM/ES/ZN moves. A new EPS normalization, name subset, index or entry clock does not
create this distinct information source. These earlier trials remain prior research; this sheet adds zero.

The increment would be original comparable future guidance revisions. Refute eligibility if no paired
source, comparable horizon/basis, observable clock, or relevant constituent exposure can be established.
If the eventual variable algebraically collapses to existing EPS surprise/overnight return, it fails novelty.
No return failure authorizes substituting the EPS field, reversing direction, changing the window or adding
post-hoc filters. Any source-complete TEST decision must be separately reviewed and preregistered first.

## 8. Failure and diversification

| Question | Prediction before returns | Evidence needed or refutation |
|---|---|---|
| What stops the mechanism? | Guidance is anticipated, immediately priced, incompatible with its old basis, or dominated by simultaneous news | Comparable original documents, publication/receipt audit and eventual frozen matched-information controls |
| What liquidity role would orders play? | A delayed marketable entry consumes liquidity and may suffer adverse selection | Quotes/receipt/fills; no passive benefit inferred from the word repricing |
| How could losses cluster? | Earnings-season clustering, systemic forecast downgrades, guidance withdrawals, opposing margin/revenue news and thin-session gaps | Fixed future execution/risk specification plus chronological stress and dependence checks |
| Which existing strategy shares losses? | Potential overlap with NQ cash momentum/VB/ONB/Twin on the same announcement sessions; unmeasured | Joint intraday paths, event exposure and conditional losses after a candidate exists |
| Could an offset arrive before breach? | No offset is established; same-symbol positions net and portfolio losses can precede a later reversal | Valid joint account chronology and whole-contract BASE/ADD/replacement/EMPTY comparisons later |

No stop, target, time exit, position size, concurrency allowance or data-repair rule is frozen at this
NEEDS DATA stage. No price test may run until they are fixed in a committed economic plan. Missing,
ambiguous or late source states must never be repaired using future prices. Stops can gap and cannot
guarantee a breach is avoided; no tail protection or cross-account hedge is proposed.

## Decision and next gate

**NEEDS DATA.** First audit a bounded set of actual issuer original old/new guidance statements and their
clocks, with same-horizon interval/basis normalization and explicit withdrawal/ambiguity handling. Do not
run futures prices or use the existing EPS field as a substitute. The main research program continues;
this source gate adds no trial, material milestone, user-action blocker, alert or reason to pause it.

A later TEST sheet needs audited coverage, opportunity/power and transmission/cost feasibility. Only then
commit≤5configuration preregistration before2018–22 returns; selected-rule2023+ previously seen historical
validation, dependence/selection/placebos, a fresh independent raw-spec checker and valid whole-contract
account comparisons remain required. This document changes none of the user's boundaries or gates.
