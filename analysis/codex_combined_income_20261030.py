"""Arithmetic on published plan benchmarks; no new backtest or account simulation."""
from pathlib import Path
import ast,hashlib,json,re,subprocess

ROOT=Path(__file__).resolve().parents[1]
REF='a01be1bfd0a3c33bc2c6745b24acbf5c14e924c1'
INPUT=ROOT/'agents/codex/inputs/combined_income_20261030'
OUT=ROOT/'analysis/outputs/codex_combined_income_20261030'
REPORT=ROOT/'agents/codex/results/combined_income_20261030.md'
FILES=['analysis/outputs/t_oneside_bench2_output.txt','analysis/outputs/personal_variants_output.txt',
       'analysis/outputs/personal_portfolio_output.txt','analysis/funded_sim150.py',
       'personal_strategies/PORTFOLIO.md','funded_strategies/FUNDED_PLAN.md']
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def money(x):return f'${x:,.0f}'
def main():
    INPUT.mkdir(parents=True,exist_ok=True);OUT.mkdir(parents=True,exist_ok=True);sources=[]
    for rel in FILES:
        data=subprocess.check_output(['git','show',REF+':'+rel],cwd=ROOT)
        p=INPUT/rel;p.parent.mkdir(parents=True,exist_ok=True)
        if p.exists():assert p.read_bytes()==data
        else:p.write_bytes(data)
        sources.append(dict(path=str(p.relative_to(ROOT)),source_path=rel,sha256=sha(p)))
    funded=(INPUT/FILES[0]).read_text()
    row=next(x for x in funded.splitlines()if x.startswith('150K plan (now)'))
    vals=[int(x.replace(',',''))for x in re.findall(r'\$([\d,]+)',row)]
    funded_y1,funded_p5,funded_y2=vals[:3]
    personal=(INPUT/FILES[1]).read_text().split('current: 19 pieces, 19 micros\n',1)[1].split('\naggressive:',1)[0]
    annual=int(re.search(r'\$([\d,]+) a year',personal)[1].replace(',',''))
    capital=int(re.search(r'capital \$([\d,]+)',personal)[1].replace(',',''))
    dd95=int(re.search(r'DD p95 \$([\d,]+)',personal)[1].replace(',',''))
    dd=int(re.search(r'max DD \$([\d,]+)',personal)[1].replace(',',''))
    caps_node=next(x for x in ast.parse((INPUT/FILES[3]).read_text()).body
                   if isinstance(x,ast.Assign)and any(isinstance(t,ast.Name)and t.id=='CAPS'for t in x.targets))
    caps=ast.literal_eval(caps_node.value.args[0]);cap=sum(caps)
    assert cap==20500 and funded_y1==18056 and funded_y2==20183 and annual==41475
    n=20;scale=10
    pa1=n*funded_y1;pa2=n*funded_y2;pp=scale*annual;combined=pa1+pp
    result=dict(date='2026-10-30 America/Los_Angeles',source_claude_ref=REF,
        user_confirmed_personal='Current19-piece portfolio, one mini per leg; no aggressive doubling',
        scenario='First modeled year after20fresh150Kfunded accounts are activated; personal already fully capitalized',
        funded=dict(accounts=n,source_mean_one_year_per_account=funded_y1,source_mean_two_year_per_account=funded_y2,
            mean_year1_payouts=pa1,mean_year2_increment_without_replacement=pa2-pa1,
            cohort_lifetime_payout_cap=n*cap,source_one_account_p5_year1=funded_p5),
        personal=dict(one_micro_mean_annual=annual,mini_equivalent_scale=scale,approx_annual_profit=pp,
            approx_monthly_average=pp/12,capital_at_published_20percent_rule=scale*capital,
            scaled_personal_dd95=scale*dd95,scaled_historical_dd=scale*dd,
            method='Linear scaling of published costed micro results; no native-mini fee/impact rerun'),
        combined=dict(reference_year1_total=combined,monthly_average=combined/12,
            year2_total_without_replacing_funded_accounts=pa2-pa1+pp),
        limitations=['Historical/bootstrap reference, not validated live income or a joint distribution',
            'Current-funded SwingTarget account replay remains pending after exit-kind correction',
            'Before taxes and future evaluation/replacement costs; existing funded activation is assumed completed',
            'No compounding; mini-cost savings or size-dependent impact are not newly credited/modelled',
            'Twenty copied accounts share risk; do not treat them as independent draws',
            'Funded cohort pays at most6payouts/account then closes under the model; recurring income needs replacement slots'],
        new_strategy_trials=0,new_account_simulations=0)
    (OUT/'calculation.json').write_text(json.dumps(result,indent=2,allow_nan=False)+'\n')
    text=f'''# Twenty activated150K funded accounts plus the full current personal portfolio

Summary: Published benchmarks imply about {money(combined)} in the first modeled year, averaging {money(combined/12)}/month.
That combines {money(pa1)} in funded cash payouts and approximately {money(pp)} in personal trading profit.
User definition: current19-piece personal portfolio at one mini per leg, without the aggressive five doubled positions.
This is conditional benchmark arithmetic before taxes/replacement fees, not a live-income forecast or a new simulation.
The same funded cohort has a {money(n*cap)} lifetime payout cap; personal sizing implies roughly {money(scale*capital)} of capital.

Sources pinned at Claude `{REF}`. [Input/hash manifest](../inputs/combined_income_20261030/manifest.json).
Script: [calculation](../../../analysis/codex_combined_income_20261030.py).
Output: [calculation.json](../../../analysis/outputs/codex_combined_income_20261030/calculation.json).
No market-return test, parameter selection or account simulation was run.

## First-year reference calculation

| Component | Basis | First year | Monthly average |
|---|---|---:|---:|
|20already activated150K funded PAs|20 x {money(funded_y1)} source mean payout|{money(pa1)}|{money(pa1/12)}|
|Current19-piece personal portfolio|10 x {money(annual)} published one-micro annual profit|{money(pp)}|{money(pp/12)}|
|Combined|Arithmetic sum of the above reference figures|**{money(combined)}**|**{money(combined/12)}**|

Funded source: `analysis/outputs/t_oneside_bench2_output.txt`, current150K base row,1,000paired two-year
bootstrap histories. Mean first-year payout is {money(funded_y1)} per account; year one is250modeled trading days.
This is the current roster (including Swing Target in place of Dual Thrust, while150K keeps Relative Strength,
Monday Long and Overnight Tick). Existing cushion, integer-size and payout rules remain part of the source model.
It does not assume constant maximum size regardless of drawdown or add T_ONESIDE to150K.

Personal source: `analysis/outputs/personal_variants_output.txt`, the current19-piece row, not conservative/aggressive.
Its published2018–2026 historical annual profit is {money(annual)} at one micro per strategy unit. One mini is10micro
equivalents for the included contracts, so the fixed-size annual reference is {money(pp)}. S30's two underlying legs
both scale with its source unit; it is not replaced with a quarter-weight ladder mix. This is the exact user-selected
current portfolio definition. The older {money(322400)} top ladder row uses a different core/S30 mix and is not used.

Personal risk figures scale the same way: published p95 annual drawdown about {money(scale*dd95)}, historical max
drawdown {money(scale*dd)}, and risk-rule capital around {money(scale*capital)} to hold the modeled p95 drawdown at20%.
This is the published risk-capital rule, not a verified broker margin requirement or a recommendation to allocate.

## These figures are not a perpetual monthly salary

The funded simulator's payout ladder is {', '.join(money(x)for x in caps)}, totaling {money(cap)} per account.
After payout six, that modeled account closes. Thus these original20accounts can pay at most {money(n*cap)} in total,
not that amount every year. The latest source mean two-year payout is {money(funded_y2)} per account, so without
replacements the source implies approximately {money(pa2-pa1)} additional funded cash in year two. With unchanged
personal size/annual reference, the illustrative second-year total would then be {money(pa2-pa1+pp)}.
Maintaining an ongoing20-slot fleet requires replacement evaluations, their fees, waiting time and failures;
no current-roster recurring-fleet result was newly simulated here. The first-year number starts after activation
and must not be substituted for the earlier ramp-from-zero projections.

Monthly figures are annual arithmetic divided by12. Payout eligibility, correlated losses and trading profits are
uneven through the year. Twenty copies are not20independent opportunities for diversification. Adding separate
payout/profit references gives no joint confidence interval or guaranteed minimum; neither source's p5 can simply
be added to the other's p5 to make a combined percentile.

## Costs and verification limits

- Figures retain the source models' trading-cost deductions and are before tax and future evaluation/replacement
  costs. Activation is assumed already paid/completed. No gross trading P&L was substituted for funded cash withdrawals.
- Personal is a tenfold scaling of costed micro results, not a fresh native-mini fill/commission/impact simulation.
  The source charges micro costs of roughly$1.25RT (NQ-normalized fees plus$0.55extra per micro trade). Mini commissions
  could differ, but no fee saving is credited here; unchanged fill quality at mini size is not certified.
- The funded {money(funded_y1)} benchmark is published research. After the reviewed Swing Target exit-kind correction,
  the complete current account replay is still pending. Do not label this a corrected independently verified forecast.
- Personal results include pieces awaiting live/forward verification and known marking/data limits; the live edge
  is unproven. Constant sizes are assumed, and transfers from Apex into personal capital are not counted again as profit.
- No combined75%-edge payout simulation exists for this exact setup. Multiplying funded payouts by0.75 would not
  reproduce drawdown, consistency, payout-cap and eligibility effects, so no such result is invented.

Inputs are rounded published summaries. Dollar arithmetic precision is not prediction accuracy.

No plan, allocation, live strategy, VPS, broker or API settings were changed. Research/scout selection history
and budgets are untouched. For Claude: `agents/codex/results/combined_income_20261030.md`.
'''
    # Readable prose without changing source identifiers or frozen hashes.
    replacements={'activated150K':'activated 150K','current19':'current 19','of20':'of 20','original20':'original 20',
        '20already activated150K':'20 already activated 150K','current150K':'current 150K',
        'row,1,000paired':'row, 1,000 paired','is250modeled':'is 250 modeled','while150K':'while 150K',
        'to150K':'to 150K','published2018':'published 2018','is10micro':'is 10 micro','at20%':'at 20%',
        'are not20independent':'are not 20 independent','risk-rule':'risk-rule','by12':'by 12',
        'roughly$1.25RT':'roughly $1.25 RT','plus$0.55extra':'plus $0.55 extra','combined75%':'combined 75%',
        'by0.75':'by 0.75','ongoing20-slot':'ongoing 20-slot','all20':'all 20'}
    for a,b in replacements.items():text=text.replace(a,b)
    REPORT.write_text(text)
    (INPUT/'manifest.json').write_text(json.dumps(dict(ref=REF,files=sources,user_confirmed_scale='one mini per leg, current19pieces'),indent=2)+'\n')
    (OUT/'manifest.json').write_text(json.dumps(dict(ref=REF,script_sha256=sha(__file__),report_sha256=sha(REPORT),calculation_sha256=sha(OUT/'calculation.json')),indent=2)+'\n')
    print(json.dumps(result,indent=2))
if __name__=='__main__':main()
