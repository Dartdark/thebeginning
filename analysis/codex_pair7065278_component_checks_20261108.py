"""Frozen synthetic checks. Run only after this file, components and plan are committed."""
import hashlib
import json
from dataclasses import replace
from datetime import datetime, timedelta, timezone
from pathlib import Path
import subprocess
from zoneinfo import ZoneInfo

import pandas as pd

from codex_pair7065278_components_20261108 import Quote, ratio, scores, desired_side

ROOT = Path(__file__).resolve().parents[1]
PATHS = ['analysis/codex_pair7065278_components_20261108.py',
         'analysis/codex_pair7065278_component_checks_20261108.py',
         'agents/codex/plans/pair7065278_reconstruction_20261108.md']
for p in PATHS:
    committed = subprocess.check_output(['git', 'show', 'HEAD:' + p], cwd=ROOT)
    if committed != (ROOT / p).read_bytes():
        raise RuntimeError('commit exact components/checks/plan before execution: ' + p)

checks = []
def check(name, condition):
    if not condition:
        raise AssertionError(name)
    checks.append(name)

def rejects(name, fn):
    try:
        fn()
    except ValueError:
        checks.append(name)
        return
    raise AssertionError(name + ' did not reject')

d = datetime(2025, 7, 15, 15, tzinfo=timezone.utc)
def q(v, unit):
    return Quote(v, v, d - timedelta(seconds=10), d - timedelta(seconds=5), unit)
u, k, f = q(50, 'USD'), q(499, 'GBX'), q(1.25, 'USD_PER_GBP')
def r(uk=k, us=u, fx=f, when=d, opened=True):
    return ratio(us, uk, fx, when, both_continuous_open=opened)

check('GBX499 preserved', abs(r() - 50/(4.99*1.25)) < 1e-12)
check('GBX501 preserved', abs(r(uk=q(501,'GBX')) - 50/(5.01*1.25)) < 1e-12)
check('GBP conversion equivalent', abs(r(uk=q(4.99,'GBP')) - r()) < 1e-12)
for name, bad in [('unknown units', replace(k,unit='UNKNOWN')), ('zero price',replace(k,bid=0)),
                  ('nonfinite price',replace(k,ask=float('inf'))), ('crossed quote',replace(k,bid=502))]:
    rejects(name, lambda bad=bad: r(uk=bad))
for name, bad in [('future event',replace(k,event_time=d+timedelta(seconds=1))),
                  ('future receipt',replace(k,available_at=d+timedelta(seconds=1))),
                  ('receipt before event',replace(k,available_at=d-timedelta(seconds=20))),
                  ('stale event',replace(k,event_time=d-timedelta(seconds=61))),
                  ('naive event',replace(k,event_time=d.replace(tzinfo=None)))]:
    rejects(name,lambda bad=bad:r(uk=bad))
rejects('naive decision',lambda:r(when=d.replace(tzinfo=None)))
rejects('wrong decision clock',lambda:r(when=d+timedelta(minutes=1)))
rejects('closed calendar',lambda:r(opened=False))
values=[1+(i%7)*0.01+i*0.001 for i in range(40)]
a=scores(values)
check('20 observation warm-up',a.iloc[:19].isna().all() and pd.notna(a.iloc[19]))
check('causal prefix',a.iloc[:25].equals(scores(values[:25])))
check('long entry',desired_side(0,-0.8)==1)
check('short entry',desired_side(0,0.8)==-1)
check('long overshoot exit no reverse',desired_side(1,0.8)==0)
check('short overshoot exit no reverse',desired_side(-1,-0.8)==0)
check('long hold',desired_side(1,-0.5)==1)
check('short hold',desired_side(-1,0.5)==-1)
check('flat band',desired_side(0,0)==0)
rejects('zero dispersion',lambda:desired_side(0,float(scores([1.0]*20).iloc[-1])))
rejects('missing ratio',lambda:scores([1,float('nan')]))
check('summer overlap clock',d.astimezone(ZoneInfo('Europe/London')).hour==16 and d.astimezone(ZoneInfo('America/New_York')).hour==11)
w=datetime(2025,1,15,15,tzinfo=timezone.utc)
check('winter overlap clock',w.astimezone(ZoneInfo('Europe/London')).hour==15 and w.astimezone(ZoneInfo('America/New_York')).hour==10)
result={'scope':'synthetic component checks only', 'checks_passed':len(checks),'checks':checks,
        'component_gate':'PASS','economic_admission':'NEEDS DATA','historical_returns_computed':False,
        'economic_trials':0,'portfolio_tests_run':False,
        'preregistration_commit':subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),
        'hashes':{p:hashlib.sha256((ROOT/p).read_bytes()).hexdigest() for p in PATHS}}
out=ROOT/'analysis/outputs/codex_pair7065278_reconstruction_20261108/components.json'
out.parent.mkdir(parents=True,exist_ok=True)
out.write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps(result,indent=2))
