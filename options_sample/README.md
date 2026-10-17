# Options sample: July-December 2022

This ZIP contains 127 trading days, from 1 July through 30 December 2022,
for SPX, SPY, TSLA and KO. All 34 CSV columns are retained. Headers and
selected rows are copied from the published archive without changing their
values, precision or ordering.

## Contents and verification

```text
README.md
LICENSE.txt
verify.py
day_by_date/
    manifest.json
    2022-07-01_options.csv
    ... (127 daily CSV files, ending 2022-12-30_options.csv)
```

Extract the ZIP, open a terminal in the extracted folder containing
`verify.py`, and run:

```sh
python verify.py --complete day_by_date
```

Use `python3` if that is your Python command. No additional packages are
needed. A successful check exits with code 0 and ends with:

```text
== 127 file(s): PASS - exactly as published (complete set: 127 of 127 listed files present) ==
```

The script checks the complete file set, checksums, column structure,
documented data rules and the presence of usable interest-rate curves.
It does not independently re-solve implied volatility or Greeks.

The sample's `manifest.json` records each extracted file's row count,
byte count and SHA-256. It also includes the published seven-tenor rate
curve for every sample date, in percent, and `rates_carried_forward` for
dates using an earlier published curve. Values and any `null` entries
are preserved; see section 6 below for tenor order and interpretation.

## Reading the sample

- SPX includes SPXW contracts. Their original `underlying` identifiers
  remain separate, so the four markets appear as five codes: SPX, SPXW,
  SPY, TSLA and KO. See note N9 below for the contract-root convention.
- Compare TSLA on 24, 25 and 26 August around its three-for-one split,
  using the contract, expiration and strike fields to identify contracts.
- Find SPX or SPXW rows where `expiration` equals `quote_date` to inspect
  same-day expirations. Compare SPX and SPY exercise and settlement fields.
- Read `iv_flag` alongside quotes to distinguish calculated values from
  unavailable values. The `quote_time` column is empty throughout this
  2022 sample; that field became available in August 2026.

The general product reference below supplies the field definitions,
units, calculation methods and data rules. Its full-archive and
subscription directory descriptions are broader than this fixed sample:
this ZIP contains final daily files only, with no provisional CSVs,
rolling manifest or `update.py` synchronization script.

The stock sample covers the same period and shares TSLA, SPY and KO.
Download both samples and read their field definitions at
https://historicaldata.net/samples.html.

The included LICENSE.txt governs this sample. This six-month subset does
not establish coverage or data quality for every year or underlying in
the full archive; check coverage for the symbols and dates you need.

---

# historicaldata.net - U.S. Equity & Index Options Data

This file describes everything needed to fetch, read, interpret, and independently verify the data. It sits in the data directory itself, so the directory explains itself without reference to any website.

---

## 1. What you have

### 1.1 The directory

Two levels, and only two. The top level holds what you read and what you run; the data itself is one plain CSV file per U.S. trading day, all of them in `day_by_date/`. No archives to unpack, no per-month subfolders.

```
README.md
LICENSE.txt
update.py
day_by_date/
    manifest.json
    last-21-days_manifest.json
    2002-02-08_options.csv
    ...
```

The manifest sits with the files it describes, and the names inside it are relative to that same directory - so `verify.py` checks whichever directory you run it in.

| Name | Contents |
|---|---|
| `day_by_date/YYYY-MM-DD_options.csv` | One U.S. trading day, final. 34 columns, header row included. |
| `day_by_date/YYYY-MM-DD_options_provisional.csv` | The same day, hours earlier (see below). Present only until the final file replaces it in the manifest; removed about a day later. |
| `day_by_date/manifest.json` | Row count, byte size and SHA-256 for every daily file, the trading days covered, and the interest-rate curves actually used (section 6). |
| `day_by_date/last-21-days_manifest.json` | The same records, limited to the most recent 21 days. Subscribers can read this one instead of the full manifest. |
| `README.md` | This document. |
| `LICENSE.txt` | The license the data is sold under. |
| `update.py` | Keeps a local copy in sync: fetches what is missing, re-fetches what does not match its checksum. Standard library only. |

Coverage: **2002-02-08 onward**, in two segments that never overlap: an archive segment built from end-of-day records, and a daily segment captured each session from 2026-08-06 onward. The manifest names the boundary (`archive_through`, `daily_from`); a trading day belongs to exactly one segment. Every listed U.S. equity and index option contract present for that day - all strikes, all expirations, whether or not they were quoted or traded.

Some columns start later than others; the `Since` column in section 2 gives the first date each one carries data.

Each trading day is published in two stages, under different names. A final file can later be replaced by a documented correction (section 10); use the current manifest to verify its size and checksum:

- **The provisional file** (`..._options_provisional.csv`) appears the same evening, around 20:00 ET. It carries the full 34-column header with quotes, open interest, volume, Greeks and implied volatility computed; the four trade-statistics columns (`trade_vwap`, `transactions`, `multileg_volume`, `active_minutes`) are blank, and prices may still receive consistency corrections. It declares itself temporary: it disappears about a day after the final file arrives.
- **The final file** (`..._options.csv`) appears around 02:00 ET the following morning, once the official end-of-day aggregates have been merged and every check has passed. *Final* means the final version of that release, not that the object can never change: when a defect is found, the affected files are recomputed and re-published under the same names, and the manifest is regenerated so that its SHA-256 values describe the current files. Every such revision is recorded in section 10. A checksum you saved verifies the copy you saved; to know whether the online file is still that copy, compare against the current manifest.

The manifest always reflects what you should use right now: it lists the provisional file only until the final one replaces it. A trading day absent from both has not been published yet. If you keep both files, prefer the final one; the verification guarantees in section 9 apply to final files.

