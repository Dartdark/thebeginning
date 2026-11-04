# CME equity-index closure audit — 2026-11-04

Summary (timestamp/source audit only; no returns tested):
The 15:15–15:30 Chicago pause existed before, and was removed for trade date **2021-06-28**.
For this repository's close-labeled minute bars, **15:16–15:30** are scheduled nontrading labels only before that date.
The first inspected Bridge ticket has 17 missing labels: 15 scheduled pause labels and **two unresolved open-market holes**.
The ordinary daily maintenance closure is 16:00–17:00 Chicago; holiday exceptions have not been fully enumerated here.

## Authoritative schedule and effective dates

| Era | Equity-index outright schedule, Chicago local time | Evidence |
|---|---|---|
| Research history 2018-01-01 through 2021-06-27 | Sunday evening through Friday: 17:00 open, 16:00 close; separate 15:15–15:30 pause on business afternoons | CME's 2012 notice established the pause; its 2015 notice moved the daily close to 16:00. The 2019 micro launch advisory explicitly combines these hours. CME's 2021 certification removes the then-existing pause. |
| Trade date 2021-06-28 onward through currently published 2026 hours | 17:00–16:00, with 16:00–17:00 maintenance and **no ordinary 15:15 pause** | CME certification 21-244R and operational notice 20210621; current CME NQ/ES product highlights corroborate. |

These are normal schedules, not an exhaustive dated holiday or unscheduled-halt calendar. The Sunday 2021-06-27 reopening belongs to Monday June 28's trade date. The affected-contract exhibit explicitly includes **ES, MES, NQ and MNQ**; the operational notice excludes the old $250 S&P contract and BTIC/TACO. Do not extend the conclusion to every contract or price series.

Primary receipts, accessed through connected public search/open on 2026-11-04 around 22:35–22:46 UTC:

