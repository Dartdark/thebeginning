# Leak-check sweep of the plan strategies (MultiCharts trade lists)

`python3 analysis/leak_checks.py --sweep`; L1 fill sanity / L2 one-bar delay as defined in `analysis/leak_checks.py`. Costs: repo standard per round trip; delay keeps the same exit.

### Vault Break (SP) (NQ, 30-min chart, 1756 trades 2018+)
- L1 fill sanity: 100.0% of 3512 fills inside their bar (+/- 2 ticks), clock offset +0 min -> **PASS**
- L2 one-bar delay: 1184 trades; net $32 (t 1.2) -> $61 (t 2.7); Sharpe kept 213% -> **BEND**

### Swing Target v3 (NQ, 1-min chart, 598 trades 2018+)
- L1 fill sanity: 100.0% of 1196 fills inside their bar (+/- 2 ticks), clock offset +0 min -> **PASS**
- L2 one-bar delay: 594 trades; net $312 (t 4.6) -> $292 (t 4.3); Sharpe kept 93% -> **BEND**

### Overnight Bias ML v2 (funded) (NQ, 15-min chart, 343 trades 2018+)
- L1 fill sanity: 100.0% of 686 fills inside their bar (+/- 2 ticks), clock offset +0 min -> **PASS**
- L2 one-bar delay: 337 trades; net $678 (t 5.3) -> $608 (t 5.2); Sharpe kept 97% -> **BEND**

### Overnight Bias v2 (combine, ADX30) (NQ, 15-min chart, 411 trades 2018+)
- L1 fill sanity: 100.0% of 822 fills inside their bar (+/- 2 ticks), clock offset +0 min -> **PASS**
- L2 one-bar delay: 405 trades; net $581 (t 5.1) -> $532 (t 5.0); Sharpe kept 98% -> **BEND**

### Overnight Tick / VIX (NQ, 5-min chart, 562 trades 2018+)
- L1 fill sanity: 100.0% of 1124 fills inside their bar (+/- 2 ticks), clock offset +0 min -> **PASS**
- L2 one-bar delay: 562 trades; net $346 (t 4.6) -> $340 (t 4.5); Sharpe kept 99% -> **BEND**

### Expiration Open Short (NQ, 5-min chart, 105 trades 2018+)
- L1 fill sanity: 100.0% of 210 fills inside their bar (+/- 2 ticks), clock offset +0 min -> **PASS**
- L2 one-bar delay: 105 trades; net $474 (t 2.6) -> $309 (t 1.8); Sharpe kept 71% -> **BEND**

### Late-Day Flow (NQ, 5-min chart, 896 trades 2018+)
- L1 fill sanity: 100.0% of 1792 fills inside their bar (+/- 2 ticks), clock offset +0 min -> **PASS**
- L2 one-bar delay: 892 trades; net $100 (t 3.7) -> $60 (t 2.6); Sharpe kept 70% -> **BEND**

### NFP Fade (NQ, 5-min chart, 79 trades 2018+)
- L1 fill sanity: 100.0% of 158 fills inside their bar (+/- 2 ticks), clock offset +0 min -> **PASS**
- L2 one-bar delay: 79 trades; net $335 (t 1.9) -> $355 (t 2.0); Sharpe kept 108% -> **BEND**

### Bridge Monday Long (NQ, 5-min chart, 217 trades 2018+)
- L1 fill sanity: 100.0% of 434 fills inside their bar (+/- 2 ticks), clock offset +0 min -> **PASS**
- L2 one-bar delay: 217 trades; net $539 (t 4.3) -> $538 (t 4.3); Sharpe kept 100% -> **BEND**

### Monday Long (NQ, 5-min chart, 451 trades 2018+)
- L1 fill sanity: 100.0% of 902 fills inside their bar (+/- 2 ticks), clock offset +0 min -> **PASS**
- L2 one-bar delay: 451 trades; net $418 (t 3.3) -> $361 (t 3.1); Sharpe kept 93% -> **BEND**

