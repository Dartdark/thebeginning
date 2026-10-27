# ORB30 EMA research replay

Source: [ORB30_EMA_Research.txt](ORB30_EMA_Research.txt).
Report: [orb30_ema.md](../results/orb30_ema.md).

This is a requested reconstruction, not the author's EA. Static and Python checks passed; PowerLanguage compilation and native MultiCharts trade parity have not been performed.

## Research chart

- One-minute NQ or MNQ, full Globex session, Central/exchange clock; load December 2017 history before the 2018 performance start for EMA warm-up.
- Intrabar Order Generation enabled. Enable native tick Bar Magnifier where owned data exist; one-minute bars alone cannot validate tick order or broker quote fills.
- EMAMode=1 (full-session completed M30 EMA), EMALength=20, RR=1.85, FlatTime=1555.
- For one-MNQ trade-price reconciliation: MNQ chart, UsePercentRisk=false, FixedContracts=1.
- To examine the stated percentage-sizing rule separately: UsePercentRisk=true (default), RiskPct=1, InitialBalance=100000. This uses this strategy's own realized backtest balance and integer contracts; it is not a shared-account balance integration. MaxContracts=100 is a cap.
- MNQ cost convention in Python: $1.24 round-trip commission and one adverse tick per stop/market fill; $1.04 commission sensitivity retained. NQ: $7.25 round trip and one adverse tick per stop/market fill. Do not apply both Python cost deductions and another platform fee deduction to the same exported ledger.
- Python limits require one full NQ point through the target. Match the platform limit-fill assumption explicitly; native tick/queue outcomes can differ.
- EMAMode=2 is the separately tested cash-bar EMA proxy. It failed the frozen design gate; do not use later results to choose it.
- RR=4 and RR=0 are experiments, not demonstrated improvements. RR=0 means no target, while keeping the stop and timed flatten.

Calendar exclusions are generated for 2018–2027. Extend and review them before using later dates. The code uses a completed-minute time decision and emergency carried-position exit, not the original EA's timer guarantee. Gap fills reanchor protection on the first observed fill tick; verify native order behavior in research. Do not install on live charts or alter the VPS.

## Python reproduction

Use the configured scientific Python with existing dependencies and scratch_data/g24.pkl. No cache rebuild is required. From the repository root:

```text
python analysis/codex_orb30_ema.py --stage checks
python analysis/codex_orb30_review.py
python analysis/codex_orb30_ema.py --stage recheck
python analysis/codex_orb30_personal.py
python analysis/codex_orb30_report.py
```

These verify saved candidate ledgers and regenerate the fixed portfolio/report, rather than select new parameters. Diagnostics can be reproduced with `--stage diagnostics` (several minutes). The saved original design and validation remain in git; running `--stage design` followed by `--stage validation` replays the same frozen rules and overwrites this study's generated outputs. It does not create a fresh holdout. Keep any changed rules as separately registered trials.

Current cache coverage stops October 9, 2026. Native CFD/MT5 parity, 2016–17 performance, original walk-forward search, margin feasibility and four full Apex account placements are not established by these outputs.
