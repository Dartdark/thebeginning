"""Zero-dependency replication & audit script for NQESCrossFlow (for Claude / independent checker).

Run:
  python strategies/NQESCrossFlow/reproduce_audit.py
"""
import os, csv, math
from collections import defaultdict

def audit():
    trades_path = os.path.join(os.path.dirname(__file__), "trades.csv")
    if not os.path.exists(trades_path):
        print(f"Error: {trades_path} not found.")
        return
        
    trades = []
    with open(trades_path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            trades.append({
                "date": int(row["date"]),
                "year": int(row["year"]),
                "side": float(row["side"]),
                "pts": float(row["pts"]),
                "pnl": float(row["pnl"]),
                "reason": row["reason"]
            })
            
    print("="*75)
    print(f"AUDIT SUMMARY: NQESCrossFlow ({len(trades)} total trades 2018-2026)")
    print("="*75)
    
    periods = [
        ("In-Sample (2018-2022)", lambda t: t["year"] <= 2022),
        ("Out-of-Sample Holdout (2023-2026)", lambda t: t["year"] >= 2023),
        ("Full History (2018-2026)", lambda t: True)
    ]
    
    for name, cond in periods:
        sub = [t for t in trades if cond(t)]
        n = len(sub)
        if n == 0:
            continue
        pnls = [t["pnl"] for t in sub]
        tot = sum(pnls)
        avg = tot / n
        variance = sum((x - avg) ** 2 for x in pnls) / (n - 1) if n > 1 else 0
        std = math.sqrt(variance)
        t_stat = avg / std * math.sqrt(n) if std > 0 else 0
        wins = [x for x in pnls if x > 0]
        losses = [abs(x) for x in pnls if x < 0]
        wr = len(wins) / n * 100
        pf = sum(wins) / sum(losses) if sum(losses) > 0 else float("nan")
        
        # Max drawdown
        cum = 0.0
        peak = 0.0
        max_dd = 0.0
        for x in pnls:
            cum += x
            if cum > peak:
                peak = cum
            dd = peak - cum
            if dd > max_dd:
                max_dd = dd
                
        # Year by year
        by_yr = defaultdict(float)
        for t in sub:
            by_yr[t["year"]] += t["pnl"]
        pos_yrs = sum(1 for y, v in by_yr.items() if v > 0)
        
        print(f"\n--- {name} ---")
        print(f"Trades: {n:3d} | Net: ${tot:9.2f} | Avg: ${avg:6.2f} | PF: {pf:4.2f} | t-stat: {t_stat:4.2f} | Win: {wr:4.1f}% | MaxDD: ${max_dd:7.2f} | Yrs+: {pos_yrs}/{len(by_yr)}")
        yr_str = ", ".join(f"{y}: ${v:+,.0f}" for y, v in sorted(by_yr.items()))
        print(f"By Year: {{{yr_str}}}")

if __name__ == "__main__":
    audit()
