"""Five predeclared synthetic admission checks of pinned FinRL 2020 code.

No trained agents, historical strategy returns or performance reconstruction.
Runs inspected original class methods/function bodies using AST and inert stubs.
"""
from pathlib import Path
from types import SimpleNamespace
import ast
import hashlib
import json
import subprocess
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
INPUT = ROOT / "agents/codex/inputs/rl_ensemble_3690996_20261030"
SOURCE = INPUT / "source"
OUT = ROOT / "analysis/outputs/codex_rl_ensemble_3690996_audit"
OUT.mkdir(parents=True, exist_ok=True)
PLAN = "05a3e1b"
subprocess.check_call(["git", "-C", str(ROOT), "cat-file", "-e",
                       PLAN + ":agents/codex/plans/rl_ensemble_3690996_mechanics_20261030.md"])


def dump(name, value):
    (OUT / name).write_text(json.dumps(value, indent=2, default=str, allow_nan=False) + "\n")


def blob(data):
    return hashlib.sha1(("blob " + str(len(data)) + "\0").encode() + data).hexdigest()


tree = {x["path"]: x for x in json.loads((INPUT / "repository_tree.json").read_text())["tree"]}
hashes = {}
for path in SOURCE.rglob("*"):
    if path.is_file():
        rel = str(path.relative_to(SOURCE))
        assert blob(path.read_bytes()) == tree[rel]["sha"], rel
        hashes[rel] = hashlib.sha256(path.read_bytes()).hexdigest()


def environment(path, clsname):
    tree_ast = ast.parse((SOURCE / path).read_text())
    cls = next(x for x in tree_ast.body if isinstance(x, ast.ClassDef) and x.name == clsname)
    env = dict(np=np, pd=pd, gym=SimpleNamespace(Env=object),
               spaces=SimpleNamespace(Box=lambda **kw: SimpleNamespace(**kw)),
               seeding=SimpleNamespace(np_random=lambda seed: (np.random.default_rng(seed), seed)),
               STOCK_DIM=30, HMAX_NORMALIZE=100, INITIAL_ACCOUNT_BALANCE=1_000_000,
               TRANSACTION_FEE_PERCENT=.001, REWARD_SCALING=1e-4)
    exec(compile(ast.Module(body=[cls], type_ignores=[]), path, "exec"), env)
    return env[clsname]


def frame():
    rows = []
    for day, price, opening in [(0, 10., 9.), (1, 20., 99.)]:
        for i in range(30):
            rows.append(dict(day=day, tic=f"T{i:02d}", adjcp=price, open=opening,
                             macd=price, rsi=50., cci=0., adx=20., turbulence=0.))
    return pd.DataFrame(rows).set_index("day")


classes = {label: environment(f"env/EnvMultipleStock_{label}.py", "StockEnv" + name)
           for label, name in [("train", "Train"), ("validation", "Validation"), ("trade", "Trade")]}
result = {"cash_budget": {}, "integer_shares": {}, "sale_fee_counter": {}, "decision_fill_clock": {}}
for label, cls in classes.items():
    obj = cls(frame()); obj.state[0] = 1000.
    obj._buy_stock(0, 100.)
    assert np.isclose(obj.state[0], -1.) and np.isclose(obj.state[31], 100.)
    result["cash_budget"][label] = dict(cash_after=obj.state[0], shares=obj.state[31],
                                        nonnegative_balance_constraint_passed=False)

    obj = cls(frame()); actions = np.zeros(30); actions[0] = .12345
    obj.step(actions)
    assert np.isclose(obj.state[31], 12.345)
    result["integer_shares"][label] = dict(continuous_action=.12345, actual_shares=obj.state[31],
                                           integer_constraint_passed=False)

    obj = cls(frame()); obj.state[0] = 0.; obj.state[31] = 10.
    obj._sell_stock(0, -10.)
    assert np.isclose(obj.state[0], 99.9) and obj.state[31] == 0 and obj.cost == 0
    fee = 100. - obj.state[0]
    result["sale_fee_counter"][label] = dict(cash_after=obj.state[0], actual_cash_fee=round(fee, 8),
                                             reported_cost=obj.cost, portfolio_cash_charges_fee=True)
    if label != "train":
        obj = cls(frame()); obj.state[0] = 0.; obj.state[31] = 10.; obj.turbulence = 1000.
        obj._sell_stock(0, -1.)
        assert np.isclose(obj.state[0], 99.9) and obj.state[31] == 0 and obj.cost == 0
        result["sale_fee_counter"][label + "_turbulence"] = dict(cash_after=obj.state[0],
                                                                actual_cash_fee=.1, reported_cost=obj.cost)

    obj = cls(frame()); before = obj.state[0]
    actions = np.zeros(30); actions[0] = .01
    observation_close = obj.state[1]
    obj.step(actions)
    fill = (before - obj.state[0]) / obj.state[31] / 1.001
    assert np.isclose(fill, 10.) and np.isclose(obj.state[1], 20.)
    result["decision_fill_clock"][label] = dict(observation_close=observation_close, fill_price=round(fill, 8),
        next_day_open=99., next_day_close=obj.state[1], later_executable_quote_used=False,
        limit="Same close supplies state and fill; no verified post-observation execution clock")

