"""Arithmetic audit of quoted examples only; no market backtest or new trial."""
import hashlib
import json
from pathlib import Path
import statistics

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'analysis/outputs/codex_ssrn2810170_review'


def drawdown(returns):
    wealth = peak = 1.0
    worst = 0.0
    for value in returns:
        wealth *= 1.0 + value
        peak = max(peak, wealth)
        worst = max(worst, 1.0 - wealth / peak)
    return worst, wealth


if __name__ == '__main__':
    OUT.mkdir(parents=True, exist_ok=True)
    sequences = [[.1,.1,-.1,.1,.1,-.1,.1,.1,-.1,.1], [-.1,-.1,-.1,.1,.1,.1,.1,.1,.1,.1]]
    rows = [dict(mean=statistics.mean(x), sample_sd=statistics.stdev(x),
                 max_drawdown=drawdown(x)[0], final_wealth=drawdown(x)[1]) for x in sequences]
    assert sorted(sequences[0]) == sorted(sequences[1])
    assert abs(rows[0]['max_drawdown'] - .1) < 1e-12
    assert abs(rows[1]['max_drawdown'] - .271) < 1e-12
    assert abs(rows[0]['final_wealth'] - rows[1]['final_wealth']) < 1e-12
    pdf = ROOT / 'agents/codex/inputs/papers/ssrn-2810170.pdf'
    result = dict(source_sha256=hashlib.sha256(pdf.read_bytes()).hexdigest(),
        source_version='First draft July 15, 2016; minor edit February 27, 2023',
        source_pages=17, sequences=rows,
        quoted_second_drawdown_approx=.33,
        conventional_compounded_second_drawdown=.271,
        bootstrap=dict(quoted_mean=.00468,quoted_sampling_sd=.00895,
                       ratio_of_quoted_numbers=.00468/.00895,
                       claimed_distance_in_sd='more than 7',
                       verdict='Quoted mean and SD do not establish the claimed distance; no corrected p-value inferred'),
        scope='Source arithmetic and synthetic path illustration only; no independent replication of market results',
        strategy_return_trials=0, account_simulations=0)
    (OUT/'arithmetic_audit.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result,indent=2))
