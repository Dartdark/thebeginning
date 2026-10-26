# NQ Correlation Risk Budget: REJECT; continue distinct research

Summary: All three frozen candidates failed 2018–22 design. Primary 30-minute rule: 44 trades,
net $-7,239.00/NQ, trade t -1.524, daily Newey-West(5) t -1.669.
The filter removed profitable trades and lost against matched controls. No 2023+ returns were tested.
All 60 evaluations retained; 58 unique rules after a disclosed redundant threshold. No milestone event.

Plan: agents/codex/plans/correlation_risk_budget.md, commit 5678dde before raw return execution.
Scripts: analysis/codex_correlation_risk_budget.py and analysis/codex_correlation_risk_budget_report.py.
Outputs: analysis/outputs/codex_correlation_risk_budget/. Five evaluations: three candidate labels and two
unselectable controls. Prior program:55 evaluations/54 unique, plus unknown much larger older searches.

## Rule as tested

At the 14:30 CT 30-minute close, model a US stock–bond portfolio from ES/ZN returns. An uncentred EWMA
second-moment matrix uses lambda0.94 after 60 admissible daily returns; initialize from their mean outer
product. At each date the state contains only strictly prior observations. Prices come from exact immediately
preceding cash-date 15:00 closes; missing/early/guarded dates are not stretched to older available closes.

For each covariance matrix, inverse-volatility weights give equal risk in two assets. Leverage targets 8%
annualized risk and caps at2. Update with today's partial return through14:30. Compare the new equity target
with a counterfactual using the SAME updated marginal variances and prior correlation. K is their difference.
Full flow F is new target minus prior model exposure drifted by today's equity and bond returns/NAV.
V is the corresponding frozen-correlation rebalance. These model outputs are signal inputs, not traded
portfolio returns. Actual AUM, allocation, orders and a mandatory execution clock are not observed.

Shared eligibility requires |F|>=0.01NAV,V!=0, finite model values and a positive prior NQ ATR. Trade sign(F)
when sign(K) agrees, |K|>=0.5|F| and |K|>=0.005(primary CRB005),0.0025(CRB0025),or0.01(CRB010).
RP30 omits K gates. VOL30 uses sign(V) on the same eligible dates and is unselectable. Only NQ is traded.

Native CT close labels; valid complete positive OHLC/nonnegative volume at14:01–14:30 in all three inputs;
normal cash dates only, no July3/Dec24. Both daily endpoints and decision/prior dates avoid the existing equity
roll window and the last12Monday–Friday dates of February/May/August/November. The latter buffers typical
Treasury rolls but does not establish exact vendor switch dates. Fixed |rES|>5% or |rZN|>3% input jumps are
unavailable; no repair or forward-return selection. ES2017 beginsJanuary, ZN2017 onlyDecember. Actual
60-observation readiness begins 2018-04-04.

Entry at native14:32-labelled open, one extra whole minute after the decision. One contract/date, no reentry,
stop0.10prior15weekdayATR,target0.20 rounded up to0.25, active entry-bar protection, flat15:00CT.
Shared grid._walk/F.replay handles target1point-through and worse-open stop gaps. NQ$7.25RT plus$5 per
market/stop fill; nativeMNQ independently$1.24RT plus$0.50 per such fill. Fixed four-tick stress retained.
No old ticket series, signal basket, fitted return combination, sizing or return rescaling.

## Design results

2018–22 only. Daily cash grid 2018-01-02–2022-12-30, 1259 sessions including
zero-return days. NQ dollars except native net_mnq rows. Whole/long/short/every year, initial-zero drawdown,
shared standard metrics, trade t, NW5/NW20, native micro costs and four-tick slippage follow.

