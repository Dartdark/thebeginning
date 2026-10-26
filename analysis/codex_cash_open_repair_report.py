"""Reconcile and report the frozen standalone design screen; no new return tests."""
from pathlib import Path
from types import SimpleNamespace
import importlib.metadata
import json
import sys

import numpy as np
import pandas as pd

sys.path.insert(0,str(Path(__file__).resolve().parent))
import codex_cash_open_repair as C


def md(frame,cols,formats=None):
    formats=formats or {}
    lines=["| "+" | ".join(cols)+" |","| "+" | ".join("---" for _ in cols)+" |"]
    for _,r in frame.iterrows():
        lines.append("| "+" | ".join(formats[k](r[k]) if k in formats else str(r[k]) for k in cols)+" |")
    return "\n".join(lines)


def causal_synthetic():
    dates=pd.bdate_range("2020-01-02",periods=150)
    def grid(mult,phase):
        o=np.full((len(dates),1440),np.nan);c=o.copy();i=np.arange(len(dates))
        o[:,511]=mult*np.exp(.001*np.sin(i*.7+phase)+.0001*i)
        c[:,900]=mult*np.exp(.001*np.cos(i*.4+phase)+.0001*i)
        return SimpleNamespace(dates=dates.strftime("%Y%m%d").astype(int).to_numpy(),o=o,c=c,
            daily_atr=lambda n:np.full(len(dates),100.))
    g,e=grid(100.,0.),grid(50.,.8)
    base=C.build_features(g,e)
    assert base.eligible.sum()>0
    g.o[120:,511]*=3.;e.c[120:,900]*=.2
    altered=C.build_features(g,e)
    pd.testing.assert_frame_equal(base[base.day<120].reset_index(drop=True),altered[altered.day<120].reset_index(drop=True))
    # Missing preceding cash close must invalidate the relevant current feature.
    g,e=grid(100.,0.),grid(50.,.8)
    probe=base[base.eligible].iloc[0]
    old=int(np.where(g.dates==int(pd.Timestamp(probe.prior_full_date).strftime("%Y%m%d")))[0][0])
    g.c[old,900]=np.nan
    missing=C.build_features(g,e)
    assert missing.loc[missing.day==probe.day,"reason"].iloc[0]=="missing_exact_anchor"
    return dict(passed=True,checks=["changing every future anchor leaves prior emitted features byte-equivalent",
        "missing prior exact close does not reach back to an earlier convenient anchor"])


