"""No-return source arithmetic/static-code audit; not a Pine emulator or strategy test."""
from pathlib import Path
import hashlib
import json
import subprocess

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / 'agents/codex/inputs/ssrn6272239'
OUT = ROOT / 'analysis/outputs/codex_donchian_6272239/audit.json'

def main():
    code = (SRC / 'repository/donchian_breakout.pine').read_text()
    checks = {
        'prior_channel_long': 'close > upper[1]' in code,
        'prior_channel_short': 'close < lower[1]' in code,
        'regime_above_average': 'atr >= atrBase * atrMult' in code,
        'trailing_activation_present': 'trail_points=atr * trailATR' in code,
        'trailing_offset_missing': 'trail_offset=' not in code,
        'price_to_tick_conversion_missing': 'syminfo.mintick' not in code,
        'bar_close_fill_setting_missing': 'process_orders_on_close' not in code,
        'on_fill_recalculation_missing': 'calc_on_order_fills' not in code,
        'realtime_tick_recalculation_enabled': 'calc_on_every_tick=true' in code,
        'explicit_quantity_missing': 'qty=' not in code and 'default_qty' not in code,
        'long_stop_uses_current_atr': 'stopL = ep - atr * riskATR' in code,
        'short_stop_uses_current_atr': 'stopS = ep + atr * riskATR' in code,
    }
    assert all(checks.values()), checks
    start, profit = 10000, 41023.96
    result = {
        'source_commit': subprocess.check_output(['git','rev-parse','HEAD'], cwd=ROOT, text=True).strip(),
        'script_sha256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        'input_sha256': {str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(SRC.rglob('*')) if p.is_file()},
        'static_checks': checks,
        'screenshot_transcription': {'timeframe':'1W', 'symbol':'Bitcoin / U.S. Dollar; CRYPTO', 'tester_date_label':'Oct 4, 2009 - Feb 15, 2026', 'profit_usd':profit, 'profit_pct':410.24, 'max_equity_drawdown_usd':8613.24, 'max_equity_drawdown_pct':51.65, 'trades':31, 'wins':28, 'profit_factor':7.076},
        'conditional_arithmetic': {'starting_equity_usd':start, 'ending_equity_if_no_external_flows_usd':start+profit, 'return_pct':profit/start*100, 'win_rate_pct':28/31*100, 'losses':31-28},
        'synthetic_stop_update': {'entry':100, 'risk_atr_multiple':2, 'atr_before':2, 'atr_after':4, 'long_stop_before':100-2*2, 'long_stop_after':100-2*4, 'note':'Illustrates current-ATR stop widening, not market performance.'},
        'owned_btc_files':[str(p.relative_to(ROOT)) for p in sorted((ROOT/'data').glob('*BTC*csv'))],
        'return_trials':0,
        'status':'Source screenshot/arithmetic/static code only. No Pine runtime compilation, author trade replication or independent backtest.'
    }
    assert round(result['conditional_arithmetic']['return_pct'],2)==410.24
    assert round(result['conditional_arithmetic']['win_rate_pct'],2)==90.32
    OUT.parent.mkdir(parents=True,exist_ok=True)
    OUT.write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps({'checks_passed':len(checks),'return_trials':0,'output':str(OUT.relative_to(ROOT))}))

if __name__ == '__main__':
    main()