# Group 5: original named turbulence function on invented, full-rank prices.
prep = (SOURCE / "preprocessing/preprocessors.py").read_text()
node = next(n for n in ast.parse(prep).body if isinstance(n, ast.FunctionDef) and n.name == "calcualte_turbulence")
env = dict(np=np, pd=pd)
exec(compile(ast.Module(body=[node], type_ignores=[]), "preprocessing/preprocessors.py", "exec"), env)
rng = np.random.default_rng(3690996)
prices = pd.DataFrame(100 * np.exp(np.cumsum(rng.normal(0, .01, (260, 30)), axis=0)))
invented = prices.rename_axis("datadate").reset_index().melt(id_vars="datadate", var_name="tic", value_name="adjcp")
original = env["calcualte_turbulence"](invented)
i = 254
v = (prices.iloc[i] - prices.iloc[:i].mean()).to_numpy()
expected_levels = float(v @ np.linalg.inv(prices.iloc[:i].cov()) @ v)
returns = prices.pct_change().dropna()
rv = (returns.loc[i] - returns.loc[:i - 1].mean()).to_numpy()
alternative_returns = float(rv @ np.linalg.inv(returns.loc[:i - 1].cov()) @ rv)
observed = float(original.turbulence.iloc[i])
assert np.isclose(observed, expected_levels) and not np.isclose(observed, alternative_returns)
runner = (SOURCE / "run_DRL.py").read_text()
models = (SOURCE / "model/models.py").read_text()
result["source_specification"] = dict(
    synthetic_price_statistic=observed, independently_reconstructed_levels=expected_levels,
    paper_return_based_counterfactual=alternative_returns,
    turbulence_uses_prices_not_paper_returns=True,
    preprocessing_backward_fill_present="fillna(method='bfill'" in prep,
    backward_fill_limit="Static occurrence only; not a measured holdout-leak incidence",
    source_validation_window_63_days="validation_window = 63" in runner,
    source_cutoff_july_7_2020="20200707" in runner,
    paper_validation_months=3, readme_validation_months=12,
    validation_sharpe_daily_scaling_uses_sqrt4="(4 ** 0.5)" in models,
    sharpe_limit="Common positive scale preserves model ranking; not a valid annualized daily Sharpe")

# No-return raw-data census. Do not construct strategy, saved-equity or benchmark returns.
raw = Path("/workspace/scratch/rl3690996/dow_30_2009_2020.csv")
if raw.exists():
    d = pd.read_csv(raw)
    coverage = d.groupby("tic").datadate.agg(["min", "max", "size"])
    coverage.to_csv(OUT / "stock_coverage.csv")
    census = dict(rows=len(d), tickers=int(d.tic.nunique()), dates=int(d.datadate.nunique()),
                  first_date=int(d.datadate.min()), last_date=int(d.datadate.max()),
                  rows_per_date_min=int(d.groupby("datadate").size().min()),
                  rows_per_date_max=int(d.groupby("datadate").size().max()),
                  duplicate_date_ticker_rows=int(d.duplicated(["datadate", "tic"]).sum()),
                  missing_by_column=d.isna().sum().to_dict(), columns=d.columns.tolist(),
                  zero_adjustment_factors=int((d.ajexdi == 0).sum()),
                  positive_prices=bool((d[["prccd", "prcod", "prchd", "prcld"]] > 0).all().all()),
                  constituent_and_corporate_action_identity_verified=False,
                  limit="Raw file availability and shape do not verify paper universe/vintage or executable prices")
    dump("data_census.json", census)

result.update(synthetic_groups=5, source_methods_executed=True, source_git_blobs_verified=True,
              economic_reproduction_admitted=False, new_strategy_return_trials=0,
              historical_training_runs=0, account_simulations=0)
dump("mechanics.json", result)
dump("run_receipt.json", dict(plan_commit=PLAN, source_commit="5b9290ed706efa34aaff96e10761af428a154076",
     source_hashes=hashes, harness_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
     versions=dict(numpy=np.__version__, pandas=pd.__version__), strategy_return_trials=0))
print(json.dumps(result, indent=2))