### 1.2 Fetching the files

Your personal download page - the link on the order confirmation page and in your purchase email - is the way in. Everything below starts from that page, and every request authenticates with the token carried in your link; there is no account and no password.

Four ways to fetch:

1. **The page itself.** One button per year; the browser asks for a folder once, then writes straight into it. Needs desktop Chrome or Edge.
2. **The Python script shown on the page.** Standard library only, your token already filled in. It reads the manifest, skips files that are already complete, and verifies every SHA-256 as it goes, so it is safe to interrupt and re-run. This is the recommended way to take everything you bought.
3. **Any HTTP client.** Every file is one HTTPS request: send the header `Authorization: Bearer <token>`, or append `?t=<token>` to the file's URL. Responses are compressed in transit, roughly 3.6x smaller than the file on disk.
4. **S3 credentials.** The page can issue read-only S3 credentials (key, secret and session token) scoped to exactly what you purchased, valid for at most 7 days; issuing fresh ones later is free and unlimited. Any S3 client works - `rclone`, `aws s3`, or an SDK. Two trade-offs, stated plainly: the S3 endpoint does not compress, so the same files cost about 3.6x more bytes on the wire than over HTTPS; and credentials for a partial range are not allowed to list the bucket, so folder-browsing tools will not connect - drive the download from `manifest.json` instead, fetching each key it names. Full-archive credentials can list, so there `rclone copy` over the whole bucket works as is.

Always fetch `manifest.json` (or `last-21-days_manifest.json`) as well - it is what lets you confirm the files are complete and unaltered.

Over S3, most clients verify each object's ETag on download automatically. For these files the ETag is the MD5 of the file, so a transfer that completes without a warning has already been checked once.


---

## 2. Column dictionary (34 columns, fixed order)

Every cell below is short and comparable, so the table stays readable in a plain text viewer. The `Note` column points to a numbered note below, for the columns that need more than a phrase.

`Since` is the first date the column carries data. `Blank means` states what an empty field tells you - it never means zero (section 3).

| #  | Column             | Type    | Unit / domain          | Since      | Blank means         | Note |
|----|--------------------|---------|------------------------|------------|---------------------|------|
| 1  | `contract`         | text    | OSI symbol             | 2002-02-08 | never blank         | N1   |
| 2  | `underlying`       | text    | symbol                 | 2002-02-08 | never blank         |      |
| 3  | `expiration`       | date    | YYYY-MM-DD             | 2002-02-08 | never blank         | N2   |
| 4  | `type`             | text    | `call` or `put`        | 2002-02-08 | never blank         |      |
| 5  | `strike`           | number  | $ per share (index: points) | 2002-02-08 | never blank    |      |
| 6  | `style`            | text    | `A` or `E`             | 2002-02-08 | never blank         |      |
| 7  | `quote_date`       | date    | YYYY-MM-DD             | 2002-02-08 | never blank         |      |
| 8  | `bid`              | number  | $ per share (index: points), > 0 | 2002-02-08 | no bid posted | N13  |
| 9  | `bid_size`         | integer | contracts, >= 1        | 2005-01-03 | no size reported    | N3   |
| 10 | `ask`              | number  | $ per share (index: points), > 0 | 2002-02-08 | no offer posted | N13 |
| 11 | `ask_size`         | integer | contracts, >= 1        | 2005-01-03 | no size reported    | N3   |
| 12 | `quote_time`       | datetime| ISO 8601 UTC, seconds  | 2026-08-06 | no quote / archive era | N11 |
| 13 | `volume`           | integer | contracts, >= 0        | 2002-02-08 | source value unusable | N12 |
| 14 | `open_interest`    | integer | contracts              | 2002-02-08 | not reported        | N4   |
| 15 | `open`             | number  | $ per share (index: points) | 2014-06-02 | did not trade  |      |
| 16 | `high`             | number  | $ per share (index: points) | 2014-06-02 | did not trade  |      |
| 17 | `low`              | number  | $ per share (index: points) | 2014-06-02 | did not trade  |      |
| 18 | `close`            | number  | $ per share (index: points) | 2002-02-08 | did not trade  |      |
| 19 | `trade_vwap`       | number  | $ per share (index: points) | 2014-06-02 | did not trade  |      |
| 20 | `transactions`     | integer | count                  | 2014-06-02 | did not trade       |      |
| 21 | `multileg_volume`  | integer | contracts              | 2019-11-04 | unknown, not zero   | N8   |
| 22 | `active_minutes`   | integer | count of 1-min bars    | 2014-06-02 | did not trade       | N14  |
| 23 | `last_trade_date`  | date    | YYYY-MM-DD             | 2002-02-08 | not seen trading    | N7   |
| 24 | `underlying_close` | number  | $ per share (index: level) | 2002-02-08 | price unavailable | N10  |
| 25 | `settlement_time`  | text    | `AM` or `PM`           | 2002-02-08 | not determinable    | N9   |
| 26 | `iv_bid`           | number  | decimal                | 2002-02-08 | no solvable bid     | N6   |
| 27 | `iv_ask`           | number  | decimal                | 2002-02-08 | no solvable ask     | N6   |
| 28 | `iv`               | number  | decimal (0.25 = 25%)   | 2002-02-08 | `iv_flag` > 1       |      |
| 29 | `iv_flag`          | integer | 0-7, see section 4     | 2002-02-08 | never blank         |      |
| 30 | `delta`            | number  | per 1.00 of underlying | 2002-02-08 | `iv_flag` > 1       | N5   |
| 31 | `gamma`            | number  | delta per 1.00 of underlying | 2002-02-08 | `iv_flag` > 1   | N5   |
| 32 | `theta`            | number  | price per year (see Units) | 2002-02-08 | `iv_flag` > 1     | N5   |
| 33 | `vega`             | number  | price per 1.00 of volatility | 2002-02-08 | `iv_flag` > 1   | N5   |
| 34 | `rho`              | number  | price per 1.00 of rate | 2002-02-08 | `iv_flag` > 1       | N5   |

