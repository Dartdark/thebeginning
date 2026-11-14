"""Build scratch_data/personal_P.pkl locally (the cloud copy is not on this PC): the personal plan's daily P&L per piece, per micro,
as of 2026-11-14 = analysis/btc_adx_personal_bench.py's 17 pieces (OT x2, CL OVX sizing) + BTC ADX longs (1 MBT a book) +
TrendSwingTrader V1 longs (1 MBT) + ES dip-buy (1 MES, session-dated VIX/VIX3M skip). Used by analysis/new_data_screen.py.
  python3 analysis/build_personal_P_local.py session
"""
import sys; sys.path.insert(0, "analysis"); sys.argv = ["x", "session"]
src = open("analysis/spy_dip_personal_bench.py", encoding="utf-8").read().split("V = {")[0]
g = {"__name__": "x", "__doc__": "x\n"}; exec(compile(src, "bench", "exec"), g)
P = g["P"].copy(); P["BTCADX_MBT"] = g["btc"]; P["TSTV1L_MBT"] = g["tst"]; P["ESDip_MES"] = g["ESf"]
P.to_pickle("scratch_data/personal_P.pkl"); print("saved", P.shape, list(P.columns))
