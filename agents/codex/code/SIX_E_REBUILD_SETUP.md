# Independent six-leg euro research engine

Implementation: `analysis/codex_six_e_rebuild.py`.
Run audit: `analysis/codex_six_e_rebuild_review.py`.
Specification: `agents/codex/plans/six_e_rebuild_20261027.md`.
Result: `agents/codex/results/six_e_rebuild_20261027.md`.

This is a Python research build, not MultiCharts/live code or a reproduction of
the absent author implementation. The first frozen design FAILED. No2023+run,
personal-plan addition or PowerLanguage draft is approved by that result.

Use the existing research Python environment with numpy,pandas,numba/scipy and
the repository's shared Grid24/calendar/metrics/resampling modules. No new paid
data, account, credentials or dependencies outside those research packages.

Synthetic checks (no market input):

```
/workspace/venvs/thebeginning/bin/python -B analysis/codex_six_e_rebuild.py --selftest
```

The retained first design used local preregf85b93a and public prereg
efe8fbabd1311a73123d585e924e205a58fa4928. Both contain the SAME frozen plan.
The runner binds code and source hashes before prices; it refuses to overwrite
`analysis/outputs/codex_six_e_rebuild_20261027/design/`. Preserve that evidence.
An explicitly requested reproducibility replay belongs in a disposable research
copy with its own retained output/run identity, never an overwrite or retune.

Pure interfaces:

- `features(daily)`: synchronized scheduled-cut inputs; rolling/lagged features.
- `targets(feature_frame)`: causal integer virtual targets by default.
- `targets(..., offline_boundaries=True)`: DATA-segment diagnostic used ONLY by
  the registered research runner; cannot be used as a live outage predictor.
- `ledger(prices, quantities, ready, dates, model)`: integerFIFOcash/mark/order
  accounting, with flat source boundaries predeclared by the caller.
- `order_price(raw, side)`: adverse M6Etick projection of the6Eproxy print.

No source timestamp/contract-roll/nativeM6Efill certification is supplied by
these interfaces. The original5%vol target is interpreted on EURnotional returns,
not personal-account equity. The six components net into one broker position;
do not send six independent accounts/orders or size from a smooth selected curve.