Columns 1-25 are observations and reference values; columns 26-34 are computed by us. Everything to the left of `iv_bid` came from the market (or an official close); everything from `iv_bid` rightward came from our solver.

Numeric precision for the computed columns (26-28 and 30-34) is **6 decimal places**. At that precision, feeding a published `iv` back into the model reproduces the quoted mid price to well under a cent, so the published value is a lossless record of the solver's result rather than a rounded summary of it.

### Units

- **Prices** (`bid`, `ask`, `open`, `high`, `low`, `close`, `trade_vwap`) and `strike` are quoted the way the market quotes them: **U.S. dollars per share** for stock and ETF options, **index points** for index options. They are *not* multiplied by the contract size. A standard U.S. option contract covers 100 shares (for an index, 100 times the level), so the dollar value of one contract is the price times 100 - but adjusted contracts (after splits, special dividends or corporate actions) carry non-standard deliverables, and the multiplier is not part of this data. Apply your own.
- **`underlying_close`** is in the same unit as the option's prices: dollars per share, or the index level.
- **`iv`, `iv_bid`, `iv_ask`** are annualised volatilities as decimals: `0.32` means 32%.
- **Greeks** are derivatives of the per-share (per-point) option price, with the underlying, volatility and rate in their natural units; the same multiplier caveat applies. `delta` is per 1.00 move of the underlying (dimensionless), `gamma` is the change in `delta` per 1.00 move of the underlying. The remaining three are scaled as follows - divide to get the conventional per-day / per-point figures:

| Column | Published as | Divide by | To get |
|---|---|---|---|
| `theta` | price change per **year** of calendar time, T measured as in section 5.2 | 365 | per calendar day |
| `vega` | price change per **1.00** (100 percentage points) of volatility | 100 | per volatility point (1%) |
| `rho` | price change per **1.00** (100 percentage points) of the risk-free rate | 100 (10,000) | per percentage point (per basis point) |

For example `theta = -117.000777` is `-0.320550` per day, `vega = 28.9697` is `0.289697` per volatility point, and `rho = 7.884765` is `0.078848` per percentage point of rate. `theta` is negative for a long position in the ordinary case (the option loses value as time passes), and its magnitude for an American contract comes from the same tree that priced it (section 5.1).

### Notes

**N1 - `contract`** OSI contract symbol, e.g. `AAPL220617C00150000`: root, then YYMMDD, then `C`/`P`, then the strike in thousandths padded to 8 digits. The same contract carries the same symbol in every file we publish, daily or archived, so the two join directly.

**N2 - `expiration`** Before 2015-02 this is the *nominal* Saturday for standard monthly contracts, which is how the exchange listed them; the payoff was fixed at Friday's close. Section 5.2 explains how that affects time to expiry.

**N3 - `bid_size` / `ask_size`** The number of contracts posted at that side's price. Available from **2005-01-03** onward; for 2002-02-08 to 2004-12-31 no source carries quote sizes and both columns are blank for the whole era.

**A size is published only when the quote it belongs to is live.** A size accompanies a real price, so a blank size means one of: that side has no price, or the source reported no size for it. In particular a size is never published as `0` - a standing quote cannot be for zero contracts, so a reported zero is an absence, not a quantity.

Coverage within the era varies by year and by contract, measured across 12 sampled sessions per year: 2005-2009 carry bid sizes on 33-37% of rows, 2011 onward on 72-78%. 2010 is a transition year and spans the whole range within itself - 32% early in the year, 84% late - so a single figure does not describe it. Treat a blank as "not reported", never as zero (section 3).

**N4 - `open_interest`** The value published for the session, which reflects the *prior* day's close of business - the industry-standard one-day lag. Do not align it with same-day volume without accounting for that.

**N5 - `delta` / `gamma` / `theta` / `vega` / `rho`** Units and scaling are in the Units paragraph above. A value that the American tree's finite differences push outside its theoretical domain is set to the nearest boundary (delta into [0,1] for calls and [-1,0] for puts, gamma >= 0, vega >= 0, rho >= 0 for calls and <= 0 for puts); values inside their domain are published exactly as computed. See section 5.5.

**N6 - `iv_bid` / `iv_ask`** Solved independently from the bid and the ask. Either can be blank while `iv` is present: a zero bid has no implied volatility, and a bid-side solution above the ask-side one is discarded as numerically untrustworthy. Useful as a per-row confidence interval on `iv`.

**N7 - `last_trade_date`** The most recent day this contract traded, looked back through the archive; equals `quote_date` when it traded today. Blank means "not observed trading at any point in the archive up to this day" - **not** that it never traded. Values early in the archive are limited by how far back the archive itself goes (section 5.7).

**N8 - `multileg_volume`** Volume attributed to multi-leg (spread) executions. The trade condition codes that identify them exist only from **2019-11-04**, so the column is blank before that date and blank there means *unknown*, not zero - filling it with 0 would misrepresent 72% of the archive.

**N9 - `settlement_time`** `AM` for index options that settle against the opening print on expiration day, `PM` otherwise. This changes the effective time to expiry (section 5.3). Blank means we could not determine it from the data and decline to guess; it is not a claim of PM.

