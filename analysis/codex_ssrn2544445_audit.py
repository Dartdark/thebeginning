"""Source units, metadata and power arithmetic; zero market-return trials."""
import hashlib
import json
import math
from pathlib import Path
import subprocess

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT/'analysis/outputs/codex_ssrn2544445_review'


if __name__ == '__main__':
    OUT.mkdir(parents=True,exist_ok=True)
    equity, future, multiplier = 500000.,20.,1000.
    q1=-math.floor(equity*.6/(future*multiplier))
    q3_printed=-math.floor(equity*-.035/multiplier)
    q3_ui=-math.floor(equity*.035/multiplier)
    assert (q1,q3_printed,q3_ui)==(-15,18,-17)
    pdf=ROOT/'agents/codex/inputs/papers/ssrn-2544445.pdf'
    result=dict(source_sha256=hashlib.sha256(pdf.read_bytes()).hexdigest(),
        review_commit=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),
        source='Donninger, Dec2014, Revision1 Jan5 2015, four-page user upload',
        equation1_quantity=q1,equation3_literal_negative_leverage=q3_printed,
        equation3_positive_UI_magnitude=q3_ui,
        min_maturity_UI=5,min_maturity_units='not defined in prose; days type/selection rule unresolved',
        nominal_5pct_stop_per_VX=future*.05*multiplier,
        nominal_stop_source_15VX=abs(q1)*future*.05*multiplier,
        source_15VX_roundtrip_cost=abs(q1)*60.,
        stop_plus_cost_equity_fraction=(abs(q1)*future*.05*multiplier+abs(q1)*60)/equity,
        stop_limit_note='Trigger level arithmetic, not a fill or maximum loss guarantee',
        source_cost_per_VX=60.,source_cost_breakeven_points=60/multiplier,
        illustrative_one_tick_per_fill_plus_10_commission=2*50+10,
        zero_stops_in_34_iid_upper95=1-.05**(1/34),
        iid_note='Hypothetical stationary independent Bernoulli upper bound; not a forecast of jump or stop risk',
        power=dict(assumed_events=34,assumed_trade_sd_per_VX=500.,
                   net_mean_for_t2=2*500/math.sqrt(34),
                   gross_mean_for_t2_source_cost=2*500/math.sqrt(34)+60,
                   status='Assumptions only; neither SD nor modern event eligibility estimated'),
        nominal_5year_CAGR=(1+.2868)**.2-1,
        owned_vix_named_files=[str(p.relative_to(ROOT)) for p in (ROOT/'data').rglob('*')
             if p.is_file() and any(x in p.name.lower() for x in ['vix','vx_','vxm'])],
        source_figures_inspected=[2,3,4],strategy_return_trials=0,account_simulations=0,
        evidence_status='Source arithmetic/filename inventory only; no matching intraday VX panel acquired')
    (OUT/'source_audit.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result,indent=2))
