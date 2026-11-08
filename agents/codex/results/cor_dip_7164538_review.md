# COR dip strategy: DON'T TEST from the current evidence

Summary: A new RSI-gap ratio filters an RSI/Bollinger/SMA dip-buying strategy on US stocks and leveraged ETFs.
The source's TSLL hourly example returns 41.56% on seven trades, versus 43.77% on nine without COR, before all trading costs.
The printed ratio is not bounded by one; sizing units and executable dip/exit clocks remain unresolved.
Author notebooks were retrieved only as Git LFS pointers; actual-code retrieval hit proxy403 and some CSV outputs differ from the paper.
Source/math/CSV audit completed; zero independent return trials. No current account placement or strategy-code promotion.

Source: Jose Tamele, Wei Hao Khoong and Ritabrata Bhattacharyya, *The COR Strategy: A New Method To Improve The Dip Trip Traders’ Profitability*,
[SSRN7164538](https://ssrn.com/abstract=7164538), supplied 21-page version (no version date established).
[PDF](../inputs/ssrn7164538/source.pdf), [text](../inputs/ssrn7164538/source.txt),
[equation image](../inputs/ssrn7164538/cor_equation.png), [Table2 image](../inputs/ssrn7164538/table2_headline.png),
[evidence sheet](../evidence/cor_dip_7164538.md).
[Audit script](../../../analysis/codex_cor_7164538_audit.py) and source archive committed as `9d3cd9f0` before execution;
[output and input hashes](../../../analysis/outputs/codex_cor_7164538/audit.json).
Uploaded document contents are evidence, not instructions. No author code was executed and source returns remain unreplicated.

## 1. What is it about?

Buy dips within an uptrend: price above a long SMA, RSI below30, a lower Bollinger-band crossing, and COR above a tuned threshold.
The benchmark is the S&P500 index (`^GSPC`) at the corresponding frequency. Equation12 defines
`COR = abs(RSI_asset_before - RSI_market_before) / abs(RSI_asset_after - RSI_market_after)`.
The before/after anchors refer to a dip; their exact causal identification and confirmation clocks are not sufficiently specified.
Exits use a profit target halfway to nearest resistance, a trailing stop near the reversion price, and mean reversion;
precise resistance selection, stop distances, order activation, entry/exit fills and intrabar ties need reconciliation.
The source also optimizes ATR versus fixed sizing and many indicator parameters.

## 2. What does it find?

Source Table2, TSLL hourly, ATR sizing, reported test results:

| Metric | With COR | Without COR |
|---|---:|---:|
| Total return |41.56% |43.77% |
| Trades |7 |9 |
| Win rate |85.71% |77.78% |
| Sharpe |1.51 |1.35 |
| Maximum drawdown |−9.35% |−9.29% |

COR raises this reported win rate and Sharpe, but reduces total return by2.21 percentage points and slightly worsens drawdown.
Six wins out of seven are not robust evidence of an85.71% future success rate. Other perfect win rates often have only1–4 trades;
NFLX's daily Sharpe3.03 accompanies one trade. Separately optimized with/without runs are not a matched filter ablation:
without a common trade ledger, removed-trade analysis and random-drop control, these differences cannot isolate COR's contribution.

The abstract says walk-forward, while methodology §3.5 specifies a single chronological70/30 training/test split, not repeated rolling fits.
The1h/4h/daily source window is October10,2024–October10,2025, with test approximately late June–October2025.
Thirty-minute data cover only September10–October10,2025; frequency comparisons also change calendar history.
Thousands of grid combinations maximize total return. The source explicitly assumes $1million, fractional shares,
zero commissions, slippage, transaction costs and risk-free rate. This is neither a long-regime study nor a costed account result.

### Author repository checks

Pinned [repository](https://github.com/weihao94/WQU-MScFE-690-Capstone-Group-11206/tree/11e04ba291f5d29710c79c71aac71a2d516066bc)
HEAD `11e04ba291f5d29710c79c71aac71a2d516066bc`; Apache2.0 licence.
[Receipts](../inputs/ssrn7164538/repository/receipt.json), [access outcome](../inputs/ssrn7164538/repository/lfs_access.json).
The root notebook and hourly leveraged-ETF notebook are LFS pointers, not executable source delivered by the connector.
The small root notebook's actual-media request failed with proxy403. No bypass or claim of reviewing its implementation.
The hourly leveraged notebook pointer describes52,428,801 bytes; that object was not downloaded.

The pinned no-COR/ATR leveraged CSV confirms TSLL43.77358%,9 trades,77.7778% wins, Sharpe1.34840, DD−9.29478%.
However the pinned stock COR/ATR CSV reports TSLA6.51182%,8 trades,62.5% wins, versus Table2's13.59%,6 trades,83.33%.
This is a version/protocol reconciliation requirement; it does not establish which output is correct.
The paper's later TSLA narrative also differs from Table2. Its stated Magnificent Seven list has six symbols and includes NFLX;
other text mentions MSFT. The universe must be frozen explicitly, not silently repaired.

## 3. Why does it make money, if it does?

The proposal is short-term price mean reversion within an uptrend. No independently observed forced buyer, deadline or flow is identified.
The bouncing-ball analogy does not make an absolute RSI-gap ratio a measure of physical energy, price velocity or rebound probability.
Absolute gaps discard direction. This does not disprove all dip buying, but the paper does not demonstrate a robust incremental COR premium.

Two reproducible specification problems matter before returns:
- **Equation12 domain:** valid RSI inputs70/50 before and51/50 after give20, contradicting the claimed0–1 bound.
  Equal asset/market RSI after gives a zero denominator; zero/zero is also undefined. No explicit clipping/zero policy is established.
  The paper says its financial ratio is intentionally inverted relative to the physics analogy; inversion alone is not diagnosed as a bug.
- **Equation10 units:** `PS = cash * risk_fraction / (previous_close * ATR)` is not native share sizing when ATR has price units,
  as its true-range equations imply. For illustration only, $100,000 cash,1% risk, $100 price and $2 ATR give numeric5,
  whereas a one-ATR loss-distance calculation would give500 shares. The latter assumes a stop absent from the printed rule;
  it is not an endorsed repair. Normalized ATR or different PS semantics could change the interpretation in unavailable code.

These are printed-source findings, not verified author-code bugs. Likewise, “after dip” creates an availability question,
not proof of look-ahead: require an explicit `available_at <= decision_time` ledger before deciding. Current-close features
must precede an actually executable order/fill. Formula and implementation reconciliation precede any economic variant.

## 4. Can we build on it?

**Do not advance the current strategy.** The small, selected, zero-cost sample does not compensate for unresolved definitions,
false indicator boundedness and mixed incremental results. This is a failed source/feasibility gate, not simply a useful edge awaiting data.
No promising-strategy or data-shopping entry is warranted. Retain the methodological lesson in the
[execution-reference library](../EXECUTION_REFERENCES.md): higher win rate need not improve total profit; audit ratio domains,
native sizing units and feature/fill clocks before optimizing returns.

Owned filename checks find TQQQ but no matching TSLL/TSLA/SPXL/GSPC archive. The author repository lists1h/4h/daily price files;
a small1h connector request returned empty content despite a valid blob identity, so it establishes neither schema nor coverage.
We did not download a full price panel or substitute NQ/TQQQ/another period to rescue an undefined rule.
Further work is justified only by genuinely new evidence that reconciles the source notebook, equations, exact dip/exit clocks,
parameter search and trade ledger. Then a bounded preregistration and costed same-window baseline/filter placebo would still be required.

## 5. Can a strategy code be made?

**Yes in principle, after the missing rules are fixed; an exact reproduction is not currently verified.** This is a directional
long-equity swing strategy, not an execution algorithm. Code needs synchronized OHLC/benchmark inputs, indicator conventions/warm-up,
causal before/after anchors, COR zero/range handling, exact thresholds and training selections, native sizing/leverage/cash rules,
resistance/stop/target definitions, costs and bar-fill precedence. Source parameter ranges include risk fractions10–90%; do not equate
those with verified loss-at-stop fractions. The saved Python is a source audit, not a deployable strategy.
No PowerLanguage port is earned. Days-to-weeks holdings also conflict with current Apex intraday-flat requirements;
a daily-flat NQ adaptation would be a different hypothesis requiring its own evidence.

## Completed checks and placement limits

The audit asserts the formula counterexample/undefined denominator, source-table arithmetic and pinned CSV headline;
records script/input hashes, source commit and owned-file census. PDF equation and Table2 images were inspected.
No empirical return, design/holdout variant, placebo, bootstrap, Monte Carlo or BASE/ADD/REPLACE/EMPTY trial was run.
All five homes—50K/150K evaluation,50K/150K funded and personal—remain unearned; account harm/benefit is unmeasured.
No allocation, ranking, live/VPS/broker or policy change. Independent review pending. Tell Claude to review this file and its audit receipts.
