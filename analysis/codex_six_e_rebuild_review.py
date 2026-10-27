"""Review retained design arithmetic only; no new inputs/returns or selection."""
from pathlib import Path
import json
import sys
import numpy as np
import pandas as pd
import codex_six_e_rebuild as E


def main():
    p=E.OUT/"design";out=E.OUT/"review"
    if out.exists():raise ValueError("Retained review exists")
    out.mkdir()
    gross=pd.read_csv(p/"gross_screen.csv");rows=[]
    for model in [*E.LEGS,"OwnEURControl","Package"]:
        d=pd.read_csv(p/(model+"_daily.csv"));t=pd.read_csv(p/(model+"_trades.csv"));o=pd.read_csv(p/(model+"_orders.csv"))
        g=gross[gross.model==model].iloc[0]
        np.testing.assert_allclose(t.net.sum(),d.net.sum(),atol=1e-5)
        np.testing.assert_allclose(d.gross.sum(),g.total_gross,atol=1e-5)
        np.testing.assert_allclose(d.net,d.gross-d.projection_slippage-d.fees,atol=1e-6)
        if len(o):
            np.testing.assert_allclose(o.fee,o.delta.abs()*1.20,atol=1e-9)
            assert o.delta.sum()==0
            assert (o.target%1==0).all()
        cost=float(d.projection_slippage.sum()+d.fees.sum())
        actual=cost/g.equivalent_RT_units if g.equivalent_RT_units else None
        rows.append(dict(model=model,total_gross=g.total_gross,total_net=d.net.sum(),actual_execution_cost=cost,
            RT_units=g.equivalent_RT_units,gross_per_RT=g.gross_per_equivalent_RT,
            nominal_2x_cost_hurdle=9.80,actual_2x_cost_hurdle=2*actual if actual else None,
            nominal_gross_pass=bool(g.gross_gate_pass),actual_cost_gross_pass=bool(g.total_gross>=2*cost)))
    E.csv(out/"actual_cost_gross_screen.csv",pd.DataFrame(rows))
    source=pd.read_csv(p/"daily_inputs.csv",parse_dates=["date"]).set_index("date")
    features=pd.read_csv(p/"features_and_targets.csv",parse_dates=["date"]).set_index("date")
    q,ends=E.targets(E.features(source),offline_boundaries=True)
    q[source.index.year<2018]=0
    expected=features[[n+"_target" for n in (*E.LEGS,"OwnEURControl")]].to_numpy(int)
    np.testing.assert_array_equal(q,expected)
    assert not features.index.year.max()>2022
    old=json.loads((p/"completed.json").read_text());assert not old["design_gate_pass"]
    assert json.loads((E.ROOT/"agents/codex/research/strategy_hunt_v2_progress.json").read_text())["budget"]["hypotheses_started"]==10
    E.dump(out/"result_integrity.json",dict(passed=True,financial_returns_recomputed=False,
        all_8_FIFO_cash_mark_ledgers_reconciled=True,frozen_targets_match_predata_run=True,
        original_executed_local_code_commit="fe0b52277a81840b59460ea416693ae3baa6ebe2",
        original_executed_public_code_commit="c4a8fc51443dab854543cd2b046bbb7a98db1921",
        postrun_API_change="Offline boundary liquidation is now an explicit opt-in; causal target API default has prefix invariance. Design runner still opts in, reproducing identical retained targets.",
        current_code_sha256=E.sha(Path(E.__file__)),original_code_sha256=json.loads((p/"pre_value_binding.json").read_text())["code"]["analysis/codex_six_e_rebuild.py"],
        actual_cost_screen_addendum="Nominal raw screen excludes extra grid projection; RSI passes nominal9.80 but fails 2x actual reconciled execution cost.",
        promotion_authorized=False,fresh_independent_raw_spec_checker=False,future2023_data_read=False))
    print(pd.DataFrame(rows).to_string(index=False))


def side_years():
    p=E.OUT/"design";rows=[]
    for model in [*E.LEGS,"OwnEURControl","Package"]:
        t=pd.read_csv(p/(model+"_trades.csv"),parse_dates=["date"])
        d=pd.read_csv(p/(model+"_daily.csv"),parse_dates=["date"])
        for year in range(2018,2023):
            days=pd.DatetimeIndex(d.loc[d.date.dt.year==year,"date"])
            for side in (1,-1):
                sub=t[t.side.eq(side)&t.date.dt.year.eq(year)]
                realized=sub.groupby("date").net.sum().reindex(days,fill_value=0.)
                rows.append(dict(side="long" if side==1 else "short",
                    basis="realized unit PnL by exit-year; not daily side-marked equity",
                    **E.metrics(realized,sub,model,str(year))))
    E.csv(E.OUT/"review/side_year_metrics.csv",pd.DataFrame(rows))
    print("Saved",len(rows),"diagnostic side/year rows; no new strategy or future inputs.")


if __name__=="__main__":
    side_years() if "--side-years" in sys.argv else main()