**SPX and SPXW.** Both are European-style, cash-settled options on the S&P 500. Standard monthly SPX contracts (third Friday) settle AM against the opening print; SPXW weekly and end-of-month contracts settle PM against the close. In this archive the two are told apart by the **contract root** - the OSI symbol with its trailing 15 characters removed (`SPX` or `SPXW`) - not by the `underlying` column: from 2014-04-01 SPXW contracts are listed under `underlying = SPXW`, before that under `SPX`, and a few sessions carry both conventions. `settlement_time` and `style` are stated on every row, so no lookup is needed; use the root when you need the product family itself.

AM settlement normally implies European exercise: the settlement value is struck at the opening on expiration day and the contract stops trading before it, so there is no window in which to exercise early. `SOX` (the Nasdaq PHLX semiconductor index) is the exception - it is American-style with AM settlement per the exchange's own specification, and it is published that way here. If you filter on `settlement_time = AM` expecting only European contracts, exclude `SOX` explicitly.

**N10 - `underlying_close`** The underlying's official closing price for `quote_date`: the 16:00 ET consolidated close for stocks and ETFs, the official closing level for indices. Unadjusted for splits and dividends, matching the option prices in the same row.

Three groups of rows carry a **quote-time last trade price instead of the official close**, because no official close is available to us for them. The value is still a real, unadjusted price of that underlying on that trading day - it is simply taken at the moment the option was quoted rather than at the close.

| | Rows affected |
|---|---|
| Stocks and ETFs before **2003-09-10** | every row of those trading days |
| Indices whose official closing level is not published to us: **NDX, HGX, OSX, UTY, XAU, XDA, XDB, XDC, XDE, XDN, XDS, XDZ** | every row, whole archive |
| Any underlying that did not trade on that day | that underlying's rows for that day |

**How much of the data this is depends entirely on the period, and the difference is large:**

| Period | Rows carrying a quote-time price instead of the close |
|---|---|
| **2002-02 to 2003-09-09** | **~98%** - no stock reference exists for these years at all; only a handful of indices can be verified |
| 2003-09-10 onward | ~1-2% - the twelve indices listed above, plus underlyings that did not trade |

An archive-wide average would be around 3% and would tell you almost nothing, so it is not quoted here. **If you work with 2002-2003 data, treat this column as a quote-time price throughout that period.**

On a calm session the two measures coincide for the great majority of underlyings; on a violently reversing session they can differ by more than 1%. If your work is sensitive to that distinction, exclude the groups above.

**N11 - `quote_time`** The moment the standing quote in this row (`bid`/`ask`) was last updated, as recorded by the consolidated feed: ISO 8601 UTC at seconds precision, e.g. `2026-08-11T19:59:58Z`. Populated from **2026-08-06** onward; no quote timestamp exists in the archive before that date, so all earlier rows are blank for the whole era.

Why it exists: an end-of-day file shows every listed contract's last standing quote as if all were equally fresh. They are not. On a typical day, roughly 43% of quotes were last updated in the final minute before the close, about 6% have stood untouched since the open, and a thin tail has not updated for days or weeks (oldest observed: 29 days). `quote_time` makes each row's freshness visible, so you can decide which quotes to trust instead of inheriting our opinion.

`quote_time` can be **earlier than `quote_date`** - that is not an error. It means the quote standing at the close was posted on an earlier day and never refreshed (a "zombie" quote). Those rows are precisely the ones this column lets you find.

**Deriving a quote age.** Take the reference moment to be 16:00 ET on `quote_date` (index options quote until 16:15 ET, so small negative ages up to about 15 minutes are normal on index rows). Convert through a real timezone rather than hardcoding an offset - 16:00 ET is 20:00 UTC in summer but 21:00 UTC in winter:

```python
import pandas as pd
qt    = pd.to_datetime(df['quote_time'], utc=True)
close = (pd.to_datetime(df['quote_date']).dt.tz_localize('America/New_York')
           + pd.Timedelta(hours=16)).dt.tz_convert('UTC')
df['quote_age'] = close - qt        # Timedelta per row; NaT where quote_time is blank
```

Two filters cover most uses:

| Filter | Keeps | Typical use |
|---|---|---|
| `quote_age <= pd.Timedelta(minutes=5)` | quotes alive into the close | volatility surfaces, IV studies |
| `quote_age < pd.Timedelta(days=1)` | everything quoted on the day itself | coverage and liquidity studies |

Rows where `quote_time` is blank (no standing quote, or archive-era data) fall out of both filters as NaT; treat them the same way you treat a blank `bid`.

**N12 - `volume`** Contracts traded that session, as reported by the source. Blank means the source's value was not usable: on a very small number of archive rows (roughly one in 100,000, concentrated in the early years) the source reports a *negative* volume, which is not a possible quantity. Those rows are published blank rather than with the impossible number, and never as 0 - 0 would assert "did not trade", which we have no basis to claim. Every published value satisfies `volume >= 0`.

**N13 - `bid` / `ask`** A published price is a price somebody actually posted, so both are strictly positive. Where a side has no quote the field is blank, never `0`: an option is never bid or offered at zero, and a zero in the raw feed is how it reports that there is nothing on that side.

This matters for anything you compute from a mid price. A blank bid means there is **no mid**, not a mid of half the ask - which is why `iv` and `iv_bid` are absent on those rows (`iv_flag = 2`) while `iv_ask` is still there. One-sided quotes are common in illiquid contracts; the ask-side implied volatility is the honest thing to use for them.

**N14 - `active_minutes`** The number of distinct one-minute bars in which this contract traded that day. It is a raw count over the contract's **own** trading day as the exchanges report it - **not** a fraction of a fixed 390-minute session, and it can exceed 390.

Why it exceeds 390: closing hours differ per product and cannot be derived from any rule we know of. Equity options generally trade 09:30-16:00 ET (390 minutes), but SPY, QQQ, IWM and a long list of ETFs trade until 16:15, and SPX/SPXW also trade in Cboe's Global Trading Hours overnight session. Measured over six recent sessions of 2.08M populated rows: 305 rows (0.015%) exceed 390, 33 rows (0.002%) exceed 405, and the maximum observed is **444** (an SPXW contract). A value of 391 on an equity option is normal too - it is the 16:00 closing bar on top of 09:30-15:59.

