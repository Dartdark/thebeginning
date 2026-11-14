"""Runs analysis/checker.py with leak_checks patched for BTC spot (TICK 0.01, PV 1 = $ per 1 BTC, cost 0 in the L2 test).
python3 checks/candidates/tst_v1_longs/run_gates.py <candidate dir>   (from repo root)"""
import sys; sys.path.insert(0, "analysis")
import leak_checks as LC
LC.TICK["BTCUSD_spot"] = 0.01; LC.PV["BTCUSD_spot"] = 1
import checker
rep, ok = checker.check(sys.argv[1]); print(rep)
