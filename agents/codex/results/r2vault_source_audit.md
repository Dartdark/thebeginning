# R2Vault PDF: independent rule and published-claim audit

Summary: The PDF specifies a testable long-only price rule, but leaves execution/session details to a declared proxy.
Annual and average-trade arithmetic reconcile; the displayed IS/OOS intervals leave a7-trade,−$3,530 remainder.
The$190,300.45 adjusted profit exactly matches a statistical count adjustment, so it cannot identify trading costs.
No new price-based strategy return was run for this audit; no original-code or author-ledger parity is certified.

Source: unchanged `agents/codex/inputs/r2vault/source.pdf`,10 pages. Visually inspected pages3-9 and extracted
both native2280x1440 platform images from page7. Script:`analysis/codex_r2vault_source_audit.py`;
machine-readable output:`analysis/outputs/codex_r2vault/source_claims_audit.json`.

## Independently extracted rules

- Instrument NQ futures,5-minute bars, long only; price input Close.
- Rolling regression uses576 closes. Recent observations receive largerX, so positive slope points toward rising prices.
- StandardR² is between0 and1. A vault is replaced wheneverR²<=.030 using the current candle's High and Low;
  this is a single-candle range, not a multi-candle opening range.
- Entry level is stored High +.20*(storedHigh−storedLow). Positive slope and the stated09:30-15:30 session
  permit a buy stop; maximum3 entries per day.
- Stated stop$1,500 and target$800 correspond to75 and40NQ points at oneNQ. Contract scaling must preserve
  that price geometry; the same numerical dollar input on oneMNQ would be a different strategy.
- Break-even is disabled. Its$400 trigger therefore has no effect. R²TakeProfitThreshold2.00 cannot trigger
  an exit when the stated standardR² remains in[0,1]. Monetary stop/target exits remain active.

The PDF does not specify timezone/DST, exact session template, regression history outside entry hours, day reset,
vault expiry/reset, whether vault replacement is restricted while positioned, stop-order lifetime, stop activation,
IOG, Bar Magnifier, rounding, collision ordering, forced EOD flattening or holiday times. A research implementation
must freeze those choices and label them as proxy assumptions; the PDF's directions do not themselves authorize
optimization or live use. No original strategy code or settings tab is visible in the supplied document.

The native screenshot title confirms@NQ5Minutes. Its equity starts near$100,000. A plotted08:55 axis label does
not establish timezone or the time of a trade. No hidden settings/calendar were found in the relevant images.
The document states two development versions and no dedicated OOS optimization; the full search registry is absent.

## Published arithmetic

| Check | Result |
|---|---:|
| Annual2017-2026 total | $265,780, exactly the full net |
| Annual2017-2024 total | $180,635, exactly the IS net |
| Annual2025+2026 total | $85,145 |
| IS$180,635 + OOS$88,675 | $269,310 |
| Full minus IS+OOS | −$3,530 |
| IS1947 + OOS564 trades | 2511; full has2518, remainder7 |
| Full exact average | $105.5520, correctly rounds to$105.55 |
| Full2518*$105.55 | $265,774.90; $5.10 difference is ordinary rounding |
| IS exact average | $92.7761, correctly rounds to$92.78 |
| OOS implied average | $157.2252 |

The full caption begins2017-01-13; IS begins2017-01-19. IS ends2024-12-31, while OOS begins2025-01-15.
The displayed periods therefore do not partition the full period. The early2025 gap could explain the−$3,530
remainder if the same strategy version/accounting is used; the7 residual trades cannot be assigned to specific
dates without a ledger. Different versions or other reporting choices cannot be ruled out from aggregates.

The native Monte Carlo image supplies1751 winning and767 losing trades, gross profit$1,417,805 and gross
loss$1,152,025. Their difference is exactly$265,780; PF1.2307068 rounds to1.23 and win69.5393% to69.54%.
Average winning trade$809.7116 and average losing trade−$1,501.9883 also match the printed screenshot.

The exact calculation

`265780 - 1417805/sqrt(1751) - 1152025/sqrt(767) = 190300.4454867`

rounds to the printed adjusted net$190,300.45. Thus subtracting that adjusted figure from net and dividing by
2518 gives$29.976 per trade, but this is not evidence of commission/slippage. Costs remain unspecified.

## Execution and risk implications

The native image reports largest win$4,950 despite an$800 target, and largest loss−$2,205 despite a$1,500 stop.
Favourable/adverse opening gaps or other unspecified implementation details may explain these observations;
they do not prove a particular rule. Do not silently assume guaranteed brackets or that the source is intraday-only.

The Monte Carlo image explicitly labels−$16,500 as maximum close-to-close drawdown, whereas the main page reports
−$17,420 maximum drawdown. Those can be different definitions. The10000 shuffled-trade paths preserve the sample
trades and show a worst−$63,225 drawdown; they are not an Apex account simulation or a future-risk guarantee.
Sharpe.44 and28.99% time in market have no supplied formulas/calendar definitions.

Original exports, exact code and actual execution settings remain needed for exact author parity. A frozen research
proxy can still answer the user's requested portfolio question without pretending those missing details are verified.
