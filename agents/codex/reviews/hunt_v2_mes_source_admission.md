# H09 independent SOURCE review: reject before gross

**SOURCE/support FAIL is confirmed. Raw screen is not authorized.** The frozen parent and quantity support is sufficient for the preregistered count gates, but the normal cash-session date **2020-11-30 has neither reference C1400 nor decision C1450 source bars**. Eligibility on that date is unknown. The preregistered whole-family source veto applies; do not delete the date, infer a nonsignal, repair prices, change the calendar or proceed to gross/stop/account returns.

Preregistration `1a8087f7358901e08fa7e284ded7a6913b58568b`; actual SOURCE implementation `2c2391039dc774dfc4cb9511e63920c229a8e6c8`. Source ran 2026-10-27T02:10:01.015192Z–02:10:52.155366Z. Review authorization is recorded in [hunt_v2_mes_source_admission.json](hunt_v2_mes_source_admission.json), explicitly `passed:false` and `raw_screen_authorized:false`.

| Bound evidence | SHA256 |
|---|---|
| `source_verified_execution.json` | `65664717db0542fbad4bc19abdf226507293e814ae88cd0a87dd23ccdf9d307c` |
| `source_gate.json` | `42d02d746d72f202dc8e96e1966ffe992d815e155600dca7a10ce893d085c9f7` |

All 15 artifact hashes and all seven code/dependency hashes in the SOURCE marker match. This independent review recomputed counts from saved pre-entry features and exact combinatorial mask support; it did not rerun the full native-data audit or reconstruct the signal from price rows.

| Design year | Parent events | Affordable EXTRA events |
|---|---:|---:|
| 2018 | 37 | 37 |
| 2019 | 17 | 17 |
| 2020 | 28 | 25 |
| 2021 | 19 | 19 |
| 2022 | 30 | 20 |
| Total | 131 | 118 |

The parent has 57 longs/74 shorts; EXTRA has 49 longs/69 shorts. All 131 have known affordability. Saved event IDs reconcile to the exact sequence 0..130. The fixed year/side/move-bin cells contain **77,051,520 distinct matched quantity masks and four variable cells**, independently recomputed using the product of exact binomial coefficients. All 131 saved held-path presence checks pass. These support facts do not override the missing normal-date decision or establish any financial edge.

For the one newly identified failure, the reviewer independently selected **only `date,time` columns** from the already bound `data/ES_1min_2020.csv`. The target date has 359 clock records, from HHMM1801 to2359. None of the ten required native minute keys j836..840 or j886..890 exists. No OHLCV column was selected or interpreted, and no range, ATR, signal, endpoint subtraction, stop, fee, null-return path or financial metric was recomputed. This is a focused metadata adjudication of new failure evidence, not an unchanged full audit retry.

The gate also emits `EXPECTED_NORMAL_PRIOR_15_CHART_TR_ATR_NOT_READY_POSITIVE` when the decision record is absent. Interpret this as **unavailable decision record** here; it is not independent proof that the preceding ATR history was unready.

The observed-chart/calendar port, source receipt/roll identity, micro prelisting price-proxy history and MES liquidity remain limitations. No MC parity, complete-feed certification, book gain or promotion follows. The prospective `analysis/codex_hunt_v2_mes_moc_gross.py` adapter was authored from source and invented fixtures, then stopped when SOURCE failed; **its actual gross path was NOT RUN** and must not be completed or used to bypass this rejection.

Running hunt counts at closure: **5/60 economic evaluations, 9/10 registered hypotheses, 4 gross screens**, plus archived65 t6 evaluations. This review adds zero to each. H09 stops; the bounded v2 program may continue within its remaining budget.

## Reproduce count/integrity adjudication without prices

From repository root, run the following with the project Python `-B`. It reads only saved SOURCE artifacts and code bytes. The separate focused clock check is `pandas.read_csv('data/ES_1min_2020.csv', usecols=['date','time'], dtype={'date':str,'time':str})`, filtered to date `20201130`; convert HHMM to `60*(HHMM//100)+HHMM%100` and compare only j836..840/j886..890. Do not select OHLCV fields.

```python
from pathlib import Path
from collections import Counter, defaultdict
from math import comb
import json, hashlib
root = Path.cwd()
out = root/'analysis/outputs/codex_hunt_v2_mes_affordability'
sha = lambda path: hashlib.sha256(Path(path).read_bytes()).hexdigest()
marker = json.loads((out/'source_verified_execution.json').read_text())
assert all(sha(out/name) == expected for name,expected in marker['artifacts_sha256'].items())
assert all(sha(root/name) == expected for name,expected in marker['code_sha256'].items())
features = json.loads((out/'source_parent_features.json').read_text())
assert all(row['event_id'] == i for i,row in enumerate(features))
assert len(features) == 131
assert sum(row['qty_extra'] for row in features) == 118
assert Counter(row['year'] for row in features) == {2018:37,2019:17,2020:28,2021:19,2022:30}
assert Counter(row['year'] for row in features if row['qty_extra']) == {2018:37,2019:17,2020:25,2021:19,2022:20}
assert Counter(row['side'] for row in features) == {1:57,-1:74}
assert Counter(row['side'] for row in features if row['qty_extra']) == {1:49,-1:69}
assert sum(row['source_known'] for row in features) == 131
cells = defaultdict(list)
for row in features:
    cells[tuple(row['stratum'])].append(row)
product, variable = 1, 0
for rows in cells.values():
    known = [row for row in rows if row['source_known']]
    n,k = len(known),sum(row['qty_extra'] for row in known)
    product *= comb(n,k)
    variable += int(0 < k < n)
assert product == 77051520 and variable == 4
held = json.loads((out/'source_held_path_audit.json').read_text())
assert len(held) == 131 and all(row['passed'] for row in held)
expected = json.loads((out/'source_expected_dates.json').read_text())
assert [row['date'] for row in expected if not row['passed']] == ['2020-11-30']
assert marker['passed'] is False
```
