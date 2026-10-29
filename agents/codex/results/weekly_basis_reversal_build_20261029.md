# Weekly basis reversal: signal prototype built; real backtest blocked

Summary: Implemented the weekly two-maturity reversal signal with information-clock and contract-identity checks.
Fourteen synthetic engineering checks pass; no historical profitability or portfolio test ran.
Full primary rules, identified paired histories and native execution/sizing facts remain missing.
The design draft is not a preregistration; evidence stays NEEDS DATA and no economic trial was spent.

User request: start creating the strategy now. [Signal code](../../../analysis/codex_weekly_basis_reversal.py),
[engineering checks](../../../analysis/codex_weekly_basis_reversal_test.py),
[implementation draft and required input handoff](../research/scout/drafts/weekly_basis_reversal_design.md).

## Implemented behavior

Reverse the prior week's front-minus-deferred relative return: front outperforming means short front/long deferred;
front underperforming means long front/short deferred; equal growth means flat. Exact rational comparisons avoid
binary-rounding direction errors. Both endpoints must identify the same contracts and measurement times.
Decision follows every settlement's available-at timestamp. Explicit expiry buffers and exit before first notice/
last trade are enforced; naive clocks, mismatched commodities/currencies, missing identities and undefined
percentage-return prices stop processing. Source and exchange-calendar selections are supplied, not guessed.

This is a research signal core, not a finished position-sizing, execution or P&L engine. Real histories were not
fed to it. Adding a price/market substitution to produce a backtest now would not implement the two-maturity rule.
Use existing repository metrics/account tools after admission rather than replacing them with a daily proxy bench.

## Verification actually executed

Configured Python ran `analysis/codex_weekly_basis_reversal_test.py -v`:14 unittest cases passed. Inputs are deliberately
synthetic `SYNTH-F/SYNTH-B` prices and clocks. Tests cover both directions/flat, late settlement receipt, same-settlement
entry rejection, changing maturity IDs, mismatched endpoints, delivery/expiry limits, invalid prices, incompatible
contracts and invalid clocks/settings. This establishes engineering behavior only. It does not demonstrate alpha,
cost savings, fills, historical Sharpe or account improvements.

## Source/data work and limits

Latest remote fetched before work:234996e. Checked the full workspace for basis manuscript/identified paired data;
only the existing source/evidence records were found under relevant names. Current runtime remains restricted/enforced.
No unchanged SSRN/Drive/CME denial was retried. New indexed searches covered the author PDF filename,
conference versions, paired-contract data and replication access. The AsianFA2026 program confirms the paper's
presentation but supplies no full text in the inspected entry. Public third-party futures-stitching test-data examples
are not an admitted modern commodity panel; generic continuous-price strategy repositories expressly lack contract
reconstruction. Neither supplies the required real-data test inputs. No account/subscription/purchase or external contact.

Author return claims remain unverified; [four source questions and prior access evidence](scout_spread_strategy_feasibility_20261029.md)
remain authoritative. No new full-paper review is claimed here. Existing source/data/schema receipts remain preserved.

## Account comparison status

| Home | Status |
|---|---|
| 50K/150K evaluation | Weekly overnight rule ineligible as-is; no simulation |
| 50K/150K funded | Weekly overnight rule ineligible as-is; no simulation |
| Personal | Potential research fit; missing source/pair/sizing/cost inputs prevents gross/design and portfolio tests |

BASE/ADD/REPLACE/EMPTY, all strategy metrics, gross-versus-cost, placebos, Monte Carlo and validation are **unrun**.
No budget reservation, return-work lease or admission PASS claimed. No allocation or live-system changes.

For Claude: this report/code/draft are an implementation checkpoint with synthetic checks, not economic verification.
