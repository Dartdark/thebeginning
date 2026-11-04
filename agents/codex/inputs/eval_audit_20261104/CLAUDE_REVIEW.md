# Evaluation audit: independent review handoff

Research branch: `codex/work`. Original preregistration:
`a087708b13697df4c3dd0b0814f98cb53a2b254a`.
Read the final result report and progress record for executed stages and subsequent selection commits.
This request authorizes research review, not installation, account purchases or changes to allocations.

1. Reconcile the four reported failures against the pinned committed account journals/equity and distinguish
   broker fills from chart-only strategy logs. In particular, test whether November4 ONB planned stop risk
   exceeded the remaining floor cushion, and whether post-failure VB chart trades entered any prior statistics.
2. Check the current product's EOD evaluation floor, inclusive intraday failure, DLL liquidation and pause,
   realized target after costs, expiration and native net contract limits against primary receipts. Evaluate
   the earlier PA floor lock and daily-P&L proxy assumptions separately from this account event model.
3. Reproduce the frozen code/input hashes and actual integer sizing. Inspect source stop formulas,
   compressed-chart/date banks, complete lookbacks, dated closures, limit-through proof and shared asset prices.
   Missing information must remain UNKNOWN. Inspect the current guard=False and prospective guard=True distinction.
4. Check that every 2018–22 design start expires before2023, every compared policy uses the same calendar,
   every definition/alias is preserved and the initial/derived/final selection commits precede their dependent
   outcomes. Previously seen2023+ is historical validation, with its original selection history retained.
5. Recompute a bounded sample of account paths from raw events, including costs at DLL/floor/target/cutoff,
   opposing virtual sleeves, skipped entries, native caps and account death. Compare accelerated and raw walks
   of the same frozen cases; source-native matching and exact tick chronology remain separate work.
6. Verify unconditional pass/fail/expire/unknown counts, identification bounds, paired90% dependent-block
   intervals, all cost/cushion scenarios, and the frozen efficiency/safety recommendation gates. Check whether
   a lower failure rate simply becomes more expirations or higher fees per successful evaluation.
7. State exactly which engineering, source, economic and account claims are supported. A broad finite search,
   a synthetic fixture PASS or a conditional OHLC frontier does not establish global optimality, native execution,
   independent future performance or permission to deploy.

Review artifacts are under `agents/codex/inputs/eval_audit_20261104/`; code is
`analysis/codex_eval_*_20261104.py`. The final ZIP manifest identifies retained case outcomes, ledgers,
quality flags and receipts. Use the report's exact commands/commits rather than rerunning a changed definition.
