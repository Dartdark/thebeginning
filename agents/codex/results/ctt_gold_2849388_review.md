# Gold transaction tax: execution reference; no strategy to test

Summary: This is a historical Indian tax/market-quality study, not a directional gold-futures strategy.
Published trading-value means imply declines of 43.95–57.08%; higher volatility is an author finding, not our replication.
The claimed 0.99 post-tax GARCH persistence recalculates to 0.974387; a claimed significant coefficient has p=0.3176.
Retain cost/participation lessons; DON'T TEST for our portfolios. No new returns, account results or strategy allocation.

Source: Velmurugan P. S. and Rinku Champramary, *CTT infuses inefficiency into Gold futures trading: An empirical Analysis*,
[SSRN2849388](https://ssrn.com/abstract=2849388), user-uploaded 20-page PDF. Title page is undated; PDF metadata says
October 7, 2016, which is a file-creation date, not independently authenticated publication/revision history.
Reviewed November 7, 2026 (America/Los_Angeles).
[PDF](../inputs/ctt_gold_2849388/source.pdf) · [complete extracted text](../inputs/ctt_gold_2849388/source.txt) ·
[access/version receipt](../inputs/ctt_gold_2849388/access.json) · [eligibility sheet](../evidence/ctt_gold_2849388.md).

Scope: complete extracted narrative, references and tables; PDF pages 8, 14 and 15 visually inspected. No raw MCX data,
GARCH estimation, bootstrap inference or causal identification independently reproduced. Published-table arithmetic only:
[script](../../../analysis/codex_two_uploads_2849388_3985691_audit.py) ·
[executed output](../../../analysis/outputs/codex_two_uploads_2849388_3985691/source_audit.json).

## Five questions

1. **What is it about?** Whether India's seller-side commodity transaction tax, introduced July 1, 2013, reduced
   activity and changed volatility/efficiency in MCX gold futures. The paper describes 1,616 daily observations from
   January 1, 2011 to July 30, 2016 and uses before/after volume comparisons, block-bootstrap Levene tests and a
   GARCH model with a tax-date dummy. This is Indian MCX gold, not CME GC/MGC or NQ/ES.
2. **What does it find?** Authors report lower turnover/open interest and higher volatility after the tax, and infer
   poorer efficiency. Table 4's published trading-value means imply **43.95–57.08% declines**, wider than the stated
   43–53% range. Table 5's standard deviations rise about **11.44–32.21%** across its windows. The strongest efficiency
   interpretation has important numerical/significance conflicts below. These remain source findings, not verified alpha.
3. **Why does it make money, if it does?** It demonstrates no trading profit. The proposed mechanism is that a higher
   tax deters marginal participants and weakens liquidity/information absorption. Less activity and more volatility do
   not identify a predictable return sign or an executable edge; they can increase trading costs and risk instead.
4. **Can we build on it?** Yes as a qualified execution/risk reference: express every tax/fee relative to traded notional
   and expected edge, and distinguish participation, volatility and forecastability. No deeper strategy investigation is
   warranted from this source. Original causal replication would need MCX contract-level history, dated tax rules,
   an authenticated event split and credible controls; owned CME candles cannot substitute for that market/history.
5. **Can a strategy code be made?** **A descriptive research model: yes; a paper-supported directional strategy: no.**
   A researcher could code the volume/variance comparisons and historical break model once data and ambiguities are
   resolved. No trade side, causal forecast rule, entry, stop, exit or size is specified. Fitting a full-history GARCH break
   is not a live signal, and no profitable volatility-timing rule is established. MultiCharts strategy code is unwarranted.

## What the arithmetic actually supports

Table 4 measures **trading value in INR lakhs**, rather than a demonstrated number of executable contracts. Recomputed
declines are 43.947%, 48.177%, 53.509%, 57.076% and 55.224% for the printed ±100/150/300/550/767 windows. These are
ratios of rounded source means; they are not independently estimated tax effects. Table 5's dispersion increase likewise
does not establish net expected profit or an exploitable conditional direction.

The historical source rate is **0.01% = 1 basis point of seller notional**, or INR10 per INR100,000 sale. This is not a
tax on margin, nor a current CME/MGC fee assumption. Any actual later strategy would need its own native costs and turnover.

| Source claim / issue | Checked interpretation |
|---|---|
| Post-tax persistence becomes 0.99, printed p.15 | Using its stated modified-model formula: pre = 0.07503 + 0.896272 = **0.971302**; post adds −0.000175 + 0.00326 = **0.974387**. The stated 0.99 is not reproduced. |
| All variance-dummy terms significant; alpha5 significantly positive | Table 6 prints alpha5 = 0.00326 with **p=0.3176**. Its positive point estimate is not conventional significance. Alpha4's reported p=0.0327 is a different result; no joint test was reproduced. |
| Tax negatively affects return, section 5.3 | The tax dummy's printed mean coefficient is **+0.000320, p=0.46820**. The unconditional before/after mean declines, but that does not turn this model coefficient into a significant negative effect. |
| Return definition | p.8 calls the return logarithmic while printing `P[t]/P[t-1]`. The table has small signed returns, so literal gross price ratios cannot describe it. Resolve with raw data/code before fitting. |
| Dates and samples | Main text ends July 30, 2016; a table footnote says through August. The “before” footnote extends to July 31, 2013 despite a July 1 tax start. Table 3 has 766 pre observations while symmetric windows include 767. These require source clarification, not convenient local assumptions. |
| Causality and efficiency | Single-market before/after comparisons do not isolate the tax from concurrent changes. Volatility persistence is not equivalent to directional inefficiency, profitable predictability or arbitrage. No raw-data identification/power check was run. |

The table-sign/p-value and arithmetic issues were confirmed against the rendered PDF, rather than inferred from text
extraction alone. We have not established whether the authors' unavailable implementation differs from the printed table.

## Eligibility, portfolio fit and next action

Exact ID/title search found no earlier review in the checked codex/work records, TIER_LIST, WATCHLIST or TODO, nor the
checked Claude tier/watch/queue records. Existing E09/E10/E12 already cover cost/turnover/volatility; retain a merged
[execution-reference follow-up](../EXECUTION_REFERENCES.md), not another alpha family or data-shopping task.

The owned filename/header census finds GC/NQ 2017+ OHLCV exports, not the source's MCX 2011–16 panel. That is a replication
limit, **not the reason an otherwise profitable strategy is blocked**: the paper supplies no trading rule or return result.
No broad acquisition, paid source, free-data detour or author contact is justified without an eligible hypothesis.

**DON'T TEST as a standalone strategy.** No promising-strategy TODO entry or new data-register row: missing information
alone does not qualify. No gross/design/historical-validation/placebo/account stage earned; BASE/ADD/REPLACE/EMPTY and
Sharpe/PF/payout metrics are **not tested / not applicable**, not zeros. No return preregistration or lease was claimed.
Independent empirical verification remains pending. No trading plan, live code, allocation, VPS or broker change.

For Claude: `agents/codex/results/ctt_gold_2849388_review.md` — historical tax-cost reference; turnover and GARCH claims
qualified; zero new economic definitions.
