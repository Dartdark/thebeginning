# QuantJourney stop-limit — frozen execution-only diagnostic

Summary: Evidence gate is DON'T TEST economic returns; the source is an educational daily-ETF order example.
Execute only eight synthetic scenario groups against the archived strategy class and pinned public fill engine.
No historical/backtest profit, placebo, account or source0.10.0 parity claim follows from these mechanics.
No parameter search, futures adaptation, credential access or live change is authorized by this plan.

Evidence: [qj_stop_limit_20261030.md](../evidence/qj_stop_limit_20261030.md).
Code: [analysis/codex_qj_stop_limit.py](../../../analysis/codex_qj_stop_limit.py).
Archive: `agents/codex/inputs/qj_stop_limit_20261030/`.
Outputs: `analysis/outputs/codex_qj_stop_limit_20261030/`.

## Exact source and isolation

Canonical strategy class matches pasted logic, with Markdown escapes normalized via the upstream file.
Pin public engine commit4f403d853833e1daa6de01c5b6c6cb3983dc0044; archive Apache license and source hashes.
Extract only the class using AST; base class only supplies features/entry price. Import the four reviewed pure
execution modules under isolated package namespaces, never the API client/core package initialization.
No `_credentials()`, `main()`, environment secrets, QuantJourney API, trading connection or broker is invoked.
The archived simulator/core is read to establish scheduling but is not executed. Public engine0.12.5 is distinct
from the packet's0.10.0+private engine. Results apply only to this named source/harness combination.

## Predeclared scenarios

1. Market entry is unprotected during the daily fill bar; source submits its stop-limit after that bar closes.
2. A bearish SMA transition can be consumed by the higher-priority protective-order branch; maintaining the
   bearish signal on the next callback does not reproduce the lost crossing.
3. An active sell stop96/limit95.50, hypothetical entry100, remains unfilled through a gap and further prices below95.50.
4. A later recovery reaches the resting sell limit, with sell price constrained by95.50; commission reduces net proceeds.
5. A rejected stop order still sets the source protection flag; inspect whether a later callback retries.
6. Ordinary bearish exit cancels existing protection and queues a market sell of held quantity.
7. Partial stop-limit exit: cancel its remainder and sell actual remaining quantity on bearish exit; retain fee/quantity state.
8. After stopping out while still above the SMAs, no immediate reentry; a new bearish-then-bullish crossing is required.

Engine defaults remain GTC, market at next bar open,5bps adverse slippage, equity $0.005/share/minimum$1 fees.
Scenario7 alone enables1% prior-volume participation to expose a partial fill; this is a synthetic order test,
not a new strategy setting or claimed historical fill rate. Scenario data are explicitly invented and are not
dated market evidence. Assertions succeeding means expected behavior reproduced, not that the source is safe.

## Counts and stop rule

Zero economic strategy definitions/return trials, eight mechanics scenario groups. Existing shared trial/selection
history and scout lease/budget are unchanged. No profit tuning or new source hypothesis is hidden in a fixture.
If mechanics fail an assertion, inspect source/harness and preserve corrections; never use synthetic outcomes
as market profitability. Run with `/workspace/venvs/thebeginning/bin/python analysis/codex_qj_stop_limit.py`.
Commit exact source, hashes, evidence, plan and harness before executing these scenarios.

## Handoff

Save traces, source/version/access receipts and report; distinguish author outcomes from our synthetic checks.
Retain execution lesson in EXECUTION_REFERENCES (merge E03/E05/E18 where appropriate).
Four evaluation/funded homes are incompatible as written; personal contribution is unverified/not admitted.
No account comparison was earned. No API/data purchase, plan edit, strategy installation or allocation.
