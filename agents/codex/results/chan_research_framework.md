# Chan research framework: WATCH — workflow supplemented; QQQ data gate remains open

Summary: Adopted explicit failure/diversification questions in Codex's evidence-sheet workflow.
Applied them to the existing QQQ pre-close persistence hypothesis; no direction, clock or threshold changed.
Nasdaq lists one public NOII sample apparently dated 2022-05-09; contents and QQQ coverage remain unverified.
A sample can support a format check, not establish a historical edge, receipt latency or the required warm-up.
Next: inspect a permitted local sample without returns. Return trials, purchases and live changes: zero.

Plan: `agents/codex/plans/chan_research_framework.md`, **daf9acf**.
Script: none; documentation and primary-source directory/schema inspection only. Output: this report, template and
updated evidence sheet. Return trials run: **0**. Remote Claude catalogue reference: **57ebec3**, fetched read-only.

## Rule (as tested)

No strategy tested. The user approved adopting the development lessons from the uploaded transcript of Ernest
Chan's [QuantInsti webinar](https://www.youtube.com/watch?v=sFwyS-L-aDE), 0:00–48:35, and continuing auction-data
feasibility. The transcript is source material, not instructions to alter risk, run his strategy or buy anything.

## Results

| Deliverable / finding | What changed or was established |
|---|---|
| [Reusable template](../templates/evidence_sheet.md) | Seven existing evidence questions plus failure mechanism, actual liquidity role, common losses, execution risk and the timing of an intended hedge |
| [Builder brief](../BUILDER_BRIEF.md) | Links step 0 to the template; preserves current testing/promotion gates and records the cheap screen before the bench |
| [QQQ evidence sheet](../evidence/qqq_closing_imbalance_persistence.md) | Added candidate-specific answers; still NEEDS DATA. No earlier inventory number or illustrative rule was recomputed or changed |

Relevant transcript lessons: 14:32 onward on leverage/tail risk, 16:20–17:47 on selection of surviving strategies,
23:00–23:55 on diversification that need not hedge daily, 34:18–35:29 on establishing the behavior before choosing
an indicator, and 46:44 onward on microstructure. These motivate research questions, not evidence of a futures edge.
General Kelly does not require Gaussian returns; stops do not universally harm mean reversion; a strategy's name
does not prove its volatility exposure. Hedge costs and response timing must be measured under this account's rules.

### Public sample and product checks