**Do not derive "minutes of silence" as `390 - active_minutes`.** There is no single session length to subtract from: the result would be negative for SPY and meaningless for SPX. If you need a silence measure, compare the contract against other contracts on the same root and date, which share the same session.

---

## 3. The blank rule - read this before writing any parser

> **A blank field means "not available". It never means zero.
> We never write 0 to stand in for a missing value.**

This is the central design commitment of this dataset. Wherever a `0` would stand for a missing value rather than a real one, we detect it and write a blank instead. Specifically:

| Pattern | What it actually means | What we publish |
|---|---|---|
| `bid = 0` or `ask = 0` | No quote on that side. An option is never bid or offered at zero - a zero is how the feed says "nothing here". | that side and its size blank; the other side retained |
| `bid > ask > 0` | Genuinely crossed quote; neither side trustworthy | both sides blank |
| `close = 0` | No closing trade recorded | `close` blank |
| underlying price `= 0` | Underlying price unavailable | `underlying_close` blank; IV/greeks not computed (`iv_flag = 7`) |
| `close` present but `volume = 0` | Stale price carried forward from an earlier session | `close` blank |
| `volume < 0` | Not a possible quantity; the source's value is unusable | `volume` blank - never 0, which would assert "did not trade" |
| `bid` or `ask` `< 0` | Not a possible price; the source's value is unusable | that side blank, along with its size column |
| `bid_size` or `ask_size` `= 0` on a live quote | A standing quote cannot be for zero contracts; the size was not reported | that size blank |

If you require a numeric column, substitute your own sentinel deliberately - do not assume blank can be read as 0. A blank `gamma` and a `gamma` of 0.000000 are different statements.

The converse of this rule is section 8: what a value, when present, is always guaranteed to satisfy.

---

## 4. `iv_flag`

| Value | Meaning | IV / greeks |
|---|---|---|
| 0 | Converged. Forward taken from put-call parity. | present |
| 1 | Converged. Forward fell back to `S*e^{rT}` (no usable parity pair). | present |
| 2 | No mid price (one or both quote sides missing). | blank |
| 3 | Mid price violates the no-arbitrage lower bound. | blank |
| 4 | Solver did not converge. | blank |
| 5 | No solution below the 500% volatility ceiling. | blank |
| 6 | No trading time remains to expiry (expiration day for PM options; the prior day for AM). | blank |
| 7 | A required input was missing (forward, strike, underlying price, or rate). | blank |

One test decides it: **`iv_flag <= 1` <=> `iv`, `delta`, `gamma`, `theta`, `vega` and `rho` are all populated.** This identity holds on every row of every file and is enforced before publication.

`iv_bid` / `iv_ask` are solved independently of the mid price, and the flag does not govern them in either direction:

- They can be **blank while `iv_flag <= 1`** - a side with no quote has no implied volatility, and a bid-side solution above the ask-side one is discarded as numerically untrustworthy.
- They can be **present while `iv_flag > 1`**. A row with no bid has no mid and therefore no `iv` (flag 2), but its ask is a real price and still implies a volatility. The same holds when the mid violates the no-arbitrage bound (flag 3) or exceeds the 500% ceiling (flag 5) while one side alone does not.

Concretely, on a sampled 2004 session 26,737 of the 29,162 rows with no bid carry an `iv_ask`. If you are building a surface from one-sided quotes, that column is the honest input - there is no mid to use.

---

## 5. How the calculated columns are produced

Columns 26-34 (`iv_bid`, `iv_ask`, `iv`, `iv_flag`, and the greeks) are computed by us from the quotes in the same row; `last_trade_date` (23) and `settlement_time` (25) are derived from the data as described below. Everything else is reported as received.

### 5.1 Model

| Exercise style | Model |
|---|---|
| `E` (European) | Black-76 on the forward |
| `A` (American) | Leisen-Reimer binomial tree, **101 steps** |

Greeks are analytic for European contracts and finite-difference for American ones, computed with the same tree that priced the contract (bump sizes: `S*1e-3` for delta and gamma, `1e-4` for vega and rho, `min(1/365, T/2)` years for theta).

The implied volatility solver is Brent's method, tolerance `1e-6`, at most 60 iterations, searching between a lower bound of `1e-4` and an upper bound of 5.0 (500%). (The Leisen-Reimer construction keeps the tree's risk-neutral probability inside (0, 1) for any positive volatility, so no model-specific lower bound is needed.)

**Everything a reproduction needs, in one place.** All inputs are in the row, in the other rows of the same file, and in the manifest:

| Input | Where it comes from |
|---|---|
| `S` | `underlying_close` of the row (see N10 for the periods where this is a quote-time price) |
| `K`, type, style | `strike`, `type`, `style` of the row |
| `T` | section 5.2, from `quote_date`, `expiration` and `settlement_time` of the row; calendar days / 365 |
| `r` | section 6: the curve stored in the manifest under `quote_date`, interpolated at this same `T` |
| `F`, `q` | section 5.4, from the bid/ask mids of the other rows of the same (root, expiration) group in the same file |
| price solved | `iv` is solved from the mid `(bid + ask) / 2`, which exists only when both sides are present and positive (section 3); `iv_bid` from `bid` alone and `iv_ask` from `ask` alone, each with the same `F`, `T` and `r`, and discarded as a pair when the bid-side solution exceeds the ask-side one |