1. [CME certification 21-244R, filed 2021-06-11](https://www.cmegroup.com/market-regulation/rule-filings/2021/6/21-244R_1.pdf), PDF pp. 2 and 4 (zero-based pp. 1, 3). The effective date is June 27 for June 28 trade date; the removed interval is 15:15–15:30CT. ExhibitA lists the four contracts. Connected extraction `turn287490view1`, lines 60–73,117,139,146,150. PDF bytes were not saved or hashed; this is a connected extraction receipt.
2. [CME Globex notice 20210621](https://www.cmegroup.com/notices/electronic-trading/2021/06/20210621.html), section “Elimination of CME Equity Futures and Options Market Pause,” extracted lines 232–239 (`turn798682view0`). The page title says June 21; the visible Notice Date is June 24. Its final operational statement confirms removal and the continuing 16:00–17:00 maintenance interval.
3. [CME clearing advisory19-118](https://www.cmegroup.com/content/dam/cmegroup/notices/clearing/2019/04/Chadv19-118.pdf), p.1 lines 1–22 (`turn287490view2`). Trade-dateMay 6, 2019 micro launch; explicit old pause and 60-minute 16:00 break. It also establishes that nativeMES/MNQ did not exist throughout 2018; mini-to-micro historical scaling needs its existing disclosure.
4. [CME September 7, 2015 Globex notice](https://www.cmegroup.com/tools-information/lookups/advisories/electronic-trading/20150907.html), “Changes to Daily Maintenance Period for CME Globex” (`turn772076search0`, `turn803718view0`). Close moved from 16:15 to 16:00 effective September 21, 2015; normal openings continued. The system maintenance interval stated there ends 16:45, which must not be mistaken for an equity futures matching reopen; the relevant product's reopen is 17:00.
5. [CME advisory12-423](https://www.cmegroup.com/tools-information/lookups/advisories/clearing/Chadv12-423.html) / [SER 6465](https://www.cmegroup.com/rulebook/files/ser-6465_Equity_Index_Futures_Options_on_Equity_Index_Futures_20121114.pdf): pause and later-close regime effective November 19, 2012 (`turn654504search0`, `turn654504search14`). The old16:15 close is superseded by receipt4 for all 2018–26 research dates.
6. Current [NQ product highlights](https://www.cmegroup.com/markets/equities/nasdaq/e-mini-nasdaq-100.timeAndSales.html?videoId=6396076863112), [ES product highlights](https://www.cmegroup.com/markets/equities/sp/e-mini-sandp500.performance.html), and [CME equity futures hours FAQ](https://www.cmegroup.com/markets/equities/sp-500-and-nasdaq-100-futures.html), connected search receipts `turn764115search0–2`. These report17:00–16:00CT with 16:00–17:00 maintenance. Search metadata is corroboration; receipts1–4 establish the historical change.

## Translation to this repository's clock

`analysis/grid24.py:1–10,24–25` says minute labels are the bars **closing** at each calendar-date minute, using MultiCharts stamps. Thus:

- Historical afternoon pause:15:15 is the final valid pre-pause close.15:16…15:30 are the 15 scheduled labels to omit;15:31 is the first full one-minute bar after reopening. Apply only to Monday–Friday calendar/account dates before 2021-06-28, within verified source coverage.
- Ordinary daily break:16:00 is a valid final close.16:01…17:00 do not describe complete trading minutes;17:01 is the first ordinary full post-open minute. A missing17:01 observation is **not** established as a scheduled closure.
- Weekend:Friday16:00 through Sunday17:00 is closed under the ordinary schedule. Calendar labels need civil-date/weekend logic; do not label every Friday evening or every Sunday daytime as missing quotes.
- All times are **America/Chicago local time with DST**, not fixed UTC−6. This audit does not independently certify the upstream feed's UTC conversion; it confirms the saved close-label convention and observed schedule transition.

The builder's proposed normal-pause configuration is consistent with the primary receipts: markets`[NQ,ES]`, `end_account_date=2021-06-27`, labels`15:16…15:30`, weekdays`[0,1,2,3,4]`. The parent must freeze the exact configuration/code before outcomes. This note does not authorize the dependent return calculation.

Omitting a scheduled nontrading label means **no invented price event**. Do not fill prices, insert a zero return, claim an executable fill during a closure, or ignore the next observed gap. Mark and test liquidation at reopening using the observed source price. Source orders or observations contradicting the supposed closure remain an explicit data/order-clock exception. If other held instruments are open, their events still occur: a closed instrument's unavailable broker risk valuation needs a stated treatment rather than automatic portfolio-level omission. The builder currently retains such mixed-open ambiguity as UNKNOWN.

## Independent timestamp-only checks

Reproduce with `/workspace/venvs/thebeginning/bin/python agents/codex/inputs/eval_audit_20261104/calendar_clock_check.py`. It reads **only date/time columns** and file bytes for SHA256, no prices, signals, P&L or returns. The receipt is `calendar_clock_counts.json`; it includes exact source hashes, counts, anomaly labels, and sample-day gaps.

| NQ overnight file | Count of15:16 labels | Count of15:30 labels | Count of15:31 labels |
|---|---:|---:|---:|
|2018|1|0|248|
|2019|0|0|249|
|2020|0|0|250|
|2021|130|130|251|
|2022|250|250|250|
|2023|248|248|248|
|2024|249|249|249|
|2025|247|247|247|
|2026|208|208|208|

In both NQ and ES 2021 files, the first15:16…15:30 observations on/after the transition are dated **20210628**. ES on 20210625 has15:14,15:15 then15:31,15:32; on 20210628 it has every intervening minute. This is independent timestamp corroboration, not proof that all missing rows are exchange closures. Some2018 source anomalies print during the nominal pause; their exact date/time labels are preserved in the JSON. Do not silently discard those observed exceptions.

For the already-committed normalized Bridge ticket from2018-04-29 19:00 through2018-04-30 15:55, the timestamp union is missing exactly 17 labels:

- 15 labels:2018-04-30 15:16 through15:30, explained by the dated CME pause.
- **2018-04-29 23:39 and2018-04-30 14:42**: open-market holes, unresolved. They remainUNKNOWN when net exposure requires a quote.

Therefore “17 missing minutes” does not mean17 unobservable open-market minutes, but neither does the scheduled pause clear this ticket's remaining 2. No account pass rate, profit, strategy viability or full Bridge admission is inferred here.

## Holidays, exceptions and remaining limits

[CME's current trading-hours page](https://www.cmegroup.com/trading-hours.html), extracted lines 50–91 and190–206 (`turn599850view0`), directs users to product/date-specific downloadable Globex calendars for 2026/27 and says schedules can change. Its rendered extraction did not expose the dynamic per-product holiday table. The BrokerTec, ClearPort, trading-floor and settlement tables on that page are **different venues/purposes**; their hours are not valid substitutes for NQ/ES Globex matching hours.

This bounded check did **not** obtain and enumerate authoritative NQ/ES dated early-close exceptions for every 2018–26 holiday or special closure. No holiday omissions beyond individually supplied authoritative receipts should be added from this note. Unresolved gaps and any exceptional-day exposure keep the existingUNKNOWN/data gate. A universalNYSE holiday calendar or a guessed 13:00 close would weaken that gate. Final expiring-contract termination (typically 08:30 on final trade date) is also different from the continuous/front-contract session and requires contract identity; this audit does not manufacture a roll calendar.

Some accessible CME educational/translated pages still display the removed pause or old16:15close, including a 2018 Trading Challenge PDF retaining©2014 specifications. Those stale summaries do not override the dated exchange change notices. Source access was public and read-only; no login, purchases, keys, broker or live systems were used.
