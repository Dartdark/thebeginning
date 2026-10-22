# Claude's evidence sheets (written 2026-10-22 before reading Codex's, no backtests; committed after Codex pushed 134e175)

| Rank | Idea | Verdict | One line |
|---|---|---|---|
| 1 | LDF sized by leveraged-ETF dollar flow (AUM) | NEEDS DATA (free/cheap) → TEST | Forced, sized and timed in advance, lands in NQ; AUM varies independently of the move; settles whether LDF's edge is really the LETF flow (Ivanov & Lenkey say it shouldn't be) |
| 2 | Real NYSE auction imbalances (ES close, then open) | NEEDS DATA (paid quote) | The order itself instead of a price proxy; upgrades ES MOC; the 08:00-09:00 CT Tue-Thu window is ~99% empty |
| 3 | Option-expiration-week long (Stivers & Sun) | DON'T TEST | Published and calendar-defined, but needs ~0.19%/day to pass; stacks on existing day positions |
| 4 | CME margin-hike deleveraging | DON'T TEST | Size unknowable, confounded with volatility, ~30-50 events |

Main conclusion: the cheap forced-flow ideas that our current data can test are mostly in TIER_LIST already. The next
edges probably need new flow data (fund AUM, exchange imbalances). Data before rules.