| model | period | side | trades | win | avg | total | t_trade | t_nw5 | t_nw20 | sharpe | sortino | profit_factor | calmar | ulcer | max_dd | cost | missing_held_minutes |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| CRB005 | 2018-22 | all | 44 | 0.29545 | -164.52 | -7239 | -1.5245 | -1.669 | -1.8949 | -0.67235 | -0.97796 | 0.55506 | -0.15355 | 7.7581 | 9436.5 | 749 | 0 |
| CRB005 | 2018 | all | 0 | nan | nan | 0 | nan | nan | nan | nan | nan | nan | nan | 0 | 0 | 0 | 0 |
| CRB005 | 2019 | all | 7 | 0.14286 | -147.96 | -1035.8 | -1.7466 | -1.2298 | -1.4041 | -1.5402 | -1.6985 | 0.21742 | -1 | 1.0066 | 1035.8 | 120.75 | 0 |
| CRB005 | 2020 | all | 11 | 0.27273 | 6.3864 | 70.25 | 0.018321 | 0.02177 | 0.032257 | 0.019139 | 0.035986 | 1.0147 | 0.018959 | 4.9434 | 3690.8 | 179.75 | 0 |
| CRB005 | 2021 | all | 11 | 0.36364 | -161.8 | -1779.8 | -1.1625 | -1.2953 | -1.3372 | -1.1451 | -1.3454 | 0.46324 | -0.81444 | 1.3993 | 2185.2 | 189.75 | 0 |
| CRB005 | 2022 | all | 15 | 0.33333 | -299.58 | -4493.8 | -1.8279 | -1.9181 | -1.8186 | -1.7099 | -2.0038 | 0.34517 | -1.004 | 6.2408 | 4493.8 | 258.75 | 0 |
| CRB005 | 2018-22 | long | 23 | 0.30435 | -138.55 | -3186.8 | -0.89844 | -1.1723 | -1.2077 | -0.40362 | -0.59188 | 0.62157 | -0.15897 | 2.9471 | 4012.5 | 391.75 | 0 |
| CRB005 | 2018 | long | 0 | nan | nan | 0 | nan | nan | nan | nan | nan | nan | nan | 0 | 0 | 0 | 0 |
| CRB005 | 2019 | long | 5 | 0.2 | -93.25 | -466.25 | -0.83569 | -0.75126 | -0.93087 | -0.86166 | -1.0182 | 0.38163 | -0.7499 | 0.59102 | 621.75 | 86.25 | 0 |
| CRB005 | 2020 | long | 5 | 0.4 | 119.75 | 598.75 | 0.2068 | 0.37843 | 0.49959 | 0.2291 | 0.4537 | 1.2835 | 0.55362 | 0.7151 | 1077.2 | 81.25 | 0 |
| CRB005 | 2021 | long | 7 | 0.42857 | -98.679 | -690.75 | -0.49898 | -0.52989 | -0.45511 | -0.52736 | -0.65293 | 0.64559 | -0.4991 | 0.75893 | 1384 | 120.75 | 0 |
| CRB005 | 2022 | long | 6 | 0.16667 | -438.08 | -2628.5 | -1.5046 | -1.6121 | -1.6878 | -1.3726 | -1.5915 | 0.27113 | -1.004 | 3.8857 | 2628.5 | 103.5 | 0 |
| CRB005 | 2018-22 | short | 21 | 0.28571 | -192.96 | -4052.2 | -1.2525 | -1.2084 | -1.7525 | -0.55304 | -0.79774 | 0.48371 | -0.14457 | 5.4304 | 5610.5 | 357.25 | 0 |
| CRB005 | 2018 | short | 0 | nan | nan | 0 | nan | nan | nan | nan | nan | nan | nan | 0 | 0 | 0 | 0 |
| CRB005 | 2019 | short | 2 | 0 | -284.75 | -569.5 | -113.9 | -1.4494 | -1.4347 | -1.417 | -1.4142 | 0 | -1 | 0.58034 | 569.5 | 34.5 | 0 |
| CRB005 | 2020 | short | 6 | 0.16667 | -88.083 | -528.5 | -0.18863 | -0.19236 | -0.31244 | -0.2051 | -0.36741 | 0.80104 | -0.19818 | 4.3859 | 2656.2 | 98.5 | 0 |
| CRB005 | 2021 | short | 4 | 0.25 | -272.25 | -1089 | -1.4705 | -1.4979 | -1.7185 | -1.2961 | -1.3713 | 0.20322 | -0.79678 | 1.2077 | 1366.8 | 69 | 0 |
| CRB005 | 2022 | short | 9 | 0.44444 | -207.25 | -1865.2 | -1.0316 | -1.0812 | -1.3843 | -1.0301 | -1.2295 | 0.42718 | -1.004 | 2.397 | 1865.2 | 155.25 | 0 |
| CRB005 | 2018-22 | net_mnq | 44 | 0.29545 | -16.967 | -746.56 | -1.5722 | -1.7181 | -1.9454 | -0.6923 | -1.0009 | 0.5456 | -0.15547 | 0.82123 | 961.16 | 97.56 | 0 |
| CRB005 | 2018-22 | stress_four_ticks | 44 | 0.27273 | -193.84 | -8529 | -1.7905 | -1.9371 | -2.1648 | -0.78234 | -1.1029 | 0.50419 | -0.16326 | 8.6437 | 10456 | 2039 | 0 |
| CRB0025 | 2018-22 | all | 44 | 0.29545 | -164.52 | -7239 | -1.5245 | -1.669 | -1.8949 | -0.67235 | -0.97796 | 0.55506 | -0.15355 | 7.7581 | 9436.5 | 749 | 0 |
| CRB0025 | 2018 | all | 0 | nan | nan | 0 | nan | nan | nan | nan | nan | nan | nan | 0 | 0 | 0 | 0 |
| CRB0025 | 2019 | all | 7 | 0.14286 | -147.96 | -1035.8 | -1.7466 | -1.2298 | -1.4041 | -1.5402 | -1.6985 | 0.21742 | -1 | 1.0066 | 1035.8 | 120.75 | 0 |
| CRB0025 | 2020 | all | 11 | 0.27273 | 6.3864 | 70.25 | 0.018321 | 0.02177 | 0.032257 | 0.019139 | 0.035986 | 1.0147 | 0.018959 | 4.9434 | 3690.8 | 179.75 | 0 |
| CRB0025 | 2021 | all | 11 | 0.36364 | -161.8 | -1779.8 | -1.1625 | -1.2953 | -1.3372 | -1.1451 | -1.3454 | 0.46324 | -0.81444 | 1.3993 | 2185.2 | 189.75 | 0 |
| CRB0025 | 2022 | all | 15 | 0.33333 | -299.58 | -4493.8 | -1.8279 | -1.9181 | -1.8186 | -1.7099 | -2.0038 | 0.34517 | -1.004 | 6.2408 | 4493.8 | 258.75 | 0 |
| CRB0025 | 2018-22 | long | 23 | 0.30435 | -138.55 | -3186.8 | -0.89844 | -1.1723 | -1.2077 | -0.40362 | -0.59188 | 0.62157 | -0.15897 | 2.9471 | 4012.5 | 391.75 | 0 |
| CRB0025 | 2018 | long | 0 | nan | nan | 0 | nan | nan | nan | nan | nan | nan | nan | 0 | 0 | 0 | 0 |
| CRB0025 | 2019 | long | 5 | 0.2 | -93.25 | -466.25 | -0.83569 | -0.75126 | -0.93087 | -0.86166 | -1.0182 | 0.38163 | -0.7499 | 0.59102 | 621.75 | 86.25 | 0 |
| CRB0025 | 2020 | long | 5 | 0.4 | 119.75 | 598.75 | 0.2068 | 0.37843 | 0.49959 | 0.2291 | 0.4537 | 1.2835 | 0.55362 | 0.7151 | 1077.2 | 81.25 | 0 |
| CRB0025 | 2021 | long | 7 | 0.42857 | -98.679 | -690.75 | -0.49898 | -0.52989 | -0.45511 | -0.52736 | -0.65293 | 0.64559 | -0.4991 | 0.75893 | 1384 | 120.75 | 0 |
| CRB0025 | 2022 | long | 6 | 0.16667 | -438.08 | -2628.5 | -1.5046 | -1.6121 | -1.6878 | -1.3726 | -1.5915 | 0.27113 | -1.004 | 3.8857 | 2628.5 | 103.5 | 0 |
| CRB0025 | 2018-22 | short | 21 | 0.28571 | -192.96 | -4052.2 | -1.2525 | -1.2084 | -1.7525 | -0.55304 | -0.79774 | 0.48371 | -0.14457 | 5.4304 | 5610.5 | 357.25 | 0 |
| CRB0025 | 2018 | short | 0 | nan | nan | 0 | nan | nan | nan | nan | nan | nan | nan | 0 | 0 | 0 | 0 |
| CRB0025 | 2019 | short | 2 | 0 | -284.75 | -569.5 | -113.9 | -1.4494 | -1.4347 | -1.417 | -1.4142 | 0 | -1 | 0.58034 | 569.5 | 34.5 | 0 |
| CRB0025 | 2020 | short | 6 | 0.16667 | -88.083 | -528.5 | -0.18863 | -0.19236 | -0.31244 | -0.2051 | -0.36741 | 0.80104 | -0.19818 | 4.3859 | 2656.2 | 98.5 | 0 |
| CRB0025 | 2021 | short | 4 | 0.25 | -272.25 | -1089 | -1.4705 | -1.4979 | -1.7185 | -1.2961 | -1.3713 | 0.20322 | -0.79678 | 1.2077 | 1366.8 | 69 | 0 |
| CRB0025 | 2022 | short | 9 | 0.44444 | -207.25 | -1865.2 | -1.0316 | -1.0812 | -1.3843 | -1.0301 | -1.2295 | 0.42718 | -1.004 | 2.397 | 1865.2 | 155.25 | 0 |
| CRB0025 | 2018-22 | net_mnq | 44 | 0.29545 | -16.967 | -746.56 | -1.5722 | -1.7181 | -1.9454 | -0.6923 | -1.0009 | 0.5456 | -0.15547 | 0.82123 | 961.16 | 97.56 | 0 |
| CRB0025 | 2018-22 | stress_four_ticks | 44 | 0.27273 | -193.84 | -8529 | -1.7905 | -1.9371 | -2.1648 | -0.78234 | -1.1029 | 0.50419 | -0.16326 | 8.6437 | 10456 | 2039 | 0 |
| CRB010 | 2018-22 | all | 33 | 0.27273 | -181.34 | -5984.2 | -1.3506 | -1.4986 | -1.7332 | -0.59702 | -0.88313 | 0.53768 | -0.13628 | 7.7166 | 8789.5 | 559.25 | 0 |
| CRB010 | 2018 | all | 0 | nan | nan | 0 | nan | nan | nan | nan | nan | nan | nan | 0 | 0 | 0 | 0 |
| CRB010 | 2019 | all | 5 | 0 | -205.25 | -1026.2 | -3.4001 | -1.7917 | -1.5761 | -1.9379 | -1.9274 | 0 | -1 | 1.0125 | 1026.2 | 86.25 | 0 |
| CRB010 | 2020 | all | 10 | 0.3 | 44.75 | 447.5 | 0.11683 | 0.14015 | 0.22 | 0.12258 | 0.23366 | 1.1019 | 0.13452 | 4.3544 | 3313.5 | 162.5 | 0 |
| CRB010 | 2021 | all | 8 | 0.25 | -307.88 | -2463 | -2.1502 | -1.9253 | -1.9434 | -1.7916 | -1.8875 | 0.2051 | -1 | 1.5654 | 2463 | 138 | 0 |
| CRB010 | 2022 | all | 10 | 0.4 | -294.25 | -2942.5 | -1.4239 | -1.5533 | -1.3574 | -1.3609 | -1.5646 | 0.33555 | -0.83435 | 5.609 | 3540.8 | 172.5 | 0 |
| CRB010 | 2018-22 | long | 16 | 0.3125 | -122.25 | -1956 | -0.57888 | -0.81288 | -0.82025 | -0.26447 | -0.40194 | 0.68852 | -0.10466 | 2.4353 | 3740.8 | 271 | 0 |
| CRB010 | 2018 | long | 0 | nan | nan | 0 | nan | nan | nan | nan | nan | nan | nan | 0 | 0 | 0 | 0 |
| CRB010 | 2019 | long | 3 | 0 | -152.25 | -456.75 | -1.6386 | -1.3322 | -1.4105 | -1.3131 | -1.3112 | 0 | -1 | 0.43894 | 456.75 | 51.75 | 0 |
| CRB010 | 2020 | long | 4 | 0.5 | 244 | 976 | 0.33418 | 0.63711 | 0.80208 | 0.3775 | 0.77189 | 1.5627 | 0.90243 | 0.21584 | 1077.2 | 64 | 0 |
| CRB010 | 2021 | long | 5 | 0.4 | -219.25 | -1096.2 | -0.96362 | -0.98173 | -0.84029 | -0.97046 | -1.0588 | 0.36697 | -0.79209 | 0.75905 | 1384 | 86.25 | 0 |
| CRB010 | 2022 | long | 4 | 0.25 | -344.75 | -1379 | -0.76532 | -0.97638 | -0.96359 | -0.80937 | -0.98836 | 0.41487 | -0.58746 | 2.7171 | 2356.8 | 69 | 0 |
| CRB010 | 2018-22 | short | 17 | 0.23529 | -236.96 | -4028.2 | -1.3626 | -1.2695 | -1.8787 | -0.595 | -0.85429 | 0.39554 | -0.14349 | 5.8361 | 5619.2 | 288.25 | 0 |
| CRB010 | 2018 | short | 0 | nan | nan | 0 | nan | nan | nan | nan | nan | nan | nan | 0 | 0 | 0 | 0 |
| CRB010 | 2019 | short | 2 | 0 | -284.75 | -569.5 | -113.9 | -1.4494 | -1.4347 | -1.417 | -1.4142 | 0 | -1 | 0.58034 | 569.5 | 34.5 | 0 |
| CRB010 | 2020 | short | 6 | 0.16667 | -88.083 | -528.5 | -0.18863 | -0.19236 | -0.31244 | -0.2051 | -0.36741 | 0.80104 | -0.19818 | 4.3859 | 2656.2 | 98.5 | 0 |
| CRB010 | 2021 | short | 3 | 0 | -455.58 | -1366.8 | -12.464 | -1.7856 | -1.9921 | -1.7278 | -1.721 | 0 | -1 | 1.3515 | 1366.8 | 51.75 | 0 |
| CRB010 | 2022 | short | 6 | 0.5 | -260.58 | -1563.5 | -1.21 | -1.1825 | -1.5531 | -1.1689 | -1.2399 | 0.24532 | -0.98339 | 2.918 | 1596.2 | 103.5 | 0 |
| CRB010 | 2018-22 | net_mnq | 33 | 0.27273 | -18.649 | -615.42 | -1.3889 | -1.5391 | -1.775 | -0.61304 | -0.90167 | 0.52905 | -0.13836 | 0.81401 | 890.28 | 72.92 | 0 |
| CRB010 | 2018-22 | stress_four_ticks | 33 | 0.24242 | -210.43 | -6944.2 | -1.5615 | -1.7165 | -1.9532 | -0.68422 | -0.983 | 0.49187 | -0.14709 | 8.4205 | 9449.5 | 1519.2 | 0 |
| RP30 | 2018-22 | all | 284 | 0.41901 | -20.067 | -5699 | -0.60249 | -0.6553 | -0.73351 | -0.26978 | -0.44164 | 0.90885 | -0.10504 | 8.1031 | 10859 | 4739 | 0 |
| RP30 | 2018 | all | 38 | 0.5 | 11.829 | 449.5 | 0.21742 | 0.22641 | 0.28031 | 0.22022 | 0.36962 | 1.0964 | 0.29852 | 0.97532 | 1511.8 | 625.5 | 0 |
| RP30 | 2019 | all | 69 | 0.34783 | -51.453 | -3550.2 | -1.8334 | -1.8487 | -2.022 | -1.811 | -2.3677 | 0.6097 | -0.81667 | 4.0845 | 4347.2 | 1160.2 | 0 |
| RP30 | 2020 | all | 54 | 0.40741 | 39.417 | 2128.5 | 0.39342 | 0.4334 | 0.60577 | 0.39509 | 0.7668 | 1.1599 | 0.50626 | 4.2509 | 4187.8 | 891.5 | 0 |
| RP30 | 2021 | all | 77 | 0.42857 | -44.263 | -3408.2 | -0.80773 | -0.85545 | -0.80548 | -0.80901 | -1.1945 | 0.80573 | -0.45135 | 4.9283 | 7551.2 | 1288.2 | 0 |
| RP30 | 2022 | all | 46 | 0.45652 | -28.663 | -1318.5 | -0.22153 | -0.25338 | -0.30283 | -0.22388 | -0.35588 | 0.92637 | -0.26321 | 6.2635 | 5029.2 | 773.5 | 0 |
| RP30 | 2018-22 | long | 154 | 0.3961 | -64.003 | -9856.5 | -1.5934 | -1.7716 | -1.986 | -0.70978 | -1.052 | 0.70825 | -0.19191 | 9.0788 | 10280 | 2601.5 | 0 |
| RP30 | 2018 | long | 25 | 0.44 | -36.65 | -916.25 | -0.58847 | -0.62112 | -0.79264 | -0.59674 | -0.89531 | 0.71993 | -0.55625 | 1.0275 | 1653.8 | 421.25 | 0 |
| RP30 | 2019 | long | 42 | 0.38095 | -44.393 | -1864.5 | -1.2631 | -1.2787 | -1.568 | -1.2556 | -1.6613 | 0.64408 | -0.78234 | 2.3306 | 2383.2 | 714.5 | 0 |
| RP30 | 2020 | long | 21 | 0.38095 | 17.988 | 377.75 | 0.11044 | 0.15445 | 0.1759 | 0.11269 | 0.21162 | 1.0684 | 0.26756 | 1.4652 | 1406.2 | 352.25 | 0 |
| RP30 | 2021 | long | 47 | 0.42553 | -67.676 | -3180.8 | -1.1197 | -1.2599 | -1.4979 | -1.1173 | -1.5162 | 0.68019 | -0.68588 | 4.1543 | 4637.5 | 795.75 | 0 |
| RP30 | 2022 | long | 19 | 0.31579 | -224.88 | -4272.8 | -1.1174 | -1.1534 | -1.2996 | -1.1129 | -1.5443 | 0.56419 | -0.97817 | 6.6462 | 4385.5 | 317.75 | 0 |
| RP30 | 2018-22 | short | 130 | 0.44615 | 31.981 | 4157.5 | 0.58282 | 0.62027 | 0.77472 | 0.26134 | 0.46855 | 1.1447 | 0.17297 | 2.9507 | 4811 | 2137.5 | 0 |
| RP30 | 2018 | short | 13 | 0.61538 | 105.06 | 1365.8 | 1.0176 | 1.0741 | 1.0735 | 1.0183 | 2.079 | 1.9817 | 1.7936 | 0.46538 | 764.5 | 204.25 | 0 |
| RP30 | 2019 | short | 27 | 0.2963 | -62.435 | -1685.8 | -1.3233 | -1.1211 | -1.3032 | -1.3071 | -1.6954 | 0.56302 | -0.63511 | 2.7259 | 2654.2 | 445.75 | 0 |
| RP30 | 2020 | short | 33 | 0.42424 | 53.053 | 1750.8 | 0.41129 | 0.43113 | 0.65338 | 0.41507 | 0.82358 | 1.2248 | 0.48956 | 3.5311 | 3562 | 539.25 | 0 |
| RP30 | 2021 | short | 30 | 0.43333 | -7.5833 | -227.5 | -0.072156 | -0.0847 | -0.08083 | -0.073238 | -0.11763 | 0.97006 | -0.063208 | 1.9632 | 3599.2 | 492.5 | 0 |
| RP30 | 2022 | short | 27 | 0.55556 | 109.42 | 2954.2 | 0.65556 | 0.71611 | 1.004 | 0.66317 | 1.199 | 1.3646 | 1.1155 | 2.9945 | 2659 | 455.75 | 0 |
| RP30 | 2018-22 | net_mnq | 284 | 0.41901 | -2.5217 | -716.16 | -0.75712 | -0.82327 | -0.92148 | -0.33892 | -0.54966 | 0.88699 | -0.12877 | 0.90622 | 1113.2 | 620.16 | 0 |
| RP30 | 2018-22 | stress_four_ticks | 284 | 0.40493 | -48.377 | -13739 | -1.445 | -1.5658 | -1.7494 | -0.64552 | -1.0074 | 0.79648 | -0.18206 | 14.163 | 15105 | 12779 | 0 |
| VOL30 | 2018-22 | all | 284 | 0.44014 | 1.5 | 426 | 0.045076 | 0.045506 | 0.042914 | 0.020194 | 0.033286 | 1.0071 | 0.0090216 | 7.0815 | 9451.5 | 4714 | 0 |
| VOL30 | 2018 | all | 38 | 0.5 | 11.829 | 449.5 | 0.21742 | 0.22641 | 0.28031 | 0.22022 | 0.36962 | 1.0964 | 0.29852 | 0.97532 | 1511.8 | 625.5 | 0 |
| VOL30 | 2019 | all | 69 | 0.37681 | -26.598 | -1835.2 | -0.8822 | -0.91163 | -1.0946 | -0.88323 | -1.2772 | 0.78388 | -0.69722 | 2.6006 | 2632.2 | 1150.2 | 0 |
| VOL30 | 2020 | all | 54 | 0.40741 | -37.62 | -2031.5 | -0.41934 | -0.47308 | -0.41506 | -0.42105 | -0.65371 | 0.86111 | -0.33596 | 7.4912 | 6023 | 896.5 | 0 |
| VOL30 | 2021 | all | 77 | 0.44156 | -23.354 | -1798.2 | -0.41488 | -0.43208 | -0.37722 | -0.41644 | -0.6376 | 0.89491 | -0.24252 | 4.4141 | 7414.8 | 1278.2 | 0 |
| VOL30 | 2022 | all | 46 | 0.52174 | 122.64 | 5641.5 | 0.90358 | 0.86669 | 0.89189 | 0.90686 | 1.6553 | 1.371 | 1.1043 | 5.4853 | 5129.2 | 763.5 | 0 |
| VOL30 | 2018-22 | long | 151 | 0.41722 | -48.541 | -7329.8 | -1.2771 | -1.2958 | -1.4449 | -0.57033 | -0.8256 | 0.76072 | -0.17308 | 8.1259 | 8476.5 | 2544.8 | 0 |
| VOL30 | 2018 | long | 25 | 0.44 | -36.65 | -916.25 | -0.58847 | -0.62112 | -0.79264 | -0.59674 | -0.89531 | 0.71993 | -0.55625 | 1.0275 | 1653.8 | 421.25 | 0 |
| VOL30 | 2019 | long | 42 | 0.40476 | -24.393 | -1024.5 | -0.66042 | -0.67954 | -0.84213 | -0.66416 | -0.95297 | 0.79161 | -0.66386 | 1.6524 | 1543.2 | 709.5 | 0 |
| VOL30 | 2020 | long | 21 | 0.38095 | -97.012 | -2037.2 | -0.7527 | -0.71365 | -0.88569 | -0.75845 | -1.0264 | 0.65785 | -0.62274 | 4.3138 | 3258.5 | 357.25 | 0 |
| VOL30 | 2021 | long | 45 | 0.44444 | -38.806 | -1746.2 | -0.60694 | -0.64973 | -0.70379 | -0.61049 | -0.88313 | 0.80546 | -0.43485 | 3.6658 | 4015.8 | 756.25 | 0 |
| VOL30 | 2022 | long | 18 | 0.38889 | -89.194 | -1605.5 | -0.43506 | -0.46627 | -0.49785 | -0.44538 | -0.67172 | 0.78635 | -0.59343 | 3.5832 | 2716.2 | 300.5 | 0 |
| VOL30 | 2018-22 | short | 133 | 0.46617 | 58.314 | 7755.8 | 1.0374 | 1.038 | 1.0602 | 0.46399 | 0.84137 | 1.2632 | 0.2962 | 3.3604 | 5241 | 2169.2 | 0 |
| VOL30 | 2018 | short | 13 | 0.61538 | 105.06 | 1365.8 | 1.0176 | 1.0741 | 1.0735 | 1.0183 | 2.079 | 1.9817 | 1.7936 | 0.46538 | 764.5 | 204.25 | 0 |
| VOL30 | 2019 | short | 27 | 0.33333 | -30.028 | -810.75 | -0.57488 | -0.4971 | -0.62434 | -0.58138 | -0.85035 | 0.77325 | -0.38461 | 2.0075 | 2108 | 440.75 | 0 |
| VOL30 | 2020 | short | 33 | 0.42424 | 0.17424 | 5.75 | 0.0014183 | 0.001726 | 0.001599 | 0.0014346 | 0.0024046 | 1.0007 | 0.001379 | 4.5584 | 4153.2 | 539.25 | 0 |
| VOL30 | 2021 | short | 32 | 0.4375 | -1.625 | -52 | -0.015853 | -0.017242 | -0.015545 | -0.016075 | -0.025857 | 0.99361 | -0.011382 | 2.4538 | 4568.8 | 522 | 0 |
| VOL30 | 2022 | short | 28 | 0.60714 | 258.82 | 7247 | 1.4543 | 1.3166 | 1.5246 | 1.432 | 2.983 | 1.9424 | 2.7363 | 2.7977 | 2659 | 463 | 0 |
| VOL30 | 2018-22 | net_mnq | 284 | 0.44014 | -0.365 | -103.66 | -0.10968 | -0.11074 | -0.1044 | -0.049138 | -0.080237 | 0.98298 | -0.021452 | 0.78988 | 967.2 | 617.66 | 0 |
| VOL30 | 2018-22 | stress_four_ticks | 284 | 0.42606 | -26.546 | -7539 | -0.79331 | -0.80058 | -0.75378 | -0.3551 | -0.55803 | 0.88384 | -0.10426 | 12.577 | 14474 | 12679 | 0 |

