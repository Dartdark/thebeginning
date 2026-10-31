"""Arithmetic audit of SSRN1025241 printed tables; no strategy/market-data test."""
import hashlib
import json
import math
from pathlib import Path


def main():
    # Order: phi1, phi2, phi3, theta1, Table4 pp29 and Table6 p31.
    base=[.0370,.4448,-.3300,-.2389]
    augmented=[.0522,1.0258,-.8854,.7690]
    signed_base=2*sum(base)
    signed_augmented=2*sum(augmented)
    absolute_spread=2*sum(abs(x) for x in base)
    total=sum(abs(x) for x in base)
    shares=dict(adverse_selection=abs(base[3])/total*100,
        order_handling=abs(base[0])/total*100,
        liquidity=(abs(base[1])+abs(base[2]))/total*100)
    assert math.isclose(absolute_spread,2.1014,abs_tol=1e-10)
    assert not math.isclose(signed_base,2.1014,abs_tol=1e-4)
    assert not math.isclose(signed_augmented,2.1014,abs_tol=1e-4)
    assert abs(shares['liquidity']-73.74)<.01
    nearby_t=[1.345909,-1.269357]
    # Explicit normal approximations, not exact finite-df t tests.
    nearby_two_sided_normal_p=[math.erfc(abs(x)/math.sqrt(2)) for x in nearby_t]
    result=dict(scope="printed-table arithmetic only; no economic trial or historical replication",
        pdf_sha256="b59595017113864c9380eb200f48c0633ecc83f0579b23458a6fa1ad6a2c4b3e",
        script_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        coefficient_order=['phi1','phi2','phi3','theta1'],table4_base=base,table4_augmented=augmented,
        printed_signed_formula_base=signed_base,printed_signed_formula_augmented=signed_augmented,
        absolute_coefficient_reconstruction=absolute_spread,absolute_coefficient_component_percent=shares,
        spread_finding="Table6 matches absolute coefficient magnitudes; its printed signed formula does not reproduce it",
        nearby_table8_t=nearby_t,nearby_two_sided_normal_p=nearby_two_sided_normal_p,
        nearby_finding="No conventional two-sided 10% significance; a directional one-sided test would need separate specification",
        author_sample=dict(raw_transactions=88562,information_ticks=69981,nearby_ticks=11687,
                           start="2000-08-28",end="2006-10-13"))
    path=Path('analysis/outputs/codex_bowe_duration_audit/checks.json')
    path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result,indent=2))


if __name__=='__main__':
    main()
