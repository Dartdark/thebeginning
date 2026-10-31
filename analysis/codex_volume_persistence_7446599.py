"""Source audit and fixed-five-minute volume measurement kernel; no return test.

The caller must independently audit dates, calendars, contracts and receipt clocks.
This numeric kernel does not construct a causal event panel or forecast model.
"""
from pathlib import Path
import hashlib
import json
import subprocess
import numpy as np

ROOT=Path(__file__).resolve().parents[1]
PDF=ROOT/'agents/codex/inputs/volume_persistence_7446599/source.pdf'
OUT=ROOT/'analysis/outputs/codex_volume_persistence_7446599'


def measure(observed, historical):
    """Paper's fixed-five-minute robustness definitions, 120 later minutes.

    historical: 10–20 prior non-announcement days x 125 aligned minutes.
    observed: release-relative minutes 0..124 (five initial plus 120 outcome).
    AUC/TTB require future outcome data; they are never initial trade signals.
    """
    v=np.asarray(observed,dtype=float); h=np.asarray(historical,dtype=float)
    if v.shape!=(125,) or h.ndim!=2 or h.shape[1]!=125 or not 10<=len(h)<=20:
        raise ValueError('Need 125 minutes and 10–20 prior matched days')
    if not np.isfinite(v).all() or not np.isfinite(h).all() or (v<0).any() or (h<0).any():
        raise ValueError('Invalid/missing volume; do not impute an absent observation as zero')
    b=np.median(np.log1p(h),axis=0)
    typical=np.expm1(b)
    ratio=(v+1)/np.exp(b)
    sa=np.log1p(v)-b
    activity=float(np.log1p(v[:5].sum())-np.log1p(typical[:5].sum()))
    auc=float(np.maximum(sa[5:],0).sum())
    start=None
    for j in range(116):
        if (ratio[5+j:5+j+5]<=1.25).all():
            start=j
            break
    return dict(initial_activity=activity,auc120=auc,log1p_auc120=float(np.log1p(auc)),
        time_to_baseline=120 if start is None else start,censored=start is None,
        baseline_streak_start_release_minute=None if start is None else 5+start,
        baseline_confirmed_release_minute=None if start is None else 9+start,
        scope='Numeric fixed-5 measurement only; outcome metrics use future observations')


def main():
    OUT.mkdir(parents=True,exist_ok=True)
    h=np.full((20,125),100.)
    flat=measure(np.full(125,100.),h)
    assert np.isclose(flat['initial_activity'],0.) and np.isclose(flat['auc120'],0.) and not flat['censored']
    assert flat['time_to_baseline']==0 and flat['baseline_confirmed_release_minute']==9
    high=measure(np.full(125,201.),h)
    assert np.isclose(high['auc120'],120*np.log(2)) and high['censored']
    # Future outcome changes cannot change the initial-activity statistic.
    v=np.full(125,100.);v[5:]=201.
    later=measure(v,h)
    assert later['initial_activity']==flat['initial_activity'] and later['auc120']>0
    v=np.full(125,100.);v[5:10]=0.
    below=measure(v,h)
    assert np.isclose(below['auc120'],0.)
    # A final streak at the end of the horizon is still observed and confirmed.
    v=np.full(125,201.);v[-5:]=100.
    end=measure(v,h)
    assert end['time_to_baseline']==115 and end['baseline_confirmed_release_minute']==124
    failures=0
    for v,h0 in ((np.full(124,1.),h),(np.full(125,-1.),h),
                 (np.full(125,np.nan),h),(np.full(125,1.),h[:9])):
        try: measure(v,h0)
        except ValueError: failures+=1
    assert failures==4
    text=subprocess.check_output(['pdftotext','-layout',str(PDF),'-'],text=True)
    a=text.index('Data Availability Statement');b=text.index('Declaration of Competing Interest',a)
    (OUT/'data_availability.txt').write_text(text[a:b])
    claims=dict(source='Author-reported results; manually transcribed and visually checked Table 5, printed p14',
        available_release_counts={'NFP':306,'ISM':307,'CPI':260},
        markets=['FTSE 100','DAX','CAC 40'],sample='2000 through 2025-07-03',
        adjusted_r2_controls=.130,adjusted_r2_plus_activity=.395,
        activity_gain_percentage_points=100*(.395-.130),
        direction_gain_percentage_points=100*(.3959-.3953),
        activity_coefficient_p2=.350,activity_coefficient_p3=.357,direction_coefficient_p3=.011,
        pooled_n_p2=2461,pooled_n_p3=2460,
        nfp_dispersion_coefficients={'FTSE':-.228,'DAX':-.149,'CAC':-.074},
        return_trial_count=0,regressions_independently_reestimated=False)
    (OUT/'author_claims.json').write_text(json.dumps(claims,indent=2)+'\n')
    audit=dict(source_sha256=hashlib.sha256(PDF.read_bytes()).hexdigest(),
        numeric_kernel_checks_pass=True,rejected_invalid_cases=failures,
        synthetic_examples={'baseline':flat,'elevated':high,'future_only':later,'late_confirmation':end},
        source_authors='Not named in the uploaded anonymized title page',
        source_revision_date='Not stated on the title page',
        no_return_forecast_or_execution_saving_verified=True,
        source_scope='Activity associations in European index futures, not NQ/ES directional alpha',
        limitations=['No event loader or availability validation in numeric kernel',
            'No turning-point estimator, tick-rule trade classifier, regression fit or cost model',
            'Full source data commercially restricted; raw data not redistributed',
            'Full-sample timing and same-day roll choice cannot become live settings'])
    (OUT/'audit.json').write_text(json.dumps(audit,indent=2)+'\n')
    print(json.dumps(claims,indent=2))


if __name__=='__main__':
    main()
