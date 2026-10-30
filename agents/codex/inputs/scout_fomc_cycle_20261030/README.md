# Input provenance

`paper_20180212.pdf`: author working manuscript,496036bytes, downloaded from the public university teaching
repository pinned in the review record. First guessed `_sources/...` path404; actual `_downloads/8a74...`path200.
The2019 filename does not override the PDF title-page date2018-02-12. No publisher-version parity claim.

`calendar.json`:39completed regular FOMC dates from owned event_days seed, crosschecked against owned official
statement-header facts. Contains original source URLs/date headers. Used only>=9weekdays after a dated public
statement, not to assume advance knowledge of a future release schedule. March2020unscheduled actions do not reset.

`nyse_sessions.csv`: secondary reproducible NYSE schedule, generated before returns with
`pandas_market_calendars==4.4.2`/`exchange_calendars==4.5.4`. Packages installed only in `/tmp/scout_calendar_deps`,
not into configured Python. Historical early closures are not selected using outcomes. Reproduction after installing
the pinned packages on a separate library path:

```python
import pandas_market_calendars as m
assert m.__version__ == '4.4.2'
m.get_calendar('NYSE').schedule('2018-01-01','2022-12-31').to_csv('nyse_sessions.csv')
```

Public source discovery used connected GitHub search while connected general web search/open returned empty
errors. This fallback is not an exhaustive SSRN search or quality ranking. Native contract/roll/path verification and
micro fee/fill data remain later executable-admission requirements; this failed cheap screen does not waive them.