### T_ONESIDE v2 (NQ, 1-min chart, 359 trades 2018+)
- L1 fill sanity: 100.0% of 718 fills inside their bar (+/- 2 ticks), clock offset +0 min -> **PASS**
- L2 one-bar delay: 357 trades; net $248 (t 3.7) -> $228 (t 3.4); Sharpe kept 92% -> **BEND**

### Relative Strength (NQ, 1-min chart, 1174 trades 2018+)
- L1 fill sanity: 100.0% of 2348 fills inside their bar (+/- 2 ticks), clock offset +0 min -> **PASS**
- L2 one-bar delay: 1173 trades; net $297 (t 3.9) -> $266 (t 3.5); Sharpe kept 91% -> **BEND**

### Dual Thrust v4 (NQ, 1-min chart, 1616 trades 2018+)
- L1 fill sanity: 100.0% of 3232 fills inside their bar (+/- 2 ticks), clock offset +0 min -> **PASS**
- L2 one-bar delay: 1591 trades; net $151 (t 4.7) -> $136 (t 4.2); Sharpe kept 90% -> **BEND**

### ES MOC follow (ES, 5-min chart, 199 trades 2018+)
- L1 fill sanity: 100.0% of 398 fills inside their bar (+/- 2 ticks), clock offset +0 min -> **PASS**
- L2 one-bar delay: 189 trades; net $214 (t 4.9) -> $100 (t 3.6); Sharpe kept 72% -> **BEND**

### CL Sunday gap fade (CL, 5-min chart, 97 trades 2018+)
- L1 fill sanity: 100.0% of 194 fills inside their bar (+/- 2 ticks), clock offset -60 min -> **PASS**
- L2 one-bar delay: 96 trades; net $688 (t 3.4) -> $699 (t 3.6); Sharpe kept 105% -> **BEND**

## Summary

| Strategy | L1 fills in bar | clock | L2 net -> delayed | t -> t | Sharpe kept | Verdict |
|---|---|---|---|---|---|---|
| Vault Break (SP) | 100.0% | +0 min | $32 -> $61 | 1.2 -> 2.7 | 213% | PASS / BEND |
| Swing Target v3 | 100.0% | +0 min | $312 -> $292 | 4.6 -> 4.3 | 93% | PASS / BEND |
| Overnight Bias ML v2 (funded) | 100.0% | +0 min | $678 -> $608 | 5.3 -> 5.2 | 97% | PASS / BEND |
| Overnight Bias v2 (combine, ADX30) | 100.0% | +0 min | $581 -> $532 | 5.1 -> 5.0 | 98% | PASS / BEND |
| Overnight Tick / VIX | 100.0% | +0 min | $346 -> $340 | 4.6 -> 4.5 | 99% | PASS / BEND |
| Expiration Open Short | 100.0% | +0 min | $474 -> $309 | 2.6 -> 1.8 | 71% | PASS / BEND |
| Late-Day Flow | 100.0% | +0 min | $100 -> $60 | 3.7 -> 2.6 | 70% | PASS / BEND |
| NFP Fade | 100.0% | +0 min | $335 -> $355 | 1.9 -> 2.0 | 108% | PASS / BEND |
| Bridge Monday Long | 100.0% | +0 min | $539 -> $538 | 4.3 -> 4.3 | 100% | PASS / BEND |
| Monday Long | 100.0% | +0 min | $418 -> $361 | 3.3 -> 3.1 | 93% | PASS / BEND |
| T_ONESIDE v2 | 100.0% | +0 min | $248 -> $228 | 3.7 -> 3.4 | 92% | PASS / BEND |
| Relative Strength | 100.0% | +0 min | $297 -> $266 | 3.9 -> 3.5 | 91% | PASS / BEND |
| Dual Thrust v4 | 100.0% | +0 min | $151 -> $136 | 4.7 -> 4.2 | 90% | PASS / BEND |
| ES MOC follow | 100.0% | +0 min | $214 -> $100 | 4.9 -> 3.6 | 72% | PASS / BEND |
| CL Sunday gap fade | 100.0% | -60 min | $688 -> $699 | 3.4 -> 3.6 | 105% | PASS / BEND |
