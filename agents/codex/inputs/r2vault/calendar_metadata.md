# R2Vault execution-calendar clarification before returns
Summary: Missing15:16–15:30 CT close-stamped minutes before2021-06-28 are a documented exchange pause.
The same interval after that date is not presumed closed. No strategy return had run when this was resolved.
This changes missing-data classification, not signal thresholds, geometry, costs or the five frozen models.

The replay timestamp audit found867 otherwise normal dates with the entire15-minute interval absent,
2018-01-02 through2021-06-25, and none after. CME removed this pause effective trade date2021-06-28.
The published [CME June2021 notice](https://www.cmegroup.com/notices/electronic-trading/2021/06/20210621.html)
and [regulatory filing, page2](https://www.cmegroup.com/market-regulation/rule-filings/2021/6/21-244R_2.pdf)
support the date boundary. A generic CME Micro FAQ still lists the old pause, so it is not the governing
historical boundary. Primary sources were checked2026-10-24.

Only the documented pre-change interval is added to the known-closure mask. Missing quotes elsewhere remain
unknown unless already covered by the repository's explicit maintenance/weekend/early-close proxy.
The feature stream still uses actual observed bars; no artificial bars, closes or fills enter the regression.
Account marks can remain at the last observed price during a verified closure. On reopening, gap-aware stop,
target and queued market-order rules apply to the actual opening price. Eligibility uses observed OR known
closed minutes; it does not silently discard all early history because of an exchange-wide pause.
