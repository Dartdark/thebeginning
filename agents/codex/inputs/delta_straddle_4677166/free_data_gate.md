# Free-data and specification gate — SSRN4677166

Checked November8,2026(America/Los_Angeles). **No matching raw return panel acquired/admitted. No strategy-return test.** Free sources only.

## Source requirements

Appendixp36 specifies41 instruments:10 equity futures,7 FX total-return indices,10 commodity futures and14 rate futures. Need exact historical return construction, currencies/hedging, prices/settlements, rolls, collateral interest/carry, original contract identifiers, calendars and executable fill clocks. Source1985–2017 replication and modern2018–22 design are different tasks.504-session warm-up must precede first decision;2023+ requires earned validation. Archived `source_audit.json` transcribes the tickers/weights.

FX Bloomberg `*USDCR` total-return indices cannot silently become spot changes or continuous6E. `YM1` in this source is Australian3Y bonds, not owned Dow futures. ED4 is not an automatic SOFR continuation. Bloomberg futures labels alone do not specify a self-financing native roll ledger.

## Actual checks

- Owned filename inventory retained by `analysis/codex_delta_straddle_4677166_audit.py`: native/continuous minute exports and several daily index/proxy files, not an admitted complete41-market return/carry universe. No raw returns calculated to select a subset.
- Connected public search queried exact author/title with code/replication/data/GitHub terms and exact `EURUSDCR` historical/download terms. Returned primary SSRN metadata, secondary discussion/adaptations and publications that mention the index; no authenticated author replication code or source-equivalent free full-history panel acquired.
- An unaffiliated GitHub result(`Nanshan1002/quant-strategies`) describes a crypto strategy adaptation, not original replication data. It was not executed or treated as author code. Public academic results naming Bloomberg series do not supply the actual input histories. Secondary commercial summaries are discovery only, not authorized purchases or substitute rules.
- The upload supplies a monthly strategy-return table, not constituent prices, daily positions/fills or cash/roll data. No vendor login, account, paid subscription, external contact or secrets used.

These bounded checks do not prove free data are unavailable everywhere. Do not repeat unchanged queries or substitute a convenient NQ/ES-only universe to claim reproduction.

## Specification gaps before TEST

Return type/log versus arithmetic and straddle drift convention; exact volatility estimator for the signal versus EWMA0.94 position sizing; signal/decision/executable fill lag; expand-window portfolio-vol initialization and leverage limits; liquidity-weight vintages and weights at contract inception; the0.25/vol no-trade band's comparison to last held position and interaction with vol/risk-target changes; missing/zero/negative price rules; collateral/carry/roll and native costs/quantity accounting. Native micro lots and contract launch dates matter for any personal implementation.

The source's printed AR(1) t-stat correction appears reversed under its marginal-volatility convention; a literal port needs reconciliation. Table19's−156.18%max drawdown also requires an explicit NAV/drawdown convention before capital interpretation. No source code supplied establishes which convention the historical simulations used.

## Resume only with genuinely new inputs

Authenticate one complete formation/rebalance/roll interval across the stated universe, with available-at inputs and a self-financing native cash ledger. Then conduct a no-return coverage/warm-up/margin/cost audit and resolve the source choices. Only a passing evidence gate and separately committed bounded protocol can precede returns. Preserve failed generic daily-NQ/ES and fast-trend history. No current account placement or intraday adaptation earned.
