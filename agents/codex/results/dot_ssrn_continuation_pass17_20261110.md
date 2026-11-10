# dot: FX volume reversal and further intraday exclusions
Author: dot. 2026-11-10. Research only; no tests or trading.

## 56. Foreign Exchange Volume
**Personal daily/overnight research; not flat-overnight or current-data ready. Serious data-delivery clock gate.**

Cespa, Gargano, Riddiough and Sarno, [SSRN 3019870](https://ssrn.com/abstract=3019870), RFS 2022. Reviewed [full accepted May 2021 manuscript and appendix](https://openaccess.city.ac.uk/id/eprint/26131/1/DP16128.pdf), particularly Sections 4–5 and Tables 1/5–7.

### Compact source specification
Thirty-one FX pairs including crosses, late 2011–December 2017. At 16:00 London, sort prior 24-hour returns into thirds, then abnormal volume into thirds within each return group. Long low-return/low-volume, short high-return/low-volume; rebalance daily. Abnormal volume is log current volume minus log prior-21-day mean volume. CLS total volume combines spot, forwards and swaps. Table 5 gross/net annual returns 17.61%/10.00%, Sharpe 1.70/.91, net maximum drawdown 17.50%. Olsen quoted spreads supply costs; slippage and size effects excluded. No untouched modern holdout established; diversification optimization uses the full sample. Pair weights/capital normalization require reconciliation.

### Material independent timing audit
[CLS's August 2025 product table](https://www.cls-group.com/media/k2bk3lza/clsmarketdata_aug_2025.pdf), page 6, distinguishes observation frequency from delivery frequency:
- Hourly observations delivered daily exist from October 31, 2011.
- Hourly spot delivery begins July 3, 2017.
- Hourly forward/swap delivery begins September 30, 2021.
The [2023 brochure](https://www.cls-group.com/media/3u3bcc2k/clsmarketdata_april2023.pdf) describes hourly spot delivery within thirty minutes after the hour. A [September 2017 announcement](https://www.cls-group.com/news/cls-to-develop-broader-range-of-forward-looking-solutions/) corroborates the new intraday product.

**Assessment:** a database stamped 16:00 is not automatically available for a 16:00 order. The study's total-volume same-clock signal/fill needs archived subscriber delivery and revision evidence. This is an unresolved executable-timing gate, not proof the mechanism is false. A later fill could change the result and must not inherit the published Sharpe.

The mechanism differs from carry, macro sorting and clock-based FX flows, but no measured contribution to the user's portfolio follows. Daily positions can remain open overnight. Owned 6E exchange volume is not CLS OTC spot/forward/swap volume; a one-market substitute changes both signal and portfolio. The [university manuscript license](https://openaccess.city.ac.uk/id/eprint/26131/) does not supply CLS/Datastream/Olsen dataset rights.

**First gate:** authenticate one historical information/receipt/fill sequence and exact normalized positions before considering data acquisition or a frozen delayed-fill validation. No such validation was run.

## Intraday source exclusions
- **SSRN 2558059:** the older abstract suggests option-implied moments forecast ten-minute ES returns. The [published author-hosted paper](https://bpb-us-w2.wpmucdn.com/blog.nus.edu.sg/dist/5/10939/files/2023/05/21_LCY-2019_Intraday-information-from-SP-500-Index-futures-options.pdf), Section 6/Table 12, instead finds no significant outright futures predictability. Positive evidence concerns option-skewness portfolios, with transaction-price rather than observed bid/ask execution. Do not promote the obsolete abstract as ES alpha.
- **SSRN 2657224:** [full manuscript](https://c.mql5.com/forextsd/forum/216/Exploring%20Irregular%20Time%20Series%20Through%20Non-Uniform%20Fast%20Fourier%20Transform.pdf) examines NG activity and GEFS temperature forecasts, September 2013–June 2014. Unsplit weather-price cointegration fails; alternative seasonal partition dates are searched. No complete trading rule, net return ledger or untouched holdout is established. Activity periodicity is not directional alpha.
- **SSRN 6415558, dividend-payment FX flows:** distinct cash-flow idea but full text not inspected. Official dissertation access has a reader-format limitation; primary-paper retrieval failed. Keep uncounted pending complete methods, costs and clocks.

## Network-source refinements, not new entries
Existing 3536046 reserve in pass 9: indexed [institutional thesis](https://ninercommons.charlotte.edu/record/1751/files/Kong_uncc_0694D_12758.pdf) passages narrow inputs to first/second monthly lags across 27 markets and 60-month estimation, 132 forecasts in 2009–19. The [author digest](https://www.bayes-cid.com/pdf/issues/2023-summer/publications/Page-37_42-CID-Summer-2023_Han-Kong.pdf) describes AICC-selected LASSO followed by OLS, highest-five/lowest-five portfolios and sign timing. Full thesis and numeric net-cost details remain inaccessible.

[Follow the Leader, arXiv 2501.07135](https://arxiv.org/pdf/2501.07135), full primary comparator: twenty-eight futures, lagged graph/trend signals, execution t+1 and return t+2 to handle asynchronous markets. Best historical net Sharpe .364 versus .233 baseline; modeled spread costs matter. Neighbor-signal equation and cost/timing notation need reconciliation; training/tuning overlaps the reported evaluation interval. Bootstrap paths are not new postpublication observations. No verified SSRN identity, no count increase. Newer 7128528 is Chinese urea/network abstract-only, not a substitute US strategy.