def main():
    out=C.OUT
    gate=json.loads((out/"design_gate.json").read_text())
    assert not gate["validation_allowed"] and gate["chosen"] is None
    assert not list(out.glob("validation*")),"Failed candidate must not advance"
    metrics=pd.read_csv(out/"design_metrics.csv")
    filters=json.loads((out/"design_filter_controls.json").read_text())
    features=pd.read_csv(out/"design_features.csv",parse_dates=["date"])
    audit=[];micro=[];years=[]
    for model in C.CONFIGS:
        t=pd.read_csv(out/f"design_{model}_trades.csv",parse_dates=["date"])
        assert t.date.max()<=pd.Timestamp("2022-12-31")
        assert (t.j0==511+C.CONFIGS[model][0]).all()
        assert (t.j1<=660).all()
        assert t.day.nunique()==len(t)
        np.testing.assert_allclose(t.pnl,(t.exit-t.entry)*t.side*20.,rtol=0,atol=1e-6)
        np.testing.assert_allclose(t.net,t.pnl-7.25-5*t.slips,rtol=0,atol=1e-6)
        np.testing.assert_allclose(t.net_mnq,t.pnl/10-1.24-.5*t.slips,rtol=0,atol=1e-7)
        expected=metrics[(metrics.model==model)&(metrics.period=="2018-22")&(metrics.side=="all")].iloc[0]
        assert expected.trades==len(t)
        np.testing.assert_allclose(expected.total,t.net.sum(),rtol=0,atol=1e-6)
        audit.append(dict(model=model,tickets=len(t),missing_held_minutes=int(t.unobserved_held_minutes.sum()),
            last_trade=str(t.date.max().date()),calendar_or_deadline_violations=0))
        micro.append(dict(model=model,net_MNQ=float(t.net_mnq.sum()),four_tick_NQ_net=float(t.stress_four_ticks.sum())))
        if model.startswith("R"):
            years.append(t.groupby(t.date.dt.year).net.sum().rename(model))
    C.dump(out/"ledger_checks.json",dict(passed=True,models=audit,independent_raw_replication=False))
    C.dump(out/"causality_checks.json",causal_synthetic())
    C.csv(out/"native_costs.csv",pd.DataFrame(micro))
    C.csv(out/"candidate_yearly_net.csv",pd.concat(years,axis=1).rename_axis("year"),index=True)
    allrows=metrics[(metrics.period=="2018-22")&(metrics.side=="all")]
    sides=metrics[(metrics.period=="2018-22")&metrics.model.str.startswith("R")]
    ff={k:lambda x:f"{x:.2f}" for k in ["profit_factor","sharpe","sortino","calmar","ulcer","t_trade","t_daily","t_nw5","t_nw20"]}
    ff.update({k:lambda x:f"${x:,.2f}" for k in ["total","avg","annual","max_dd"]})
    ff["win"]=lambda x:f"{x:.1%}";ff["trades"]=lambda x:str(int(x))
    p=allrows[allrows.model=="R5_Z1"].iloc[0]
    ft=pd.DataFrame([dict(model=k,**v) for k,v in filters.items()])
    stats_table=md(allrows,["model","trades","win","total","avg","profit_factor","t_trade","t_nw5","max_dd"],ff)
    side_table=md(sides,["model","side","trades","annual","sharpe","sortino","profit_factor","calmar","ulcer","max_dd","t_trade"],ff)
    filter_table=md(ft,["model","removed_trades","removed_net","removed_t","p_random_net_ge_kept","p_kept_better_net_and_dd"],
        {"removed_net":lambda x:f"${x:,.2f}","removed_t":lambda x:f"{x:.2f}",
         "p_random_net_ge_kept":lambda x:f"{x:.1%}","p_kept_better_net_and_dd":lambda x:f"{x:.1%}"})
    micro_table=md(pd.DataFrame(micro),["model","net_MNQ","four_tick_NQ_net"],
        {k:lambda x:f"${x:,.2f}" for k in ["net_MNQ","four_tick_NQ_net"]})
    yearly=md(pd.concat(years,axis=1).rename_axis("year").reset_index(),["year","R5_Z1","R15_Z1","R5_Z2"],
        {k:lambda x:f"${x:,.2f}" for k in ["R5_Z1","R15_Z1","R5_Z2"]})
    counts=features[features.date.dt.year>=2018].reason.value_counts().to_dict()
    report=f"""# NQ Cash-Open Repair: REJECT — new standalone rule fails design; t6 not achieved

Summary: Built a new NQ-only entry rule from raw NQ/ES prices, not a combination of existing strategy trades.
Primary 5-minute rule: {int(p.trades)} design trades, PF {p.profit_factor:.2f}, trade t {p.t_trade:.2f}, daily NW(5) t {p.t_nw5:.2f}.
The 15-minute and stronger-dislocation variants also fail; none qualifies for validation or the requested t6 target.
Five models including two controls were tested; 2023+ returns/account benches were not run.
Reject this hypothesis; no fitted rescue, PowerLanguage, ranking, allocation or live change.

Plan: `agents/codex/plans/cash_open_repair.md`, **a9af875**, committed before new returns.
Evidence: `agents/codex/evidence/cash_open_repair.md`. Scripts: `analysis/codex_cash_open_repair.py`,
`analysis/codex_cash_open_repair_report.py`. Output: `analysis/outputs/codex_cash_open_repair/`.
Current research branch codex/work; latest Claude context5d1096d inspected without merging/editing its files.

## Rule as tested

**Instrument:** NQ; one position, one trade/day. **Timeframes:** 5 or 15 minutes for signals, one-minute fills.

1. At the cash open compare NQ and ES's overnight log returns, each from the preceding full cash session's
   exact15:00 close to today's08:31-labeled open (08:30 wall time, Central).
2. Estimate NQ-on-ES beta, residual mean and residual sample SD using only the preceding60 valid observations.
   Today's normalized NQ-specific deviation is z. No coefficient is fitted to trade profits.
3. If |z|>=1, wait for the first5-minute NQ bar to close. Buy only when NQ underperformed overnight and that
   opening bar rises; short only when NQ outperformed overnight and the opening bar falls.
4. Enter the next native minute open. Stop0.15 and target0.30 times the prior15-day calendar ATR, distances
   rounded up to a quarter-point. Stop/target active on the entry bar; no trail, BE or reentry.
5. Exit by11:00CT. No holiday/early-close entries. The preregistered quarterly-roll window and anchor failures
   skip before entry; no return-based day deletion. ES is an input, never a second traded position.

R15_Z1 uses the first15-minute bar. R5_Z2 uses5minutes and |z|>=2. BASE5/BASE15 follow the first bar on all
same-data/calendar-eligible days without the overnight gate; these controls cannot be selected as new strategies.
This is a new rule relative to the repository's existing RS intraday-continuation and ONB range-breakout entries.
Its underlying inventory/overnight-reversal idea has related prior failures; novelty does not supply an edge.

## Design results: 2018-22 only

Primary NQ costs: **$7.25 round trip plus one adverse tick ($5) per market/stop fill**; target exits have no extra
slippage and require a full point through. Native MNQ fees are separately modeled, not mini fees divided by ten.
Daily sample has1259 scheduled cash sessions, including zero-trade days. Annual metrics use252sessions/year.

{stats_table}

All three candidates fail the committed gate: >=100 trades, positive net, trade t>=2, daily NW5 t>=1.5,
PF>=1.20, at least4 positive design years, positive native-MNQ and four-tick stressed net.
R5_Z2 also has too few trades. No model was chosen; the full-history t6 claim is **not established**.

Whole/long/short metrics:

{side_table}

Yearly net per NQ, all sides:

{yearly}

The primary has only3 of5 positive years. Its long side is stronger (t1.43), still below the gate; selecting
longs after seeing this would be another trial, not a valid rescue. No short-only or long-only candidate was tested.

## Filter and cost controls

{filter_table}

Each filter is compared to1,000 equal-sized random subsets of its unfiltered base. R5_Z1 removes941 trades
that earn$30,307.75 in total; random subsets match or beat its net50.1% of the time. Its greater remaining
average does not establish incremental value. All removed groups make positive aggregate profit.
The stronger gate does not establish an improvement either. Controls share valid-anchor/warm-up/calendar masks,
and every kept trade matches its base's entry, direction and result exactly.

{micro_table}

Native MNQ fee assumption: $1.24 RT plus$0.50 per slipped fill. Four-tick stress retains NQ$7.25 commission
and charges$20 per slipped fill. Positive primary dollar totals are weak relative to uncertainty; they are not a pass.

## Data, clocks and engineering checks

Only raw NQ/ES minute inputs and shared grid/execution/metric/calendar functions are used. No prior strategy
trade list, old portfolio P&L or ML model supplies entries or candidate performance.
Design price arrays are truncated at2022-12-31 before feature generation/execution. No2023+ candidate return,
plot or ranking was generated.2017 provides limited warm-up; the rule waits until60 prior valid observations.
Design eligibility census: {json.dumps(counts,sort_keys=True)}.
Three dates lack exact anchors; no older convenient close or future-filled observation substitutes for them.
Predeclared roll/calendar exclusions are assumptions about valid data, not evidence that each excluded day
contains a contract switch. Continuous prices are not back-adjusted; surviving roll-related artifacts remain possible.

Every candidate has zero unobserved held minutes in this design sample. BASE5 has2, retained/inventoried;
controls are not repaired after outcomes. No source calendar violation or after11:00 exit occurs.
Next-open entries use08:36/08:46close labels, approximately08:35/08:45wall time, respectively.
The11:00exit is a bar-close fill. Stop gap fills use worse observed opens; OHLC minute ordering and actual
MNQ queues remain unverified. Shared engine MAE can include full exit-minute extremes; it is not a tick-path audit.

Synthetic checks cover prior-only features, future-anchor perturbations, missing preceding-close behavior,
calendar/roll guards, warm-up, entry-bar stops, worse gap stops, target-through and initial-zero DD.
Ledger checks reconcile price/quantity/costs, one trade/day, phase boundary and deadline. These are engineering
checks, not independent raw-signal replication, platform confirmation, or a statistical promotion pass.
No shared cache was built; NQ/ES grids existed only in this process. No scientific package was installed.

## Account placement and stopping

| Context | Result |
|---|---|
|50K evaluation|Does not advance: all new candidates fail design. No pass-rate estimate.|
|150K evaluation|Same failed design; no benefit inferred from another account size.|
|50K funded|Does not advance; no payout/blown comparison run.|
|150K funded|Does not advance; no payout/blown comparison run.|
|Personal A-D/current19|Does not advance; no addition/replacement recommendation or uncomputed marginal-benefit claim.|

The cheap-screen stop rule deliberately blocks2023+ validation, full bootstrap/account work and PowerLanguage
after a failed design. No account simulation or forward-log allocation was needed to reject these candidates.
No forced "t6" label, pooled old-strategy return series, fitted weight, changed threshold or post-results clock was used.
Related prior searches (RS, CO-OC, opening momentum, inventory failures) remain disclosed; five models here
are additional trials, not five fresh independent opportunities to claim significance.

## Reproduction and next step

```bash
/workspace/venvs/thebeginning/bin/python -B analysis/codex_cash_open_repair.py --phase design --prereg a9af875
/workspace/venvs/thebeginning/bin/python -B analysis/codex_cash_open_repair_report.py
```

Artifacts are created exclusively and checked against pre-existing bytes. Input hashes and final script/artifact
hashes are saved. No shared plan, root TODO, existing live source, broker/VPS/API setting or other branch was edited.
No validation or parameter search beyond the five frozen configurations. No independent checker/promotion claim.
Recommended next step: discard this hypothesis and research a different information source/mechanism, with a
separate preregistration; do not optimize this design failure into an asserted t6 strategy.
Claude review path: `agents/codex/results/cash_open_repair.md`.
"""
    result=C.ROOT/"agents/codex/results/cash_open_repair.md"
    C.write(result,report)
    files=sorted(p for p in out.rglob("*") if p.is_file() and "numba_cache" not in p.parts and p.name!="final_manifest.json")
    files += [C.ROOT/"analysis/codex_cash_open_repair.py",Path(__file__),result]
    C.dump(out/"final_manifest.json",dict(prereg="a9af875",new_economic_models=5,chosen=None,
        new_validation_runs=0,python=sys.version,
        versions={x:importlib.metadata.version(x) for x in ["numpy","pandas","numba","scipy","openpyxl"]},
        artifacts={str(p.relative_to(C.ROOT)):C.sha(p) for p in files}))
    print("New standalone rule: REJECT. No candidate passes design; no t6 established. Report:",result)


if __name__=="__main__":main()
