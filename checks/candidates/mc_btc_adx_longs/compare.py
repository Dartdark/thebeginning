"""Compare the replica (replica.py outputs) with the reference: paper books = analysis/btc_adx_ensemble_test.run(setup()) both sides;
real side = btc_adx_whole_contract_check version (a) = jesse_rebuilds_personal_bench.mark(th=NaT), re-done per trade here (same formula).
Run from repo root after replica.py."""
import sys, warnings; warnings.filterwarnings("ignore"); sys.path.insert(0, "analysis"); sys.path.insert(0, "checks/candidates/mc_btc_adx_longs")
import numpy as np, pandas as pd
import btc_adx_ensemble_test as PB
import importlib.util as _iu; _sp = _iu.spec_from_file_location("btc_rep", "checks/candidates/mc_btc_adx_longs/replica.py"); RP = _iu.module_from_spec(_sp); _sp.loader.exec_module(RP)
OUT = "checks/candidates/mc_btc_adx_longs/"
MULT, TICK, COMM = 0.1, 5.0, 2.5

ref = PB.run(PB.setup())
ref.to_csv(OUT + "ref_paper.csv", index=False)
# futures arrays as the reference (UTC bar-open 15m candles from the same roll-adjusted 1-min)
src = open("analysis/btc_adx_futures_test.py", encoding="utf-8").read().split("\nm = load_fut()")[0].split("import btc_adx_ensemble_test as P")[1].split("\n", 2)[2]
ns = {"np": np, "pd": pd, "glob": __import__("glob")}; exec(src, ns)
f = ns["load_fut"](); f15 = PB.rs(f, "15min"); fac = f.f.resample("15min", label="left", closed="left").last().reindex(f15.index).to_numpy()
FT = f15.index.to_numpy(); FO, FL, FC = (f15[k].to_numpy() for k in ("open", "low", "close"))


def ref_real(S):
    rows = []
    for k in S.itertuples():
        ie = np.searchsorted(FT, np.datetime64(k.t)); ix = np.searchsorted(FT, np.datetime64(k.tx))
        if ix >= len(FT) or ie >= ix: continue
        pe = FC[ie] + TICK; real = pe / fac[ie]; stop = pe * (1 - k.R)
        hit = np.flatnonzero(FL[ie + 1:ix + 1] <= stop); end, xp, why = ix, FC[ix] - TICK, "out"
        if len(hit): jj = ie + 1 + hit[0]; xp = min(stop, FO[jj]) - TICK; end = jj; why = "stop"
        rows.append((k.t, k.book, FT[ie] + np.timedelta64(15, "m"), FT[end] + np.timedelta64(15, "m"), pe, xp, why, (xp - pe) / pe * real * MULT - COMM))
    return pd.DataFrame(rows, columns=["t", "book", "entry_utc", "exit_utc", "entry", "exit", "why", "pnl"])


def loc2utc(x):
    return pd.DatetimeIndex(x).tz_localize("America/Chicago", ambiguous=True, nonexistent="shift_forward").tz_convert("UTC").tz_localize(None)


lines = []
def pr(*a):
    s = " ".join(str(x) for x in a); print(s); lines.append(s)


