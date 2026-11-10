Author/origin: **dot**. Original acquisition report retained November 10, 2026. No acquisition or QA rerun for this publication. Raw data stays outside Git; paths below refer to the original PC package, not this report directory. See ../DOT_CONTRIBUTIONS.md for attribution and scope.

# Pre-2018 ES/NQ minute data: acquired, not yet admitted

Summary: Free ES and NQ continuous one-minute OHLCV files were downloaded from Syncster's public Hugging Face dataset on 2026-11-10. Both start 2016-05-29 22:01 UTC. Isolated pre-2018 CSV extracts contain 547,204 ES rows and 531,547 NQ rows. Existing project files were not changed. Unknown feed, roll construction, bar labeling and redistribution rights prevent treating this as a certified research extension.

## Files
- ES.parquet and NQ.parquet: original complete downloads, through 2026-10-20 23:59 UTC.
- ES_1min_pre2018_UTC.csv and NQ_1min_pre2018_UTC.csv: separately extracted rows before 2018; original UTC timestamps preserved. These do not use the project's Central-time/bar-close format.
- README.md: saved publisher dataset card.
- manifest_qa.json: hashes, byte sizes, exact year counts and basic quality checks.
- validate_extract.py: reproducible local extraction and QA; packages/ contains isolated PyArrow dependencies.

## Source and usage
https://huggingface.co/datasets/syncster-data/historical-market-data
Publisher: Syncster_APP. Dataset card says free, research and education only, provided as-is without accuracy or completeness guarantees. License metadata is `other`; no standalone license appeared in the root listing. This is not a clear commercial-use or redistribution grant. Do not publish/rehost the raw data. No account, key, payment or vendor contact was used.

The card says continuous futures and UTC timestamps but does not document original exchange/feed provenance, dated contract IDs, roll dates, adjustment type or whether timestamps label bar start/end. There is no dated-contract field in the files. Preserve these unknowns. Do not concatenate into trusted project data, replace existing files, calculate strategy returns or label this independent validation without resolving these points and checking overlap prices/session coverage.

## Checks
Both files have zero duplicate timestamps, out-of-order rows, off-minute timestamps, null OHLCV values, negative volumes or OHLC ordering violations. Most adjacent timestamps differ by one minute. These tests do not prove complete sessions, correct prices, tick-volume semantics, correct contract rolls or lawful upstream redistribution.

ES: 202,505 rows in 2016; 344,699 in 2017. NQ: 189,928 rows in 2016; 341,619 in 2017. See manifest for full-history counts and hashes.

## Already-owned data inspected read-only
C:\CodexRepo\data\ES_1min_2017.csv: 344,401 rows, Jan 2 17:02 through Dec 29 16:00.
C:\CodexRepo\data\NQ_1min_2017.csv: 74,717 rows, May 1 08:00 through Dec 29 15:15.
C:\CodexRepo\data\NQ_1min_ON_2017.csv: 17,749 rows, Dec 1 00:02 through Dec 29 16:00.
Repository README describes Central time; grid24 describes bar-close labels. All three have no duplicate timestamps or invalid OHLC ordering. Their existence does not mean 2017 is complete, especially NQ overnight.

## Earlier alternatives checked
- FirstRateData NQ: continuous data advertised from Jan 2 2008 and individual contracts from NQZ08; full history paid, free sample is limited. https://firstratedata.com/i/futures/NQ
- Kibot: ES/NQ paid minute history from 2009; free download page explicitly excludes futures. https://www.kibot.com/free-historical-intraday-data.html
- Databento NQ: catalog advertises history since June 6 2010, but account/data entitlement route not used. https://databento.com/catalog/cme/GLBX.MDP3/futures/NQ
- MarketParquet: full intraday history paid, free recent sample/daily tier insufficient for older extension. https://marketparquet.com/guides/free-nq-mnq-futures-historical-data
- QuantShare downloader offers past three trading days, not historic pre-2018 coverage. https://www.quantshare.com/item-1268-one-minute-data-for-intraday-futures
No verified free complete pre-May-2016 ES/NQ minute archive was obtained in this pass. No strategy tests, live/broker/VPS access, program resumes, Git commits or pushes occurred. Local git status was not reliable inside the sandbox, so the repository was left entirely unchanged.
