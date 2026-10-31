# Sector bubble riding: DON'T TEST for current futures portfolios

Summary: Weekly Chinese equity-sector rotation buys sectors with persistent explosive-price signals.
Authors report 13.41% annual return versus 11.87% buy-and-hold over 2006–2020, a 1.54-point difference.
Their daily versions report−3.30%,−29.76% and 3.01% after costs; all trail the benchmark.
Critical-value vintages, real-price construction, cost accounting and tradable replication remain unresolved.
Useful timing/turnover reference; no new owned-data-compatible candidate or return trial.

Source: Haoran Liu, O-Chia Chuang and Jin Xu, *Sector Trading and Bubble Riding Behavior: Construction and
Evaluation of Trading Strategy Based on Bubble Test*, SSRN 4494963. All 15 uploaded PDF pages read, including
methodology, result tables and references; Table 4/5 visually checked. The PDF says not peer reviewed.
Version pinned to uploaded bytes, metadata modified 2023-06-29; SSRN revision history not independently checked.

[Owned PDF](../inputs/bubble_riding_4494963_20261031/source.pdf) ·
[text](../inputs/bubble_riding_4494963_20261031/source.txt) ·
[source-table audit script](../../../analysis/codex_bubble_riding_audit_20261031.py) ·
[claims](../../../analysis/outputs/codex_bubble_riding_audit_20261031/claims.json) ·
[arithmetic/hashes](../../../analysis/outputs/codex_bubble_riding_audit_20261031/audit.json).

Plan: none admitted. New economic definitions/return trials/account simulations 0. Direct uploaded-paper review;
scout lease/budget/progress and earlier selection history unchanged. No trading-plan or live change.

## Four questions

1. **What is it about?** Weekly long-only rotation among ten CSI 300 equity-sector indices using recursive
   explosive-price tests. Buy qualifying sectors equally; otherwise hold the broad CSI 300 index.
2. **What does it find?** The selected two-consecutive-signal rule reports final wealth$6.64 per$1 and 13.41%
   annually against$5.40/11.87% for the benchmark over January 2006–December 2020. Authors' daily implementations
   disappoint after costs. These are source results, not independently reproduced net returns or our account stats.
3. **Why could it make money?** Persistent sector enthusiasm and slow correction may let investors profit before
   an explosive trend ends. Two observations may reduce premature entries and turnover. This is a proposed trend
   persistence mechanism, not identified compulsory orders or a guarantee of selling before a crash.
4. **Can we build on it?** Retain methodology, but do not prioritize a new futures strategy from this evidence.
   The source is sector rotation, not timing a single index future. Switching it to NQ/ES would remove its central
   allocation choice. No independently justified new owned-market economic rule warrants a trial or TODO entry.

## Source rule and information clock

The data comprise Tuesday/Wednesday sector closes, Wednesday CSI 300 closes, and weekly CPI constructed with
Denton interpolation,2006-01-04 to 2020-12-30. Sectors are energy, materials, industrials, consumer discretionary,
staples, health care, financials, information technology, communications and utilities (PDF 8).

Use GSADF/BSADF right-tailed regressions, BIC lag choice up to six, and wild-bootstrap critical values to detect
explosive behavior. Three indicators: PSYI uses the current bubble flag; MPSYI also requires positive recent
return; DPSYI requires current and previous bubble flags. Sell when the relevant indicator turns off. Observe
Tuesday close and execute Wednesday, using weekly Wednesday close data for evaluation (PDF 5–8). This explicit
lag is a useful source feature, but exact fill availability, holidays and executable vehicles still need definition.

A backward-looking statistic can be causal, but retrospective shaded bubbles do not alone demonstrate that every
label and critical value was available then. Bootstrap seeds/settings, prefix calibration, fixed minimum-window
convention, CPI release/revision/interpolation vintages and exact use of real versus nominal prices are not
specified enough to certify real-time reproduction. This is an unresolved gate, not a proved look-ahead error.

## Reported comparison and limits

|Weekly rule|Final wealth per$1|Annual return|Printed trading periods|
|---|---:|---:|---:|
|Current bubble PSYI|6.39|13.13%|122|
|Bubble plus positive return MPSYI|5.02|11.32%|168|
|Two consecutive bubble flags DPSYI|6.64|13.41%|87|
|Broad index buy-and-hold|5.40|11.87%|2|

Source Table 1/PDF 10. The selected annual advantage is 1.54 percentage points. The Sharpe row is labelled percent
and reports 6.66 versus 6.13 for DPSYI/BH, without enough scaling/annualization detail to present 6.66 as a verified
conventional annual Sharpe. No maximum drawdown, trade ledger or account-level contribution is supplied.

The 90%/95%/99% confidence alternatives report 11.88%/13.41%/13.22%. Selection and confidence comparisons use the
same historical sample. Rolling overlapping 1–6-year windows are robustness descriptions, not independent holdouts.
DPSYI beats BH in 36.39% of one-year windows, loses in 28.32%, ties in 35.29%; it does not beat BH in most individual
one-year windows if ties are included. Six-year outperformance fraction is 64.12%, still an overlapping sample.

Daily PSYI/MPSYI/DPSYI gross wealth 7.81/9.68/7.90 falls to 0.70/0.02/1.37 after costs (Table 4/PDF 13).
The paper calls costs 0.5% of total real return per round trip. Our independent arithmetic finds that
`gross_wealth*(1−0.005)^reported_periods` approximately matches these rounded endpoints. This is consistent
with a multiplicative wealth haircut per reported period; it does not prove the actual implementation or mean
0.5% of positive profit only. Capital allocated across sectors, actual turnover, round-trip versus one-way charges,
benchmark costs, dividends and executable instrument tracking remain unresolved. We did not derive corrected returns.
Daily annualization also needs a dated ledger rather than assuming it shares the weekly effective sample.

## Fit and decision

Owned CME minute bars and SPY/SPX series are not the source's ten Chinese sector indices or tradable sector baskets.
The source names no readily interchangeable futures sector implementation. Weekly overnight holdings fail ordinary
Apex intraday fit; neither 50K/150K evaluation nor funded has an eligible admitted rule. Personal rotation is a
different investment universe, with no tested benefit to the existing futures book.

Deduplication found TIER_LIST's López de Prado/SADF methods reference: bubble tests do not themselves establish
trades. Exact SSRN/title not found in the checked results/TODO/TIER_LIST search. This source adds concrete sector
allocation and cost evidence, but does not justify recycling prior futures momentum/indicator families.

**DON'T TEST for current books.** No expensive acquisition project or substitute return screen is warranted by the
modest selected-sample advantage and unresolved implementation. No promising-strategy queue entry. Reconsider only
with a specific owned-market economic adaptation and independently reproducible net evidence. Missing data alone
is not the reason for rejecting a new test. No design,2023+ validation, placebo, Monte Carlo, account comparison,
independent economic verification or allocation occurred. Retain turnover/clock lessons in EXECUTION_REFERENCES E10.

For Claude: `agents/codex/results/bubble_riding_4494963_review_20261031.md`.
