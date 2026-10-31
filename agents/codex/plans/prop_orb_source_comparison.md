# NQ PROP ORB: source-comparison scope, no strategy-return test

Summary: Compare the new source with the user's existing ORB candidates and make the assumed baseline explicit.
Show exact rule, timing, sizing and execution differences; do not choose a winner from unmatched headline figures.

Evidence: `agents/codex/evidence/prop_orb_comparison.md` (NEEDS DATA).
Codex starting point: `45904c33eb34940e91a4b164442118da2a4dfa1a`.
Claude context: `8f6b75cc1c6044f712c3ad5f1a774de60dd14859`.
This is a source-review record after inspection, not a preregistration of unseen returns.

Main baselines: current `apex_strategies/NQ_Overnight_Bias_ADX30.txt` and
`funded_strategies/NQ_Overnight_Bias_ML.txt`; also identify the recent merged ORB/Anomaly relative and
Valeris 848 as separate comparators. The user subsequently confirmed the current plan's Overnight Bias/ORB baseline;
the comparison already used those evaluation/funded sources and requires no change of findings.

Allowed: unchanged source/hash, literal rule/default comparison, normalized clock arithmetic, synthetic signal/fill-risk
examples, primary MultiCharts documentation, existing published context and independent read-only checks.
Not scoped: source fixes, chart changes, compilation, new price returns, optimization, account replay, cache rebuild or live work.

Decision: no replacement recommendation without exact-version matched evidence. Material source safety/specification
differences and unavailable new-version results are reported independently of which comparator the user intended.
New strategy-return variants / account simulations: **0 / 0**. Nobody changes the plan or ranks the new idea through this review.
