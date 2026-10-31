# Correlation risk-budget study: pre-return review

This is an economics/spec/implementation preflight with maker context, not an independent performance
verdict. No raw strategy returns were inspected by the reviewer. A promising candidate still needs a fresh
spec-only raw-data checker, dependence/selection/placebo checks and valid joint account paths.

- A read-only mechanism screen found the ES–ZN covariance input distinct from the older ES marginal-volatility
  and CTA-trigger models. Sources document risk-parity mechanics, not this NQ trade or its execution clock.
- The two-asset equal-risk weights and K=E1−EV attribution are algebraically consistent: updated marginal
  variances are the same in the full and frozen-correlation models.
- Before any return execution, shared eligibility was clarified to exclude V==0 so every candidate date has
  a VOL30 counterpart. Opposite-side controls share bracket distances/time limits/cost models, while their
  actual stop/target exits and fill costs may differ.
- The common equity-roll guard alone was insufficient for ZN. The preregistration adds a last12Monday–Friday
  Treasury window in February/May/August/November, using a buffer around CME's typical ten-business-day
  window. This is a calendar proxy; actual vendor switch dates and original-contract parity remain unresolved.
- ZN2017 data starts in December. No full-year warm-up is assumed. Actual admissible observations must reach
  60 before the model can signal; later missing inputs do not stretch returns across older available dates.
- The code review found no blocking mismatch: covariance state is emitted before the current-date update;
  2017 references load explicitly and no existing2023–26 price file is loaded during design; attribution,
  shared eligibility, subset controls, 14:30→14:32 clocks and stratified sampling match the plan.
- Synthetic checks passed equal-risk contributions, covariance direction, current/future state invariance,
  missing updates, the actual-count warm-up, zero-V eligibility, roll windows and shared execution checks.

Evidence, plan and runner were committed as5678dde before raw strategy-return execution. No reviewer
modified files, ran return tests, committed code or contacted external people. Covariance can become stale
during guarded/missing intervals; the model calibration, real fund orders/AUM and clock remain assumptions.

After execution, a read-only saved-ledger completion audit reconciled native NQ/MNQ/stress costs, exact
RP30 subsets, entry/exit labels, all prior observation dates, zero held gaps and every1,000-path diagnostic.
No new replay or returns were run by the reviewer. VOL30's $426/NQ was negative after nativeMNQ costs;
all candidate whole-strategy returns were negative. Neither this audit nor the preflight promotes a strategy.

The completion audit confirmed an algebraically redundant threshold that the preflight missed:
|F|>=0.01 and |K|>=0.5|F| already imply |K|>=0.005. CRB0025 is exactly CRB005. All five evaluations remain
counted, but new unique rules number four. The original preregistration/gate/binding remain unchanged;
design_trial_count_audit.json corrects projected59unique to actual58unique across60evaluations. The
253-trial conservative lower bound still counts every evaluation. No post-return economic rule change.