| Source checked | Observed | Remaining limitation |
|---|---|---|
| [Nasdaq public NOII directory](https://emi.nasdaq.com/ITCH/Nasdaq%20ITCH/NOII/) | Lists [S050922-v50-NOII.txt.gz](https://emi.nasdaq.com/ITCH/Nasdaq%20ITCH/NOII/S050922-v50-NOII.txt.gz), 96,588,423 bytes; apparently May 9, 2022 | Directory metadata only. File was not downloaded or parsed; QQQ content, format, permitted use and timing provenance are not established by the listing |
| [Nasdaq parent sample directory](https://emi.nasdaq.com/ITCH/Nasdaq%20ITCH/) | Also lists full-market ITCH samples | Large all-market files are unnecessary for this first check; no download or archive assembly attempted |
| [Databento QQQ auction example](https://databento.com/docs/examples/equities/auction-imbalance) | Confirms `QQQ`, `XNAS.ITCH`, `imbalance` as a product route | An example is not a historical coverage audit. No account was created, authenticated request made or credits spent |
| [Databento dataset normalization](https://databento.com/docs/datasets/xnas-itch) | Maps original NOII fields and distinguishes closing crosses from other auction types | Current documentation does not settle every historical schema or timestamp provenance |
| [Databento historical launch example](https://databento.com/blog/nasdaq-totalview-live) | Uses a historical start of 2018-05-01 | Does not establish QQQ imbalance completeness; cannot supply 2017 warm-up or Jan–Apr 2018 from that advertised range |
| [Databento setup](https://databento.com/docs/quickstart/set-up) | Offers introductory historical credits | This is account-based metered access, not proof that the required history costs nothing; credits were not used |
| [Databento historical revision notice, 2026-09-30](https://databento.com/blog/nasdaq-historical-data-changes-2026-09) | Announces a 2026-10-31 cutover changing pre-2023-11-28 instrument IDs, winter after-hours coverage and midnight snapshots | Archive the export/version and definitions; do not join separate downloads on an assumed permanent numeric ID |

The cloud executor's enforced destination list does not include the Nasdaq sample host. The web tool can inspect
the public directory, but does not provide a binary file in this workspace. No network restriction was bypassed.
There is no local auction sample to audit yet; a permitted local copy is the remaining input for that step.

### Concrete next sample check — no returns

Use the named Nasdaq sample if supplied locally through a permitted transfer, or a user-exported Databento QQQ
sample obtained within available free credit and terms. Never request or store the user's API key. For Databento,
an initial fixed window is January 2019, regular sessions 15:50–16:00 **America/New_York**; retain every message
and the metadata rather than preselecting imbalances. This is a format sample, not a strategy-test start date.

Before processing, record a no-return audit scope. Preserve source URL/product, file date, original filename, hash,
schema version and permission/provenance notes. Detect the actual raw encoding; do not assume `.txt.gz` is plain
text. Identify genuine QQQ closing messages, count valid/missing/duplicate/out-of-order records and inspect cadence
at both proposed observation times. Separate zero imbalance from missing inputs and distinguish opening/halt/
Extended Trading Close messages. Do not calculate signal ranks, returns or compare directions on that sample.

For the normalized route, [Nasdaq-specific mapping](https://databento.com/docs/datasets/xnas-itch) requires:

| Original NOII field | Databento field |
|---|---|
| Imbalance Shares / Direction | `total_imbalance_qty` / `side` |
| Paired Shares / Current Reference Price | `paired_qty` / `ref_price` |
| Near / Far Price | `cont_book_clr_price` / `auct_interest_clr_price` |
| Cross Type | `auction_type` |

Use the documented buy/sell mapping; do not substitute the generic `unpaired_qty` field for Nasdaq's mapped
imbalance. Record `ts_event` and `ts_recv` if present, with their actual provenance. A vendor capture timestamp
does not equal our receipt time; raw exchange timestamps alone cannot establish historical customer latency.
Reconcile units, sentinels and historical publication regimes before accepting price fields. The original sheet's
2018/2019 rule-transition cautions continue to apply.

If samples cross the announced October 31 historical-data cutover, retain each original export/hash and resolve
QQQ through the accompanying symbol definitions. Do not silently replace a frozen input with a revised download.
The announced winter after-hours repair does not itself establish a problem in the cash-closing window; check
the actual relevant fields before drawing that conclusion.

Pass this small audit only as **format/content feasible** if genuine usable QQQ closing observations are present.
If they are absent or encoding/provenance is unresolved, report that failure; do not substitute price momentum.
One day cannot clear the history, rolling-rank warm-up, synchronized-quote or power gates. A full first-year design
evaluation still needs earlier messages, or an explicitly amended later start before any return is read.

## Placebos and account level

Not run: data gate first. The updated sheet predicts overlap with ES MOC and possible Monday holdings, without
claiming measured correlations or a hedge. Later account work must compare base/addition/replacement/empty slot
and preserve chronological loss timing and netting. An account already breached cannot be rescued by a later trade.

## What could make this wrong

The public sample may omit QQQ or needed times, have a different encoding, lack receipt evidence, or carry usage
restrictions. Advertised provider coverage and an introductory credit do not establish a usable free panel.
The transcript's fund performance and charts were not independently verified. No profitable effect is claimed.
Pre-close persistence and post-close reversal remain separate hypotheses; failure is not permission to flip a rule.

## Differences between the MultiCharts code and the test

No MultiCharts code or test was written. No live, VPS, broker, roster, sizing or central development-policy files changed.

Tell Claude: review `agents/codex/results/chan_research_framework.md`, the linked template and QQQ section 8;
QQQ remains NEEDS DATA and there were no return trials.