## Actual filter and counterfactual controls

Each candidate is an exact executable RP30 subset, with identical entry/side/brackets/exits/costs. Base,
kept and removed totals, removed mean/t and1,000 uniform matched-size subsets:

```json
{
  "CRB005": {
    "non_executable_signal_only": false,
    "base_trades": 284,
    "kept_trades": 44,
    "removed_trades": 240,
    "base_net": -5699.0,
    "kept_net": -7239.0,
    "removed_net": 1540.0,
    "removed_avg": 6.416666666666667,
    "removed_t": 0.18911310328365688,
    "random_subsets": 1000,
    "random_net_mean": -853.175,
    "p_random_net_ge_kept": 0.972,
    "p_kept_better_net_and_dd": 0.013
  },
  "CRB0025": {
    "non_executable_signal_only": false,
    "base_trades": 284,
    "kept_trades": 44,
    "removed_trades": 240,
    "base_net": -5699.0,
    "kept_net": -7239.0,
    "removed_net": 1540.0,
    "removed_avg": 6.416666666666667,
    "removed_t": 0.18911310328365688,
    "random_subsets": 1000,
    "random_net_mean": -853.175,
    "p_random_net_ge_kept": 0.972,
    "p_kept_better_net_and_dd": 0.013
  },
  "CRB010": {
    "non_executable_signal_only": false,
    "base_trades": 284,
    "kept_trades": 33,
    "removed_trades": 251,
    "base_net": -5699.0,
    "kept_net": -5984.25,
    "removed_net": 285.25,
    "removed_avg": 1.1364541832669324,
    "removed_t": 0.03423449240791304,
    "random_subsets": 1000,
    "random_net_mean": -649.925,
    "p_random_net_ge_kept": 0.96,
    "p_kept_better_net_and_dd": 0.004
  }
}
```