for mode in ("MC", "MCfix", "WARM"):
    P = pd.read_csv(OUT + f"paper_{mode}.csv", parse_dates=["t", "tx"]); Rl = pd.read_csv(OUT + f"real_{mode}.csv", parse_dates=["entry_time", "exit_time"])
    lo = P.t.min(); r = ref[ref.t >= pd.Timestamp("2019-07-01")]; p = P[P.t >= pd.Timestamp("2019-07-01")]
    m = r.merge(p, on=["t", "side", "book"], how="outer", suffixes=("_ref", "_rep"), indicator=True)
    both = m[m._merge == "both"]
    pr(f"\n=== {mode}: paper books (both sides), entries from 2019-07-01 ===")
    pr(f"ref {len(r)}, replica {len(p)}, matched entries (t, side, book) {len(both)} = {len(both) / len(r):.1%} of ref, {len(both) / len(p):.1%} of replica")
    pr(f"  of matched: same exit time {np.mean(both.tx_ref == both.tx_rep):.1%}, same exit reason {np.mean(both.why_ref == both.why_rep):.1%}")
    pr("  unmatched ref by year:", m[m._merge == "left_only"].t.dt.year.value_counts().sort_index().to_dict(),
       "unmatched replica by year:", m[m._merge == "right_only"].t.dt.year.value_counts().sort_index().to_dict())
    m.to_csv(OUT + f"paper_match_{mode}.csv", index=False)
    for y in range(2019, 2027):
        ry = r[r.t.dt.year == y]; by = both[both.t.dt.year == y]
        if len(ry): pr(f"  {y}: ref {len(ry):3d} matched {len(by):3d} ({len(by) / len(ry):.0%}) exit-same {np.mean(by.tx_ref == by.tx_rep) if len(by) else np.nan:.0%}")
    # ----- real side -----
    S0 = ref[(ref.t >= pd.Timestamp(FT[0])) & (ref.tx <= pd.Timestamp(FT[-1])) & (ref.side == 1)].reset_index(drop=True)
    RR = ref_real(S0)
    Rl["pnl"] = RP.usd(Rl)
    idt = P.set_index("id")[["t", "book"]]
    Rl = Rl.join(idt, on="id")
    Rl["entry_utc"] = loc2utc(Rl.entry_time) - pd.Timedelta(minutes=15)       # fill at the OPEN of the bar stamped entry_time
    Rl["exit_utc"] = loc2utc(Rl.exit_time) - pd.Timedelta(minutes=15)
    st = pd.Timestamp("2019-07-01"); RRp = RR[RR.t >= st]; Rlp = Rl[Rl.t >= st]
    mm = RRp.merge(Rlp, on=["t", "book"], how="outer", suffixes=("_ref", "_rep"), indicator=True); b2 = mm[mm._merge == "both"]
    pr(f"--- {mode}: real MBT longs from 2019-07-01: ref {len(RRp)} trades ${RRp.pnl.sum():,.0f}, replica {len(Rlp)} trades ${Rlp.pnl.sum():,.0f}")
    pr(f"  matched by paper entry (t, book) {len(b2)} = {len(b2) / len(RRp):.1%} of ref; entry fill same 15m moment {np.mean(b2.entry_utc_ref == b2.entry_utc_rep):.1%}; "
       f"exit within 15 min {np.mean((b2.exit_utc_rep - b2.exit_utc_ref).abs() <= pd.Timedelta(minutes=15)):.1%}; same exit kind {np.mean(b2.why_ref == b2.why_rep.replace('entrybar_guard', 'stop')):.1%}")
    pr(f"  P&L corr per matched trade {np.corrcoef(b2.pnl_ref, b2.pnl_rep)[0, 1]:.3f}; matched sum ref ${b2.pnl_ref.sum():,.0f} vs replica ${b2.pnl_rep.sum():,.0f}; "
       f"unmatched ref ${mm[mm._merge == 'left_only'].pnl_ref.sum():,.0f} ({(mm._merge == 'left_only').sum()}), unmatched replica ${mm[mm._merge == 'right_only'].pnl_rep.sum():,.0f} ({(mm._merge == 'right_only').sum()})")
    pr("  replica exit kinds:", Rlp.why.value_counts().to_dict(), "ref:", RRp.why.value_counts().to_dict())
    yrs = (pd.Timestamp(FT[-1]) - st).days / 365.25
    pr(f"  $/yr ref {RRp.pnl.sum() / yrs:,.0f} replica {Rlp.pnl.sum() / yrs:,.0f}; by year ref " + " ".join(f"{y}:{v:+,.0f}" for y, v in RRp.groupby(RRp.t.dt.year).pnl.sum().items())
       + " | replica " + " ".join(f"{y}:{v:+,.0f}" for y, v in Rlp.groupby(Rlp.t.dt.year).pnl.sum().items()))
    d = b2.assign(diff=b2.pnl_rep - b2.pnl_ref).sort_values("diff")
    pr("  largest per-trade differences (rep - ref):")
    for x in pd.concat([d.head(4), d.tail(3)]).itertuples():
        pr(f"    {x.t} b{x.book} ref {x.why_ref} {x.exit_utc_ref} ${x.pnl_ref:,.0f} | rep {x.why_rep} {x.exit_utc_rep} ${x.pnl_rep:,.0f}")
    mm.to_csv(OUT + f"real_match_{mode}.csv", index=False)
    if mode == "WARM":
        # fills.csv for the checker gates (replica real trades, local Central stamps)
        fl = Rl.assign(entry_time=Rl.entry_time - pd.Timedelta(minutes=15), exit_time=Rl.exit_time - pd.Timedelta(minutes=15), side=1)[["entry_time", "exit_time", "side", "entry", "exit"]]
        fl.to_csv(OUT + "fills.csv", index=False)
        Rl.assign(date=Rl.exit_time.dt.normalize().dt.date, net=Rl.pnl).to_csv(OUT + "trades_replica.csv", index=False)
open(OUT + "compare_output.txt", "w").write("\n".join(lines) + "\n")