The Leisen-Reimer tree is the standard construction with Peizer-Pratt inversion formula 2, an odd number of steps (101), `d1`/`d2` computed with the continuous dividend yield `q`, `p = h(d2)`, `p' = h(d1)`, up factor `u = e^{(r-q)dt} p'/p`, down factor `d = (e^{(r-q)dt} - p u)/(1-p)`, discounting by `e^{-r dt}` and early exercise tested at every node. `theta` for American contracts is the difference quotient `(V(T - dt) - V(T))/dt`; European greeks are the closed-form Black-76 derivatives. Published values are rounded to 6 decimals. A European row reproduces to within the solver tolerance with any correct Black-76 implementation; an American row reproduces to the published precision only with the same tree construction, and a difference beyond roughly `1e-4` in `iv` indicates a construction difference rather than a data error.

### 5.2 Time to expiry

`T = (expiration - quote_date) / 365`, in calendar days, with two subtractions that can both apply:

- **Saturday expirations** (the listing convention before 2015-02): the payoff is fixed at Friday's close, so one day is subtracted.
- **AM settlement** (`settlement_time = AM`): the contract settles against the opening print on expiration day, so its last trading day is the preceding session - one day is subtracted.

A pre-2015 monthly index contract with AM settlement has both, and loses two days.

### 5.3 Settlement time

`settlement_time` is determined empirically per (root, expiration) from observed trading activity around expiration, not from a product whitelist. Cash-settled index options with AM settlement are the only ones affected. Physically settled equity options are always PM.

### 5.4 Forward price and implied dividend

Contracts are grouped by (root, expiration), where the root is the OSI symbol with the trailing 15 characters removed. Within each group:

1. Consider strikes where **both** the call and the put have `bid > 0` and `ask > 0`.
2. Take the strike closest to `underlying_close`. If two are equidistant, the one appearing first in the file wins.
3. `F = K + e^{rT}*(C_mid - P_mid)`.
4. If no such pair exists, or the result is not positive, fall back to `F = S*e^{rT}` and set `iv_flag = 1` on every row of the group.

The continuous dividend yield implied by that forward is `q = r - ln(F/S)/T`. European contracts are priced off `F` directly; American contracts use `(S, q)` in the tree.

### 5.5 Greek clamping

Finite differences on the American tree can push delta marginally past 1 or flip the sign of rho for deep in-the-money contracts. Values that fall outside their theoretical domain are set to the nearest boundary (delta into [0,1] / [-1,0], gamma and vega to 0 when negative, rho to 0 when its sign is wrong for the option type). That is the only adjustment applied: a value already inside its domain is published exactly as computed, and no scaling or smoothing is applied to any greek.

### 5.6 `close` and `volume`

`close` is published only when the contract traded that session. A last trade price that is merely carried forward from an earlier session is suppressed rather than republished. From 2014-06 onward a second, independent record of trading is cross-checked as well: when it shows no trading for a contract that nonetheless came with a price, the price is withheld.

### 5.7 `last_trade_date`

Computed by rolling forward through the archive: on each day, contracts that traded record that date; contracts that did not carry their previous value. A blank means the contract has not been observed trading at any point in the archive up to that day - **not** that it never traded. In particular, values early in the archive are limited by how far back the archive itself goes.

`quote_date - last_trade_date` is therefore a staleness measure with a floor, not an absolute contract history.

---

## 6. Interest rates

The risk-free rate is the U.S. Treasury daily par yield curve (constant maturity). `manifest.json` records, for every trading day it covers, the curve that was actually used:

```json
"rates": { "2002-03-01": [1.78, 1.77, 2.33, 3.18, 4.43, 4.98, null] }
```

- **Order:** 1 month, 3 months, 1 year, 2 years, 5 years, 10 years, 30 years.
- **Unit:** percent (1.78 means 1.78%). Divide by 100 before use.
- **`null`** means Treasury published no value for that tenor on that date. The most significant case is the 30-year, which the Treasury discontinued from **2002-02-19 to 2006-02-08**. A missing tenor is dropped from the curve; it is never treated as 0%.
- **Interpolation:** linear in time-to-expiry between the two bracketing tenors, with the tenors at 1/12, 0.25, 1, 2, 5, 10 and 30 years; flat outside the first and last available tenor. The time-to-expiry used is the same `T` as in section 5.2, after its calendar adjustments.
- **Bond-market holidays:** on days when the bond market is closed but options trade (Columbus Day, Veterans Day), no curve is published. The most recent curve within the preceding five days is used. When this happens the manifest records it:

```json
"rates_carried_forward": { "2016-10-10": "2016-10-07" }
```

The values stored under the trading date are always the ones actually used, so no reconstruction is required on your side. Every manifest we publish carries `rates` for every day it lists, and `verify.py` checks that a package's manifest does (section 9): seven tenors, each a finite number or `null`, with at least one finite value - a curve of seven `null`s, or one carrying `NaN`, `Infinity` or a boolean, is treated as missing. A package whose manifest lacks usable curves cannot be used to reproduce the calculated columns.

---

## 7. Known limitations

Stated plainly, because you should know them before building on the data:

1. **Adjusted contracts are absent for the whole archive segment, 2002-02-08 through 2026-08-05.** Contracts adjusted for splits, mergers and special dividends (OSI symbols whose root carries a numeric suffix, such as `TSLA1`) do not appear in the end-of-day records the archive segment is built from. They are present in the daily segment from 2026-08-06 onward (23,978 rows on 2026-09-04), so a series that spans the boundary gains these contracts at that date rather than through any corporate action.
2. **Before 2014-06 there is no second witness for `close`.** The volume gate described in section 5.6 still applies, but the independent cross-check is not available for those years, so a small number of stale prices may survive.
3. **`volume` can be marginally overstated.** Reconciled tick-by-tick for a sample day, roughly 2.6% of traded contracts differ, almost always by small amounts; total daily volume differed by 0.014%. Separately, about one archive row in 100,000 arrives from the source with a negative volume; those are published blank rather than passed through (N12).
4. **`bid_size` / `ask_size` are blank before 2005-01-03**, and are unevenly populated for years after that (36% of rows on a sampled 2005 session, 83% on a sampled 2010 session). This is an archive-wide limitation, not a per-row unknown. See N3.
5. **`open_interest` lags by one session** (section 2, column 14). This is the industry convention, not an error, but do not align it with same-day volume without accounting for it.
6. **Binary options are excluded** (e.g. `XSPBX`). Vanilla option models do not describe binary payoffs; a solver would return numbers that look reasonable and mean nothing.
7. **2022-06-30 carries pre-split contracts for two underlyings.** AMZN (20-for-1, effective 2022-06-06) and DXCM (4-for-1, effective 2022-06-13) still list contracts at their pre-split strikes on that day alongside the adjusted ones (about 5,200 rows in total). They are what the source carried; nothing was synthesised. A put-call pairing on that day should be done per strike series, not per underlying.
8. **Check the current manifest for missing trading days and supplementary coverage.** Eleven historical gaps remain in 2002: 05-30, 05-31, 06-14, 06-17, and the trading days from 12-02 through 12-10. Six later dates require supplementary end-of-day records: 2024-06-03, 2026-05-27, 2026-06-17, 2026-07-09, 2026-07-17 and 2026-07-23. As a supplementary file is published, its date leaves `trading_days_missing` and its manifest entry is marked `source: alternate-eod`. These supplementary records have reduced index coverage, including unavailable XSP, DJX and XEO series. The current manifest, rather than this list of candidate dates, identifies which files are available.

9. **Some historical settlement labels are blank.** Identified BKXPM, OSXPM and SOXPM rows have blank `settlement_time` although these series settle PM. Their exercise styles and IV/Greeks calculations are unaffected by this label omission. The correction fills only `settlement_time`; use the matching manifest when checking a corrected file.
10. **Some index quotes are missing on particular dates.** A review of the segment beginning in July 2022 identified affected index series on 2025-01-29, 2025-04-30, 2025-07-30 and 2025-10-29, including NDXP and XEO contracts. Other contracts on these dates remain available. Missing bid/ask inputs can leave midpoint IV and Greeks unavailable; do not replace the blanks with zero. This list is not a claim that the earlier archive has no quote gaps.

---

## 8. Invariants - what is true of every row

Every statement below holds for **every row of every published file**. They are not descriptions of what we usually see: each one is checked on every row before a day is allowed to be published, and a file that violates any of them is not published at all. You can assert them in your loader. If a check fails, first confirm the file checksum and parser settings. If the original file still fails, report its filename and the verifier output to info@historicaldata.net; a failed check must not automatically be attributed to the user.