The same uniform draws reconcile to the shared helper and are saved in design_uniform_draws.json.
Another1,000 subsets preserve kept count within (year,equity-return sign,equity standardized-magnitude bin,
frozen-correlation-flow sign); bins are[0,1),[1,2),[2,infinity). Full arrays are in design_stratified_drops.json;
cells and summary follow. These are random-drop diagnostics, not selected strategies.

```json
{
  "CRB005": {
    "runs": 1000,
    "informative": true,
    "actual_executable_subsets": true,
    "cells": [
      {
        "year": 2019,
        "equity_sign": -1,
        "equity_magnitude_bin": 0,
        "vol_sign": 1,
        "base": 16,
        "kept": 3
      },
      {
        "year": 2019,
        "equity_sign": 1,
        "equity_magnitude_bin": 0,
        "vol_sign": 1,
        "base": 18,
        "kept": 1
      },
      {
        "year": 2019,
        "equity_sign": 1,
        "equity_magnitude_bin": 1,
        "vol_sign": -1,
        "base": 17,
        "kept": 2
      },
      {
        "year": 2019,
        "equity_sign": 1,
        "equity_magnitude_bin": 1,
        "vol_sign": 1,
        "base": 2,
        "kept": 1
      },
      {
        "year": 2020,
        "equity_sign": -1,
        "equity_magnitude_bin": 0,
        "vol_sign": 1,
        "base": 10,
        "kept": 2
      },
      {
        "year": 2020,
        "equity_sign": -1,
        "equity_magnitude_bin": 1,
        "vol_sign": -1,
        "base": 3,
        "kept": 1
      },
      {
        "year": 2020,
        "equity_sign": -1,
        "equity_magnitude_bin": 1,
        "vol_sign": 1,
        "base": 2,
        "kept": 1
      },
      {
        "year": 2020,
        "equity_sign": -1,
        "equity_magnitude_bin": 2,
        "vol_sign": -1,
        "base": 6,
        "kept": 1
      },
      {
        "year": 2020,
        "equity_sign": 1,
        "equity_magnitude_bin": 0,
        "vol_sign": 1,
        "base": 5,
        "kept": 2
      },
      {
        "year": 2020,
        "equity_sign": 1,
        "equity_magnitude_bin": 1,
        "vol_sign": -1,
        "base": 18,
        "kept": 3
      },
      {
        "year": 2020,
        "equity_sign": 1,
        "equity_magnitude_bin": 2,
        "vol_sign": -1,
        "base": 5,
        "kept": 1
      },
      {
        "year": 2021,
        "equity_sign": -1,
        "equity_magnitude_bin": 0,
        "vol_sign": 1,
        "base": 19,
        "kept": 2
      },
      {
        "year": 2021,
        "equity_sign": -1,
        "equity_magnitude_bin": 1,
        "vol_sign": -1,
        "base": 9,
        "kept": 3
      },
      {
        "year": 2021,
        "equity_sign": -1,
        "equity_magnitude_bin": 1,
        "vol_sign": 1,
        "base": 1,
        "kept": 1
      },
      {
        "year": 2021,
        "equity_sign": 1,
        "equity_magnitude_bin": 0,
        "vol_sign": -1,
        "base": 2,
        "kept": 1
      },
      {
        "year": 2021,
        "equity_sign": 1,
        "equity_magnitude_bin": 0,
        "vol_sign": 1,
        "base": 22,
        "kept": 1
      },
      {
        "year": 2021,
        "equity_sign": 1,
        "equity_magnitude_bin": 1,
        "vol_sign": -1,
        "base": 14,
        "kept": 2
      },
      {
        "year": 2021,
        "equity_sign": 1,
        "equity_magnitude_bin": 1,
        "vol_sign": 1,
        "base": 2,
        "kept": 1
      },
      {
        "year": 2022,
        "equity_sign": -1,
        "equity_magnitude_bin": 0,
        "vol_sign": 1,
        "base": 14,
        "kept": 4
      },
      {
        "year": 2022,
        "equity_sign": -1,
        "equity_magnitude_bin": 1,
        "vol_sign": -1,
        "base": 8,
        "kept": 6
      },
      {
        "year": 2022,
        "equity_sign": 1,
        "equity_magnitude_bin": 0,
        "vol_sign": -1,
        "base": 1,
        "kept": 1
      },
      {
        "year": 2022,
        "equity_sign": 1,
        "equity_magnitude_bin": 0,
        "vol_sign": 1,
        "base": 4,
        "kept": 1
      },
      {
        "year": 2022,
        "equity_sign": 1,
        "equity_magnitude_bin": 1,
        "vol_sign": -1,
        "base": 11,
        "kept": 3
      }
    ],
    "kept_net": -7239.0,
    "kept_dd": 9436.5,
    "random_net_mean": -1992.82,
    "p_random_net_ge_kept": 0.941,
    "p_kept_better_net_and_dd": 0.025
  },
  "CRB0025": {
    "runs": 1000,
    "informative": true,
    "actual_executable_subsets": true,
    "cells": [
      {
        "year": 2019,
        "equity_sign": -1,
        "equity_magnitude_bin": 0,
        "vol_sign": 1,
        "base": 16,
        "kept": 3
      },
      {
        "year": 2019,
        "equity_sign": 1,
        "equity_magnitude_bin": 0,
        "vol_sign": 1,
        "base": 18,
        "kept": 1
      },
      {
        "year": 2019,
        "equity_sign": 1,
        "equity_magnitude_bin": 1,
        "vol_sign": -1,
        "base": 17,
        "kept": 2
      },
      {
        "year": 2019,
        "equity_sign": 1,
        "equity_magnitude_bin": 1,
        "vol_sign": 1,
        "base": 2,
        "kept": 1
      },
      {
        "year": 2020,
        "equity_sign": -1,
        "equity_magnitude_bin": 0,
        "vol_sign": 1,
        "base": 10,
        "kept": 2
      },
      {
        "year": 2020,
        "equity_sign": -1,
        "equity_magnitude_bin": 1,
        "vol_sign": -1,
        "base": 3,
        "kept": 1
      },
      {
        "year": 2020,
        "equity_sign": -1,
        "equity_magnitude_bin": 1,
        "vol_sign": 1,
        "base": 2,
        "kept": 1
      },
      {
        "year": 2020,
        "equity_sign": -1,
        "equity_magnitude_bin": 2,
        "vol_sign": -1,
        "base": 6,
        "kept": 1
      },
      {
        "year": 2020,
        "equity_sign": 1,
        "equity_magnitude_bin": 0,
        "vol_sign": 1,
        "base": 5,
        "kept": 2
      },
      {
        "year": 2020,
        "equity_sign": 1,
        "equity_magnitude_bin": 1,
        "vol_sign": -1,
        "base": 18,
        "kept": 3
      },
      {
        "year": 2020,
        "equity_sign": 1,
        "equity_magnitude_bin": 2,
        "vol_sign": -1,
        "base": 5,
        "kept": 1
      },
      {
        "year": 2021,
        "equity_sign": -1,
        "equity_magnitude_bin": 0,
        "vol_sign": 1,
        "base": 19,
        "kept": 2
      },
      {
        "year": 2021,
        "equity_sign": -1,
        "equity_magnitude_bin": 1,
        "vol_sign": -1,
        "base": 9,
        "kept": 3
      },
      {
        "year": 2021,
        "equity_sign": -1,
        "equity_magnitude_bin": 1,
        "vol_sign": 1,
        "base": 1,
        "kept": 1
      },
      {
        "year": 2021,
        "equity_sign": 1,
        "equity_magnitude_bin": 0,
        "vol_sign": -1,
        "base": 2,
        "kept": 1
      },
      {
        "year": 2021,
        "equity_sign": 1,
        "equity_magnitude_bin": 0,
        "vol_sign": 1,
        "base": 22,
        "kept": 1
      },
      {
        "year": 2021,
        "equity_sign": 1,
        "equity_magnitude_bin": 1,
        "vol_sign": -1,
        "base": 14,
        "kept": 2
      },
      {
        "year": 2021,
        "equity_sign": 1,
        "equity_magnitude_bin": 1,
        "vol_sign": 1,
        "base": 2,
        "kept": 1
      },
      {
        "year": 2022,
        "equity_sign": -1,
        "equity_magnitude_bin": 0,
        "vol_sign": 1,
        "base": 14,
        "kept": 4
      },
      {
        "year": 2022,
        "equity_sign": -1,
        "equity_magnitude_bin": 1,
        "vol_sign": -1,
        "base": 8,
        "kept": 6
      },
      {
        "year": 2022,
        "equity_sign": 1,
        "equity_magnitude_bin": 0,
        "vol_sign": -1,
        "base": 1,
        "kept": 1
      },
      {
        "year": 2022,
        "equity_sign": 1,
        "equity_magnitude_bin": 0,
        "vol_sign": 1,
        "base": 4,
        "kept": 1
      },
      {
        "year": 2022,
        "equity_sign": 1,
        "equity_magnitude_bin": 1,
        "vol_sign": -1,
        "base": 11,
        "kept": 3
      }
    ],
    "kept_net": -7239.0,
    "kept_dd": 9436.5,
    "random_net_mean": -1992.82,
    "p_random_net_ge_kept": 0.941,
    "p_kept_better_net_and_dd": 0.025
  },
  "CRB010": {
    "runs": 1000,
    "informative": true,
    "actual_executable_subsets": true,
    "cells": [
      {
        "year": 2019,
        "equity_sign": -1,
        "equity_magnitude_bin": 0,
        "vol_sign": 1,
        "base": 16,
        "kept": 1
      },
      {
        "year": 2019,
        "equity_sign": 1,
        "equity_magnitude_bin": 0,
        "vol_sign": 1,
        "base": 18,
        "kept": 1
      },
      {
        "year": 2019,
        "equity_sign": 1,
        "equity_magnitude_bin": 1,
        "vol_sign": -1,
        "base": 17,
        "kept": 2
      },
      {
        "year": 2019,
        "equity_sign": 1,
        "equity_magnitude_bin": 1,
        "vol_sign": 1,
        "base": 2,
        "kept": 1
      },
      {
        "year": 2020,
        "equity_sign": -1,
        "equity_magnitude_bin": 0,
        "vol_sign": 1,
        "base": 10,
        "kept": 1
      },
      {
        "year": 2020,
        "equity_sign": -1,
        "equity_magnitude_bin": 1,
        "vol_sign": -1,
        "base": 3,
        "kept": 1
      },
      {
        "year": 2020,
        "equity_sign": -1,
        "equity_magnitude_bin": 1,
        "vol_sign": 1,
        "base": 2,
        "kept": 1
      },
      {
        "year": 2020,
        "equity_sign": -1,
        "equity_magnitude_bin": 2,
        "vol_sign": -1,
        "base": 6,
        "kept": 1
      },
      {
        "year": 2020,
        "equity_sign": 1,
        "equity_magnitude_bin": 0,
        "vol_sign": 1,
        "base": 5,
        "kept": 2
      },
      {
        "year": 2020,
        "equity_sign": 1,
        "equity_magnitude_bin": 1,
        "vol_sign": -1,
        "base": 18,
        "kept": 3
      },
      {
        "year": 2020,
        "equity_sign": 1,
        "equity_magnitude_bin": 2,
        "vol_sign": -1,
        "base": 5,
        "kept": 1
      },
      {
        "year": 2021,
        "equity_sign": -1,
        "equity_magnitude_bin": 0,
        "vol_sign": 1,
        "base": 19,
        "kept": 1
      },
      {
        "year": 2021,
        "equity_sign": -1,
        "equity_magnitude_bin": 1,
        "vol_sign": -1,
        "base": 9,
        "kept": 3
      },
      {
        "year": 2021,
        "equity_sign": -1,
        "equity_magnitude_bin": 1,
        "vol_sign": 1,
        "base": 1,
        "kept": 1
      },
      {
        "year": 2021,
        "equity_sign": 1,
        "equity_magnitude_bin": 0,
        "vol_sign": -1,
        "base": 2,
        "kept": 1
      },
      {
        "year": 2021,
        "equity_sign": 1,
        "equity_magnitude_bin": 1,
        "vol_sign": -1,
        "base": 14,
        "kept": 1
      },
      {
        "year": 2021,
        "equity_sign": 1,
        "equity_magnitude_bin": 1,
        "vol_sign": 1,
        "base": 2,
        "kept": 1
      },
      {
        "year": 2022,
        "equity_sign": -1,
        "equity_magnitude_bin": 0,
        "vol_sign": 1,
        "base": 14,
        "kept": 2
      },
      {
        "year": 2022,
        "equity_sign": -1,
        "equity_magnitude_bin": 1,
        "vol_sign": -1,
        "base": 8,
        "kept": 4
      },
      {
        "year": 2022,
        "equity_sign": 1,
        "equity_magnitude_bin": 0,
        "vol_sign": -1,
        "base": 1,
        "kept": 1
      },
      {
        "year": 2022,
        "equity_sign": 1,
        "equity_magnitude_bin": 0,
        "vol_sign": 1,
        "base": 4,
        "kept": 1
      },
      {
        "year": 2022,
        "equity_sign": 1,
        "equity_magnitude_bin": 1,
        "vol_sign": -1,
        "base": 11,
        "kept": 2
      }
    ],
    "kept_net": -5984.25,
    "kept_dd": 8789.5,
    "random_net_mean": -1720.535,
    "p_random_net_ge_kept": 0.904,
    "p_kept_better_net_and_dd": 0.015
  }
}
```

