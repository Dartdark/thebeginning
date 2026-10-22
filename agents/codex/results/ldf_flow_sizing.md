# LDF flow sizing: WATCH — amendments ready; waiting for promised 2017 export
Summary: Accepted all three review changes and committed them before any LDF outcome calculation.
The user confirmed the 2017 daytime export is coming; wait for it and preserve the 2018-22 design.
Added 63/252-session momentum controls, a 63-session placebo tercile and a return-free correlation checkpoint.
D-1 assets plus mandatory D-2 stress now permit the exploratory screen; dated supplied fund copies are archived.
No strategy return screen has run; next step is verify the export, save input diagnostics, then execute design once.

Plan: `agents/codex/plans/ldf_flow_sizing.md`; amendments `7875d7c`, `c64903a`, `6ca8950`.
Script: `analysis/codex_ldf_flow_sizing.py`; implementation `441062e`, hash guard/archive `ddbc163`.
Output: `analysis/outputs/codex_ldf_flow_sizing/`. Return trials: **0**. Funded simulations: **0**.
Review: Claude `075254b:agents/codex/results/REVIEW_ldf_flow_sizing_prereg.md`.

## Rule and amendments

The sole selectable rule remains low/middle/high 1/2/3 MNQ versus the current 2 MNQ LDF, using prior assets
and lagged liquidity. Two-session asset lag is a mandatory stress. The review's momentum controls and
placebo dimension are included. Calendar-session endpoint returns are known before the decision.

The interim later-start choice was superseded by the user's explicit confirmation that the 2017 export is
coming, before outcomes. No later-start experiment was run. The script refuses to proceed without the
promised full 2017 daytime export; it can read the file from the Claude branch without merging that branch
or modifying the shared data directory. No strategy cache rebuild is needed for warmup features.

## Results and checks

No new performance metrics, placebos or account results exist. The input-stage attempt archived the supplied
fund files, then stopped on the absent 2017 daytime file before calculating candidate features or outcomes.
The earlier inventory's 492 design entries and illustrative power bounds remain planning figures, not a result.

Synthetic/numerical checks passed: future appended observations do not alter earlier rolling ranks; minimum
rank warmup is enforced; HAC contrast statistics are scale invariant; singular regressions are rejected;
the existing grid is truncated at 2022; a synthetic 2023 outlier is excluded before the accepted MC loader.
These synthetic checks are not strategy research trials. Configuration and dependencies are ready.

## Data limitations and next action

`fund_snapshots/20261022T050515Z/` contains byte-preserved copies of Claude's `c23fc02` issuer files, SHA256,
UTC storage time and provenance. These are **not independently freshly downloaded issuer files**. An issuer
download probe was blocked by the environment HTTP proxy (403); no bypass was attempted. Forward ingestion
must archive actual received files and timestamps, not treat today's stored git copy as historical receipt proof.

No 2023+ candidate calculations, funded bench, new MultiCharts code or live change. After the export arrives,
run `.../python -B analysis/codex_ldf_flow_sizing.py inputs`, inspect and commit the return-free checkpoint,
then `.../python -B analysis/codex_ldf_flow_sizing.py design`. Respect every registered stop; do not silently rerun.

Tell Claude: all review amendments are registered; `agents/codex/results/ldf_flow_sizing.md` records readiness
and the sole pending input, the user's 2017 daytime export. Zero LDF return trials so far.
