"""No-return power/cost arithmetic; assumptions, not measured opportunity or SD."""
import json
from math import sqrt
from pathlib import Path

def main():
    cases = []
    for sd in (100, 200, 400):
        for retained in (1.0, 0.5, 0.2):
            n = int(252 * 5 * retained)
            for effective_fraction in (1.0, 0.5):
                needed = 2 * sd / sqrt(n * effective_fraction)
                cases.append(dict(assumed_sd_es_dollars=sd, assumed_retained_fraction=retained,
                    assumed_n=n, effective_n=n * effective_fraction,
                    required_net_for_t2=round(needed, 2),
                    required_gross_at_reference_cost30=round(needed + 30, 2)))
    result = dict(return_trials=0, kind='assumed power budget; no market data read',
        es_point_value=50, reference_commission_rt=5, reference_slippage_two_ticks=25,
        reference_total_cost=30, reference_cost_stress_1_5x=45,
        recorded_arca_list_months=105, recorded_list_per_month=500,
        recorded_full_history_list_cost=105*500, recorded_design_list_cost=60*500,
        list_price_is_not_personal_quote=True, cases=cases)
    out = Path(__file__).resolve().parents[1] / 'analysis/outputs/codex_spy_close_evidence'
    out.mkdir(parents=True, exist_ok=True)
    (out/'budget.json').write_text(json.dumps(result, indent=2)+'\n')
    print('Wrote assumed power/cost budget; 0 return trials.')

if __name__ == '__main__':
    main()