VOL30 on the identical candidate dates uses the same contract count, bracket distances, time limit and cost
MODEL, with a possibly different side. Actual exits/fill costs can differ. This is a matched whole-rule
counterfactual, not a removed-trade ledger. Candidate results are worse than their matched counterfactual:

```json
{
  "CRB005": {
    "candidate_tickets": 44,
    "matched_counterfactual_tickets": 44,
    "candidate_net": -7239.0,
    "counterfactual_net": -1114.0,
    "same_side_fraction": 0.6590909090909091,
    "side_changing_whole_rule_comparison": true
  },
  "CRB0025": {
    "candidate_tickets": 44,
    "matched_counterfactual_tickets": 44,
    "candidate_net": -7239.0,
    "counterfactual_net": -1114.0,
    "same_side_fraction": 0.6590909090909091,
    "side_changing_whole_rule_comparison": true
  },
  "CRB010": {
    "candidate_tickets": 33,
    "matched_counterfactual_tickets": 33,
    "candidate_net": -5984.25,
    "counterfactual_net": 140.75,
    "same_side_fraction": 0.5454545454545454,
    "side_changing_whole_rule_comparison": true
  }
}
```

No candidate passed the >=100/positive-net/t>=2/NW5>=1.5/PF>=1.20/four-positive-year/native-micro/stress
gate, let alone the total-profit/random-drop and matched-counterfactual gates. The near-zero VOL30 result,
or positive side/year subsets, cannot be nominated after seeing returns. Complete frozen gates:

