"""Builds MINED_INDEX.md from TIER_LIST.md: every tested item grouped by mechanism family, with its tier and markets, so a
stage-0 evidence check (S_RANK_PROGRAM.md) takes seconds. Re-run after adding TIER_LIST rows:
  python3 tools/build_mined_index.py
Families come from keyword rules (first match wins); check the 'Other' group after a run and add keywords if needed.
"""
import re
from collections import defaultdict

FAM = [  # (family, keywords) - order = priority
    ("Options / dealer flow / volatility products", r"gamma|gex|0dte|vix|volatility risk premium|option[- ]income|straddle|witching|expir"),
    ("News / scheduled releases", r"\bnfp\b|payroll|cpi|ppi|release|fomc|\beia\b|treasury auction|auction tail|10y / 30y|rig count|\bapi\b inventory"),
    ("Close / auction / settlement flows", r"\bmoc\b|closing|close |settle|last hour|last[- ]30|late[- ]day|\bldf\b|end of day|end-of-day|lbma|fix\b|eos\b"),
    ("Calendar / rebalancing", r"monday|month[- ]end|quarter|turn of the month|holiday|weekday|day of week|rebalanc|pension|seasonal|friday|sunday|weekend|calendar|blackout"),
    ("Overnight / session handoffs", r"overnight|asia|asian|tokyo|london|europe|european|reopen|globex|gap|onb\b|night"),
    ("Opening range / breakouts", r"opening range|\borb\b|breakout|break-out|vault|dual thrust|donchian|first valid|opening drive|open \+|range break|initial balance|\bib\b"),
    ("Order flow / microstructure", r"order[- ]flow|delta|imbalance|book|large trade|liquidity|tick|footprint|absorption"),
    ("Mean reversion / fades", r"revers|fade|bollinger|\bibs\b|mean[- ]revert|vwap|pullback|exhaust"),
    ("Momentum / trend", r"momentum|trend|drift|noise|continuation|follow"),
    ("Cross-asset / pairs / relative value", r"relative strength|pair|spread|cross-asset|lead-lag|ratio|vs rates|dollar|correl"),
    ("ML / signal search / filters / sizing", r"\bml\b|ridge|machine|signal search|filter|sizing|regime|kelly|cushion|walk-forward|gauge"),
]
MKT = [("NQ", r"\bnq\b|mnq|nasdaq|ndx|qqq"), ("ES", r"\bes\b|mes\b|s&p|spx|spy"), ("YM", r"\bym\b|dow"), ("GC", r"\bgc\b|gold|mgc"),
       ("CL", r"\bcl\b|crude|wti|\boil\b|mcl"), ("BTC", r"btc|bitcoin|mbt|crypto"), ("ZN", r"\bzn\b|treasur|bond"), ("FX", r"6e|6b|eur|jpy|fx\b")]

rows, tier = [], None
for ln in open("TIER_LIST.md").read().split("\n"):
    m = re.match(r"^## (S\+|S|A|B|C|D|F)\s*$", ln)
    if m: tier = m.group(1); continue
    if ln.startswith("## "): tier = None
    if tier and ln.startswith("| ") and not ln.startswith("| Item") and not ln.startswith("|---"):
        cells = [c.strip() for c in ln.strip("|").split("|")]
        if cells[0].startswith("(none"): continue
        name = re.sub(r"\*\*", "", cells[0]); typ = cells[1] if len(cells) > 1 else ""
        short = re.split(r" \(|: ", name, maxsplit=1)[0][:90]
        text = (name + " " + typ).lower()
        fam = next((f for f, k in FAM if re.search(k, text)), "Other")
        mk = ", ".join(m_ for m_, k in MKT if re.search(k, text)) or "-"
        files = sorted(set(re.findall(r"`((?:analysis|checks|funded_strategies|personal_strategies|agents)/[^`]+)`", ln)))[:2]
        src = "Paper/book" if re.search(r"paper|book", typ.lower()) else ""
        rows.append((fam, tier, short, mk, src, ", ".join(files)))

order = {t: i for i, t in enumerate(["S+", "S", "A", "B", "C", "D", "F"])}
G = defaultdict(list)
for r in rows: G[r[0]].append(r)
out = ["# Mined index: what has already been tested (auto-built from TIER_LIST.md by `tools/build_mined_index.py`)", "",
       "Stage-0 check (S_RANK_PROGRAM.md): before proposing an idea, find its family and market here, then read the full",
       "TIER_LIST row (search the item name) and its script / output. Also grep HANDOFF.md, NEW_CHAT_BRIEF.md and",
       "analysis/outputs/ for the mechanism. Tiers: A/B work, C weak, D below costs, F fails. Rebuild after new TIER_LIST rows.", "",
       f"{len(rows)} items. Families by count: " + ", ".join(f"{f} {len(v)}" for f, v in sorted(G.items(), key=lambda kv: -len(kv[1]))), ""]
for f, _ in FAM + [("Other", "")]:
    if f not in G: continue
    out += [f"## {f} ({len(G[f])})", "", "| Tier | Item | Markets | Where |", "|---|---|---|---|"]
    for _, t, nm, mk, src, fl in sorted(G[f], key=lambda r: (order[r[1]], r[2].lower())):
        out.append(f"| {t} | {nm}{' (' + src + ')' if src else ''} | {mk} | {fl} |")
    out.append("")
open("MINED_INDEX.md", "w").write("\n".join(out))
print(len(rows), {f: len(v) for f, v in G.items()})
