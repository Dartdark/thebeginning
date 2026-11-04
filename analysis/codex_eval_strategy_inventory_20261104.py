"""Read existing strategy registry/ledger metadata only; no new returns or allocations.

Inputs: current codex/work files and pinned read-only Claude13e29ca snapshot.
Outputs stay in the authorized research-input directory.
"""
from pathlib import Path
import hashlib,io,json,re,subprocess
import pandas as pd

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'agents/codex/inputs/eval_audit_20261104'
REF='13e29ca7b45daabeb0ed2d8c286448610f594dab'

def gitbytes(path):return subprocess.check_output(['git','show',REF+':'+path],cwd=ROOT)

def meta(path,source='local'):
    p=ROOT/path
    try:b=p.read_bytes() if source=='local' else gitbytes(path)
    except (FileNotFoundError,subprocess.CalledProcessError):return {'path':path,'source':source,'available':False}
    r={'path':path,'source':source,'available':True,'bytes':len(b),'sha256':hashlib.sha256(b).hexdigest()}
    if path.endswith('.csv'):
        try:
            d=pd.read_csv(io.BytesIO(b));r.update(rows=len(d),columns=list(d.columns))
            r['date_coverage']={}
            for col in ['date','entry_date','exit_date','entry_at','exit_at']:
                if col in d:
                    x=pd.to_datetime(d[col],errors='coerce')
                    r['date_coverage'][col]={'first':str(x.min()),'last':str(x.max())}
        except Exception as e:r['parse_error']=str(e)
    return r

