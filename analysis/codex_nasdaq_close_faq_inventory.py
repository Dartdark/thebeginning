"""FAQ evidence inventory only: calendars, PDF provenance, occupancy, volume and assumed power.

No OHLC fields, auction signals, candidate returns, strategy caches or account simulations.
"""
from pathlib import Path
import hashlib
import json
import math
import subprocess

import exchange_calendars as xcals
import numpy as np
import pandas as pd

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/"analysis/outputs/codex_nasdaq_close_faq"
INPUT=ROOT/"agents/codex/inputs/nasdaq_closing_faqs"
MAP=ROOT/"analysis/outputs/codex_sge_delivery_screen/roster_minute_occupancy.csv"


def digest(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def main():
    OUT.mkdir(parents=True,exist_ok=True)
    cal=xcals.get_calendar("XNYS",start="2017-01-01",end="2023-01-03")
    s=cal.schedule.loc["2018-01-01":"2022-12-31"].copy()
    closes=pd.to_datetime(s.close).dt.tz_convert("America/New_York")
    regular=s[closes.dt.hour.eq(16)].copy()
    dates=regular.index.tz_localize(None) if regular.index.tz is not None else regular.index
    weights=pd.Series(dates.weekday).value_counts().sort_index().to_dict()
    owned=[]; hashes={}
    for year in range(2018,2023):
        p=ROOT/f"data/NQ_1min_{year}.csv"
        x=pd.read_csv(p,usecols=["date","time","volume"])
        x=x[x.time.eq(1500)].copy() # bar closing 15:00 spans the proposed final cash minute
        assert not x.date.duplicated().any()
        x["day"]=pd.to_datetime(x.date.astype(str),format="%Y%m%d")
        x=x[x.day.isin(dates)]
        owned.append(x[["day","volume"]]); hashes[str(p.relative_to(ROOT))]=digest(p)
    v=pd.concat(owned,ignore_index=True).set_index("day").reindex(dates)
    v.index.name="date"
    v.to_csv(OUT/"nq_final_minute_volume.csv")
    m=pd.read_csv(MAP)
    details=[]
    for weekday,g in m.groupby("weekday"):
        # Conservative inclusive endpoints from the saved map; no event conditioning.
        use=g[g.minute.between(899,900)]
        assert len(use)==2
        details.append(dict(weekday=int(weekday),day=g.day.iloc[0],map_dates=int(g.dates.iloc[0]),
            regular_cash_dates=int(weights[weekday]),flat_fraction=float(1-use.any_open_fraction.mean()),
            any_position_fraction=float(use.any_open_fraction.mean())))
    gaps=pd.DataFrame(details)
    gaps.to_csv(OUT/"occupancy_gap.csv",index=False)
    n_reference=int(len(regular)*.2)
    n_base=int(n_reference*.5)
    power=[]
    for n,label in [(n_reference,"assumed_20pct_frequency_case"),(n_base,"50pct_persistence_planning_case")]:
        for sd in (300.,600.):
            net=2*sd/math.sqrt(n)
            power.append(dict(case=label,n=n,assumed_sd=sd,net_for_t2=net,
                gross_for_t2=net+17.25,gross_points_for_t2=(net+17.25)/20,
                baseline_round_trip=17.25,gross_floor_1_5_cost=25.875))
    pd.DataFrame(power).to_csv(OUT/"planning_power.csv",index=False)
    metadata={}
    for name in ("openclose_faqs.pdf","ClosingCrossfaq.pdf"):
        p=INPUT/name
        extracted=subprocess.check_output(["pdftotext","-layout",str(p),"-"],text=True)
        p.with_suffix(".txt").write_text("\n".join(line.rstrip() for line in extracted.rstrip().split("\n"))+"\n")
        info=subprocess.check_output(["pdfinfo",str(p)],text=True)
        fields=dict(line.split(":",1) for line in info.splitlines() if ":" in line)
        metadata[name]=dict(sha256=digest(p),pages=int(fields["Pages"]),
            creation=fields.get("CreationDate","").strip(),modified=fields.get("ModDate","").strip(),
            text_sha256=digest(p.with_suffix(".txt")))
    median=float(v.volume.median())
    # An explicit scenario, not an observed QQQ imbalance or actual NQ hedge requirement.
    scenarios=[]
    for eta in (0.,.25,1.):
        contracts=100_000_000*eta/(20_000*20)
        scenarios.append(dict(hypothetical_qqq_imbalance_usd=100_000_000,assumed_nq_level=20_000,
            assumed_hedge_fraction=eta,hypothetical_nq_contracts=contracts,
            fraction_of_observed_median_minute_volume=contracts/median))
    manifest=dict(source_commit="b2c8d74",plan_commits=["499f12f","10bd236"],
        trials=0,candidate_returns_computed=False,price_columns_read=False,caches_built=False,purchases=0,
        historical_noii_messages_owned=False,free_2018_archive_verified=False,
        pdfs=metadata,design_cash_sessions=len(s),regular_1600ET_sessions=len(regular),
        excluded_early_close_sessions=len(s)-len(regular),
        regular_sessions_by_year={int(k):int(z) for k,z in pd.Series(dates.year).value_counts().sort_index().items()},
        final_minute_bars_present=int(v.volume.notna().sum()),final_minute_bars_missing=int(v.volume.isna().sum()),
        median_final_minute_nq_contracts=median,p10_final_minute_nq_contracts=float(v.volume.quantile(.1)),
        gap_fraction_weighted_by_regular_sessions=float(np.average(gaps.flat_fraction,weights=gaps.regular_cash_dates)),
        gap_fraction_weighted_by_saved_map_dates=float(np.average(gaps.flat_fraction,weights=gaps.map_dates)),
        gap_interpretation="weekday-marginal inclusive endpoints only; not auction-event-conditioned or whole-window joint probability",
        n_planning_at_20pct_frequency=n_reference,n_planning_with_half_persistence=n_base,
        hypothetical_flow_scenarios=scenarios,power=power,
        timing=dict(snapshot_1_ET="15:55:10",snapshot_2_ET="15:58:10",decision_CT="14:58:10",entry_CT="14:59:00",exit_CT="15:00:00",decision_to_entry_seconds=50),
        source_sha256={str(MAP.relative_to(ROOT)):digest(MAP),**hashes},
        limitations=["XNYS calendar proxies normal Nasdaq cash closes; verify Nasdaq-specific halts/schedules before any test",
            "SDs, extreme fraction, persistence fraction, dollar imbalance and hedge fractions are assumptions; rolling ranks do not ensure a fixed 20pct event rate",
            "No observed imbalance size, hedge sign, expected return or causal transmission is established",
            "No message files or receipt timestamps downloaded; historical product documentation is not a coverage audit"])
    (OUT/"inventory.json").write_text(json.dumps(manifest,indent=2)+"\n")
    print(json.dumps({k:z for k,z in manifest.items() if k not in ("source_sha256","pdfs","limitations")},indent=2))


if __name__=="__main__":
    main()
