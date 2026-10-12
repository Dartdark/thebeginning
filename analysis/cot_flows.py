"""CFTC Commitments of Traders, Traders in Financial Futures (futures only), 2017-2026,
from data/cot/fut_fin_txt_YYYY.zip (cftc.gov historical compressed files).

load_cot(code) -> weekly positioning for one contract (NQ E-mini 209742, ES E-mini 13874A),
indexed by the Tuesday "as of" date. Net positions are scaled by open interest.
features_for(g, code) -> per trading row, the latest report usable that day: released Friday
15:30 ET, so applied from the following Monday (as-of date + 6 days), never earlier.
Ranks are against the previous 156 weeks (3 years) only.
"""
import glob, zipfile
import numpy as np
import pandas as pd

NQ, ES = "209742", "13874A"


def load_cot(code=NQ, pattern="data/cot/fut_fin_txt_*.zip"):
    dfs = []
    for f in sorted(glob.glob(pattern)):
        z = zipfile.ZipFile(f)
        for n in z.namelist():
            dfs.append(pd.read_csv(z.open(n), low_memory=False, dtype={"CFTC_Contract_Market_Code": str}))
    d = pd.concat(dfs)
    d = d[d.CFTC_Contract_Market_Code.str.strip() == code].copy()
    d["date"] = pd.to_datetime(d["Report_Date_as_YYYY-MM-DD"])
    d = d.drop_duplicates("date").set_index("date").sort_index()
    oi = d.Open_Interest_All.astype(float)
    out = pd.DataFrame(index=d.index)
    out["oi"] = oi
    for k, a, b in (("lev", "Lev_Money_Positions_Long_All", "Lev_Money_Positions_Short_All"),
                    ("am", "Asset_Mgr_Positions_Long_All", "Asset_Mgr_Positions_Short_All"),
                    ("dealer", "Dealer_Positions_Long_All", "Dealer_Positions_Short_All"),
                    ("nonrep", "NonRept_Positions_Long_All", "NonRept_Positions_Short_All")):
        out[k] = (d[a].astype(float) - d[b].astype(float)) / oi
        out[k + "_chg"] = out[k].diff()
        r = out[k].rolling(156, min_periods=52)
        out[k + "_rank"] = out[k].rolling(157, min_periods=53).apply(lambda x: (x[:-1] < x[-1]).mean(), raw=True)
        out[k + "_z"] = (out[k] - r.mean().shift(1)) / r.std().shift(1)
    out["oi_chg"] = np.log(oi).diff()
    return out


def features_for(g, code=NQ):
    c = load_cot(code)
    usable = c.copy(); usable.index = usable.index + pd.Timedelta(days=6)
    dates = pd.DatetimeIndex(g.ts[g.trading])
    f = usable.reindex(usable.index.union(dates)).ffill().reindex(dates)
    f.index = g.trading
    return f
