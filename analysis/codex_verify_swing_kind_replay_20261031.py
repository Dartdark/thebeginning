"""Reconcile saved paired account histories to reported summaries, without rerunning returns."""
from pathlib import Path
import hashlib
import json
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "analysis/outputs/codex_swing_kind_replay_20261031"
script_sha = hashlib.sha256((ROOT / "analysis/codex_swing_kind_replay_20261031.py").read_bytes()).hexdigest()
checks = {}
for account, cap in ((50, 13000), (150, 20500)):
    meta = json.loads((OUT / f"{account}_run.json").read_text())
    assert meta["script_sha256"] == script_sha
    chunks = [np.load(OUT / f"{account}_chunk_{i}.npz") for i in range(10)]
    assert len({str(x["signature"]) for x in chunks}) == 1
    summary = pd.read_csv(OUT / f"{account}_summary.csv", index_col=0)
    result, year = {}, {}
    for key in meta["plans"]:
        r = np.concatenate([x[key] for x in chunks])
        y = np.concatenate([x[key + "_y1"] for x in chunks])
        assert r.shape == (500, 5) and y.shape == (500,)
        assert np.isfinite(r).all() and np.isfinite(y).all()
        assert (r[:, 0] >= y).all() and (y >= 0).all() and (r[:, 0] <= cap).all()
        assert np.isin(r[:, 3], [0, 1]).all() and np.isin(r[:, 1], np.arange(7)).all()
        assert (r[r[:, 1] == 6, 0] == cap).all()
        expected = dict(y1=y.mean(), y2=r[:, 0].mean(), blown=r[:, 3].mean(),
                        y1_p5=np.percentile(y, 5), y2_p5=np.percentile(r[:, 0], 5),
                        all6_2y=np.mean(r[:, 1] == 6),
                        days6=np.median(np.where(r[:, 1] == 6, r[:, 2], np.inf)))
        for field, value in expected.items():
            assert np.isclose(summary.loc[key, field], value), (account, key, field)
        result[key], year[key] = r, y
    effects = pd.read_csv(OUT / f"{account}_paired_effects.csv")
    for row in effects.itertuples():
        a, b = result[row.a], result[row.b]
        delta = year[row.a] - year[row.b] if row.metric == "y1" else a[:, 0 if row.metric == "y2" else 3] - b[:, 0 if row.metric == "y2" else 3]
        assert np.isclose(delta.mean(), row.mean)
        assert np.isclose(delta.std(ddof=1) / np.sqrt(500), row.mc_se)
        assert np.count_nonzero(delta) == row.changed_histories
    checks[str(account)] = dict(histories=500, plans=5, summaries_reconciled=True,
        paired_effects_reconciled=True, checkpoint_signatures_match=True,
        old_fixed_two_year_outcomes_identical=bool(np.array_equal(result["REPLACE_FIXED"], result["REPLACE_OLD"])),
        old_fixed_two_year_cash_and_failure_identical=bool(np.array_equal(result["REPLACE_FIXED"][:, [0, 1, 3]], result["REPLACE_OLD"][:, [0, 1, 3]])),
        changed_run_duration_histories=int(np.count_nonzero(result["REPLACE_FIXED"][:, 2] - result["REPLACE_OLD"][:, 2])),
        changed_first_payout_day_histories=int(np.count_nonzero(result["REPLACE_FIXED"][:, 4] - result["REPLACE_OLD"][:, 4])),
        changed_first_year_histories=int(np.count_nonzero(year["REPLACE_FIXED"] - year["REPLACE_OLD"])))
checks["all_checks_passed"] = True
(OUT / "verification.json").write_text(json.dumps(checks, indent=2) + "\n")
print(json.dumps(checks, indent=2))
