"""Frozen bounded portfolio menu for the user's evaluation-plan audit.

Generation inspects no market outcomes. Every distinct account/book/governor is
registered, including zero exposure, old controls and unsuccessful allocations.
This is portfolio-allocation research, not new signal/entry/exit optimization.
"""
from itertools import combinations,product
import hashlib,json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
BASE=ROOT/'agents/codex/inputs/eval_audit_20261104'
ALL_KEYS=['VB','ONB30','EOS','BRIDGE','ONBML','LDF','MON','NFP','CLS','MOC','RS','DT','TOS','OT','FC2B','ST','PT','VCS']
RISK_KEYS=['VB','ONB30','ONBML','EOS','LDF','MON','NFP','RS','DT','TOS','MOC','CLS']
GOVERNORS=[(1.,1.),(.15,.35),(.25,.50),(.35,.65)]
MAX_DEFINITIONS=3000

def lots(value):return {'kind':'lots','value':int(value)}
def risk(value):return {'kind':'risk','value':float(value)}

def base_book(size,ml=False):
    return {'VB':lots(8 if size==50 else 20),'ONBML' if ml else 'ONB30':risk(1100 if size==50 else 2750),
            'EOS':risk(500 if size==50 else 1250),'BRIDGE':lots(2 if size==50 else 5)}

def canonical(book):return {k:v for k,v in sorted(book.items()) if v['value']>0}

def signature(size,book,governor):
    value=json.dumps([size,canonical(book),governor],sort_keys=True,separators=(',',':')).encode()
    return hashlib.sha256(value).hexdigest()[:16]

def generate():
    rows=[];seen={}
    def add(size,family,label,book,gov=None,role='candidate',parent_id=None):
        book=canonical(book);gov=gov or {'risk_fraction':0.,'aggregate_stop_fraction':1.,'cushion_buffer':0.,'target_guard':False}
        sig=signature(size,book,gov)
        if sig in seen:
            seen[sig]['aliases'].append(label);return seen[sig]
        trail=2000. if size==50 else 4000.
        vec={k:(v['value']/trail if v['kind']=='risk' else v['value']*100./trail) for k,v in book.items()}
        row={'candidate_id':f'E{size}_{sig}','account':size,'family_id':family,'label':label,'book':book,
             'governor':gov,'role':role,'parent_id':parent_id,'exposure_vector':vec,'aliases':[],
             'source_rules':'Frozen source strategy signals/exits; allocation only. Intraday broker stops/target guard modeled.'}
        rows.append(row);seen[sig]=row;return row
    for size in [50,150]:
        trail=2000. if size==50 else 4000.
        add(size,'reference','CURRENT',base_book(size),role='reference')
        add(size,'empty','EMPTY',{},role='unselectable_control')
        for scale in [.25,.375,.5,.625,.75,.875,1.,1.125,1.25,1.5]:
            book={k:(lots(int(v['value']*scale)) if v['kind']=='lots' else risk(v['value']*scale)) for k,v in base_book(size).items()}
            add(size,'uniform_size',f'CURRENT_x{scale}',book)
        vb=[0,2,4,6,8] if size==50 else [0,5,10,15,20]
        onb=[0,550,800,1100] if size==50 else [0,1400,2000,2750]
        eos=[0,250,500] if size==50 else [0,625,1250]
        bridge=[0,1,2] if size==50 else [0,2,5]
        for ml in [False,True]:
            key='ONBML' if ml else 'ONB30'
            for a,b,c,d in product(vb,onb,eos,bridge):
                if not any([a,b,c,d]):continue
                add(size,'reweight_ML' if ml else 'reweight_current',f'{key}_VB{a}_risk{b}_EOS{c}_Bridge{d}',
                    {'VB':lots(a),key:risk(b),'EOS':risk(c),'BRIDGE':lots(d)})
        for key in ALL_KEYS:
            for f in [.10,.25,.50]:
                book={key:lots({.10:1,.25:2,.50:4}[f])} if key in ['BRIDGE','OT'] else {key:risk(trail*f)}
                add(size,'standalone',f'ONLY_{key}_risk{f}',book)
        for n in [2,3]:
            for keys in combinations(RISK_KEYS,n):
                if {'ONB30','ONBML'}.issubset(keys):continue
                for f in [.10,.20,.30]:
                    add(size,f'{n}_leg_equal_risk',f'{"+".join(keys)}_each{f}',{k:risk(trail*f) for k in keys})
        for replace in ['VB','ONB30']:
            for key in ['FC2B','ST','PT','VCS']:
                for f in [.10,.25,.50]:
                    book={k:v for k,v in base_book(size).items() if k!=replace};book[key]=risk(trail*f)
                    add(size,'other_strategy_swap',f'{replace}_to_{key}_risk{f}',book)
        rosters=[['VB','ONBML','EOS','LDF','NFP','MON','MOC','CLS','TOS'],
                 ['RS','DT','TOS','FC2B','ST','PT','EOS','NFP'],
                 ['VB','ONBML','EOS','LDF','MON','NFP','MOC','CLS','RS','DT','TOS','FC2B','ST','PT','VCS']]
        for i,keys in enumerate(rosters):
            for gross in [.5,1.,1.5]:
                add(size,'diversified_roster',f'ROSTER{i}_aggregate_risk{gross}',{k:risk(trail*gross/len(keys)) for k in keys})
        # Governors on two source-defined books, no selection needed.
        for ml in [False,True]:
            for per,total in GOVERNORS:
                gov={'risk_fraction':per,'aggregate_stop_fraction':total,'cushion_buffer':100. if size==50 else 250.,'target_guard':False}
                add(size,'floor_aware_reference',f'{"ML" if ml else "CURRENT"}_CAP_{per}_{total}',base_book(size,ml),gov)
            # Separate execution-policy counterfactual; not assumed installed.
            gov={'risk_fraction':0.,'aggregate_stop_fraction':1.,'cushion_buffer':0.,'target_guard':True}
            add(size,'target_guard_reference',f'{"ML" if ml else "CURRENT"}_MARKET_TARGET_GUARD',base_book(size,ml),gov)
    assert len(rows)+30<=MAX_DEFINITIONS,(len(rows),MAX_DEFINITIONS)
    return rows