def main():
    OUT.mkdir(parents=True,exist_ok=True)
    tier=gitbytes('TIER_LIST.md').decode();section='';rows=[]
    for number,line in enumerate(tier.splitlines(),1):
        if line.startswith('## '):section=line[3:].strip()
        if not line.startswith('|') or line.startswith('|---'):continue
        fields=[x.strip() for x in re.split(r'(?<!\\)\|',line)[1:-1]]
        if not fields or fields[0] in ['Item','Tier','**S+**','**S**','**A**','**B**','**C**','**D**','**F**']:continue
        if section not in ['S+','S','A','B','C','D','F']:continue
        if fields[0].startswith('(none'):continue
        rows.append(dict(section=section,line=number,title=fields[0],fields=fields,raw_row=line))
    catalog=dict(scope='Complete ranked registry rows, including papers/methods/account variants and repeated families; not distinct strategies or new trials.',source_commit=REF,source_path='TIER_LIST.md',source_sha256=hashlib.sha256(tier.encode()).hexdigest(),rows=len(rows),entries=rows)
    (OUT/'tier_registry_snapshot_13e29ca.json').write_text(json.dumps(catalog,indent=2,ensure_ascii=False)+'\n')
    ledgers=[meta(str(p.relative_to(ROOT))) for p in sorted((ROOT/'analysis/outputs/codex_portfolio_audit_20261031').glob('*_unit_ledger.csv'))]
    paths=[
      'checks/candidates/fc_2b/trades.csv','checks/candidates/fc_2b/mc_v2_trades_all.csv',
      'checks/candidates/dual_thrust/trades.csv','checks/candidates/dual_thrust/mc_trades.csv',
      'checks/candidates/swing_target/mc_trades_v3.csv','checks/candidates/papertrend/mc_trades_claude.csv',
      'checks/candidates/t_oneside/mc_trades_T_ONESIDE_v2.csv','checks/candidates/relative_strength/trades.csv',
      'checks/candidates/fvb/trades.csv','checks/candidates/s47_v2/mc_trades_S47_v2.csv',
      'checks/candidates/kusho/python_trades_v9_RTH_rolladj.csv','checks/candidates/twin_continuation/trades.csv',
      'checks/candidates/bb_mrm/mc_trades.csv','checks/candidates/overnight_tick/python_trades.csv',
      'checks/candidates/s30_ibs/daily_nq_es_per_micro.csv',
      'analysis/outputs/codex_s03_v2/v2_trades.csv',
      'mc_reports/Backtesting Strategy Performance Report _ @NQ - 15 Minutes NQ Overnight Bias.xlsx',
      'mc_reports/Backtesting Strategy Performance Report _ @NQ - 15 Minutes Overnight Bias ML (funded) v2.xlsx',
      'mc_reports/Backtesting Strategy Performance Report VB v1.xlsx',
      'mc_reports/Backtesting Strategy Performance Report EOS v1.xlsx',
      'mc_reports/Backtesting Strategy Performance Report _ @NQ - 5 Minutes Bridge Monday Longs.xlsx',
      'mc_reports/Backtesting Strategy Performance Report _ @NQ - 5 Minutes Vol-Control Sell Flow.xlsx']
    assets=[meta(p) for p in paths]
    assets += [meta(p,'claude:'+REF) for p in [
      'analysis/outputs/bridge_noise_15m_trades_rth_longs.csv',
      'checks/candidates/bridge_noise_15m_longs/trades.csv',
      'checks/candidates/bridge_noise_15m_longs/fills.csv',
      'checks/candidates/bridge_noise_15m/NQ_Noise_RTH_Anchor.txt']]
    # This record is a routing decision, not a signal-definition search or new grade.
    choices=[
      ('VB','Vault Break','NQ','A','baseline','VB','mc_reports/Backtesting Strategy Performance Report VB v1.xlsx','Existing eval driver; high overlap/correlation needs account replay, not standalone profit selection.'),
      ('ONB30','Plain Overnight Bias ADX30','NQ','A','baseline','ONB30','mc_reports/Backtesting Strategy Performance Report _ @NQ - 15 Minutes NQ Overnight Bias.xlsx','Current eval uses plain ONB ADX30/0.25ATR, not funded ML. Latest losing stretch is not a new independent selection sample.'),
      ('EOS','Expiration Open Short','NQ','A','baseline','EOS','mc_reports/Backtesting Strategy Performance Report EOS v1.xlsx','Rare (~monthly) event; dollar-risk sizing is floored separately per account.'),
      ('BRIDGE','Bridge Monday Long','NQ','A','baseline','BRIDGE','mc_reports/Backtesting Strategy Performance Report _ @NQ - 5 Minutes Bridge Monday Longs.xlsx','Sunday19:00→Monday15:55 within one account session; no source stop; path/overlap and calendar checks required.'),
      ('ONBML','Overnight Bias ML v2','NQ','S','conditional_existing_alternative','ONBML','mc_reports/Backtesting Strategy Performance Report _ @NQ - 15 Minutes Overnight Bias ML (funded) v2.xlsx','High-priority source-supported swap. Preserve original fold/filter training and explicit unfinished open-position row; do not invent a stronger filter.'),
      ('LDF','Late-Day Flow','NQ','A','conditional_existing_alternative','LDF','mc_reports/Backtesting Strategy Performance Report _ @NQ - 5 Minutes Late Day Flow.xlsx','Current funded core, fixed14:00flow rule; late-time footprint differs but still equity beta.'),
      ('MON','Monday Long','NQ','A','conditional_existing_alternative','MON','mc_reports/Backtesting Strategy Performance Report _ @NQ - 5 Minutes NQ Monday Longs.xlsx','Current150Kfunded keeps it;50Kfunded replaced with OT. Apply current holiday exclusions, not historical mis-sized Monday rows.'),
      ('NFP','NFP Fade','NQ','B','conditional_existing_alternative','NFP','mc_reports/Backtesting Strategy Performance Report _ @NQ - 5 Minutes NFP Fade.xlsx','Sparse monthly calendar; observed early loss/offset timing matters more than annual correlation.'),
      ('CLS','CL Sunday up-gap fade','CL','A','conditional_existing_alternative','CLS','funded_strategies/CL_Sunday_Gap_Fade.txt','Principal existing non-equity diversifier. Prior normalized audit flags missing held bars on85/87trades; full native path admission is not automatic.'),
      ('MOC','ES MOC Follow','ES','B','conditional_existing_alternative','MOC','analysis/es_moc_confirm.py','ES adds instrument diversity but remains equity beta;2023+weaker. Original report/fixed raw source needed, not daily curve.'),
      ('RS','Relative Strength NQ/ES','NQ','B','conditional_existing_alternative','RS','checks/candidates/relative_strength/trades.csv','Both/long settings are already separately studied. Preserve beta/Zclock and do not treat daily NQ hedge signal as a second uncorrelated market.'),
      ('DT','Dual Thrust v4','NQ','A','conditional_existing_alternative','DT','checks/candidates/dual_thrust/trades.csv','MCconfirmed. Current150Kfunded DT2retained; prior evaluation swaps/adds were worse or tied. Count all old selection.'),
      ('TOS','T_ONESIDE stopped fade T','NQ','B','conditional_existing_alternative','TOS','checks/candidates/t_oneside/mc_trades_T_ONESIDE_v2.csv','50Kfunded replaces RS longs with fade T only. Full T+OS strategy differs;08:29pre-bell fill sensitivity matters.'),
      ('OT','Overnight Tick/VIX','NQ','A','conditional_existing_alternative','OT','checks/candidates/overnight_tick/python_trades.csv','Source order-flow design panel stops2026-07-07; later no rows are missing coverage, not verified zero signals.69/516held-path gaps in normalized audit; no stop, overnight tail risk.'),
      ('FC2B','Flow-Confirmed Opening Drive v2','NQ','A','conditional_research_alternative',None,'checks/candidates/fc_2b/mc_v2_trades_all.csv','Use MCv2reference (up-tick Volume semantics/holiday flatten), not overconfident proxy. Prior eval add1–3MNQapproximately no gain; current personal forward log.'),
      ('ST','Swing Target v3','NQ','B','conditional_research_alternative',None,'checks/candidates/swing_target/mc_trades_v3.csv','Latest funded swaps reverted10/31 after corrected replay; adoption gain inconclusive. Use exact MCv3 ledger and numeric stop/target/time kinds; historical CODE_BEholiday repairs are not exactv3.'),
      ('PT','PAPERTREND v2','NQ','B','conditional_research_alternative',None,'checks/candidates/papertrend/mc_trades_claude.csv','Source matching MCledger preferred; original upload was different PL. Long/short and disaster-stop settings preserve source. Prior eval50K+1tie/150Kno gain.'),
      ('VCS','Vol-Control Sell Flow','NQ','B','conditional_research_alternative',None,'mc_reports/Backtesting Strategy Performance Report _ @NQ - 5 Minutes Vol-Control Sell Flow.xlsx','Previously removed funded and omitted eval tiny gain after search; not unexplored. Requires exact lagged vol-control source; source MCavailable.'),
      ('FVB','First Valid Breakout','NQ','B','research_only_not_promotion',None,'checks/candidates/fvb/trades.csv','Fat-tail positive Bledger, prior all eval/funded comparisons worse; shorts-only improvement post-hoc. Freeze original whole rule if inspected; no rescued short selection.'),
      ('S47','Europe-Open Impulse v2','NQ','B','research_only_not_promotion',None,'checks/candidates/s47_v2/mc_trades_S47_v2.csv','MCparity exists but~3700searches and agreement condition added after2023+. Entry/exit fixes/version mapping needed; personal forward only, prior evaltie/worse.'),
      ('NBL','Bridge noise-area15m RTH-anchored longs','NQ','B','blocked_current_early_close_code',None,'claude:'+REF+':analysis/outputs/bridge_noise_15m_trades_rth_longs.csv','Newlatest11/03personal addition. MC98.9%entries and longs t5.4sourceclaims; raw code misses earlyclose flat (9port/4checker carries). No Apex admission until separately frozen repair; 1minute entry delay reduces edge. Prior50Kadd small,150Kno gain.'),
      ('TWIN','Twin Continuation v2.1','NQ','A','blocked_current_Apex_path_and_risk',None,'checks/candidates/twin_continuation/trades.csv','Personalonly: wide/multiday swing stop; v1ledger differs fromv2.1holiday/SetExitOnClose fixes. Prior capped Apex variants/36replacements mostlytie/worse. No new 15:45/stop-cap rescue.'),
      ('KUSHO','Kusho v9','NQ','B','blocked_original_multiday_held_exposure',None,'checks/candidates/kusho/python_trades_v9_rolladj.csv','Original21:00/weekend holds personal-only. Existing15:45RTHvariant ledger available separately but already weaker Apex bench; no silent shortening.'),
      ('S30','S30 IBS reversal NQ+ES','NQ/ES','B','blocked_multiday_no_stop',None,'checks/candidates/s30_ibs/daily_nq_es_per_micro.csv','Personal-only multi-day/no-stop. Daily series not an evaluation native path. New daily-flat conversion would be a new strategy.'),
      ('S03','Noise-area S03v2','NQ','B','research_only_not_promotion',None,'agents/codex/results/s03_v2.md','Existing family tested extensively, account gains weak/negative; cannot treat BridgeNBLor recent uploaded15mcode as independent new evidence.'),
      ('PVT','Prior VWAP Trap','NQ','B','research_only_not_promotion',None,'checks/candidates/prior_vwap_trap/trades_python.csv','Prior Apex benches worse, placebo levels similarly strong; personal capital-expansion bench only.'),
      ('BBMRM','Bollinger open mean reversion','NQ','C','closed_unless_forward_checkpoint',None,'checks/candidates/bb_mrm/mc_trades.csv','Removed byuser after MCweaker than Python; post-hoc49winning extra trades overstated original. Do not restore from old Bsectionheading.'),
      ('REBOUND','NQ Overnight Rebound','NQ','C','closed_no_allocation',None,'agents/codex/results/overnight_rebound.md','One thousand fixed-source trades positive but filter/timing benefit unproven and personal profit/DDworse; not new current risk diversifier.'),
      ('NOCTURNE','Nocturne N0','NQ','C','closed_weak_recent_stop_kills',None,'checks/candidates/nocturne/python_nights.csv','Recent2024–26t0.75, no stop; stop erases edge; frozen forward checkpoint not a new evalsearchcandidate.'),
      ('PRIMESYNC','PrimeSync','ES/NQ','not_admitted','closed_failed_account_gates',None,'agents/codex/results/primesync_accounts.md','Already tested one micro/frozen entry on all homes; no allocation gate passed. Code not compiled/trade matched.'),
      ('R1144','Ricochet S1144','NQ','not_admitted','closed_failed_design',None,'agents/codex/results/ricochet1144_20261104.md','Latest directupload two causal profiles fail adjusted significance and source/data gates. Not an eligible rescue through portfolio search.'),
      ('GC_ASIA','Gold Asian-range breakout','GC','C/watch','closed_prior_eval_no_gain',None,'analysis/gold_asian_breakout_gc_test.py','Userparked10/14; filtered rarity/weak standalone; no prior evaluation improvement. Native MGCcosts/quote risk need distinct admission.'),
      ('GC_COMBO','GC Combo v2','GC','source_needs_data','blocked_signed_tick_field_and_source_match',None,'agents/codex/results/gc_combo_v2_review.md','UpTicks/DownTicks sign missing from existing GCexports; price proxy fails. LucidFlexclaims are not Apex results.'),
      ('ZN_AUCTION','Treasury auction flow','ZN','F','closed_cost_failure',None,'analysis/treasury_auction_test.py','Prior intraday drift below roundtrip costs and postauctionrebound absent; COT/auctiondate new filters cannot silently revive.'),
      ('NG_STORAGE','NG unconditional storage-calendar short','NG','dont_test','closed_source_gate_failure',None,'agents/codex/results/ng_3575861_full_review_20261030.md','Fullsource post2011netnegative; corrected NGdata retained for distinct ideas, not a late portfolio rescue.'),
      ('6E_FIX','Europe-fix drift','6E','design_reject','closed_design_reject',None,'agents/codex/results/scout_europe_fix_20261029.md','Existing scout failed gross/cost gate; source/data-blocked unrelated FXhypotheses do not make this eligible.')
    ]
    candidates=[dict(zip(['key','name','market','reported_tier','evaluation_routing','normalized_key','source_path','limits'],row)) for row in choices]
    stops={
      'VB':dict(type='fixed_points',points=75,target_points=40,source='MC VB v1 Settings StopPts75/TargetPts40 verified; apex_strategies/NQ_Vault_Break.txt'),
      'ONB30':dict(type='prior_ATR_multiple',multiple=.25,length=15,target_R=3,source='MCplainONB Settings ADXMin30,StopAtrPct0.25,AtrDays15 verified; chart own weekday calendar-dateTR semantics must match'),
      'EOS':dict(type='prior_ATR_multiple',multiple=.30,length=15,source='MCEOSv1 Settings StopAtrPct0.30,AtrDays15 verified'),
      'ONBML':dict(type='prior_ATR_multiple',multiple=.30,length=15,target_R=3,source='MCONBMLv2 Settings ADXMin20,StopAtrPct0.30,AtrDays15 verified; existing frozen WFfilter'),
      'LDF':dict(type='prior_ATR_multiple',multiple=.25,length=15,source='build_lab.REPORTS LDF_MC and fixed source; verify actual settings/clock before native sizing'),
      'MON':dict(type='prior_ATR_multiple',multiple=.50,length=15,source='build_lab.REPORTS MON_MC; current holiday exclusions apply'),
      'NFP':dict(type='prior_ATR_multiple',multiple=.50,length=15,source='build_lab.REPORTS NFP_MC; GoodFriday exclusion applies'),
      'BRIDGE':dict(type='no_protective_stop',points=None,target_points=100,source='BridgeMonday fixed source and current plan; fixed2/5MNQ baseline, no invented stop-risk sizing'),
      'OT':dict(type='no_protective_stop',points=None,source='OvernightTick/VIX source; fixed native quantity, no stop-distance/risk-budget guarantee'),
      'CLS':dict(type='prior_ATR_multiple',multiple=.75,length=15,source='cl_sunday_fade_confirm.python_trades sourcefr.atr; exact chart/TR and rawfr construction need matching'),
      'MOC':dict(type='prior_ATR_multiple',multiple=.25,length=15,source='s_rank_es_round1_test fixed ES MOC; native MES $5/point'),
      'RS':dict(type='prior_mean_RTH_range_multiple',multiple=.60,length=20,target_multiple=1.,source='relative_strength_test.trades average08:30–15:00range of20clean prior sessions; not WilderATR'),
      'DT':dict(type='fixed_points',points=50,target_points=100,source='DualThrustv4 declared/current MCconfirmed source'),
      'TOS':dict(type='prior_mean_RTH_range_multiple',multiple=.40,length=20,source='Tfade only with note stop; ATRd means prior20full-session08:31–15:00meanhigh-low, not true range. OS0.30is a different sleeve.'),
      'FC2B':dict(type='fixed_points',points=100,trail_points=150,break_even_trigger_points=66,source='FC_2B_v2.txt SLpoints100,TrailPts150,BreakEvenR0.66; MCv2reference'),
      'ST':dict(type='prior_mean_RTH_range_multiple',multiple=.70,length=20,target_multiple=.35,break_even_trigger_multiple=.30,source='NQ_Swing_Target_v3.txt; exact v3knowncalendar skips, not oldCODE_BEpatchedlateexit'),
      'PT':dict(type='prior_mean_RTH_range_multiple',multiple=2.,length=14,source='PAPERTRENDv2disaster stop; papertrend_test atr means mean14RTHhigh-low, not WilderATR'),
      'VCS':dict(type='prior_ATR_multiple',multiple=.25,length=15,source='build_lab.REPORTS VCS_MC; original lagged volmodelsettings still need match'),
      'NBL':dict(type='fixed_points',points=50,target_points=25,source='LatestClaudeRTHanchor source; historical earlyclose defect prevents present Apex admission'),
      'FVB':dict(type='per_trade_stop_field',column='stop',source='checks/candidates/fvb/trades.csv; source0.18ATR14fromsignal; native entry-stop distance not inferred from realized loss'),
      'S47':dict(type='current_completed_overnight_range_multiple',multiple=.5,source='S47v2fixed source; known before09:31entry; exact overnight clock needed')
    }
    for c in candidates:
        c['entry_stop_specification']=stops.get(c['key'],dict(type='excluded_or_unverified_no_assumed_stop',source=c['source_path']))
        c['native_point_value']={'NQ':2.,'ES':5.,'CL':100.,'GC':10.}.get(c['market'])
        c['coverage_reference']='normalized_ledger_metadata' if c['normalized_key'] else 'other_asset_metadata or declared source_path'
        c['independent_review_status']='Existing MC/checker claims only; no new independent return review in this inventory. See limits and source registry.'
        c['ledger_path']=('analysis/outputs/codex_portfolio_audit_20261031/'+c['normalized_key']+'_unit_ledger.csv') if c['normalized_key'] else {'FC2B':'checks/candidates/fc_2b/mc_v2_trades_all.csv'}.get(c['key'],c['source_path'])
        c['ledger_units']='Native micro raw gross/fee_units/slippage_one_tick; recompute costed path, not NQnet/10.' if c['normalized_key'] else 'Inspect schema/provenance; most MCcandidate CSV gross/net are per1NQ, original price units retained.'
        c['normalized_window']='2018-04-02–2026-07-07 fixed audit universe; first/last actual ticket is not a no-signal coverage certificate.' if c['normalized_key'] else None
    verification={
      'VB':'MCconfirmed established core; live-match recent claims separately audited. Actual default stop75points verified in MCSettings.',
      'ONB30':'MCconfirmed original eval ADX30/.25ATR. Not the MLv2model; current defaultsource .30 differs from evalInputs.',
      'EOS':'MCconfirmed established rare-event strategy; no new verification here.',
      'BRIDGE':'MC217/217matched prior claim; current two/five native lots, no stop. Price-touch/session inference limits remain.',
      'ONBML':'Existing frozenMLv2MCreport and sourcewalk-forward claims; MLfilter fit/cutoff must remain pinned, not freshly selected.',
      'LDF':'MCconfirmed current funded core, lagged source clocks unchanged.',
      'MON':'MCconfirmed; later source/calendar excludes July3/December24holiday-Monday rows.',
      'NFP':'MCconfirmed; later source excludes GoodFriday row.',
      'CLS':'MC96/97prior match; normalized audit85/87trades missing heldminutes. Quotes/roll/fills not independently certified.',
      'MOC':'MC199trade prior match/sourceclaim; recent weaker; legacy whole-day/close-mark shortcuts do not certify nativefloor.',
      'RS':'MC1157shared-day P&Lcorr1.000priorclaim/checkerPASS_WITH_CONCERNS. Sourcebeta anddata clocks required.',
      'DT':'MC1610vs1611,1609identical priorclaim/checkerPASS_WITH_CONCERNS; DSR0.939concern. Current150KfundedDT2retained.',
      'TOS':'MCfade348/358priorclaim,checkerPASS_WITH_CONCERNS; requires stoppedTfade source, not unprotectedfullbook.',
      'OT':'MC529sharednights97%andcorr1.000priorclaim; underlyingOFendsJuly7. Nativetimes recovered bysource ratherthan dailyextrema.',
      'FC2B':'MCv2reference773trades; checkerPASS_WITH_CONCERNS. Python Volume/up-tick mismatch makesMCledgerreference; forwardlogged.',
      'ST':'MCv3matched581of602priorrecordeddays and99%entryprices,checker/parity/adoptionnotallindependent. Numeric exit-kind accounting correction invalidates strong oldswapclaim.',
      'PT':'MCClaude-codeledger supports currentpersonal; originalposteduploadwasothercode. CheckeroldPythonFAILDSR; sourceMCt4.35claim doesnotadmitApex.',
      'NBL':'LatestMC RTH-anchor98.9%entries/longt5.4sourceclaim,checkerPASS_WITH_CONCERNS; early-close carries stillknown. CodexpriorfullGlobexvariantdifferentfrozenrules wasrejected.',
      'S47':'MC710/714entriespriorclaim; source~3700settings/NYagreementafter2023+seen. Correctedentry-barstop/versionneedsmapping.',
      'FVB':'CheckerPASS_WITH_CONCERNS,source1944vs2041claimed mismatch,concentration; priorApexaccounttestsnegative.'}
    for c in candidates:c['mc_and_reviewer_status']=verification.get(c['key'],c['limits'])
    obj=dict(scope='Metadata/source inventory only; zero new strategy returns or portfolio combinations computed. Routing is research eligibility, not a tier/allocation change.',codex_head=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),latest_claude_ref=REF,registry_rows=len(rows),curated_strategy_families=len(candidates),current_eval_rosters={'50K':{'VB':8,'ONB30_risk':1100,'ONB30_ATR':.25,'EOS_risk':500,'EOS_ATR':.3,'BRIDGE':2},'150K':{'VB':20,'ONB30_risk':2750,'ONB30_ATR':.25,'EOS_risk':1250,'EOS_ATR':.3,'BRIDGE':5}},normalized_ledger_metadata=ledgers,other_asset_metadata=assets,candidates=candidates,
      current_roster_notes=['LatestClaudeNEW_CHAT_BRIEFconfirms#2/#4failed11/04; evalroster unchanged.','Funded latest keeps50KVB2/1+Tfade,150KDT2; SwingTargetfundedswapsreverted10/31.','Latestpersonalpieces table addsNBL11/03(total20labels), while whole-portfolio narrative still says19; stale prose is not canonical roster.'],
      native_costs={'NQmicro':{'point_value':2,'tick':.25},'ESmicro':{'point_value':5,'tick':.25},'CLmicro':{'point_value':100,'tick':.01},'commission':'Prior native audit main1.04RT,fee1.24RTsensitivity,one tickpermarket/stop fill; MES/MCL1.04assumed. Reconcile actual fees/current source before tests; no blanketNQnet/10.'},
      no_new_return_tests=True)
    (OUT/'strategy_inventory.json').write_text(json.dumps(obj,indent=2,ensure_ascii=False)+'\n')
    text='''# Evaluation strategy universe: source and data inventory

Summary: Screened the latest 368 ranked registry entries and mapped 36 strategy families without new returns.
Current evaluations still use VB/ONB30/EOS/Bridge; 18 established/conditional alternatives have a research route.
Sixteen saved native-unit ledgers exist; their old NPZ/pickle runtime paths are absent in this workspace.
Existing non-equity alternatives are limited; CL held-minute gaps and common equity exposure remain material.
Latest Claude adds NBL to personal, but its missing early-close exit prevents Apex use as written.

## Scope and source boundary

Pinned latest Claude: `13e29ca7b45daabeb0ed2d8c286448610f594dab` (read-only git show).
The full [ranked registry snapshot](tier_registry_snapshot_13e29ca.json) retains every row, including failed
families, papers, tools, sizing rules and repeated economic definitions. Its 368 rows are not 368 distinct strategies.
The [machine inventory](strategy_inventory.json) gives candidate status, exact ledger/source paths, schemas,
hashes, date metadata, entry-stop formula, units and documentary MC/checker status. This is not independent
historical replication, a new ranking, new hypothesis or allocation. No return, signal, sizing sweep or account
combination was run by this inventory script. Hash/schema/date reads do not certify native fills or data coverage.

## Current rosters and recent source changes

|Home|Existing eval inputs|
|---|---|
|50K|VB8MNQ; plain ONB ADX30 risk$1,100 at0.25ATR; EOS risk$500 at0.30ATR; Bridge2MNQ|
|150K|VB20MNQ; plain ONB ADX30 risk$2,750 at0.25ATR; EOS risk$1,250 at0.30ATR; Bridge5MNQ|

Verified workbook Settings: VB StopPts75/TargetPts40/AtrDays15; plain ONB ADXMin30/StopAtrPct0.25/
AtrDays15/RewardRisk3; EOS StopAtrPct0.30/AtrDays15; ONBML ADXMin20/StopAtrPct0.30/AtrDays15/RewardRisk3.
`build_lab.REPORTS['VB'][1]=0.30ATR` is sizing metadata, **not the actual fixed75point Vault Break stop**.
At entry, fixed stop risk perMNQ is points×$2; dollar-risk quantity must floor using its own account's dollar
budget before combining paths. Actual source default ONB0.30 does not override the evaluation's explicit0.25input.

Latest Claude NEW_CHAT_BRIEF confirms #2/#4 failedNovember4 and the eval roster is unchanged. Funded changes
are different:50KusesVB2/1plusTfade;150KkeepsDT2. Swing Target funded swaps were revertedOctober31after
corrected replay found the prior gain inconclusive. Do not use stale TIER/adoption prose as today's roster.
Latest personal pieces table adds RTH-anchored noise-area longs November3 (20labels), but its whole-book prose
still says19. This discrepancy is source-version bookkeeping, not permission to copy an outdated performance table.

## Core/conditional research universe

“Conditional” means a source/data route exists for a separately preregistered comparison. It does not mean the
strategy is already approved for the eval plan or that a new test will pass. All are subject to native paths/costs,
source clocks, original selection, integer quantities and chronological account replay.

|Key|Strategy|Reported tier / role|Entry-stop specification|Canonical raw ledger/source|
|---|---|---|---|---|
'''
    for c in candidates:
        if c['evaluation_routing'] not in ['baseline','conditional_existing_alternative','conditional_research_alternative']:continue
        spec=c['entry_stop_specification'];stop=(str(spec['points'])+'points') if spec.get('type')=='fixed_points' else (str(spec.get('multiple'))+'×prior'+str(spec.get('length',''))+' '+spec['type']) if 'multiple' in spec else 'No protective stop' if spec['type']=='no_protective_stop' else spec['type']
        text+=f"|{c['key']}|{c['name']}|{c['reported_tier']};{c['evaluation_routing']}|{stop}|`{c['ledger_path']}`|\n"
    text+='''

For ONB/EOS/MON/LDF/NFP/VCS, reproduce the source's completed-day true-range/weekday calculation before sizing;
do not replace it with an unrelated RTH average. RS,Tfade,ST andPT use the specified mean RTHhigh-low ranges,
not WilderATR. Native point values:MNQ$2,MES$5,MCL$100; tick values differ. Bridge andOT have no source stop;
an invented stop-distance cap would change their strategy, not merely their lot count.

## Screened exclusions and research-only routes

|Key|Route|Reason retained|
|---|---|---|
'''
    for c in candidates:
        if c['evaluation_routing'] in ['baseline','conditional_existing_alternative','conditional_research_alternative']:continue
        text+=f"|{c['key']}|{c['evaluation_routing']}|{c['limits']}|\n"
    text+='''

No daily-only S30, multi-day Twin/Kusho, missing-input GCCombo, failed R1144/PrimeSync/NGcalendar/6Efix, or
previously rejected generic families were promoted into the test pool. An explicit new bounded user-directed
comparison may include an existing eligible research alternative, but is not authority to erase prior failures,
choose a post-hoc short-only variant, silently shorten holds or count another ticker as independent evidence.

## Data availability and usable loaders

`analysis/outputs/codex_portfolio_audit_20261031/*_unit_ledger.csv` contains16 existing native-unit ledgers:
VB,VB_N,VB_F,ONB30,ONBML,EOS,BRIDGE,LDF,MON,NFP,RS,DT,TOS,OT,CLS,MOC. Schema:
`entry_at,exit_at,side,qty,entry,exit,kind,gross,fee_units,slippage_one_tick,missing_held_bars,exit_after_1559`.
`gross` is already native-micro dollars (NQ$2/point), not full-NQ dollars. Use raw prices/native values to
rebuild a consistent cost bridge. `j0/j1` are17→16account-session coordinates; datetime columns are safer
for reconstruction. Numeric stop0/target1/time2 mappings matter. Wrong string exit kinds previously changed
slippage and adverse paths; see [Swing Target correction](../../results/swing_kind_replay_20261031.md).

The pinned old normalized universe isApril2,2018–July7,2026. First/last actual trade timestamps in a CSV
are not proof of full no-signal coverage. Later absent OTrows represent an order-flow input cutoff, not zero
returns. The original MCreports/extended raw ledgers can extend some strategies independently only after
matching source version/calendar/clock/cost. No missing day may be converted into a known no-trade day.

Direct MCcandidate CSVs with raw prices and `date,t_in,t_out,exit_date,kind` exist for FC2Bv2,DT,STv3,PT,
Tfade,S47andBBMRM. Their HHMM fields are chart stamps, not certified native fill minutes. Some source
trade CSVs omit times entirely; use the corresponding MCworksheet/source adapter rather than fabricate them.
Latest NBLledgers/fills/source exist at Claude13e29ca, not necessarily the codex/work tree. All detected paths,
row counts, columns and first/last date fields are in the machine inventory.

The prior audit runtime `agents/codex/runtime/portfolio_audit_20261031/` is absent here; `/workspace/scratch`
is effectively empty and `scratch_data` only has a greenorb subfolder. Do not claim NPZ/pickle paths were loaded
without rebuilding them. `analysis/codex_portfolio_audit_prepare.py` documents the prior normalized loaders but
requires its pinned old source worktree and includes historical source approximations; it must not be blindly
executed/imported as a current selector. Importing some old test scripts also executes returns at module level.

Important prior audit limits: CL85/87andOT69/516trades have missing held-minute OHLC; Bridge has one touch
mismatch; VBsingle-print flags are missing on eight recorded days; ONBMLhas an explicit unfinished sentinel.
The relevant [portfolio audit](../../results/portfolio_audit_20261031.md) retains them. Source-minute extrema summed
across strategies are conservative account-risk proxies, not synchronized tick paths; a common bias can change
relative floor outcomes, so it does not automatically cancel between portfolios.

Current saved native audit used1.04microRTcommission as primary (user-reported MNQrange0.99–1.08),1.24fee
sensitivity and one native tick permarket/stop fill. MES/MCL1.04was assumed, not observed. Old benches often
used NQ$7.25/10=$0.725perMNQ and fractional “scale0.75” quantities. Reconcile actual chosen cost and whole
contracts before calling a size/mix optimal. This inventory creates no new comparison outcome.

## Reproduce this inventory only

`/workspace/venvs/thebeginning/bin/python analysis/codex_eval_strategy_inventory_20261104.py`

Reads the pinned Git objects and existing files, hashes/schema/date metadata, and writes this note plus JSON.
No local/VPS trading file, plan, broker setting, API key, paused program, return ledger or allocation is changed.
'''
    (OUT/'strategy_inventory.md').write_text(text)
    print(json.dumps({'registry_rows':len(rows),'curated_families':len(candidates),'native_unit_ledgers':len(ledgers),'other_assets':len(assets),'new_returns':0}))

if __name__=='__main__':main()
