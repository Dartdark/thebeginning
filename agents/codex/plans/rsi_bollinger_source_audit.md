# Uploaded RSI/Bollinger strategy: source and data-readiness audit

User says this is not the gold-breakout strategy from the video, but asks to check it too.
Treat the pasted `MeanReversionRSI` class as an independent personal-account candidate.
Work on `codex/work`, starting from `2a206bf`. The user subsequently answered **both** to gold and NQ with hourly
decisions and four-hour confirmation. Inspect GC/MGC and NQ/MNQ data readiness separately; do not pool markets.

## Scope before any historical return

Preserve the supplied source verbatim. Inspect source and current official Jesse behavior; use a pinned public
source reference where possible. Check risk sizing, stop/target initialization, missing attributes, pending-order
cancellation and absent external configuration. Report what the code actually does, not its comments.

A small reproducible script may execute the original methods with explicit synthetic indicator/position fixtures
and a source-matched sizing helper. This is a method/quantity audit, not a Jesse engine run, fill simulation, market
backtest or strategy-return trial. Include examples where the helper's notional cap binds as well as where it does
not; do not simply claim every trade risks 15%. Test how changing ATR between submission and fill changes risk.

For both markets' feasibility, inspect existing CSV headers/date/time fields only, and report coverage/hours.
Do not read prices/returns or build caches. Check existing catalogue and data loaders for possible reuse.
Only allowed write paths under agents/codex and analysis/codex_* / analysis/outputs/codex_*.

## Gates and stop rule

Write an evidence sheet with the seven questions and failure/diversification supplement. A price-based setup has
no demonstrated forced-flow mechanism; document that limitation. Source defects and
unverified data/execution parity prevent a TEST verdict. No parameter search, stop/target tuning, alternative
signals, historical return screen, funded bench, purchases, credentials, external messages or live changes.

No source correction is silently substituted for the supplied version. Any later original-versus-corrected return
comparison needs a separate frozen plan identifying every rule/sizing difference and counting both versions.
Archive a source-readiness report with Summary at most five lines; commit and push the completed audit.
Return trials in this scope: zero. Do not claim statistical performance or copy the other strategy's video results.
