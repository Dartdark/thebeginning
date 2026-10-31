# Research controls supplement — adopted 2026-10-26

Applies to future Codex research alongside BUILDER_BRIEF.md, USER_CODE_WORKFLOW.md and DEVELOPMENT_PROCESS.md. User authorized useful Jansen process integration. Existing evidence/preregistration, five-variant budget, cheap-screen stop rules, promotion gates and write/live boundaries remain binding.

## Required additions to each applicable preregistration/report

1. **Information clock:** record event_time, available_at (publication/receipt plus justified delay), decision_time and first executable fill. A feature must satisfy available_at <= decision_time. Historical revisions and retrospective pattern labels retain separate knowledge times. Unverified availability is a data blocker.
2. **Label maturity and split boundaries (learned models only):** record label_start and label_end; training outcomes must have matured before fit_time. Purge training examples whose outcome intervals overlap validation; specify any additional dependence/feature buffer and its rationale. Shared past feature history alone is not automatically leakage. No shuffling time-series splits.
3. **Fold-local fitting:** fit scalers, missing-value treatment, feature selection, universe selection and model parameters on training data only. Tune within inner chronological folds when needed; report outer-fold performance separately. Unchanged fixed rules do not acquire an ML pipeline requirement.
4. **Baseline ladder:** compare the new feature against the same-window price-only or calendar-only rule, and ML against a simple frozen linear/logistic baseline. Compare identical eligible universes, holding periods, cost assumptions and actual integer sizing. A higher IC/accuracy does not establish higher net P&L or account contribution.
5. **Run identity:** retain candidate/family ID, preregistration commit, code SHA, input hashes and versions, data/schema eras, fixed settings/costs, sample counts, exclusions/unresolved paths, random seeds, dependency versions and result paths. Separate implementation reruns from new parameter/mechanism trials; reruns do not erase earlier looks.
6. **Decision-to-fill cost bridge:** report gross P&L, commission, spread/slippage, latency assumptions and native micro costs separately without double counting. Show breakeven extra cost per trade and a prespecified execution stress. Unresolved fills remain visible; reconcile trade totals to daily/account totals.
7. **Evidence boundary:** mark exploration, design selection and final evaluation explicitly. Already-seen 2023+ stays historical validation. A changed trading protocol, universe or feature availability is a substantive change, not a harmless new parameter. Register changes before new returns.

## Apply now: SPY auction project

Before any return study, the existing spy_close_imbalance_data_gate.md additionally requires:
- Feature clock table for imbalance, indicative/reference prices, prior-auction denominator and ES quotes; vendor capture time is not local receipt.
- Schema-era flag for the 2025-11-13 Arca quantity-definition change; no hindsight harmonization chosen on returns.
- Price-only comparator and one simple signed-imbalance baseline, frozen before a larger model.
- Label interval ending at the frozen liquidation time; adjacent observations from the same auction must not become independent train/test samples.
- Run manifest and gross-to-net bridge above. Two sample days can establish parsing, not validate profitability.

These are Codex operating requirements, not amendments to shared trading allocations or permission to trade. Human-readable checks are required now; automated enforcement across historical scripts is not claimed.

## Sources and attribution

Adapted from Jansen third-edition public chapter guides, inspected 2026-10-26:
https://github.com/stefan-jansen/machine-learning-for-trading/tree/main/06_strategy_definition
https://github.com/stefan-jansen/machine-learning-for-trading/tree/main/11_ml_pipeline
Our explicit timestamp fields, manifest checklist and auction application are local implementation choices, not verbatim Jansen requirements.

## Retained comparison lesson — user, 2026-10-30

From [SSRN6656198 review](results/ssrn6656198_review.md): at an already-authorized comparison, record incumbent and eligible frozen alternative code/rule versions, each evidence cutoff, common-date coverage and live-versus-paper status. Execution health does not establish comparative superiority; missing observations are not no-trade days. Preserve enough specification and provenance to revisit a serious alternative under its existing checkpoint/retirement rule. This is a local process adaptation of an untested organizational theory, not demonstrated trading benefit. It does not revive rejected definitions, add monitoring/agents/schedules, or alter trading and research gates. The user explicitly asked to retain the lesson after the review.
