# Existing-data paper audit: five screened baseline slots
Author: dot | 2026-11-10 | No new return tests

## Summary
- Actual raw rows and reader code verified, not filenames alone.
- Five distinct papers have existing price-data adaptations; all were already tested or rejected in the project.
- These are slots16–20 in the expanded screen, NOT five new strong strategy recommendations.
- Exact replication is often blocked by original-market or input differences even when a proxy is easy to code.
- Search continues for stronger replacements; no failed definition is reopened here.

## Verified data
Repository: Dartdark/thebeginning, codex/work. Paths below link directly to the user's existing data/code and contain no new data uploads.

- [NQ2018](https://github.com/Dartdark/thebeginning/blob/codex/work/data/NQ_1min_2018.csv): date,time,open,high,low,close,volume;110,366rows,258dates,2018-01-02 08:00–2018-12-31 15:15. No duplicate date/time keys or nonfinite numeric rows in audit. Daily counts31–436 require holiday/partial-session handling.
- [NQ2026](https://github.com/Dartdark/thebeginning/blob/codex/work/data/NQ_1min_2026.csv): same schema;92,585rows,216dates,2026-01-02 08:00–2026-10-30 15:15.
- NQ_1min_ON_2017.csv: actual December2017 overnightOHLCV rows inspected, not proof of later completeness.
- YM_1min_2017.csv:26,338rows,2017-12-01 00:02–2017-12-29 16:00, sameOHLCV schema.
- [VIX_daily.csv](https://github.com/Dartdark/thebeginning/blob/codex/work/data/VIX_daily.csv): DATE,OPEN,HIGH,LOW,CLOSE;9,301rows,1990-01-02–2026-10-23.
- treasury_auctions.csv: actual auction date/security term/competitive closing time/reopening/amount/bid-to-cover/yield/CUSIP fields, December2017–October2026. Calendar availability does not provide executable Treasury quotes.
- [grid24.py](https://github.com/Dartdark/thebeginning/blob/codex/work/analysis/grid24.py) defines minute bar-CLOSE timestamps in Chicago time, NQ daytime08:00–15:15 and separate overnight15:16–07:59. No dated-contract identifier in theseCSV schemas.

Large ES2018/2026,YM2026 and NQovernight2026 blob reads failed with Transport closed. They are unread, not empty. SPY_daily.csv is only DATE,CLOSE with values around2252 in early2017; it does not establish nativeSPY prices. [DATA_NEEDED](https://github.com/Dartdark/thebeginning/blob/codex/work/agents/codex/DATA_NEEDED.md) D55 explicitly leaves nativeSPY minute data missing.

MinuteOHLCV cannot resolve tick sequencing, bid/ask spread, within-bar stop/target priority, latency or native micro-contract fills. Files and prior reader code establish capability to reconstruct certain price hypotheses, not data sufficiency for any paper mentioning futures.

##16. Market Intraday Momentum
[SSRN2440866](https://ssrn.com/abstract=2440866), Gao et al.
- About/mechanism: opening return predicts final-half-hour return, potentially delayed information/rebalancing.
- Existing adaptation: NQ prior15:00close→09:00direction, trade14:30→15:00CT. VerifiedNQ fields suffice; exact originalSPY study needs missing native data.
- Code: analysis/gao_intraday_momentum_test.py.
- Existing result: NQ−$28/trade, Sharpe−0.47;ES−$40,t−3.1.
- Tags: intraday design; existing-data adaptation yes; exact-source replication no; DUPLICATE/FAILED.
- Decision: baseline only. Data feasibility does not justify rerunning a failed rule.

##17. Overnight-Intraday Reversal Everywhere
[SSRN2730304](https://ssrn.com/abstract=2730304), also circulated as Market Closure and Short-Term Reversal.
- About/mechanism: buy assets with low prior overnight returns, sell high, intraday; potential temporary liquidity compensation.
- Existing seven-market adaptation:15:00→08:30signal,08:30→15:00trades, lagged risk scaling. Code analysis/co_oc_reversal_test.py mapsNQ/ES/YM/GC/CL/ZN/6E inputs.
- Existing result: gross−$42/day,net−$155;equity-only gross≈0.
- Tags: intraday holding despite overnight signal; partial current-panel audit; original32-market replication unavailable; DUPLICATE/FAILED.
- Decision: no promotion. A simultaneous cross-sectional long-short portfolio also differs from a standalone intraday instrument implementation.

##18. A Tale of One Day
[SSRN4192163](https://ssrn.com/abstract=4192163), Xu and Zhu.
- About/mechanism: morning momentum/afternoon reversal in individual stocks, potentially liquidity and microstructure effects.
- Existing adaptation: follow prior08:30–10:30move or fade13:00–15:00, hold next08:30–15:00CT; also20-day formation. Code analysis/morning_afternoon_test.py inspected.
- Existing result: following morning netNQ−$61,ES−$42,YM−$31/trade. NQafternoon fade+$62 but t0.8 and3/9positive years.
- Tags: intraday futures adaptation feasible from verifiedNQ fields; original stock cross-section unavailable; DUPLICATE/FAILED.
- Decision: do not mistake a futures proxy for replicating the stock mechanism.

##19. Market Sentiment and an Overnight Anomaly
[SSRN3829582](https://ssrn.com/abstract=3829582), Vojtko and Hanicová.
- About/mechanism: sentiment/trend-conditioned overnightSPY exposure.
- Existing adaptation: NQ/VIX20-dayMA variants, overnight holding; analysis/ond_sentiment_filter_test.py uses inputs before trade date.
- Existing result: OND mean$71→$33 with trend filter,$30 withVIXfilter.
- Tags: PERSONAL/OVERNIGHT, not user's intraday category; existingNQ/VIX adaptation partial audit; nativeSPY/news-sentiment inputs absent; DUPLICATE/FAILED.
- Decision: no post-hoc filter inversion. Later overnight coverage must be validated independently.

##20. Opening-Range Reversal in Dow Jones Futures
[SSRN7124578](https://ssrn.com/abstract=7124578), Ladia.
- About/mechanism: opening up-push followed by short reversal; dealer0DTE explanation is a hypothesis.
- Existing reconstruction: YMopening push→short, time exit/1:1bracket, analysis/anti_papers_1018_test.py. ActualYM schema inspected but exact source rules are withheld.
- Existing result: corrected first-five-minute windowYM−$16/trade,t−1.3 in2023–26; earlier reconstruction−$50,t−2.2.
- Tags: intraday reconstruction possible; exact replication BLOCKED; existing-data coverage not fully recertified; DUPLICATE/FAILED.
- Decision: cannot count a withheld-rule paper as currently reproducible just becauseOHLC data exist.

## Evidence and status
All quoted project performance is from [TIER_LIST](https://github.com/Dartdark/thebeginning/blob/codex/work/TIER_LIST.md), not tests run in this assignment. This pass verified primary paper metadata and repository implementations, not five new full-source reviews. These five preserve the distinction between “we have fields to test a hypothesis” and “we have a new strong candidate.” Fresh-qualified quota remains unfilled. No return tests, live access, paid data or schedules performed.
