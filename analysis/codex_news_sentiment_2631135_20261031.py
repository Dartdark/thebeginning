"""Source claims and algebra audit only, no real returns or candidate optimization."""
from pathlib import Path
import hashlib,json,subprocess
import numpy as np
root=Path(__file__).resolve().parents[1]
inputs=root/'agents/codex/inputs/news_sentiment_2631135_20261031'
out=root/'analysis/outputs/codex_news_sentiment_2631135_20261031'
out.mkdir(parents=True,exist_ok=True)
claims=[dict(name='Sentiment trend',annualized_mean_pct=16.90,vol_pct=26.50,sharpe=.64,max_dd_pct=49.09,trades=673,winners=449,losers=224,holding_weeks=9.51),
dict(name='Sentiment shock',annualized_mean_pct=12.24,vol_pct=25.22,sharpe=.49,max_dd_pct=56.37,trades=896,winners=576,losers=320,holding_weeks=6.96),
dict(name='SP500 benchmark',annualized_mean_pct=6.30,vol_pct=21.18,sharpe=.30)]
scores=np.array([.1,.3,-.2,.4]);telescoping=float(np.diff(scores).sum())
assert np.isclose(telescoping,scores[-1]-scores[0])
probs=np.array([[.8,.1,.1],[.2,.3,.5]]);relevance=np.array([1.,.2])
feature=float(np.mean(relevance*(probs[:,0]-probs[:,2])))
assert np.isclose(feature,.32) # article-count denominator, NOT sum of relevance weights
record=dict(scope='Source-transcribed claims plus synthetic feature algebra; not independent economic replication',
 source='Song et al. 2015, SSRN2631135',
 input_sha256={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in inputs.iterdir() if p.is_file()},
 pdfinfo=subprocess.check_output(['pdfinfo',str(inputs/'paper.pdf')],text=True),
 author_claims=claims,synthetic_checks=dict(telescoping_delta=telescoping,relevance_article_mean=feature,passed=2),
 economic_trials=0,real_returns_computed=False)
(out/'source_audit.json').write_text(json.dumps(record,indent=2)+'\n')
print(json.dumps(record,indent=2))
