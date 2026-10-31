"""Turn a MultiCharts 'List of Trades' sheet into a checker trades.csv (net = MC profit - $17.25 a round trip).
  python3 checks/candidates/fc_2b/mc_to_trades.py REPORT.xlsx OUT.csv"""
import sys, pandas as pd
d = pd.read_excel(sys.argv[1], sheet_name="List of Trades", header=2)
e = d[d["Type"].astype(str).str.startswith("Entry")].reset_index(drop=True)
x = d[d["Type"].astype(str).str.startswith("Exit")].reset_index(drop=True)
assert len(e) == len(x)
t = pd.DataFrame({"date": pd.to_datetime(e["Date"]).dt.normalize(), "side": e["Type"].map({"EntryLong": 1, "EntryShort": -1}),
                  "entry": e["Price"].astype(float), "exit": x["Price"].astype(float), "kind": x["Signal"],
                  "t_in": pd.to_datetime(e["Date"]).dt.strftime("%H%M").astype(int), "t_out": pd.to_datetime(x["Date"]).dt.strftime("%H%M").astype(int),
                  "exit_date": pd.to_datetime(x["Date"]).dt.normalize(), "gross": e["Profit ($)"].astype(float)})
t["net"] = t.gross - (7.25 + 2 * 0.25 * 20)
t.to_csv(sys.argv[2], index=False); print(len(t), "trades,", t.date.min().date(), "-", t.date.max().date(), "net", round(t.net.sum()))
