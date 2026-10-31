"""Printed-table consistency only; no historical market-return tests."""
import json, hashlib
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
SRC=ROOT/'agents/codex/inputs/bubble_riding_4494963_20261031'
OUT=ROOT/'analysis/outputs/codex_bubble_riding_audit_20261031'


def main():
    claims={'weekly':{
        'PSYI':{'wealth':6.39,'annual_pct':13.13,'sharpe_row_as_printed':6.55,'trading_periods':122},
        'MPSYI':{'wealth':5.02,'annual_pct':11.32,'sharpe_row_as_printed':5.80,'trading_periods':168},
        'DPSYI':{'wealth':6.64,'annual_pct':13.41,'sharpe_row_as_printed':6.66,'trading_periods':87},
        'BH':{'wealth':5.40,'annual_pct':11.87,'sharpe_row_as_printed':6.13,'trading_periods':2}},
        'daily':{
        'PSYI':{'gross_wealth':7.81,'net_wealth':.70,'gross_annual_pct':21.15,'net_annual_pct':-3.30,'periods':481},
        'MPSYI':{'gross_wealth':9.68,'net_wealth':.02,'gross_annual_pct':23.60,'net_annual_pct':-29.76,'periods':1207},
        'DPSYI':{'gross_wealth':7.90,'net_wealth':1.37,'gross_annual_pct':21.28,'net_annual_pct':3.01,'periods':348}},
        'confidence_annual_pct':{'90':11.88,'95':13.41,'99':13.22},
        'source_cost_wording':'Round trip cost0.5% of total real return; implementation ambiguous',
        'source_period':'2006-01-04 to2020-12-30', 'evidence':'Transcribed author claims, not independent returns'}
    audit={'weekly_selected_minus_BH_annual_pp':13.41-11.87,
           'daily_hypothetical_multiplicative_cost_consistency':{
            k:v['gross_wealth']*(1-.005)**v['periods'] for k,v in claims['daily'].items()},
           'note':'Approximate agreement with rounded net wealth does not prove author cost code, turnover or execution.',
           'new_economic_return_trials':0,'account_simulations':0,
           'source_sha256':hashlib.sha256((SRC/'source.pdf').read_bytes()).hexdigest(),
           'text_sha256':hashlib.sha256((SRC/'source.txt').read_bytes()).hexdigest(),
           'code_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest()}
    OUT.mkdir(parents=True,exist_ok=True)
    for name,value in [('claims.json',claims),('audit.json',audit)]:
        (OUT/name).write_text(json.dumps(value,indent=2)+'\n')
    print(json.dumps(audit,indent=2))


if __name__=='__main__':main()
