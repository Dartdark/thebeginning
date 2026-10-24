"""Spot BTC-USD 1-minute bars from Coinbase's public API (2026-10-24; MultiCharts has no spot BTC feed here, and the BTC
Reopen MR V4 port needs spot as Data2). Writes data/BTCUSD_spot_1min_YYYY.csv in the repo's format: date, time (Central
time, DST-aware, bar stamped at its CLOSE like MultiCharts), open, high, low, close, volume (BTC). Coinbase returns
candles stamped at their open in UTC, at most 300 per request; minutes without trades are missing (no filling).
Resumable: an existing year file is extended from its last bar.
  python3 tools/exporters/coinbase_btc_1m.py [START YYYY-MM-DD] [END YYYY-MM-DD]
"""
import sys, os, time, json, urllib.request, urllib.error
import pandas as pd

URL = "https://api.exchange.coinbase.com/products/BTC-USD/candles?granularity=60&start={}&end={}"
START = pd.Timestamp(sys.argv[1] if len(sys.argv) > 1 else "2018-06-01", tz="UTC")
END = pd.Timestamp(sys.argv[2] if len(sys.argv) > 2 else pd.Timestamp.utcnow().strftime("%Y-%m-%d"), tz="UTC")
OUT = "data/BTCUSD_spot_1min_{}.csv"


def fetch(a, b):
    for k in range(8):
        try:
            req = urllib.request.Request(URL.format(a.strftime("%Y-%m-%dT%H:%M:%SZ"), b.strftime("%Y-%m-%dT%H:%M:%SZ")),
                                         headers={"User-Agent": "thebeginning-research"})
            with urllib.request.urlopen(req, timeout=30) as r:
                return json.loads(r.read())
        except (urllib.error.URLError, TimeoutError, ConnectionError, json.JSONDecodeError):
            time.sleep(2 ** k * 0.5)
    raise RuntimeError(f"failed {a} {b}")


def to_rows(c):
    d = pd.DataFrame(c, columns=["t", "low", "high", "open", "close", "volume"]).drop_duplicates("t").sort_values("t")
    ct = (pd.to_datetime(d.t, unit="s", utc=True) + pd.Timedelta(minutes=1)).dt.tz_convert("America/Chicago")
    return pd.DataFrame(dict(date=ct.dt.strftime("%Y%m%d").astype(int), time=(ct.dt.hour * 100 + ct.dt.minute).astype(int),
                             open=d.open.values, high=d.high.values, low=d.low.values, close=d.close.values,
                             volume=d.volume.round(6).values, _utc=d.t.values))


if __name__ == "__main__":
    t = START; buf = []; n = 0
    last_saved = {}
    for f in sorted(os.listdir("data")):
        if f.startswith("BTCUSD_spot_1min_") and START.year <= int(f[17:21]) <= END.year:   # own years only (parallel runs)
            x = pd.read_csv("data/" + f)
            if len(x):
                ts = pd.Timestamp(str(x.date.iloc[-1]) + f"{x.time.iloc[-1]:04d}", tz="America/Chicago").tz_convert("UTC")
                t = max(t, ts)                                         # resume after the last saved bar's close
    print(f"from {t} to {END}", flush=True)
    while t < END:
        b = min(t + pd.Timedelta(minutes=300), END)
        c = fetch(t, b - pd.Timedelta(seconds=1))
        if c: buf.append(to_rows(c))
        t = b; n += 1
        time.sleep(0.15)
        if n % 500 == 0 or t >= END:
            if buf:
                d = pd.concat(buf); buf = []
                d["yr"] = d.date // 10000
                for yr, g in d.groupby("yr"):
                    p = OUT.format(yr); g = g.drop(columns=["yr", "_utc"])
                    if os.path.exists(p):
                        g = pd.concat([pd.read_csv(p), g]).drop_duplicates(["date", "time"], keep="last")
                    g.sort_values(["date", "time"]).to_csv(p, index=False)
            print(f"  {n} requests, at {t}", flush=True)