```json
{
  "prereg": "5678dde",
  "gates": {
    "CRB005": {
      "count": false,
      "net": false,
      "t": false,
      "nw5": false,
      "pf": false,
      "years": false,
      "micro": false,
      "stress": false,
      "removed_loses": false,
      "kept_total_ge_base": false,
      "uniform_net": false,
      "uniform_joint": false,
      "stratified_net": false,
      "stratified_joint": false,
      "matched_frozen_correlation": false
    },
    "CRB0025": {
      "count": false,
      "net": false,
      "t": false,
      "nw5": false,
      "pf": false,
      "years": false,
      "micro": false,
      "stress": false,
      "removed_loses": false,
      "kept_total_ge_base": false,
      "uniform_net": false,
      "uniform_joint": false,
      "stratified_net": false,
      "stratified_joint": false,
      "matched_frozen_correlation": false
    },
    "CRB010": {
      "count": false,
      "net": false,
      "t": false,
      "nw5": false,
      "pf": false,
      "years": false,
      "micro": false,
      "stress": false,
      "removed_loses": false,
      "kept_total_ge_base": false,
      "uniform_net": false,
      "uniform_joint": false,
      "stratified_net": false,
      "stratified_joint": false,
      "matched_frozen_correlation": false
    }
  },
  "passing": [],
  "selected": null,
  "counted_program_evaluations": 60,
  "unique_program_models": 59,
  "exact_actual_subset_controls": true,
  "program_continues": true
}
```