def derived_governors(nominees,registry):
    """At most3 frozen design nominees/account; deterministic reserved next phase."""
    seen={signature(r['account'],r['book'],r['governor']) for r in registry};rows=[]
    for parent in nominees:
        size=int(parent['account'])
        for per,total in GOVERNORS:
            gov={'risk_fraction':per,'aggregate_stop_fraction':total,'cushion_buffer':100. if size==50 else 250.,'target_guard':False}
            sig=signature(size,parent['book'],gov)
            if sig in seen:continue
            seen.add(sig)
            r=dict(parent);r.update(candidate_id=f'E{size}_{sig}',family_id='floor_aware_nominee',
                governor=gov,parent_id=parent['candidate_id'],aliases=[],label=parent['label']+f'_CAP_{per}_{total}')
            rows.append(r)
        gov={'risk_fraction':0.,'aggregate_stop_fraction':1.,'cushion_buffer':0.,'target_guard':True}
        sig=signature(size,parent['book'],gov)
        if sig not in seen:
            seen.add(sig);r=dict(parent);r.update(candidate_id=f'E{size}_{sig}',family_id='target_guard_nominee',
                governor=gov,parent_id=parent['candidate_id'],aliases=[],label=parent['label']+'_MARKET_TARGET_GUARD');rows.append(r)
    assert len(registry)+len(rows)<=MAX_DEFINITIONS
    return rows

def main():
    rows=generate();BASE.mkdir(parents=True,exist_ok=True)
    obj={'program':'evaluation-audit-20261104','scope':'User-requested broad portfolio/sizing audit; source strategies unchanged.',
         'max_economic_definitions':MAX_DEFINITIONS,'initial_definitions':len(rows),
         'reserved_derived_governors':30,'selection_data':'2018-04-02–2022-12-31 only',
         'historical_validation':'Previously seen2023+; freeze nominees before one validation.',
         'scout_counts_unchanged':{'hypotheses':4,'definitions':10},'candidates':rows}
    (BASE/'policies.json').write_text(json.dumps(obj,indent=2)+'\n')
    print(json.dumps({'definitions':len(rows),'per_account':{s:sum(r['account']==s for r in rows) for s in [50,150]},
                      'max_with_reserved':len(rows)+30,'scope':'No market returns or account outcomes.'}))

if __name__=='__main__':main()
