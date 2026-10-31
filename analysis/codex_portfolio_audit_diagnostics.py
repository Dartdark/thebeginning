"""Descriptive attribution and source/size checks; no new allocation or return search."""
from codex_portfolio_audit_config import *
import numpy as np
import pandas as pd
import sys
sys.path.insert(0,str(SOURCE/"analysis"))
import metrics as M

meta=dict(np.load(RUNTIME/"dates_atr.npz"));dates=pd.to_datetime(meta["dates"].astype(str))
side_rows=[];size_rows=[];retention=[];concentration=[]
for home,plan in ROSTERS.items():
    daily=pd.read_csv(OUT/f"{home}_main_daily.csv",parse_dates=["date"]).set_index("date")
    admitted=daily.admitted
    total=daily.loc[admitted,"net"]
    sides={1:pd.Series(0.,index=dates),-1:pd.Series(0.,index=dates)}
    closed={1:[],-1:[]}
    by_asset={"NQ":pd.Series(0.,index=dates),"ES":pd.Series(0.,index=dates),"CL":pd.Series(0.,index=dates)}
    for key,spec in plan.items():
        base=spec[1]/(meta["atr"]*spec[2]*2) if isinstance(spec,list) else np.full(len(dates),spec)
        q=np.floor(base+1e-9)
        t=pd.read_csv(OUT/f"{key}_unit_ledger.csv",parse_dates=["date"])
        t=t[t.date.isin(dates[admitted.to_numpy()])].copy()
        lookup=pd.Series(q,index=dates);t["lots"]=t.date.map(lookup)
        t["net"]=(t.gross-SCENARIOS["main"][0]*t.fee_units-t.slippage_one_tick)*t.lots
        for side in [1,-1]:
            z=t[(t.side==side)&(t.lots>0)]
            sides[side]+=z.groupby("date").net.sum().reindex(dates,fill_value=0.)
            closed[side].extend(z.net.tolist())
        for asset,z in t.groupby("market"):
            by_asset[asset]+=z.groupby("date").net.sum().reindex(dates,fill_value=0.)
        unit=dict(np.load(RUNTIME/f"{key}.npz"));all_t=pd.read_csv(OUT/f"{key}_unit_ledger.csv")
        risk_complete=unit["valid"]
        all_dates=pd.to_datetime(all_t.date);ix=dates.get_indexer(all_dates)
        retention.append(dict(home=home,component=key,recorded_unit_trades=len(all_t),
            trades_on_known_book_days=int(all_dates.isin(dates[admitted.to_numpy()]).sum()),
            trades_on_complete_component_days=int(risk_complete[ix].sum()),
            trades_missing_any_held_quote=int((all_t.missing_held_bars>0).sum()),
            missing_held_bars=int(all_t.missing_held_bars.sum()),
            max_missing_bars_per_trade=int(all_t.missing_held_bars.max()),
            closed_cash_known_does_not_certify_minute_adverse=True))
        # Static sizing displays source ambiguity without running a competing allocation.
        if not isinstance(spec,list):
            for f in [.5,.75,1.]:
                legacy=int(np.floor(spec*f+1e-9));actual_input=int(np.floor(spec))
                size_rows.append(dict(home=home,component=key,source_full_size=spec,f=f,
                    inherited_floor_after_fractional_intent=legacy,
                    integer_full_size_input=actual_input,
                    floor_after_integer_full_size_input=int(np.floor(actual_input*f+1e-9)),
                    ambiguous=not float(spec).is_integer()))
    assert np.allclose((sides[1]+sides[-1]).loc[admitted],total)
    for side in [1,-1]:
        x=sides[side].loc[admitted];r=M.perf(x,closed[side],capital=10000)
        peak=np.maximum.accumulate(np.r_[0.,x.cumsum()])[1:]
        r.update(net=x.sum(),max_dd=float((peak-x.cumsum()).max()),home=home,side="long" if side==1 else "short",
                 t_daily=float(x.mean()/x.std()*np.sqrt(len(x))) if x.std()>0 else None,
                 annualized_native_cash=float(x.mean()*252),sizing="full-size baseline, not account-cushion-adjusted")
        side_rows.append(r)
    for asset,x in by_asset.items():
        x=x.loc[admitted]
        concentration.append(dict(home=home,market=asset,net=x.sum(),annual=x.mean()*252,
            covariance_share_of_daily_portfolio_variance=x.cov(total)/total.var(),
            standalone_daily_vol=float(x.std()),definition="Cov(asset daily P&L,total)/Var(total); can be negative or >1"))
pd.DataFrame(side_rows).to_csv(OUT/"long_short_attribution.csv",index=False)
pd.DataFrame(size_rows).to_csv(OUT/"fixed_lot_sizing_audit.csv",index=False)
pd.DataFrame(retention).to_csv(OUT/"trade_coverage_retention.csv",index=False)

P=pd.read_csv(OUT/"personal_main_components.csv",index_col=0,parse_dates=True)
P=P.loc[P.admitted].drop(columns="admitted");total=P.sum(axis=1)
groups={"NQ_only":P.drop(columns=["CLSundayFade_perMCL","ESMOCFollow_perMES","S30"]).sum(axis=1),
        "ES_only":P.ESMOCFollow_perMES,"CL_only":P.CLSundayFade_perMCL,"S30_NQ_ES_mixed":P.S30}
for market,x in groups.items():
    concentration.append(dict(home="personal",market=market,net=x.sum(),annual=x.mean()*252,
        covariance_share_of_daily_portfolio_variance=x.cov(total)/total.var(),standalone_daily_vol=x.std(),
        definition="Cov(group daily P&L,total)/Var(total); S30 cannot be falsely split into NQ/ES without its marked component ledgers"))
pd.DataFrame(concentration).to_csv(OUT/"market_concentration.csv",index=False)

dump(OUT/"structural_findings.json",dict(
    current_source=SOURCE_COMMIT,
    source_plan_reversion="6082472: VB2/1 and T fade on50K; DT2 on150K; ST remains personal",
    source_document_conflict="FUNDED_PLAN T_ONESIDE row says REVERTED but NEW_CHAT_BRIEF and current cushion table explicitly retain T; baseline follows those current inputs",
    evaluation_VB_risk_before_fees={"stop_points":75,"50K_8MNQ":1200,"150K_20MNQ":3000},
    latest_brief_50K_cushion=1064,
    fiftyK_full_size_VB_stop_exceeds_reported_cushion=True,
    personal_contract_legs={"NQ":17,"ES":2,"CL":1,"strategy_labels":19},
    personal_identity_limits=["Twin v1 ledger is not literal current v2.1","Kusho weekend/overnight P&L remains exit-day booked",
        "continuous-contract rolls/actual micro quotes and margin solvency not certified",
        "personal printed core ladder16 pieces predates ST and PAPERTREND additions; current ex-S30 is18 strategy labels"],
    account_model_limits=["sparse missing adverse quotes are not actual zero losses",
        "per-strategy same-market long/short adverse extrema can be mutually inconsistent within a minute",
        "no broker-level netting/order routing, account position caps or rejected-order execution modeled",
        "source risk budget uses proxy prior15-day Grid24 ATR, not per-trade logged MC StopPts",
        "current Apex terms were not independently reverified; account tools retain source rule assumptions",
        "historical ledger and resampled estimates do not establish future edge or current live-account odds"],
    decisions="No live change; no removal/resizing/new allocation selected from these attributions"))
print("DIAGNOSTICS COMPLETE")
