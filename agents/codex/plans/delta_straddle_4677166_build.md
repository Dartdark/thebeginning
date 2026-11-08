# SSRN4677166: bounded offline implementation

User request: build the rules and test whether they could fit a personal account; save in Git.
Evidence remains NEEDS DATA AND SPECIFICATION, not TEST. This commits an engineering protocol before
mechanical tests. No economic returns, subset strategy, parameter search or account simulation is authorized
by this engineering plan. Existing free acquisition receipts remain current; do not repeat unchanged queries.

## Frozen implementation (one interpreted version; zero financial variants)

Build an offline Python signal/whole-lot target engine for the exact 41 source identifiers/Appendix weights.
Average erf(sqrt(T)*mean(simple daily returns)/(sample standard deviation*sqrt(2))) across
32/64/126/252/504 sessions. Use unadjusted sample SD within each horizon, not the disputed printed AR(1)
correction. Sizing vol: EWMA squared returns, lambda .94, initialized at first squared return;
annualize sqrt(252). Reject zero sizing vol and zero horizon sample SD. These are explicit interpretations,
not authenticated author choices. Require all 41 markets and at least 504 complete aligned sessions.

Use caller-supplied, past-only portfolio risk multiplier: target notional = NAV * .10 * multiplier *
source weight * blended signal / annualized vol. The multiplier must be positive, at most 10, with an
authenticated sample-end/available-at strictly prior to the decision. Default synthetic multiplier 1.
Do not fabricate an expanding-window risk calibration from nonexistent portfolio returns. Native instrument
mapping is external and mandatory: exact dated contract, positive USD return-notional per lot, dated margin
per lot, lot costs and provenance. FX total-return indices need an independently justified execution mapping.

Round target lots toward zero. Compare target USD notional to **confirmed held lots**, using a band
.25 * NAV * .10 * multiplier * source weight / annual vol. Hold inside the band, including small sign
changes; execute at equality. Compute all changes from the actual held lots; proposals never update holdings.
Mandatory contract rolls bypass the band: close old dated lots/open new dated lots, charging both legs.
Only identical return-notional mappings within a contract may be compared; mappings may differ on rolls.
The source does not specify these roll/rounding details; they are local research choices.

Use independent positive gross-notional and margin budgets, supplied by the caller. After the band, apply
one common scale to proposed whole lots if aggregate budgets are breached, round toward zero, then check
budgets again. Risk reductions bypass the band. Expose all clipping and whole-lot tracking error. These are
budget guards, not stop losses or guaranteed loss limits. No leverage optimization or automatic account size.

Clock: aligned sessions and per-observation event/available timestamps; strictly ordered events, availability
not before events, both no later than decision. Final observation must be the declared last complete session;
calendar provenance and next-session identity required. Positive latency separates decision from earliest
eligible fill. No same-close fill, holiday inference, default missing return, forward filling or last-price substitution.
Contract snapshots/margin/multiplier may not be future or stale. Reject zero/negative native reference price
through the positive return-notional contract mapping rather than divide by it. Do not claim support for a
negative-price historical interval until a different risk-notional definition is preregistered.

Deliver CLI, labeled synthetic full-universe packet, deterministic behavioral tests, validation/audit JSON,
input documentation and a personal-account admission check. Audit owned files without computing returns.
The admission check must distinguish missing-data/specification blockers from code failures; synthetic
inputs can never authorize a personal verdict. No backtester may convert proposals to fictional fills.

## Mechanism, decision and comparison

Persistent trends are the proposed mechanism; no measured compelled trader. The rule can lose on reversals,
whipsaws, carry and costs. Overlap with personal PAPERTREND/other directional trend sleeves is plausible,
not measured. An eligible financial study would compare BASE/ADD/REPLACE(PAPERTREND)/EMPTY against the
then-current book, at actual integer size and current costs. It requires separate TEST evidence and committed
economic protocol, design 2018–22 plus warmup, then earned 2023+ historical validation, long/short/year metrics,
placebos and account risk. No such comparisons or Sharpe estimates in this build.

Engineering passes only if analytic signal checks, future-data rejection, input immutability, exact universe,
band against actual holdings, sign reversal, roll/cost accounting, whole-lot rounding, zero-risk guards and
hard budgets pass independently specified tests. A pass establishes implementability only. Personal remains
unadmitted without full executable data/cash/roll/carry/collateral and margin history. All four Apex homes remain
ineligible under the source's multiday holding rule; an intraday change would be a different strategy.
