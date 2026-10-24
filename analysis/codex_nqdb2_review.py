"""NQDB2 static source/default/unit audit. No market returns or account simulation."""
from decimal import Decimal as D
import hashlib
import json
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
INPUT = ROOT/'agents/codex/inputs/nqdb2'
OUT = ROOT/'analysis/outputs/codex_nqdb2_review'


def defaults(text, names):
    inputs=text.split('Inputs:',1)[1].split('Variables:',1)[0]
    return {n:re.search(r'\b'+re.escape(n)+r'\(\s*([^)]*)\)',inputs).group(1).strip() for n in names}


def main():
    s=(INPUT/'source.txt').read_text()
    vb=(INPUT/'vault_break_sp_reference.txt').read_text()
    c=json.loads((INPUT/'context.json').read_text())
    raw=(INPUT/'vault_break_sp_reference.txt').read_bytes()
    assert hashlib.sha1(f'blob {len(raw)}\0'.encode()+raw).hexdigest()==c['current_vb_blob']
    ds=defaults(s,['NoiseMult','BoundaryATRLen','EarliestEntry','LatestEntry','MaxTradesPerDay','VWAPExitBars',
        'TakeProfitDollars','StopLossDollars','VetoMode','CtxDriftLen','CtxDriftThreshPct','FlattenTime',
        'ExitOnBarClose','NumContracts','CutoffDate'])
    dv=defaults(vb,['NoiseMult','AtrDays','FirstDecision','LastEntryTime','FlattenTime','TargetPts','StopPts',
        'MaxTradesPerDay','UseHolidayTimes','EarlyLastEntry','EarlyFlattenTime','NumContracts','FlaggedContracts'])
    flags=dict(
        supplied_header_names_driftbreak_v2='DriftBreak v2' in s,
        uploaded_uses_calendar_date='If Date <> Date[1] then begin' in s,
        uploaded_uses_hl_range='Value1 = SessHigh - SessLow;' in s,
        uploaded_vwap_uses_volume='((High + Low + Close) / 3.0) * Volume' in s,
        current_vb_uses_total_intraday_ticks='if BarType < 2 then BarVol = Ticks else BarVol = Volume;' in vb,
        current_vb_excludes_sunday='DayOfWeek(Date[1]) >= 1 and DayOfWeek(Date[1]) <= 5' in vb,
        current_vb_true_range='MaxList(DayHi, PrevDayClose) - MinList(DayLo, PrevDayClose)' in vb,
        latest_entry_active='and (Time <= LatestEntry)' in s,
        drift_gate_present='If DriftDown then CtxOK = false;' in s,
        brackets_unconditional='SetStopPosition;\nSetProfitTarget(TakeProfitDollars * NumContracts);\nSetStopLoss(StopLossDollars   * NumContracts);' in s,
        exit_on_close_present='SetExitOnClose;' in s,
        uploaded_has_early_close_calendar=any(k in s for k in ['IsEarlyClose','EarlyFlatten','EarlyLastEntry']),
        iog_forced_off=bool(re.search(r'\[\s*IntrabarOrderGeneration\s*=\s*false\s*\]',s,re.I)),
        counter_counts_submissions='DTrades = DTrades + 1;' in s,
        current_vb_counts_completed_trades='TradesToday = TotalTrades - DayStartTrades;' in vb,
        vwap_prev_only_guarded='If CurrentBar <> LastCtxBar then begin' in s,
        exact_veto_already_named_in_tier=bool(c['exact_veto_tier_hits']),
    )
    assert flags['brackets_unconditional'] and flags['latest_entry_active'] and flags['current_vb_true_range']
    assert not flags['uploaded_has_early_close_calendar'] and not flags['iog_forced_off']
    units=[]
    for symbol,pv in [('NQ',D(20)),('MNQ',D(2))]:
        for qty in (1,2):
            units.append(dict(symbol=symbol,contracts=qty,point_value=str(pv),
                target_points=str(D(ds['TakeProfitDollars'])/pv),stop_points=str(D(ds['StopLossDollars'])/pv),
                nominal_position_target_usd=str(D(ds['TakeProfitDollars'])*qty),
                nominal_position_stop_usd=str(D(ds['StopLossDollars'])*qty)))
    # Invented closes, not historical returns. Default veto allows a small negative drift.
    examples=[]
    for now in (D(9980),D(9995),D(10020)):
        drift=(now-D(10000))/D(10000)*100
        examples.append(dict(previous_close='10000',current_close=str(now),drift_percent=str(drift),
                             default_veto=drift<=-D(ds['CtxDriftThreshPct'])))
    assert [x['default_veto'] for x in examples]==[True,False,False]
    times=[(m//60)*100+m%60 for m in range(0,1440,30)]
    upload_times=[t for t in times if int(ds['EarliestEntry'])<=t<=int(ds['LatestEntry']) and t<int(ds['FlattenTime'])]
    vb_times=[t for t in times if int(dv['FirstDecision'])<=t<int(dv['LastEntryTime'])]
    assert upload_times==vb_times and upload_times[-1]==1400
    assert '$82' in c['prior_v8_row'] and '$92' in c['prior_v8_row']
    out=dict(verdict='WATCH as a Vault Break variant; NEEDS DATA for exact-source validation',
        new_strategy_return_trials=0,account_simulations=0,context=c,
        input_sha256={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(INPUT.iterdir()) if p.is_file()},
        script_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        upload_defaults=ds,current_vb_source_defaults=dv,source_flags=flags,
        drift_window_minutes=int(ds['CtxDriftLen'])*30,vwap_exit_consecutive_minutes=int(ds['VWAPExitBars'])*30,
        window_minutes_are_nominal_bar_durations=True,
        regular_half_hour_grid={'upload_decisions':upload_times,'current_vb_decisions':vb_times,
                               'same_normal_entry_times':upload_times==vb_times},
        cutoff_calendar_yyyymmdd=int(ds['CutoffDate'])+19000000,unit_examples=units,
        static_veto_examples=examples,illustrations_are_not_measured_returns=True,
        prior_variant_reported={'name':'Bridge VaultBreak v8','mean_per_nq':'82','old_v1_mean_per_nq':'92',
            'pf':'1.23','old_v1_pf':'1.26','not_results_for_this_upload':True},
        performance_report_and_selection_registry_supplied=False,
        required_next_evidence=['Original untrimmed header and chart session/template, IOG, volume and fill settings',
            'Existing exact-version MultiCharts report and timestamped trade export',
            'Frozen veto/selection history; price data already exists, split-volume or MC parity resolves VWAP'],
        references=['https://www.multicharts.com/trading-software/index.php?title=Volume',
                    'https://www.multicharts.com/trading-software/index.php?title=SetExitOnClose',
                    'https://www.multicharts.com/trading-software/index.php?title=SetStopLoss'])
    OUT.mkdir(parents=True,exist_ok=True)
    (OUT/'summary.json').write_text(json.dumps(out,indent=2)+'\n')
    print(json.dumps({k:out[k] for k in ['verdict','new_strategy_return_trials','account_simulations',
        'drift_window_minutes','unit_examples']},indent=2))


if __name__=='__main__':
    main()
