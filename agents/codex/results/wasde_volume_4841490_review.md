# WASDE futures/options volume: retain a conditional lead; NEEDS DATA AND SPECIFICATION

Summary: Zhang finds announcement-related trading activity and opposite-signed futures/options volume predictors.
The reported 5–20-day relationships are in-sample regressions, not an executable net-return strategy.
The ending-stock variable is a monthly forecast revision, not a surprise relative to market expectations.
Day-zero returns, contract selection, volume aggregation and data availability need resolution before replication.
Retain for lower-priority personal-account research; missing agricultural/options inputs block return tests.

Source: Tianyang Zhang, *Trading Activity of Commodity Futures and Options Around USDA Announcements*,
[SSRN 4841490](https://ssrn.com/abstract=4841490), uploaded 28-page PDF, fully read including tables and appendix.
PDF metadata creation May 25, 2024; publication/revision history not independently authenticated.
[Archived source](../inputs/ssrn4841490/source.pdf) and [text](../inputs/ssrn4841490/source.txt).
PDF SHA-256: `49df2c9701320a4cc68b55ffaa3dc2496a41ff4a00e136df0c2b71cc3612f025`.
Gate script: `analysis/codex_wasde_4841490_gate.py`; receipt: `analysis/outputs/codex_wasde_4841490_gate/gate.json`.
Return trials: **0**. All empirical numbers below are author-reported, not independently reproduced.

## 1. What is it about?

How futures and options activity changes around monthly USDA World Agricultural Supply and Demand Estimates
(WASDE) releases, and whether pre-release activity predicts later agricultural futures returns.
The Bloomberg sample runs January 1995–December 2018, covering seven tabled markets: wheat, corn, soybeans,
soybean oil, soybean meal, sugar and cotton. The data prose also lists oats while calling the universe seven;
oats is absent from the reported market tables, so exact source-universe reconciliation is needed.
The paper reports 288 monthly releases and 42,691 commodity-daily observations (pp. 4–5).

Contract observations are tied to the underlying option expiration: from 65 calendar days before expiration
through Tuesday of the preceding week (Figure 1, p. 16, visually inspected). This is not simply a continuous
front-month futures study. Options/futures volume-ratio extremes are trimmed at both 1% tails.

## 2. What does it find?

Announcement-day abnormal futures activity spikes, with options activity generally responding less distinctly
and sometimes more persistently (Tables 2–6, pp. 22–26). The abnormal measure is an **absolute deviation** from
other days' average volume in the same month, not signed buying pressure or an always-positive volume increase.

Table 7 (p. 27) pools post-announcement return regressions with time-clustered standard errors:

| Predictor | Through day +5: coefficient (t) | Through day +20: coefficient (t) |
|---|---:|---:|
| Monthly ending-stock forecast revision | −3.800 (−3.759) | +0.022 (+0.270) |
| Log futures volume | +0.285 (+2.136) | +0.037 (+2.433) |
| Log options volume | −0.275 (−2.888) | −0.040 (−3.737) |

The other volume-coefficient t-statistics are futures +1.792/+2.499 and options −2.786/−3.502 at +10/+15 days.
The +5 and +20 regressions have 2,173 and 2,074 observations, with R² 0.023 and 0.013, respectively.
These are regression coefficients in the source's units, **not tradable percentage returns, trade t-statistics,
annualized Sharpe ratios or portfolio profit estimates**. Economic units/aggregation require clarification.
No walk-forward or held-out trading test, net-cost ledger, sizing rule, drawdown or account simulation is supplied.

## 3. Why does it make money, if it does?

The proposed mechanisms are producers adjusting hedges after crop-supply news and informed traders positioning
before publication (pp. 3, 9–13). A higher ending-stock forecast can lower the crop's price through expected supply
and storage economics (Appendix A). But forecast **revision** is not an unexpected announcement: consensus may
already anticipate it. Nor does unsigned options volume identify informed direction, participants or causal flow.
The paper itself leaves the opposite signs of the two volume predictors as a future research question (p. 13).

Thus the paper establishes historical conditional associations, not that an investor captured profits after
costs or that the private-information explanation is uniquely identified. Ordinary seasonal hedging, maturity,
liquidity, common commodity factors and prior returns remain important alternative explanations.

## 4. Can we build on it?

**Potentially, with matched agricultural futures/options data and clarified clocks.** The most specific lead is
pre-announcement relative futures/options activity predicting later returns, rather than a generic price breakout.
It is relevant to possible personal-account commodity research. The 5–20-day holdings are ineligible for the
50K/150K evaluation and funded portfolios as written. Turning them into intraday corn/soybean trades would be
a different hypothesis; this source provides no intraday edge or transmission into NQ/ES.

Material gates before any return study:

- **Information timing:** Section 4 includes return day zero. A forecast revision becomes known at publication,
  so one cannot count a prior close-to-release move as profit from that revision. Resolve exact return endpoints,
  historical release times/session regimes, first executable post-release price and data receipt delay. For the
  volume-only variant, all inputs must be finalized and available before its independently frozen entry clock.
- **Retrospective normalization:** Section 3's same-month non-event average can use days after the event.
  It is suitable for an ex-post event description, not directly an available pre-event feature. Future deployment
  would require a registered past-only alternative, explicitly labeled as an adaptation.
- **Contract and option definition:** clarify whether futures/options volumes are summed or averaged across
  the pre-event window and which strikes, call/put types, expirations and maturities are aggregated. Preserve
  the option-to-futures mapping, expiration calendar, two dated maturities for the basis control, and trim rules.
  Fit any trimming cutoffs on past training data rather than selecting the entire future sample.
- **Inference:** several markets share releases; adjacent 20-day windows can overlap. Do not treat commodity rows
  or horizons as independent confirmations. Use chronological splits, matured labels, appropriate clustering,
  fixed effects/seasonal controls and simple price-only/calendar-only baselines before claiming incremental value.
- **Execution/accounting:** prices, limits/halts, spreads, fees, roll rules, contract multipliers, integer size,
  collateral/margin and open losses are absent from the proposed trading interpretation. Higher event volume
  is not proof of a tighter spread, smaller impact or an available fill. No native execution saving is measured.

## Input feasibility and stopping decision

The saved script searches owned `data/` filenames for agricultural market/WASDE inputs; it found no matching files.
This is a bounded filename census, not proof that every opaque file has been semantically exhausted. Existing TODO
already requests ZC/ZS intraday exports, but those alone would not supply historical contract-matched options
activity, deferred futures, vintaged forecasts or the original 1995–2018 panel.

Normal proxy-routed public requests to the USDA WASDE page and CME agricultural volume/open-interest page both
returned tunnel **403 Forbidden**; the receipt retains exact URLs/errors. No historical product, licence or price
was verified, and no purchase, alternate access route or synthetic replacement was attempted. A successful public
landing page would itself establish neither the needed historical panel nor field definitions.

**NEEDS DATA AND SPECIFICATION.** Retain the precise lead in the research queue. Resume only with genuinely new
matched data or specification: first reconcile one report/contract's information clocks and volumes without
returns, then establish 2018–22 coverage, effective event count and costs in a committed bounded preregistration.
Do not infer a passing power gate from the author's pooled 1995–2018 sample. No parameter search, market-return
test, account stage, grade or allocation is earned now. Independent economic verification remains pending.

For Claude: `agents/codex/results/wasde_volume_4841490_review.md`.