## Trial accounting correction

The lower threshold was redundant at preregistration: |F|>=0.01 and |K|>=0.5|F| already require |K|>=0.005.
CRB0025 and CRB005 are algebraically the same rule. I should have caught this before execution. Their saved
signal and ticket ledgers reconcile exactly. All five evaluations remain counted; the actual new unique count
is four. Original preregistration and gate's projected59-unique field are preserved, not silently rewritten.
The authoritative correction is design_trial_count_audit.json and progress now records60evaluations/58unique.
Selection/multiple-testing lower bounds continue to use all60 evaluations, not the smaller unique count.

```json
{
  "id": "crb_0025_equivalent_005",
  "prereg": "5678dde",
  "prior_evaluations": 55,
  "prior_unique": 54,
  "new_evaluations": 5,
  "new_unique": 4,
  "cumulative_evaluations": 60,
  "corrected_cumulative_unique": 58,
  "original_prereg_and_gate_projected_unique": 59,
  "reason": "abs(F)>=0.01 and abs(K)>=0.5*abs(F) already imply abs(K)>=0.005; the 0.0025 threshold is algebraically redundant with 0.005, not merely empirically equal.",
  "all_failed_evaluations_retained": true,
  "original_artifacts_unchanged": true
}
```

## Data, clocks, remaining limitations and decision

