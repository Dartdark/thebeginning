"""Paper arithmetic and input inventory only. No historical return/signal screen."""
import hashlib
import json
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / 'agents/codex/inputs/delta_straddle_4677166'
NORMAL = lambda x: .5 * (1 + math.erf(x / math.sqrt(2)))


def main():
    signal = lambda x: 2 * NORMAL(x) - 1
    assert signal(0) == 0 and abs(signal(2) + signal(-2)) < 1e-12
    assert all(-1 <= signal(x) <= 1 for x in [-100, -2, 0, 2, 100])
    corr = 6 / math.pi * math.asin(.5 * math.sqrt(.5))
    # Fixed, invented AR(1) covariance calculation, not fitted market parameters.
    rho, n = .1, 100
    mean_variance_ratio = 1 + 2 * sum((1-k/n) * rho**k for k in range(1,n))
    corrected_multiplier = 1 / math.sqrt(mean_variance_ratio)
    printed_multiplier = math.sqrt((1+rho)/(1-rho))
    assert corrected_multiplier < 1 < printed_multiplier
    # Transcription of Appendixp36. Weights already include asset-class allocation.
    universe = {
      'equities': [('GX1',2.24),('VG1',3.53),('Z1',1),('ES1',12.06),('FTJGUSSE',.69),
                   ('NQ1',1.32),('NI1',1.08),('TP1',.88),('KM1',.94),('HI1',1.26)],
      'fx_total_return': [('EURUSDCR',9.46),('GBPUSDCR',3.87),('SEKUSDCR',.67),
                          ('CADUSDCR',1.54),('JPYUSDCR',6.75),('AUDUSDCR',2.07),('NZDUSDCR',.63)],
      'commodities': [('CO1',4.64),('CL1',9.75),('HO1',1.06),('XB1',.96),('NG1',1.77),
                      ('GC1',2.89),('SI1',.60),('HG1',.65),('C1',.60),('S1',2.09)],
      'rates': [('ED4',2.52),('TU1',1.38),('FV1',2.06),('TY1',3.83),('US1',.85),
                ('DU1',1.58),('OE1',2.96),('RX1',5.04),('OAT1',.82),('IK1',.65),
                ('G1',.60),('JB1',1.47),('YM1_Australian3Y',.56),('XM1',.66)]}
    owned_names = sorted(p.name for p in (ROOT/'data').glob('*') if p.is_file())
    report = {
      'review_local_date':'2026-11-08', 'source_written_date':'2018-02-06',
      'ssrn_posted_date':'2024-01-17', 'strategy_trials':0,
      'signal_fixture':{str(t):signal(t) for t in [-2,0,2]},
      'ratio_two_correlation':corr,
      'ar1_footnote_check':{'rho':rho,'n':n,'mean_variance_ratio':mean_variance_ratio,
        'finite_sample_t_multiplier':corrected_multiplier,'printed_t_multiplier':printed_multiplier,
        'interpretation':'Positive autocorrelation inflates mean variance; printed correction direction is reversed under marginal-return volatility convention'},
      'universe_transcription':universe,
      'universe_count':sum(map(len,universe.values())),
      'weight_sums_pct':{c:sum(w for _,w in rows) for c,rows in universe.items()},
      'source_claims':{'table7':{'annual_return_pct':9.27,'vol_pct':9.04,'sharpe':1.03,'max_dd_pct':-13.60},
                       'table19_fast':{'gross_return_pct':7.85,'net_return_pct':-3.23,'net_sharpe':-.36,'max_dd_pct':-156.18},
                       'table18_sharpe_no_floor':.92,'table18_sharpe_floor_025':1.03},
      'owned_data_filenames_only':owned_names,
      'data_gate':'No source-equivalent full universe, FX total-return/carry, authenticated native rolls/cash ledger or original execution protocol admitted',
      'hashes':{str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in BASE.rglob('*') if p.is_file()},
      'script_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest()}
    assert report['universe_count'] == 41
    (ROOT/'analysis/outputs/codex_delta_straddle_4677166/source_audit.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps({'universe_count':41,'correlation_ratio_2':corr,'ar1_check':'printed correction reversed', 'strategy_trials':0}))


if __name__ == '__main__':
    main()