| Invariant | Holds when |
|---|---|
| The header is exactly the 34 names of section 2, in that order; every row has exactly 34 fields; every non-blank value parses as its column's type in section 2 (a finite decimal number, an integer, a valid date, or one of the listed codes - never NaN, Infinity or text); and the columns marked *never blank* in section 2 are not blank | always |
| `quote_date` equals the date in the filename | always |
| `type` is `call` or `put`; `style` is `A` or `E`; neither is ever blank | always |
| `strike > 0` | always |
| `volume >= 0`; `open_interest >= 0` | when present (N12, N4) |
| `bid_size >= 1` and `bid > 0`; `ask_size >= 1` and `ask > 0` | when the size is present (N3) |
| `active_minutes >= 1` | when present (N14) |
| `bid > 0`; `ask > 0`; `bid <= ask` | when present |
| `underlying_close > 0` | when present |
| `low <= open <= high` and `low <= close <= high` | when the OHLC columns are present |
| `close > 0`, and `close` present implies `volume > 0` | when present (section 5.6) |
| `volume > 0` implies `last_trade_date` equals `quote_date` | always (N12, N7) |
| `iv_flag` is an integer 0-7 and is never blank | always |
| `iv` and the five greeks are present exactly when `iv_flag <= 1`, and all absent otherwise | always (section 4) |
| `iv_bid` present implies `bid > 0`; `iv_ask` present implies `ask > 0` | always (section 4) |
| `iv_bid <= iv <= iv_ask` | when all three are present |
| `0.0001 <= iv <= 5.0`, and the same bounds for `iv_bid` / `iv_ask` | when present (the solver's search interval, section 5.1) |
| `delta` in [0,1] for calls and [-1,0] for puts; `gamma >= 0`; `vega >= 0`; `rho >= 0` for calls and `<= 0` for puts | when present (N5) |
| `settlement_time` is `AM`, `PM` or blank, and `AM` implies `style = E` for every underlying except `SOX` | always (N9) |
| `active_minutes` blank before 2014-06; `multileg_volume` blank before 2019-11-04; the two size columns blank before 2005-01-03; `quote_time` blank before 2026-08-06 | always (whole-era absences, section 2) |

Two things deliberately **not** on this list, because we do not enforce them and you should not assume them:

- **`bid` and `ask` are not both guaranteed present.** A contract with no standing quote has both blank; one-sided quotes are normal, especially for deep out-of-the-money and expiring contracts.
- **`iv` is not guaranteed present.** It is absent whenever `iv_flag > 1`, which is a statement about the quote, not a defect. See section 4.
- **`iv_bid` / `iv_ask` are not guaranteed present even when `iv_flag <= 1`.** They are solved independently of `iv`; a zero bid has no implied volatility, and an inverted pair is discarded. Roughly two thirds of rows carry both. See N6.

---

## 9. Verifying what you received

A verification script, `verify.py`, ships with the free sample and with every purchase. It is pure Python 3 with no dependencies:

```
python3 verify.py                      # every .csv in the current folder
python3 verify.py day_by_date          # a folder, with its manifest beside the files
python3 verify.py --complete day_by_date   # a fixed package or a whole purchase: require every listed file
python3 verify.py 2002-03-01_options.csv
python3 verify.py --lenient mycopy     # files you have edited yourself
python3 verify.py --contract           # list every check and the section it comes from
```

**What it checks.** Three layers, each reported separately:

1. **Structure, on every row** - the first row of the section 8 table: the header is exactly the 34 columns in the documented order, every row has 34 fields, every non-blank value parses as its column's type (a finite number, an integer, a valid date, a listed code - NaN, Infinity and stray text are failures), and the never-blank columns are not blank.
2. **The invariants of section 8, on every row** - all nineteen, and nothing else. Each failure quotes the invariant it violated and names the section it comes from. That correspondence is checked before every release: a promise here with no check behind it would be one you had to take on faith, and a check with no promise behind it would be an undocumented second contract.
3. **The manifest** - every file the manifest lists and you hold matches its recorded SHA-256, byte count and row count; the manifest carries an interest-rate curve for every day it lists (section 6); and the trading days you hold have no unexplained gaps against the U.S. market calendar. A manifest that cannot be parsed is a failure.

**What PASS means.** The summary line states the scope, so a green result never implies more than was examined:

- *Default mode* is strict about content and tolerant about scope. Files the manifest lists that you do not hold are reported as not present, not as failures, because a purchase can be a subset of the archive - the summary says how many of the listed files are present and that completeness was not asserted.
- *`--complete`* also requires the set: a manifest must be present, every file it lists must be here, no unlisted data file may be here, and every listed day must have a rate curve. Use it for the free sample and after downloading a whole purchase. PASS then means: complete and exactly as published.
- *`--lenient`* is for files you have modified yourself. Columns are located by name, checks whose columns are missing are skipped and named, and the result is labelled `PASS (lenient)` with the number of skipped checks - it never asserts the published format.

Exit code `0` means verified and passed, `1` means at least one failure, `2` means nothing was verified (no data files, an empty folder, a usage error). A run that examined no data never returns `0`.

**Revisions and older manifests.** After a revision (section 10) a file matches the current manifest and not an older one you may have kept, such as a rolling-window manifest from before the revision. A file that matches at least one manifest beside it is accepted and the stale manifest is named in a warning; a file that matches none is a failure.

**What it does not do.** It does not re-solve the implied volatilities or the greeks, and that is a decision rather than an omission: checking our numbers with our own formulas would only prove we are self-consistent. Sections 5 and 6 specify the model and every input for your own pricing library - that is the independent check, and it is a different kind of check from the structural and integrity verification this script performs.

Non-fatal warnings are reported separately from failures; a warning is usually a genuine gap in market history rather than a defect.


## 10. Revisions

Published files are never edited silently. When a defect is found, the affected files are recomputed, re-verified against every invariant in section 8, and re-published under the same names; the manifest is regenerated so that each file's SHA-256 is again the one listed. Every such revision is recorded here with its scope, the columns that changed, the reason, and the date. Columns not listed are byte-for-byte unchanged. A copy you saved before a revision still verifies against the checksums you saved with it; only the current manifest describes the current files (section 1.1).

| # | Date | Scope | Columns changed | Reason |
|---|------|-------|-----------------|--------|
| R1 | 2026-08-25 | 12 daily files, 2026-08-06 to 2026-08-21 | `volume` (all rows where it differed); `last_trade_date` (561 rows) | `volume` had been taken from the most recent available daily aggregate rather than the session's own; corrected to the session's aggregate. |
| R2 | 2026-09-03 | 2,078 files, 2014-04-01 to 2022-06-30: rows whose `underlying` is `SPXW` (17,515,487 rows) | `style` (`A` to `E`); `iv`, `iv_bid`, `iv_ask`, `iv_flag`, `delta`, `gamma`, `theta`, `vega`, `rho` | Weekly S&P 500 contracts are European-style and cash-settled. From 2014-04-01 the archive carries them under their own `underlying` symbol, and that symbol was missing from the list that assigns exercise style, so these rows were marked American and priced with the American tree. Earlier files list the same contracts under `SPX` and were already correct. |
| R3 | 2026-09-03 | 43 files (2022-02-23 to 2022-06-30 and 2026-08-06 to 2026-09-01): contracts of the `SPXW` root listed under `underlying` = `SPX` (392,070 rows) | `settlement_time` (blank to `PM`) | The same root rule that fixed R2 also determines settlement time; for these rows it had been left blank where `PM` is the documented value. No other column of these rows changed. |
| R4 | 2026-09-05 to 2026-09-07 | 106 files, five months in 2024-2026 (2024-10, 2024-12, 2025-09, 2026-03, 2026-05) | `last_trade_date` (rows where it was blank or stale) | These five months were first built out of chronological order, so the rolling table behind `last_trade_date` (section 5.7) started empty for each of them and carried no trade observations from before that month. Rebuilt in order. `last_trade_date` only moved forward: rows where it was blank gained a value, and rows that carried a stale earlier date (a long-dated contract's last trade as seen before 2022-07) were updated to the later trade. No other column changed. |

Each revision was verified before re-publication in the same order as an original release: recompute, pass every invariant, upload, update the ledger, confirm the bucket matches the ledger, and only then regenerate the manifest. For R2 an additional check was applied first: recomputing each file with no input changed had to reproduce the published bytes exactly, proving that the inputs, the solver and the interest-rate curve were still those of the original release. R3 changed `settlement_time` only; the Greeks of those rows were not recomputed.
