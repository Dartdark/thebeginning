# Code-reading cheat sheet (phrases, not words)

Learn each line as one phrase. Add a line every time you learn a new one.

## Tables and columns
| Code | Plain English |
|---|---|
| `d` | the daily table (one row per day) |
| `x` | one day's minute bars |
| `d.close` | each day's close (the column) |
| `d["sig"] = ...` | make a new column called `sig` |
| `d[d.side != 0]` | only the rows where `side` isn't 0 |
| `x[x.hhmm < 1000]` | only the bars before 10:00 |
| `.iloc[0]` | the first row |

## Time (the look-ahead phrases)
| Code | Plain English | Safe at today's open? |
|---|---|---|
| `.shift(1)` | yesterday's value, on today's row | yes |
| `.shift(-1)` | **tomorrow's** value, on today's row | **never** in a signal |
| `.rolling(14).mean()` | average of the last 14 days **including today** | no |
| `.rolling(14).mean().shift(1)` | average of the 14 days **through yesterday** | yes |
| `.expanding().mean()` | average of all days up to and **including today** | no |
| `.expanding().mean().shift(1)` | average of all days **through yesterday** | yes |
| `.rolling(20).max()` | highest of the last 20 days **including today** | no |
| `.mean()`, `.max()`, `.std()` on the whole column | over **the whole table** (all years, future included) | **no** |
| `groupby(year)` then rank / mean | within **the whole year**, future days included | **no** |
| `d.close`, `d.high`, `d.low`, `d.volume` (today) | final only at the **end of today** | no (fine for tomorrow's trade) |
| `x[x.hhmm < 1000].high.max()` | highest high before 10:00 | yes, for a 10:00 decision |

## Logic
| Code | Plain English |
|---|---|
| `>`, `<`, `==`, `!=` | bigger, smaller, equal, not equal |
| `&`, `\|` | and, or (for whole columns) |
| `np.where(cond, a, b)` | where cond is true use a, else b |
| `if A: ... else: ...` | if A, do this, otherwise that |
| `for r in rows:` | for each row, one at a time |
| `def name(inputs):` | a function: a named set of steps; runs when called |
| `return t` | what the function hands back |

## Reviewer's 4 steps for time travel
1. When is the trade? 2. Which numbers does the decision use? 3. For each: which rows go in, and when is the last one
final? 4. Any of them final after the trade means look-ahead.
