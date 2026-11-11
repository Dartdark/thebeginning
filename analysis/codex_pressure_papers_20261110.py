"""Hash uploaded source PDFs and reconcile screenshot arithmetic; no trading returns."""
from pathlib import Path
import hashlib
import json
import subprocess

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'analysis/outputs/codex_pressure_papers_20261110'
INPUT = ROOT / 'agents/codex/inputs/pressure_papers_20261110'
SOURCES = {
    '0803.1769v1': dict(path='/workspace/attachments/a377f2ab-3793-4292-bd22-c813e8cecef4/0803.1769v1.pdf',
        url='https://arxiv.org/abs/0803.1769v1', title='Stock price jumps: news and volume play a minor role',
        version='arXiv v1, 12 March 2008; uploaded cover also prints November 26, 2024'),
    '2106.07040v1': dict(path='/workspace/attachments/d6af99fa-8845-4c12-9a59-ecc68e5d4823/2106.07040v1.pdf',
        url='https://arxiv.org/abs/2106.07040v1', title='Exogenous and Endogenous Price Jumps Belong to Different Dynamical Classes',
        version='arXiv v1, 13 June 2021; screenshot cites the 2022 publication'),
    '0307332v2': dict(path='/workspace/attachments/76760584-cf88-42ed-b808-9d310980da07/0307332v2.pdf',
        url='https://arxiv.org/abs/cond-mat/0307332v2', title='Fluctuations and response in financial markets: the subtle nature of random price changes',
        version='arXiv cond-mat v2, 25 August 2003; uploaded cover also prints November 26, 2024'),
}


def main():
    OUT.mkdir(parents=True, exist_ok=True); INPUT.mkdir(parents=True, exist_ok=True)
    manifest = {}
    for key, meta in SOURCES.items():
        p = Path(meta['path'])
        text = subprocess.check_output(['pdftotext', '-layout', str(p), '-'], text=True)
        assert key in text
        manifest[key] = dict(filename=p.name, url=meta['url'], title=meta['title'], version=meta['version'],
            pdf_sha256=hashlib.sha256(p.read_bytes()).hexdigest(),
            text_sha256=hashlib.sha256(text.encode()).hexdigest(),
            pages=sum(bool(s.strip()) for s in text.split('\f')), bytes=p.stat().st_size)
    screen = dict(trades=855, percent_profitable=82.22, gross_profit=236839.0, gross_loss=167454.0,
        net_profit=69385.0, profit_factor_displayed=1.41, max_strategy_drawdown=9963.0,
        account_size_required=7223.0, return_on_account_percent_displayed=960.61,
        longs=420, shorts=435, long_net=30695.0, short_net=38690.0,
        sharpe_displayed=0.26, time_in_market_percent_displayed=0.42,
        trading_period_display='7 Yrs, 10 Mths, 20 Dys, 11 Hrs, 5 Mins',
        trader_target_R_claim=0.3, costs_and_size_verified=False, OOS_verified=False,
        source='User-supplied screenshot and chat quotation; transcribed, not an audited trade ledger')
    winners = [n for n in range(screen['trades'] + 1) if round(100 * n / screen['trades'], 2) == screen['percent_profitable']]
    assert len(winners) == 1
    n = winners[0]; nonwinners = screen['trades'] - n
    win = screen['gross_profit'] / n
    loss = screen['gross_loss'] / nonwinners
    ratio = win / loss
    derived = dict(implied_winners=n, nonwinners_including_any_breakevens=nonwinners,
        avg_winner_reported_dollars=win, avg_loser_dollars_assuming_no_breakevens=loss,
        avg_win_loss_ratio_assuming_no_breakevens=ratio,
        loss_win_ratio_assuming_no_breakevens=loss / win,
        profit_factor=screen['gross_profit'] / screen['gross_loss'],
        reported_net_per_trade=screen['net_profit'] / screen['trades'],
        net_profit_to_reported_drawdown=screen['net_profit'] / screen['max_strategy_drawdown'],
        return_on_account_percent=100 * screen['net_profit'] / screen['account_size_required'],
        fixed_point3R_reward_oneR_loss_breakeven_before_costs=1 / 1.3,
        win_rate_margin_percentage_points=100 * (n / screen['trades'] - 1 / 1.3),
        gross_bucket_ratio_breakeven_assuming_no_breakevens=1 / (1 + ratio))
    assert screen['gross_profit'] - screen['gross_loss'] == screen['net_profit']
    assert screen['longs'] + screen['shorts'] == screen['trades']
    assert screen['long_net'] + screen['short_net'] == screen['net_profit']
    assert round(derived['profit_factor'], 2) == screen['profit_factor_displayed']
    assert round(derived['return_on_account_percent'], 2) == screen['return_on_account_percent_displayed']
    (INPUT / 'source_manifest.json').write_text(json.dumps(manifest, indent=2) + '\n')
    result = dict(screenshot_claims=screen, arithmetic=derived, new_return_trials=0,
        exact_trader_rules_available=False, native_execution_verified=False,
        script_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest())
    (OUT / 'screenshot_arithmetic.json').write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps(dict(sources=manifest, arithmetic=derived, new_return_trials=0), indent=2))


if __name__ == '__main__':
    main()
