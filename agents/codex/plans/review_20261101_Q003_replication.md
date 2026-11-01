# Fixed implementation review: replicate the existing Q003 rejection, no new search

Task: `agents/codex/inputs/review_20261101/dff44f1/agents/codex/TASK_review_2026-11-01.md`.
Claude source pinned to dff44f136141aaf78c99c7042a8aca570bbff29a; Codex parent765e8db.
This protocol and exact script are committed on codex/work BEFORE the design-return replication.

This is a settling implementation/accounting check of an already examined F result, not a new strategy hypothesis,
variant search or holdout opening. Preserve Q003's three existing definitions, failed verdict and earlier multiplicity.
No scout lease/budget is used: the scout remains paused at its existing checkpoint; this is the explicit review task.

Evidence/source: original Q003 PREREG and exact Python source are snapshotted with GitHub blob identities. London's
16:00 fix maps through date-specific Europe/London -> America/Chicago conversion. Use only owned6E2018–2022 CSV files,
read by the unchanged frozen Grid24 parser. No2023+ data files, no pickle cache and no execution/account outcomes are read.
Rules unchanged: V1 month-end pre-fix follow, V2 month-end post-fix fade, V3 every-day pre-fix follow. Exact source entry/exit
bar indices and sign rules are retained, including its two-minute post-fix entry convention. No inferred prices or rescue.
Costs per6E: commission$5 plus two adverse$6.25 ticks=$17.50 per round trip. Source prices stay raw; the bridge subtracts
cost once. No actual-fill claim. Original event eligibility is last available session of each month, not a new calendar.

Run: `/workspace/venvs/thebeginning/bin/python analysis/codex_review_20261101.py --q003`.
Exact script's default mode executes only disconnected synthetic/source checks; no live helpers, alerts or PowerShell run.
In replication mode, reconstruct every eligible raw entry/exit/side independently beside the frozen source function;
assert trade/date/net parity and trade-to-daily accounting. Record all three variants' counts, averages, gross/net bridge,
t-stat, PF, yearly totals and standard metrics; repeat the original best-variant500-draw seed7 design placebo.
Stage1 remains t>=2, PF>=1.15, minimum40 event trades/80 every-day trades. Source chooses highest design t only.

Decision: if the existing rejection reproduces, close this settling check and stop. If different, record source/input
coverage differences and stop. Do not choose a new definition, alter gates, open2023+, run accounts or infer promotion.
Output: `analysis/outputs/codex_review_20261101/Q003_replication.json`, full design trades CSV and execution log.
Archive exact raw/source/script hashes, Python/package versions and this committed parent. This check cannot establish
that every currency-fixing strategy fails or that historical price-return results equal broker execution.
