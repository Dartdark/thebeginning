"""VIX term-structure sleeve (Predicting Alpha 'North Star' VIX rules, as restated in the user's PDF 'VIX_Strategy_Replication_1',
2026-10-25; checks/candidates/vix_sleeve/). Independent re-run of the PDF's ETF version on free daily data:
  data/VIX_daily.csv (Cboe), data/VIX3M_daily.csv (Cboe), data/SPX_daily.csv and data/VIXY_daily.csv (Yahoo, split-adjusted).
  RV20 = 100 x stdev(ln SPX returns, 20 sessions) x sqrt(252); VRP = VIX - RV20; contango = VIX < VIX3M.
  Table: VRP > 0 & contango -> short full; VRP <= 0 & contango -> short half; VRP <= 0 & inverted -> long full;
  VRP > 0 & inverted -> cash. Size = min(VIX / 100, 0.40) of NAV (half on the half row). Trade on the week's last session
  or when the regime changes; the 40% cap is enforced daily. Borrow 3.5% a year on short notional; commission ~1 bp of
  traded notional (the PDF's $0.005 a share); no cash interest.
Variants: (A) the PDF's base case, today's closes and a fill at today's VIXY close (VIX closes at 16:15, VIXY at 16:00: a
mild look-ahead); (B) the PDF's causal bound, yesterday's closes and a fill at today's close; (C) new here: today's closes,
fill at the NEXT morning's VIXY open (what a trader without a 15:30 snapshot can do); (D) short-only versions.
  python3 analysis/vix_sleeve_test.py > analysis/outputs/vix_sleeve_test_output.txt
"""
import numpy as np, pandas as pd

rd = lambda f, c: pd.read_csv(f, parse_dates=[c]).set_index(c)
vix = rd("data/VIX_daily.csv", "DATE").CLOSE; v3 = rd("data/VIX3M_daily.csv", "DATE").CLOSE
spx = rd("data/SPX_daily.csv", "date").close; vx = rd("data/VIXY_daily.csv", "date")
df = pd.concat(dict(vix=vix, v3=v3, spx=spx, o=vx.open, c=vx.close), axis=1).dropna()
df = df[df.index >= "2010-11-01"]
rv = np.log(df.spx).diff().rolling(20).std() * np.sqrt(252) * 100
df["vrp"] = df.vix - rv; df["cont"] = df.vix < df.v3
reg = np.select([(df.vrp > 0) & df.cont, (df.vrp <= 0) & df.cont, (df.vrp <= 0) & ~df.cont], [-1.0, -0.5, 1.0], 0.0)
df["reg"] = np.where(rv.notna(), reg, np.nan)
base = np.minimum(df.vix / 100, 0.40)
df["w_t"] = df.reg.abs().where(df.reg.abs() != 0.5, 0.5) * 0 + np.sign(df.reg) * np.where(df.reg.abs() == 0.5, 0.5, 1.0) * base
wk = df.index.to_series().dt.isocalendar().week.astype(int).values
last_of_week = np.r_[wk[1:] != wk[:-1], True]
df["trade_day"] = last_of_week | (df.reg != df.reg.shift(1))


def run(mode="A", short_only=False, borrow=0.035, comm=0.0001, start="2011-01-04", cap=0.40):
    d = df[df.index >= pd.Timestamp(start) - pd.Timedelta(days=40)].copy()
    tw = d.w_t.copy()
    if short_only: tw = tw.clip(upper=0)
    if mode == "B": tw, td = tw.shift(1), d.trade_day.shift(1).fillna(False)
    else: td = d.trade_day
    nav, w = 1.0, 0.0; out = []
    o, c = d.o.to_numpy(), d.c.to_numpy(); tw_, td_ = tw.to_numpy(), td.to_numpy()
    pend = None
    for i in range(1, len(d)):
        if d.index[i] < pd.Timestamp(start): continue
        # close(i-1) -> open(i) -> close(i)
        r_on = o[i] / c[i - 1] - 1; r_day = c[i] / o[i] - 1
        nav *= 1 + w * r_on; w = w * (1 + r_on) / (1 + w * r_on) if (1 + w * r_on) else 0
        if mode == "C" and pend is not None:                       # yesterday's decision, filled at today's open
            nav -= abs(pend - w) * comm * nav; w = pend; pend = None
        nav *= 1 + w * r_day; w = w * (1 + r_day) / (1 + w * r_day) if (1 + w * r_day) else 0
        if w < 0: nav -= borrow / 252 * abs(w) * nav
        tgt = tw_[i]
        if np.isfinite(tgt):
            if mode == "C":
                if td_[i]: pend = tgt
                elif abs(w) > cap: pend = np.sign(w) * cap
            else:
                if td_[i]: nav -= abs(tgt - w) * comm * nav; w = tgt
                if abs(w) > cap: nav -= (abs(w) - cap) * comm * nav; w = np.sign(w) * cap
        out.append((d.index[i], nav, w))
    R = pd.DataFrame(out, columns=["date", "nav", "w"]).set_index("date")
    r = R.nav.pct_change().fillna(0); yrs = len(r) / 252
    dd = (R.nav / R.nav.cummax() - 1).min()
    return dict(cagr=R.nav.iloc[-1] ** (1 / yrs) - 1, vol=r.std() * np.sqrt(252), sharpe=r.mean() / r.std() * np.sqrt(252), mdd=dd,
                calmar=(R.nav.iloc[-1] ** (1 / yrs) - 1) / -dd), R, r


