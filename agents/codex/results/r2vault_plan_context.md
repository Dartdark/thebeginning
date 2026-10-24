# R2Vault: current-plan and adapter inventory

Summary: All five plan baselines remain unchanged at Claude revision `172322e`.
Forty-seven pinned source/input blobs match the previous reviewed Anson context.
The expanded baseline cache hash matches; no market cache or baseline needs rebuilding.
No prior exact R2Vault strategy was found, and no new R2Vault returns were calculated.

Source evidence: `analysis/outputs/codex_r2vault/context_inventory.json`.
Previous source pin: `e34d71c`; current context: `172322e5151f45e2cbf1da4dbd9efb20ba12d1a9`.

| Context | Current baseline and adapter |
|---|---|
| 50K evaluation | VB8, ONB ADX30 risk1100, Bridge2, EOS risk500; `codex_anson_plan.evaluation_parts` |
| 150K evaluation | VB20, ONB risk2750, Bridge5, EOS risk1250; integer quantities calculated after dollar-risk scaling |
| 50K funded | VB2/1, ONB ML risk400, Monday1, EOS risk700, LDF2, NFP risk500, Bridge1, CLS2, MOC2, RS longs1; cushion reference1500 |
| 150K funded | Non-RS 50K roster scaled1.5, RS both sides1, Dual Thrust2; fractional full-size bases retained before cushion rounding, reference3000 |
| Personal | Current14 pieces and starter setsA–D; published legacy fees, Twin16:00 daily marks, Overnight Anomaly and Dual Thrust; `codex_anson_personal.py` |

The ignored prepared cache `agents/codex/runtime/anson_plan.pkl` remains SHA256
`f5856163feab7b28315be7a3564c455d8dc8ec42429bf4cd66521817ce3fcf99`.
Load it under `codex_anson_plan.pinned_imports` so canonical pickle classes resolve
to the pinned modules. RS and Dual Thrust additions were already reconciled against
their committed ledgers. Reuse the exact funded lookup and original-simulator
parity checks from `codex_anson_accounts.py`; supply R2Vault-specific execution
paths and explicit run configuration rather than duplicating the account engine.

Inherited limits remain: approximate CL/MOC intraday paths, the small unresolved
50K published-reference gap, account-specific evaluation tie handling, fractional
150K funded bases and the personal fee/Twin-version approximations. The corrected
150K evaluation sizes differ from the old fractional-size published benchmark.

Repository searches found no R2Vault/R2_Vault/RSquare/576-regression strategy in the
current code, ranked list or watchlist. Vault Break is a plausible replacement-slot
control because both are momentum breakouts; this is a structural hypothesis, not
a measured correlation or evidence that their rules are identical.

The supplied PDF describes576 closes, R² <=0.030 vault updates, positive slope,
a20% vault-range buffer, three entries/day, a75-point stop and40-point target.
Its R² exit threshold2.00 cannot trigger when R² is bounded0..1. It gives no
explicit session-end flatten; the bar universe, timezone and executable order
details must be frozen in the preregistration. Its2017–2024 author-design sample
cannot be fully reproduced from the existing cache beginning2017-12.