```json
{
  "price_intake": {
    "NQ": {
      "symbol": "NQ",
      "rows": 1769357,
      "exact_duplicates": 0,
      "conflicting_keys": 0,
      "first": 20171201,
      "last": 20221230,
      "clock": "native CT minute close labels"
    },
    "ES": {
      "symbol": "ES",
      "rows": 2096132,
      "exact_duplicates": 0,
      "conflicting_keys": 0,
      "first": 20170102,
      "last": 20221230,
      "clock": "native CT minute close labels"
    },
    "ZN": {
      "symbol": "ZN",
      "rows": 1681117,
      "exact_duplicates": 0,
      "conflicting_keys": 0,
      "first": 20171201,
      "last": 20221230,
      "clock": "native CT minute close labels"
    }
  },
  "reference_exclusions": {
    "eligible_return": 912,
    "predeclared_roll_endpoint": 402,
    "missing_exact_market_date": 165,
    "non_normal_endpoint": 24,
    "fixed_input_jump_guard": 6,
    "no_previous_cash_date": 1
  },
  "first_design_date_with_60_prior_observations": "2018-04-04",
  "event_and_execution_counts": {
    "CRB005": {
      "input": {
        "shared_full_flow_or_zero_counterfactual_gate": 502,
        "predeclared_roll_endpoint": 335,
        "covariance_attribution_or_magnitude_gate": 240,
        "incomplete_known_30min_window": 67,
        "prior_covariance_warmup": 46,
        "signal": 44,
        "non_normal_endpoint": 20,
        "invalid_model_or_fixed_partial_jump_guard": 5
      },
      "execution": {
        "suppressed_invested_or_same_close": 0,
        "suppressed_daily_cap": 0,
        "missing_scheduled_entry": 0
      },
      "signals": 44,
      "executed": 44
    },
    "CRB0025": {
      "input": {
        "shared_full_flow_or_zero_counterfactual_gate": 502,
        "predeclared_roll_endpoint": 335,
        "covariance_attribution_or_magnitude_gate": 240,
        "incomplete_known_30min_window": 67,
        "prior_covariance_warmup": 46,
        "signal": 44,
        "non_normal_endpoint": 20,
        "invalid_model_or_fixed_partial_jump_guard": 5
      },
      "execution": {
        "suppressed_invested_or_same_close": 0,
        "suppressed_daily_cap": 0,
        "missing_scheduled_entry": 0
      },
      "signals": 44,
      "executed": 44
    },
    "CRB010": {
      "input": {
        "shared_full_flow_or_zero_counterfactual_gate": 502,
        "predeclared_roll_endpoint": 335,
        "covariance_attribution_or_magnitude_gate": 251,
        "incomplete_known_30min_window": 67,
        "prior_covariance_warmup": 46,
        "signal": 33,
        "non_normal_endpoint": 20,
        "invalid_model_or_fixed_partial_jump_guard": 5
      },
      "execution": {
        "suppressed_invested_or_same_close": 0,
        "suppressed_daily_cap": 0,
        "missing_scheduled_entry": 0
      },
      "signals": 33,
      "executed": 33
    },
    "RP30": {
      "input": {
        "shared_full_flow_or_zero_counterfactual_gate": 502,
        "predeclared_roll_endpoint": 335,
        "signal": 284,
        "incomplete_known_30min_window": 67,
        "prior_covariance_warmup": 46,
        "non_normal_endpoint": 20,
        "invalid_model_or_fixed_partial_jump_guard": 5
      },
      "execution": {
        "suppressed_invested_or_same_close": 0,
        "suppressed_daily_cap": 0,
        "missing_scheduled_entry": 0
      },
      "signals": 284,
      "executed": 284
    },
    "VOL30": {
      "input": {
        "shared_full_flow_or_zero_counterfactual_gate": 502,
        "predeclared_roll_endpoint": 335,
        "signal": 284,
        "incomplete_known_30min_window": 67,
        "prior_covariance_warmup": 46,
        "non_normal_endpoint": 20,
        "invalid_model_or_fixed_partial_jump_guard": 5
      },
      "execution": {
        "suppressed_invested_or_same_close": 0,
        "suppressed_daily_cap": 0,
        "missing_scheduled_entry": 0
      },
      "signals": 284,
      "executed": 284
    }
  }
}
```

Daily reference audit retains every cash date from2017, including missing/roll/jump exclusions. All design
cash dates have per-model event reasons; raw hashes and all signal features are saved. No conflicting or exact
duplicate native keys, missing scheduled entries, invested/cap suppression or held gaps occurred in the saved
ledgers (0 held-gap tickets). Synthetic and pre-return code reviews found no blocking spec mismatch;
they had maker context and are not an independent raw-spec promotion verdict.

The model is not a replication of ECB's European four-asset analysis. NQ transmission, current fund AUM,
calibration and14:30execution timing remain unverified. Covariance can become stale through guarded/missing
intervals. Input jump guards and calendar buffers do not prove original-contract continuity or receipt latency.
There are too few candidate events and negative net evidence, including both primary sides. Do not weaken
guards or magnitude/attribution thresholds to rescue this family.

No2023+historical validation, post-pass random-side/time placebos, expensive resampling/MC, independent
promotion, account tests or PowerLanguage followed rejection. No invented account pass/payout improvement.
Continue a DISTINCT mechanism. This failure emits no milestone, crosses no4.5/5/6 threshold and does not
pause the research continuation or change the read-only watcher.
Actual raw-data execution: 2026-10-26T05:34:23.401961+00:00 to 2026-10-26T05:34:52.874109+00:00.
Claude review path: agents/codex/results/correlation_risk_budget.md.
