# Jansen comparison and integration: process controls adopted

Summary: Our process already covers hypotheses, preregistration, costs, walk-forward testing, placebos and account contribution.
Added explicit information/label clocks, fold-local preprocessing, baseline comparisons and run/cost records.
Integrated through the Codex builder brief and a required process supplement; applied the checklist to the auction project.
No new models, engine migration, historical performance claim or trading change.
Scope is documented workflow enforcement for future work; existing scripts were not retroactively audited.

## Comparison

| Area | Existing practice | Difference now |
|---|---|---|
| Evidence boundary | Plans before returns; design/validation gates | Explicitly distinguish exploration, protocol changes and implementation reruns |
| Data timing | Point-in-time cautions, strong auction-specific checklist | Standard event/availability/decision/fill fields for every applicable project |
| Time-series evaluation | Walk-forward and train/design separation | Explicit label-end maturity, overlap purging and justified buffers |
| Preprocessing | No universal checklist covering every fitting operation | Scalers, imputation, feature selection and fitted universe rules restricted to each training fold |
| Baselines | Random controls and account base/add/replace/empty-slot | Same-window price/calendar baseline; simple linear baseline before complex ML |
| Reproducibility | Committed scripts, plans and outputs; some hashes/seeds | Standard manifest covering data, code, settings, exclusions, seeds and environment |
| Costs | Commission/slippage, stresses and real-fee corrections | Consistent gross-to-net bridge, availability delay and native micro fee disclosure |
| Account objective | Apex bootstrap, personal capital ladder | Retained: Jansen's generic portfolios do not replace account-specific accounting |

Existing overlap was checked against DEVELOPMENT_PROCESS.md, BUILDER_BRIEF.md, evidence template and spy_close_imbalance_data_gate.md. These additions standardize practices partly present already; absence of a universal checklist is not proof that every prior study leaked information.

## Changes made

- Added agents/codex/RESEARCH_CONTROLS.md as an adopted Codex operating supplement.
- Added a mandatory read/application hook to the latest remote BUILDER_BRIEF.md without overwriting concurrent work.
- Added a concrete no-return application checklist for SPY auction research inside the supplement.
- Preserved the source code/market-data acquisition blockers, existing trial budget and cheap-screen gates.
- No packages installed, strategy rules tuned, returns computed or live monitoring changed.

The source inspection covers the current public README and chapter 6/11 guides, not the entire book or every notebook. Sources are linked in the supplement. We did not import Jansen's libraries or copy notebooks. Automated validators can be added when an actual data/model pipeline supplies the required timestamps; this change does not claim machine enforcement.

Tell Claude: read agents/codex/RESEARCH_CONTROLS.md and this comparison; the shared DEVELOPMENT_PROCESS.md was not edited.
