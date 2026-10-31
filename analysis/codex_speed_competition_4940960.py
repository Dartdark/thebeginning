"""Source-formula arithmetic only for SSRN 4940960; zero market return trials."""
from pathlib import Path
import hashlib
import json
import subprocess
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
PDF = ROOT/'agents/codex/inputs/speed_competition_4940960/source.pdf'
OUT = ROOT/'analysis/outputs/codex_speed_competition_4940960'


def precision(n, f, sigma2=1., noise2=0., eta=0.):
    """Lemma 3; sigma2 = fundamental variance, noise2 = early signal-error variance.

    Eta = incremental information precision parameter, not measured latency.
    No demand/profit/execution claim follows from this calculation.
    """
    if n < 1 or sigma2 <= 0 or noise2 < 0 or not 0 <= f <= n or not 0 <= eta <= noise2/sigma2:
        raise ValueError('Invalid theoretical parameter domain')
    s = n-f
    xi1 = (f+1)/sigma2*(sigma2+noise2)/(sigma2+(f+1)*noise2)
    den = (1-(f+1)*s*eta)*sigma2+(f+1)*(s+1)*noise2
    if den <= 0:
        raise ValueError('Nonpositive conditional-precision denominator')
    xi2 = (f+1)*(s+1)/sigma2*(sigma2+noise2)/den
    return xi1, xi2


def main():
    OUT.mkdir(parents=True,exist_ok=True)
    n=20
    rows=[]
    cases=[('benchmark',0.,0.),('diffusion_eta1',25.,1.),('diffusion_eta20',25.,20.)]
    for case,noise2,eta in cases:
        for f in range(n+1):
            a,b=precision(n,f,noise2=noise2,eta=eta)
            rows.append(dict(case=case,n=n,fast=f,slow=n-f,fundamental_variance=1.,
                early_signal_error_variance=noise2,eta=eta,intermediate_precision=a,overall_precision=b))
    df=pd.DataFrame(rows)
    df.to_csv(OUT/'model_precision.csv',index=False)
    base=df[df.case=='benchmark']
    assert int(base.iloc[base.overall_precision.argmax()].fast)==10
    assert np.allclose(base.overall_precision,(base.fast+1)*(n-base.fast+1))
    assert np.allclose(base.intermediate_precision,base.fast+1)
    assert np.all(np.diff(base.intermediate_precision)>0)
    fastdiff=df[df.case=='diffusion_eta20']
    assert np.all(np.diff(fastdiff.overall_precision)<0)
    assert np.all(np.diff(fastdiff.intermediate_precision)>0)
    # No diffusion is not the same as perfect information when noise remains.
    assert not np.isclose(precision(n,10,noise2=25.,eta=0.)[0],11.)
    bad=0
    for kwargs in ({'f':-1},{'sigma2':0.},{'eta':1.,'noise2':0.}):
        values=dict(n=n,f=10); values.update(kwargs)
        try:
            precision(**values)
        except ValueError:
            bad+=1
    assert bad==3
    text=subprocess.check_output(['pdftotext','-layout',str(PDF),'-'],text=True)
    empirical=text[text.index('3.4. Empirical Implications'):text.index('4. Information Diffusion',text.index('3.4. Empirical Implications'))]
    (OUT/'proposed_empirical_section.txt').write_text(empirical)
    result=dict(source_sha256=hashlib.sha256(PDF.read_bytes()).hexdigest(),
        source_title='Speed Competition and Strategic Trading',authors=['Xue-Zhong He','Junqing Kang'],
        evidence='Analytical model plus source numerical illustrations; proposed empirical design, no implemented strategy test',
        arithmetic_checks_pass=True,invalid_parameter_cases_rejected=bad,market_return_trials=0,
        calibrated_to_NQ_or_ES=False,full_equilibrium_or_HFT_recomputed=False,
        maximum_benchmark_precision=float(base.overall_precision.max()),benchmark_maximizing_fast=10,
        illustrative_parameters='N=20, sigma=1; early-signal sd=5 in diffusion cases, following Figure 4',
        source_caveat='Proposition 3(iii) prose says overall precision falls but its printed derivative refers to xi1>0; not an OCR correction',
        owned_orderflow_header=pd.read_csv(ROOT/'data/OF_1min_2026_3.csv',nrows=0).columns.tolist())
    (OUT/'audit.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result,indent=2))


if __name__=='__main__':
    main()
