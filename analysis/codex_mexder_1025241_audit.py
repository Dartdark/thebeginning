"""Deterministic checks of printed source tables, not a market-return backtest."""
from pathlib import Path
import hashlib
import json
import math

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'analysis/outputs/codex_mexder_1025241_audit'


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    reported_spread = 2.1014
    panels = {
        'Table4_A': dict(phi1=.0370, phi2=.4448, phi3=-.3300, theta1=-.2389),
        'Table4_B': dict(phi1=.0522, phi2=1.0258, phi3=-.8854, theta1=.7690),
    }
    checks = {}
    for name, parameters in panels.items():
        implied = 2 * sum(parameters.values())
        checks[name] = dict(printed_parameters=parameters,
                           formula='Table6: S=2*(theta1+phi1+phi2+phi3)',
                           calculated_spread=implied, reported_Table6_spread=reported_spread,
                           difference=implied-reported_spread,
                           max_rounding_error_from_four_4decimal_coefficients=.0004,
                           reconciles_with_printed_formula=abs(implied-reported_spread) <= .0004)
    nearby = {name: dict(t=t, approximate_two_sided_normal_p=math.erfc(abs(t)/math.sqrt(2)))
              for name, t in [('expected_duration', 1.345909), ('volume', -1.269357)]}
    pdf = ROOT / 'agents/codex/inputs/ssrn1025241/source.pdf'
    result = dict(source_pdf_sha256=hashlib.sha256(pdf.read_bytes()).hexdigest(),
                  source='Bowe/Hyde/McFarlane October2007, SSRN1025241',
                  spread_checks=checks, nearby_Table8=nearby,
                  scope='Printed-source arithmetic only; no model fitting or raw-data reproduction',
                  limits='No raw transactions, quote signs, fitted estimates or undisclosed transformations supplied. '
                         'p-values are normal-reference approximations, not re-estimated inference.',
                  new_economic_trials=0)
    assert not any(v['reconciles_with_printed_formula'] for v in checks.values())
    (OUT/'checks.json').write_text(json.dumps(result, indent=2)+'\n')
    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    main()