def show(nm, x):
    s = x[0]; return f"   {nm:<58} CAGR {s['cagr']:6.1%}  vol {s['vol']:5.1%}  Sharpe {s['sharpe']:4.2f}  maxDD {s['mdd']:6.1%}  Calmar {s['calmar']:4.2f}"


if __name__ == "__main__":
    print(__doc__.split("\n")[0])
    mix = df.reg[df.index >= "2011-01-04"].value_counts(normalize=True).round(3).to_dict()
    print(f"\n1. Regime mix 2011-2026 (PDF: short full 76.8%, half 12.4%, long 3.3%, cash 7.6%): "
          f"short full {mix.get(-1.0, 0):.1%}, half {mix.get(-0.5, 0):.1%}, long {mix.get(1.0, 0):.1%}, cash {mix.get(0.0, 0):.1%}")
    print("\n2. VIXY sleeve, 2011-01-04 .. 2026-10-23 (PDF base: CAGR 10.6%, vol 12.9%, Sharpe 0.85, maxDD -20.8%; causal bound 5.7%, -30.2%):")
    A = run("A"); B = run("B"); C = run("C")
    print(show("(A) PDF base: today's closes, fill today's close", A))
    print(show("(B) PDF causal: yesterday's closes, fill today's close", B))
    print(show("(C) today's closes, fill tomorrow's open (tradable)", C))
    print(show("(A) short-only", run("A", short_only=True)))
    print(show("(B) short-only", run("B", short_only=True)))
    print(show("(C) short-only", run("C", short_only=True)))
    print(show("(C) zero borrow", run("C", borrow=0)))
    print(show("(C) borrow 10% a year", run("C", borrow=0.10)))
    print(show("(C) from 2018", run("C", start="2018-01-02")))
    print(show("(C) from 2022", run("C", start="2022-01-03")))
    print("\n   by year, (A) / (B) / (C):")
    yA, yB, yC = ((1 + x[2]).groupby(x[2].index.year).prod() - 1 for x in (A, B, C))
    print("   " + "  ".join(f"{y}: {yA[y]:+.0%}/{yB[y]:+.0%}/{yC[y]:+.0%}" for y in yA.index))
    # correlation with the personal book (daily $; sleeve at $30k NAV)
    import io, contextlib, runpy, sys
    sys.path.insert(0, "analysis")
    with contextlib.redirect_stdout(io.StringIO()):
        gg = runpy.run_path("analysis/personal_portfolio.py", run_name="__main__")
    P = gg["P"]; s = C[2].reindex(P.index).fillna(0) * 30000; tot = P.sum(axis=1)
    print(f"\n3. Sleeve (C) at $30k NAV vs our 17-piece personal book (2018+): daily corr {np.corrcoef(s, tot)[0, 1]:+.2f}; "
          f"sleeve ${s.sum() / (len(s) / 252):,.0f} a year, book ${tot.sum() / (len(tot) / 252):,.0f}")
    for nm, x in (("book alone", tot), ("book + sleeve (C) at $30k", tot + s)):
        e = x.cumsum(); print(f"   {nm:<28} Sharpe {x.mean() / x.std() * np.sqrt(252):.2f}  max DD ${-(e - e.cummax()).min():,.0f}  "
                              f"worst day ${x.min():,.0f}  ${x.sum() / (len(x) / 252):,.0f} a year")
