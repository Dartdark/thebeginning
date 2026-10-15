"""Trials log and multiple-testing check (added 2026-10-15).

Every item ranked in TIER_LIST.md is a trial; many were scans of several variants. This script
  1. rebuilds TRIALS.csv from TIER_LIST.md: one row per ranked item, its tier, the number of variants it tested (parsed from
     'N tests' / 'N variants' / 'N combinations' in its text, else 1; override in VARIANTS below), and the first t-stat quoted;
  2. prints the bar a new result must clear: N_items = ranked items (each idea counted once), N_all = all variants;
     t_threshold(N) (Bonferroni, one-sided 5%) and the noise Sharpe the best of N trials reaches;
  3. deflated Sharpe ratio (metrics.deflated_sharpe, per trade) of every strategy in the plan, from the MultiCharts trade
     lists, at N = 1, N_items and N_all; DSR >= 0.95 passes;
  4. lists every tier S-B item with its quoted t against t_threshold(N_items).
Rule from now on (DEVELOPMENT_PROCESS.md): a NEW strategy or filter is only promoted above C if its t clears
t_threshold(N_items) or its DSR at N_items is >= 0.95, unless it was pre-registered from an economic mechanism with <= 3
variants (then the bar is t >= 2.0 and a clean placebo / replication) -- the reason is written in its TIER_LIST row.
  python3 analysis/trials.py [SCRATCH_DIR]
"""
import sys, io, re, contextlib, runpy, warnings; warnings.filterwarnings("ignore"); sys.path.insert(0, "analysis")
import numpy as np, pandas as pd
import metrics as M

SP = (sys.argv[1] if len(sys.argv) > 1 else "scratch_data").rstrip("/") + "/"
VARIANTS = {}          # item-name prefix -> number of variants, when the text doesn't say
PLAN = {"VB": "Vault Break", "ONB_ML": "Overnight Bias ML v2", "MON": "Monday Long", "EOS": "Expiration Open Short",
        "LDF": "Late-Day Flow", "NFP": "NFP Fade", "BRIDGE": "Bridge Monday Long", "VCS": "Vol-Control Sell (dropped)"}


def parse_tier_list(path="TIER_LIST.md"):
    rows, tier = [], None
    for line in open(path, encoding="utf-8"):
        m = re.match(r"^## ([SABCDF])\s*$", line.strip())
        if m: tier = m.group(1); continue
        if line.startswith("## "): tier = None; continue
        if tier is None or not line.startswith("| ") or line.startswith("|---") or line.startswith("| Item"): continue
        txt = line.replace("\\|", "/"); cells = [c.strip() for c in txt.strip().strip("|").split("|")]
        name = re.sub(r"[*`]", "", cells[0])[:140]
        nums = [int(x.replace(",", "")) for x in re.findall(r"(\d[\d,]*)\s+(?:strategy x feature\s+)?(?:tests|variants|combinations|splits|filters)\b", txt)]
        var = max([n for n in nums if n < 5000] + [1])
        for k, v in VARIANTS.items():
            if name.startswith(k): var = v
        t = re.search(r"\bt\s*=?\s*([−-]?\d+\.\d+)", txt)
        rows.append(dict(tier=tier, item=name, variants=var, t_quoted=float(t.group(1).replace("−", "-")) if t else np.nan))
    return pd.DataFrame(rows)


if __name__ == "__main__":
    pd.set_option("display.width", 220); pd.set_option("display.max_colwidth", 70)
    print(__doc__.split("\n")[0])
    L = parse_tier_list(); L.to_csv("TRIALS.csv", index=False)
    n_items, n_all = len(L), int(L.variants.sum())
    print(f"\nTRIALS.csv: {n_items} ranked items, {n_all} variants in all; by tier {L.tier.value_counts().reindex(list('SABCDF')).to_dict()}")
    print("\nThe bar for the best of N trials (one-sided 5%):")
    for nm, n in (("one pre-registered test", 1), ("a 10-variant scan", 10), ("N_items", n_items), ("N_all", n_all)):
        print(f"   {nm:<24} N {n:5d}: |t| >= {M.t_threshold(n):.2f}; best noise Sharpe on 252 days x sqrt(252) = "
              f"{M.expected_max_sr(n, 252) * np.sqrt(252):.2f}, on 1,000 trades per trade x sqrt(n) = {M.expected_max_sr(n, 1000) * np.sqrt(1000):.2f}")

    print("\nDeflated Sharpe of the plan's strategies (per trade, MultiCharts lists, $7.25 + 1 tick):")
    sys.argv = ["x", SP]
    with contextlib.redirect_stdout(io.StringIO()):
        T = runpy.run_path("analysis/plan_agreement_test.py", run_name="__main__")["T"]
    rows = []
    for k, nm in PLAN.items():
        x = T[T.strat == k].net
        if len(x) < 10: continue
        t = x.mean() / x.std() * np.sqrt(len(x))
        rows.append(dict(strategy=nm, trades=len(x), t=round(t, 2), PSR=M.psr(x), DSR_items=M.deflated_sharpe(x, n_items),
                         DSR_all=M.deflated_sharpe(x, n_all), passes_items=M.deflated_sharpe(x, n_items) >= 0.95))
    print(pd.DataFrame(rows).round(3).to_string(index=False))

    print(f"\nTier S-B items: quoted t vs t_threshold(N_items) = {M.t_threshold(n_items):.2f} (t not quoted = blank):")
    top = L[L.tier.isin(list("SAB"))].copy(); top["clears"] = top.t_quoted.abs() >= M.t_threshold(n_items)
    print(top[["tier", "item", "variants", "t_quoted", "clears"]].to_string(index=False))
